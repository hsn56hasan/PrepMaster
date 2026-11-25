"""
Konu Yolu (/api/path/*): seviye/konu kilitleri, sonuç kaydı (yıldız + XP), ünite ve karışık tekrar.
İçerik: data/lessons.json (her seviyede 4 ünite x 5 konu = en az 20 gündelik hayat konusu).
"""
import json
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_lesson_path.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "lesson_path_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402
from backend.lesson_path import LessonPath, LEVELS  # noqa: E402

LESSONS = json.loads((BASE_DIR / "data" / "lessons.json").read_text(encoding="utf-8"))


class TestLessonContent(unittest.TestCase):
    def test_every_level_has_at_least_20_topics_with_full_exercises(self):
        levels = {lv["level"]: lv for lv in LESSONS["levels"]}
        self.assertEqual(list(levels), LEVELS)
        ids = set()
        for code, lv in levels.items():
            topics = [t for u in lv["units"] for t in u["topics"]]
            self.assertGreaterEqual(len(topics), 40, code)
            for t in topics:
                self.assertNotIn(t["id"], ids)
                ids.add(t["id"])
                self.assertEqual(len(t["vocab"]), 8, t["id"])
                self.assertEqual(len(t["phrases"]), 5, t["id"])
                self.assertEqual(len(t["quiz"]), 4, t["id"])
                sp = t.get("speaking") or {}
                self.assertEqual([l["who"] for l in sp.get("dialogue", [])], ["A", "B"] * 3, t["id"])
                self.assertEqual(len(sp.get("prompts", [])), 2, t["id"])
                for q in t["quiz"]:
                    self.assertEqual(q["q"].count("___"), 1, t["id"])
                    self.assertEqual(len(q["options"]), 4, t["id"])
                    self.assertTrue(0 <= q["answer"] < 4, t["id"])


class TestLessonPathRules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = LessonPath(json.loads(json.dumps(LESSONS)))

    def test_levels_open_up_to_start_level_only(self):
        self.assertTrue(self.path.level_unlocked({}, "B1", "A1"))
        self.assertTrue(self.path.level_unlocked({}, "B1", "B1"))
        self.assertFalse(self.path.level_unlocked({}, "B1", "B2"))

    def test_next_level_opens_after_80_percent(self):
        order = self.path.topic_order["A1"]
        need = int(len(order) * 0.8)
        prog = {tid: {"stars": 2} for tid in order[:need - 1]}
        self.assertFalse(self.path.level_unlocked(prog, "A1", "A2"))
        prog[order[need - 1]] = {"stars": 1}
        self.assertTrue(self.path.level_unlocked(prog, "A1", "A2"))
        self.assertFalse(self.path.level_unlocked(prog, "A1", "B1"))

    def test_topics_open_in_order(self):
        order = self.path.topic_order["A1"]
        self.assertTrue(self.path.topic_unlocked({}, "A1", order[0]))
        self.assertFalse(self.path.topic_unlocked({}, "A1", order[1]))
        self.assertTrue(self.path.topic_unlocked({order[0]: {"stars": 1}}, "A1", order[1]))
        self.assertFalse(self.path.topic_unlocked({order[0]: {"stars": 0}}, "A1", order[1]))

    def test_overview_marks_current_and_unit_review(self):
        order = self.path.topic_order["A1"]
        prog = {tid: {"stars": 3, "best_pct": 100, "xp_total": 15} for tid in order[:5]}
        ov = self.path.overview(prog, "A1", "A1")
        self.assertEqual(ov["current_topic"], order[5])
        self.assertTrue(ov["units"][0]["review_unlocked"])
        self.assertFalse(ov["units"][1]["review_unlocked"])
        self.assertEqual(ov["stats"]["xp_total"], 75)
        self.assertEqual(ov["stats"]["perfect"], 5)
        self.assertNotIn('"_level"', json.dumps(ov))
        self.assertNotIn('"_unit"', json.dumps(ov))

    def test_review_prefers_weakest_topics(self):
        order = self.path.topic_order["A1"]
        prog = {order[0]: {"stars": 3, "last_at": "2026-01-02"}, order[1]: {"stars": 1, "last_at": "2026-01-03"},
                order[2]: {"stars": 2, "last_at": "2026-01-01"}}
        b = self.path.review_bundle(prog, "A1")
        self.assertEqual([t["id"] for t in b["topics"]], [order[1], order[2], order[0]])


class TestLessonPathApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app_module.app)
        cls.suffix = str(os.getpid())
        cls.order = app_module.lesson_path.topic_order["A1"]

    @classmethod
    def tearDownClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_lesson_path.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def _register(self, username, level="A1"):
        username = f"{username}_{self.suffix}"
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": f"{username}@example.com", "username": username,
            "password": "Parola123!", "full_name": "Yol Test", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        h = {"Authorization": f"Bearer {d['token']}"}
        r = self.client.post("/api/placement/result", json={"level": level}, headers=h)
        self.assertEqual(r.status_code, 200, r.text)
        return d["user"]["id"], h

    def test_requires_login(self):
        self.assertEqual(self.client.get("/api/path/overview").status_code, 401)
        self.assertEqual(self.client.post("/api/path/result", json={"node_id": "a1-01", "correct": 1, "total": 1}).status_code, 401)

    def test_overview_starts_at_placement_level(self):
        _, h = self._register("yol_b1", "B1")
        ov = self.client.get("/api/path/overview", headers=h).json()
        self.assertEqual(ov["start_level"], "B1")
        unlocked = {l["level"]: l["unlocked"] for l in ov["levels"]}
        self.assertTrue(unlocked["A1"] and unlocked["B1"])
        self.assertFalse(unlocked["B2"])
        self.assertEqual(ov["stats"]["total"], sum(len(app_module.lesson_path.topic_order[L]) for L in LEVELS))

    def test_locked_topic_cannot_be_opened_or_scored(self):
        _, h = self._register("yol_kilit")
        self.assertEqual(self.client.get(f"/api/path/topic/{self.order[1]}", headers=h).status_code, 403)
        r = self.client.post("/api/path/result", json={"node_id": self.order[1], "correct": 13, "total": 13}, headers=h)
        self.assertEqual(r.status_code, 403)
        self.assertEqual(self.client.get("/api/path/topic/a2-01", headers=h).status_code, 403)
        self.assertEqual(self.client.get("/api/path/topic/yok-99", headers=h).status_code, 404)

    def test_result_stars_xp_and_unlock_flow(self):
        _, h = self._register("yol_akis")
        t = self.client.get(f"/api/path/topic/{self.order[0]}", headers=h)
        self.assertEqual(t.status_code, 200)
        self.assertEqual(len(t.json()["topics"][0]["vocab"]), 8)

        fail = self.client.post("/api/path/result", json={"node_id": self.order[0], "correct": 5, "total": 13}, headers=h).json()
        self.assertEqual((fail["stars"], fail["xp_gained"], fail["next_topic"]), (0, 0, None))
        self.assertEqual(self.client.get(f"/api/path/topic/{self.order[1]}", headers=h).status_code, 403)

        ok = self.client.post("/api/path/result", json={"node_id": self.order[0], "correct": 13, "total": 13}, headers=h).json()
        self.assertEqual(ok["stars"], 3)
        self.assertEqual(ok["xp_gained"], 15)
        self.assertTrue(ok["first_completion"])
        self.assertEqual(ok["next_topic"], self.order[1])
        self.assertEqual(self.client.get(f"/api/path/topic/{self.order[1]}", headers=h).status_code, 200)

        # Daha kötü tekrar en iyi yıldızı düşürmez
        again = self.client.post("/api/path/result", json={"node_id": self.order[0], "correct": 10, "total": 13}, headers=h).json()
        self.assertEqual((again["stars"], again["best_stars"], again["xp_gained"]), (2, 3, 10))
        self.assertFalse(again["first_completion"])
        self.assertEqual(again["xp_total"], 25)

        ov = self.client.get("/api/path/overview?level=A1", headers=h).json()
        self.assertEqual(ov["current_topic"], self.order[1])
        self.assertEqual(ov["units"][0]["topics"][0]["stars"], 3)

    def test_correct_is_clamped_and_validated(self):
        _, h = self._register("yol_dogrula")
        r = self.client.post("/api/path/result", json={"node_id": self.order[0], "correct": 99, "total": 13}, headers=h)
        self.assertEqual(r.status_code, 422)
        r = self.client.post("/api/path/result", json={"node_id": "A1-01; DROP", "correct": 1, "total": 1}, headers=h)
        self.assertEqual(r.status_code, 422)
        r = self.client.post("/api/path/result", json={"node_id": "zz-01", "correct": 1, "total": 1}, headers=h)
        self.assertEqual(r.status_code, 404)

    def test_unit_review_and_mixed_review(self):
        _, h = self._register("yol_unite")
        self.assertEqual(self.client.get("/api/path/review?level=A1", headers=h).status_code, 404)
        self.assertEqual(self.client.get("/api/path/unit/a1-u1", headers=h).status_code, 403)
        for tid in self.order[:5]:
            r = self.client.post("/api/path/result", json={"node_id": tid, "correct": 12, "total": 13}, headers=h)
            self.assertEqual(r.status_code, 200, r.text)
        u = self.client.get("/api/path/unit/a1-u1", headers=h)
        self.assertEqual(u.status_code, 200)
        self.assertEqual(len(u.json()["topics"]), 5)
        r = self.client.post("/api/path/result", json={"node_id": "a1-u1", "correct": 15, "total": 15}, headers=h).json()
        self.assertEqual(r["xp_gained"], 20)
        rev = self.client.get("/api/path/review?level=A1", headers=h)
        self.assertEqual(rev.status_code, 200)
        self.assertEqual(rev.json()["id"], "review-a1")
        self.assertEqual(len(rev.json()["topics"]), 4)
        r = self.client.post("/api/path/result", json={"node_id": "review-a1", "correct": 14, "total": 15}, headers=h).json()
        self.assertEqual(r["xp_gained"], 10)
        ov = self.client.get("/api/path/overview?level=A1", headers=h).json()
        self.assertEqual(ov["units"][0]["review_stars"], 3)


if __name__ == "__main__":
    unittest.main()
