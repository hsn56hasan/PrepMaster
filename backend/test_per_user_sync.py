"""
Kullanıcı bazlı veri + web/mobil eşitleme testleri (14.11.2026, YOL-HARITASI #11).

"Mobil" istekleri, mobil uygulamanın gönderdiği gövdelerin aynısıyla taklit edilir
(Outbox.buildPushBody -> /api/sync/push, ardından /api/sync/pull).
"""

import json
import os
import sqlite3
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_per_user_sync.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "per_user_sync_suite_secret_key_2026_qwerty"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec

DATA = BASE_DIR / "data"
QUESTIONS = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
VOCAB = json.loads((DATA / "vocabulary.json").read_text(encoding="utf-8"))


def wrong_of(q):
    return next(o["key"] for o in q["options"] if o["key"] != q["correct_answer"])


class TestPerUserSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p in BASE_DIR.joinpath("backend").glob("test_per_user_sync.db*"):
            p.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        for p in BASE_DIR.joinpath("backend").glob("test_per_user_sync*.db*"):
            try:
                p.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False

    def _register(self, username):
        res = self.client.post("/api/auth/register", json={
            "email": f"{username}@example.com", "username": username, "password": "Parola123!",
            "full_name": "Test Ogrenci", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    # ------------------------------------------------------------ yalıtım
    def test_users_do_not_see_each_others_data(self):
        _, a = self._register("ayse")
        _, b = self._register("burak")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        w = VOCAB[0]["id"]

        self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 30,
            "answers": {q["id"]: wrong_of(q)},
        }, headers=a)
        self.client.post(f"/api/vocabulary/{w}/status", json={"status": "mastered"}, headers=a)

        # A görüyor
        self.assertTrue(any(m["question_id"] == q["id"] for m in self.client.get("/api/mistakes", headers=a).json()))
        self.assertEqual(len(self.client.get("/api/exam/history", headers=a).json()), 1)
        self.assertEqual(self.client.get("/api/stats", headers=a).json()["mastered_vocab"], 1)

        # B görmüyor
        self.assertEqual(self.client.get("/api/mistakes", headers=b).json(), [])
        self.assertEqual(self.client.get("/api/exam/history", headers=b).json(), [])
        stats_b = self.client.get("/api/stats", headers=b).json()
        self.assertEqual(stats_b["mastered_vocab"], 0)
        self.assertEqual(stats_b["unresolved_mistakes"], 0)
        vocab_b = {v["id"]: v["status"] for v in self.client.get("/api/vocabulary", headers=b).json()}
        self.assertEqual(vocab_b[w], "unreviewed")
        pull_b = self.client.get("/api/sync/pull", headers=b).json()
        self.assertEqual((pull_b["mistakes"], pull_b["vocab_progress"], pull_b["exam_history"]), ([], {}, []))

        # B, A'nın hatasını silemez/çözemez
        self.client.post(f"/api/mistakes/{q['id']}/resolve", headers=b)
        self.client.delete(f"/api/mistakes/{q['id']}", headers=b)
        self.assertTrue(any(m["question_id"] == q["id"] for m in self.client.get("/api/mistakes", headers=a).json()))

    def test_profile_is_per_user(self):
        _, a = self._register("profila")
        _, b = self._register("profilb")
        self.client.post("/api/profile", json={"university_id": "boun", "current_level": "C1"}, headers=a)
        self.assertEqual(self.client.get("/api/profile", headers=a).json()["current_level"], "C1")
        self.assertEqual(self.client.get("/api/profile", headers=b).json()["current_level"], "B2")

    def test_progress_endpoints_require_login(self):
        for method, url in [("get", "/api/profile"), ("get", "/api/mistakes"), ("get", "/api/stats"),
                            ("get", "/api/exam/history"), ("get", "/api/sync/pull"), ("get", "/api/report/summary"),
                            ("post", "/api/sync/push"), ("post", "/api/mistakes/x/resolve"), ("delete", "/api/mistakes/x")]:
            kwargs = {"json": {}} if method == "post" else {}
            res = getattr(self.client, method)(url, **kwargs)
            self.assertEqual(res.status_code, 401, f"{method.upper()} {url} -> {res.status_code}")
        q = QUESTIONS[0]
        res = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": "B2", "duration_seconds": 1, "answers": {q["id"]: "A"}})
        self.assertEqual(res.status_code, 401)
        res = self.client.post(f"/api/vocabulary/{VOCAB[0]['id']}/status", json={"status": "mastered"})
        self.assertEqual(res.status_code, 401)

    # ------------------------------------------------------------ web <-> mobil
    def test_mobile_offline_changes_appear_on_web(self):
        uid, auth = self._register("mobilci")
        q1, q2 = QUESTIONS[10], QUESTIONS[11]
        w1, w2 = VOCAB[5]["id"], VOCAB[6]["id"]
        # Mobilin çevrimdışı giden kutusu (Outbox.buildPushBody biçimi)
        push = {
            "profile": {"university_id": "metu", "current_level": "C1"},
            "mistakes": [
                {"question_id": q1["id"], "university_id": q1["university_id"], "level": q1["level"],
                 "category": q1["category"], "last_wrong_answer": wrong_of(q1), "last_wrong_at": "2026-11-14 10:00:00"},
                {"question_id": q2["id"], "university_id": q2["university_id"], "level": q2["level"],
                 "category": q2["category"], "last_wrong_answer": wrong_of(q2), "last_wrong_at": "2026-11-14 10:01:00"},
            ],
            "resolved_mistakes": [q2["id"]],  # çevrimdışıyken önce yanlış, sonra doğru yaptı
            "vocab_progress": {w1: "mastered", w2: "learning"},
            "exam_attempts": [{"university_id": "metu", "level": "C1", "score": 60, "total_questions": 5,
                               "correct_count": 3, "duration_seconds": 300, "answers": {}, "created_at": "2026-11-14T10:05:00"}],
        }
        res = self.client.post("/api/sync/push", json=push, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)

        # Web aynı veriyi görüyor
        web_mistakes = [m["question_id"] for m in self.client.get("/api/mistakes", headers=auth).json()]
        self.assertEqual(web_mistakes, [q1["id"]])
        profile = self.client.get("/api/profile", headers=auth).json()
        self.assertEqual((profile["university_id"], profile["current_level"]), ("metu", "C1"))
        vocab = {v["id"]: v["status"] for v in self.client.get("/api/vocabulary", headers=auth).json()}
        self.assertEqual((vocab[w1], vocab[w2]), ("mastered", "learning"))
        hist = self.client.get("/api/exam/history", headers=auth).json()
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["score"], 60)
        # Telefonda çevrimdışı çalışma da seriye işlenir
        self.assertEqual(self.client.get("/api/stats", headers=auth).json()["profile"]["streak_days"], 1)

    def test_web_resolution_reaches_mobile_and_is_not_resurrected(self):
        _, auth = self._register("ikicihaz")
        q = QUESTIONS[20]
        # Mobilde yanlış (çevrimiçi)
        self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 10,
            "answers": {q["id"]: wrong_of(q)}}, headers=auth)
        self.assertIn(q["id"], [m["question_id"] for m in self.client.get("/api/sync/pull", headers=auth).json()["mistakes"]])
        # Web'de çözüldü
        self.client.post(f"/api/mistakes/{q['id']}/resolve", headers=auth)
        # Mobil eşitler: giden kutusu boş (kendi değişikliği yok) -> yalnızca çeker
        pull = self.client.get("/api/sync/pull", headers=auth).json()
        self.assertNotIn(q["id"], [m["question_id"] for m in pull["mistakes"]])
        # Mobil, başka bir şey değiştirip gönderse bile çözülmüş hata geri gelmez
        self.client.post("/api/sync/push", json={"vocab_progress": {VOCAB[9]["id"]: "learning"}}, headers=auth)
        self.assertEqual(self.client.get("/api/mistakes", headers=auth).json(), [])

    def test_mobile_offline_wrong_again_reopens_resolved_mistake(self):
        _, auth = self._register("tekraryanlis")
        q = QUESTIONS[30]
        self.client.post("/api/exam/submit", json={"university_id": "general", "level": q["level"],
                         "duration_seconds": 5, "answers": {q["id"]: wrong_of(q)}}, headers=auth)
        self.client.post(f"/api/mistakes/{q['id']}/resolve", headers=auth)
        self.client.post("/api/sync/push", json={"mistakes": [{"question_id": q["id"], "last_wrong_answer": wrong_of(q)}]},
                         headers=auth)
        self.assertEqual([m["question_id"] for m in self.client.get("/api/mistakes", headers=auth).json()], [q["id"]])

    def test_sync_push_rejects_garbage_values(self):
        _, auth = self._register("copcu")
        res = self.client.post("/api/sync/push", json={
            "profile": {"university_id": "hogwarts", "current_level": "Z9", "target_score": 5000},
            "vocab_progress": {VOCAB[1]["id"]: "hacked"},
            "exam_attempts": [{"score": 9999, "total_questions": -4}],
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        p = self.client.get("/api/profile", headers=auth).json()
        self.assertEqual((p["university_id"], p["current_level"], p["target_score"]), ("itu", "B2", 100))
        self.assertEqual(self.client.get("/api/sync/pull", headers=auth).json()["vocab_progress"], {})
        self.assertEqual(self.client.get("/api/exam/history", headers=auth).json()[0]["score"], 100.0)

    # ------------------------------------------------------------ göç
    def test_migration_from_old_schema_keeps_rows_and_backs_up(self):
        old_path = BASE_DIR / "backend" / "test_per_user_sync_eski.db"
        for p in BASE_DIR.joinpath("backend").glob("test_per_user_sync_eski.db*"):
            p.unlink()
        c = sqlite3.connect(old_path)
        c.executescript("""
            CREATE TABLE vocab_progress (word_id TEXT PRIMARY KEY, user_id INTEGER DEFAULT 1, status TEXT,
                                         review_count INTEGER DEFAULT 1, last_reviewed TEXT);
            CREATE TABLE mistake_vault (question_id TEXT PRIMARY KEY, user_id INTEGER DEFAULT 1, university_id TEXT,
                                        level TEXT, category TEXT, wrong_count INTEGER DEFAULT 1, last_wrong_answer TEXT,
                                        last_wrong_at TEXT, is_resolved INTEGER DEFAULT 0, resolved_at TEXT);
            CREATE TABLE question_bookmarks (question_id TEXT PRIMARY KEY, user_id INTEGER DEFAULT 1, note TEXT,
                                             created_at TEXT);
            INSERT INTO vocab_progress (word_id, status) VALUES ('v-1', 'mastered');
            INSERT INTO mistake_vault (question_id, user_id, university_id, wrong_count) VALUES ('q-1', 1, 'itu', 3);
            INSERT INTO mistake_vault (question_id, user_id, university_id) VALUES ('q-2', 7, 'boun');
        """)
        c.commit()
        c.close()

        original = db.DB_PATH
        try:
            db.DB_PATH = old_path
            db.init_db()
            db.init_db()  # ikinci çalıştırma bir şey bozmamalı
            self.assertEqual(db.get_vocab_progress(1), {"v-1": "mastered"})
            self.assertEqual([m["question_id"] for m in db.get_mistakes(1)], ["q-1"])
            self.assertEqual(db.get_mistakes(1)[0]["wrong_count"], 3)
            self.assertEqual([m["question_id"] for m in db.get_mistakes(7)], ["q-2"])
            # artık iki kullanıcı aynı soruyu ayrı ayrı tutabiliyor
            db.record_mistake(7, "q-1", "itu", "B2", "General", "C")
            self.assertEqual(db.get_mistakes(1)[0]["wrong_count"], 3)
            pk = [r[1] for r in sqlite3.connect(old_path).execute("PRAGMA table_info(mistake_vault)") if r[5]]
            self.assertEqual(pk, ["user_id", "question_id"])
            backups = list(old_path.parent.glob(old_path.name + ".yedek-kullanici-gocu-*"))
            self.assertEqual(len(backups), 1, "Göçten önce tek bir yedek alınmalı")
        finally:
            db.DB_PATH = original
            for p in BASE_DIR.joinpath("backend").glob("test_per_user_sync_eski.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
