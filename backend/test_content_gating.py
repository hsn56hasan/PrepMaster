"""
Kilitli üniversite içeriği (dinleme / konuşma) yalnızca erişimi olana gider.
Eskiden /api/listening ve /api/speaking her şeyi herkese döndürüyordu; APK ve web aynı açığı paylaşıyordu.
"""
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_content_gating.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "gating_suite_secret_key_2026_qazwsxedcrfv"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec


class TestContentGating(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False

    def _register(self, username):
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": f"{username}@example.com", "username": username,
            "password": "Parola123!", "full_name": "Kilit Test", "university_id": "itu"})
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    def _unis(self, items):
        return {i.get("university_id") for i in items}

    def test_anonymous_sees_only_general_listening_and_speaking(self):
        for path in ("/api/listening", "/api/speaking", "/api/listening?university_id=boun",
                     "/api/speaking?university_id=boun"):
            items = self.client.get(path).json()
            self.assertTrue(items, path)
            self.assertEqual(self._unis(items), {"general"}, path)

    def test_locked_detail_is_403_and_general_detail_is_open(self):
        locked_l = next(i for i in app_module.listening_data if i["university_id"] == "boun")
        locked_s = next(i for i in app_module.speaking_data if i["university_id"] == "boun")
        open_l = next(i for i in app_module.listening_data if i["university_id"] == "general")
        self.assertEqual(self.client.get(f"/api/listening/{locked_l['id']}").status_code, 403)
        self.assertEqual(self.client.get(f"/api/speaking/{locked_s['id']}").status_code, 403)
        self.assertEqual(self.client.get(f"/api/listening/{open_l['id']}").status_code, 200)
        _, auth = self._register("kilitli1")
        self.assertEqual(self.client.get(f"/api/listening/{locked_l['id']}", headers=auth).status_code, 403)

    def test_unlocked_university_content_becomes_visible(self):
        uid, auth = self._register("acik1")
        db.unlock_university_membership(uid, "boun")
        items = self.client.get("/api/listening?university_id=boun", headers=auth).json()
        self.assertIn("boun", self._unis(items))
        self.assertNotIn("metu", self._unis(self.client.get("/api/listening", headers=auth).json()))
        locked_s = next(i for i in app_module.speaking_data if i["university_id"] == "boun")
        self.assertEqual(self.client.get(f"/api/speaking/{locked_s['id']}", headers=auth).status_code, 200)


if __name__ == "__main__":
    unittest.main()
