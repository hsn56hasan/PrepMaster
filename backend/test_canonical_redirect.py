"""
Asıl alan adına yönlendirme (CANONICAL_HOST): sayfalar 301 ile taşınır, API ve APK taşınmaz.
"""
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))
os.environ["PREPMASTER_DB_PATH"] = str(BASE_DIR / "backend" / "test_canonical_redirect.db")
os.environ["SECRET_KEY"] = "canonical_suite_secret_key_2026_plmoknijb"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.security as sec

OLD = "prepmaster-web-production.up.railway.app"


class TestCanonicalRedirect(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.CANONICAL_HOST = "prepkampus.com"
        self.addCleanup(setattr, app_module, "CANONICAL_HOST", "")

    def get(self, path, host):
        return self.client.get(path, headers={"host": host}, follow_redirects=False)

    def test_pages_on_old_hosts_move_permanently(self):
        for host in (OLD, "www.prepkampus.com", "prepkampus.online"):
            r = self.get("/kvkk?x=1", host)
            self.assertEqual(r.status_code, 301, host)
            self.assertEqual(r.headers["location"], "https://prepkampus.com/kvkk?x=1")

    def test_api_and_apk_are_never_redirected(self):
        self.assertEqual(self.get("/api/config", OLD).status_code, 200)
        r = self.get("/api/download/apk", OLD)
        self.assertNotEqual(r.status_code, 301)

    def test_canonical_and_local_hosts_served(self):
        self.assertEqual(self.get("/kvkk", "prepkampus.com").status_code, 200)
        self.assertEqual(self.get("/kvkk", "127.0.0.1:8050").status_code, 200)

    def test_off_by_default(self):
        app_module.CANONICAL_HOST = ""
        self.assertEqual(self.get("/kvkk", OLD).status_code, 200)


if __name__ == "__main__":
    unittest.main()
