"""
Panel özeti (/api/dashboard/overview): bölüm/kur ilerlemesi, kategoriye göre hatalar, günün planı.
İlerleme question_progress tablosundan gelir; deneme ve pratik cevapları buraya yazılır.
"""
import json
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_dashboard_overview.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "dashboard_overview_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402

QUESTIONS = json.loads((BASE_DIR / "data" / "questions.json").read_text(encoding="utf-8"))


def wrong_of(q):
    return next(o["key"] for o in q["options"] if o["key"] != q["correct_answer"])


class TestDashboardOverview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Başka test modülleri önce yüklendiyse onların veritabanı kullanılır; DB_PATH değiştirilmez.
        db.init_db()
        cls.client = TestClient(app_module.app)
        cls.suffix = str(os.getpid())

    @classmethod
    def tearDownClass(cls):
        # Yalnız tek başına çalıştırıldığında kendi dosyasını siler
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_dashboard_overview.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def _register(self, username):
        username = f"{username}_{self.suffix}"
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": f"{username}@example.com", "username": username,
            "password": "Parola123!", "full_name": "Panel Test", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/dashboard/overview").status_code, 401)

    def test_general_pool_progress_mistakes_and_plan(self):
        _, h = self._register("panel_genel")
        b2 = [q for q in QUESTIONS if q["id"].startswith("q-orj-b2-")]
        grammar = [q for q in b2 if q["category"] == "Grammar"][:3]
        self.assertEqual(len(grammar), 3)

        # 2 doğru, 1 yanlış pratik cevabı
        for q, key in ((grammar[0], grammar[0]["correct_answer"]), (grammar[1], grammar[1]["correct_answer"]),
                       (grammar[2], wrong_of(grammar[2]))):
            r = self.client.post("/api/practice/answer", json={"question_id": q["id"], "chosen_answer": key}, headers=h)
            self.assertEqual(r.status_code, 200, r.text)

        data = self.client.get("/api/dashboard/overview?level=B2", headers=h).json()
        self.assertEqual(data["pool"], "general")
        self.assertEqual(data["level"], "B2")
        self.assertEqual(sum(s["total"] for s in data["sections"]), len(b2))
        g = next(s for s in data["sections"] if s["category"] == "Grammar")
        self.assertEqual((g["answered"], g["correct"]), (3, 2))
        b2_level = next(lv for lv in data["levels"] if lv["level"] == "B2")
        self.assertEqual((b2_level["answered"], b2_level["correct"]), (3, 2))
        self.assertEqual(data["kpis"]["unresolved_mistakes"], 1)
        self.assertEqual(data["mistakes_by_category"], {"Grammar": 1})

        plan = {p["id"]: p for p in data["plan"]}
        self.assertEqual(plan["vocab"]["target"], 20)
        self.assertIn("weakest", plan)
        self.assertEqual(plan["mistakes"]["done"], 0)

        # Yanlış soru tekrar doğru cevaplanınca kasadan çıkar ve bugünün çözümü sayılır
        self.client.post("/api/practice/answer", json={"question_id": grammar[2]["id"],
                                                       "chosen_answer": grammar[2]["correct_answer"]}, headers=h)
        data = self.client.get("/api/dashboard/overview?level=B2", headers=h).json()
        g = next(s for s in data["sections"] if s["category"] == "Grammar")
        self.assertEqual(g["correct"], 3)
        self.assertEqual(data["kpis"]["unresolved_mistakes"], 0)
        self.assertEqual({p["id"]: p for p in data["plan"]}["mistakes"]["done"], 1)

    def test_exam_submit_counts_towards_progress_and_school_pool_after_unlock(self):
        uid, h = self._register("panel_okul")
        db.unlock_university_membership(uid, "itu")
        itu_b1 = [q for q in QUESTIONS if q["university_id"] == "itu" and q["level"] == "B1"]
        picked = itu_b1[:4]
        answers = {q["id"]: q["correct_answer"] for q in picked}
        answers[picked[3]["id"]] = wrong_of(picked[3])
        r = self.client.post("/api/exam/submit", json={
            "university_id": "itu", "level": "B1", "duration_seconds": 120, "answers": answers,
        }, headers=h)
        self.assertEqual(r.status_code, 200, r.text)

        data = self.client.get("/api/dashboard/overview?level=B1", headers=h).json()
        self.assertEqual(data["pool"], "school")
        self.assertEqual(sum(s["total"] for s in data["sections"]), len(itu_b1))
        b1 = next(lv for lv in data["levels"] if lv["level"] == "B1")
        self.assertEqual((b1["total"], b1["answered"], b1["correct"]), (len(itu_b1), 4, 3))
        self.assertEqual(data["kpis"]["exams_taken"], 1)

    def test_resolving_an_already_resolved_mistake_does_not_count_twice(self):
        uid, _ = self._register("panel_tekrar")
        q = next(x for x in QUESTIONS if x["id"].startswith("q-orj-a1-"))
        db.record_mistake(uid, q["id"], "general", "A1", q["category"], "A")
        db.resolve_mistake(uid, q["id"])
        db.resolve_mistake(uid, q["id"])
        self.assertEqual(db.get_today_activity(uid)["mistakes_resolved"], 1)


if __name__ == "__main__":
    unittest.main()
