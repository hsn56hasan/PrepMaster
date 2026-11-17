"""
DoS / flood koruması regresyon testleri.
"""

import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_dos_protection.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "dos_protection_suite_secret_key_2026_abcdefgh"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec


def _find_dos_middleware():
    stack = app.middleware_stack or app.build_middleware_stack()
    node = stack
    while node is not None:
        if isinstance(node, sec.DoSProtectionMiddleware):
            return node
        node = getattr(node, "app", None)
    raise AssertionError("DoSProtectionMiddleware bulunamadı")


class TestDoSProtection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        db.init_db()
        cls.client = TestClient(app)
        cls.client.get("/api/universities")  # ara katman yığını kurulsun
        cls.mw = _find_dos_middleware()

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_PATH.exists():
            try:
                TEST_DB_PATH.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()
        self._saved = (self.mw.burst_count, self.mw.api_per_min, self.mw.strikes_to_ban, self.mw.max_body)

    def tearDown(self):
        self.mw.burst_count, self.mw.api_per_min, self.mw.strikes_to_ban, self.mw.max_body = self._saved
        sec.rate_limiter.reset()

    def test_burst_flood_gets_429_with_retry_after(self):
        self.mw.burst_count = 5
        codes = [self.client.get("/api/universities").status_code for _ in range(8)]
        self.assertEqual(codes[:5], [200] * 5)
        self.assertIn(429, codes[5:])
        res = self.client.get("/api/universities")
        self.assertEqual(res.status_code, 429)
        self.assertIn("Retry-After", res.headers)

    def test_repeat_offender_is_temporarily_banned(self):
        self.mw.burst_count = 2
        self.mw.strikes_to_ban = 3
        for _ in range(10):
            self.client.get("/api/universities")
        # Patlama penceresi sıfırlansa bile yasak sürer
        sec.rate_limiter.reset("dos:burst:testclient")
        res = self.client.get("/api/universities")
        self.assertEqual(res.status_code, 429)
        self.assertIn("geçici olarak durduruldu", res.json()["detail"])

    def test_oversized_body_rejected_with_413(self):
        self.mw.max_body = 1024
        res = self.client.post("/api/auth/login", content=b"x" * 5000,
                               headers={"Content-Type": "application/json"})
        self.assertEqual(res.status_code, 413)

    def test_normal_usage_unaffected(self):
        for _ in range(20):
            self.assertEqual(self.client.get("/api/universities").status_code, 200)

    def test_railway_client_ip_header_separates_users(self):
        saved = sec.CLIENT_IP_HEADER
        sec.CLIENT_IP_HEADER = "X-Real-IP"
        try:
            self.mw.burst_count = 3
            for _ in range(5):
                self.client.get("/api/universities", headers={"X-Real-IP": "203.0.113.10"})
            blocked = self.client.get("/api/universities", headers={"X-Real-IP": "203.0.113.10"})
            other = self.client.get("/api/universities", headers={"X-Real-IP": "198.51.100.20"})
            self.assertEqual(blocked.status_code, 429)
            self.assertEqual(other.status_code, 200, "Bir kullanıcının sınırı diğerini etkilememeli")
        finally:
            sec.CLIENT_IP_HEADER = saved

    def test_admin_login_requires_env_password_in_production(self):
        saved = app_module.ADMIN_PASSWORD
        app_module.ADMIN_PASSWORD = ""
        try:
            res = self.client.post("/api/admin/login", json={"username": "admin", "password": "PrepMasterAdmin2026!"})
            self.assertEqual(res.status_code, 503)
            self.assertNotIn("token", res.json())
        finally:
            app_module.ADMIN_PASSWORD = saved

    def test_support_and_kvkk_endpoints(self):
        info = self.client.get("/api/support/info").json()
        self.assertEqual(info["email"], "prepmasteryonetici@gmail.com")
        self.assertEqual(info["phone"], "05398381887")
        self.assertEqual(len(info["documents"]), 5)

        kvkk_page = self.client.get("/kvkk")
        self.assertEqual(kvkk_page.status_code, 200)
        self.assertIn("6698 Sayılı Kişisel Verilerin Korunması Kanunu", kvkk_page.text)
        self.assertIn("prepmasteryonetici@gmail.com", kvkk_page.text)
        self.assertIn("0539 838 18 87", kvkk_page.text)

        t_res = self.client.post("/api/support/ticket", json={
            "category": "KVKK Başvurusu",
            "full_name": "Test Öğrenci",
            "email": "test@itu.edu.tr",
            "phone": "05398381887",
            "message": "KVKK kapsamında veri işleme bilgisi talep ediyorum."
        })
        self.assertEqual(t_res.status_code, 200, t_res.text)
        self.assertTrue(t_res.json()["success"])

    # Aynı IP'yi paylaşan öğrenciler (yurt/kampüs/CGNAT) birbirini kilitlememeli
    def test_logged_in_students_behind_same_ip_have_separate_budgets(self):
        self.mw.burst_count = 5
        ta = {"Authorization": "Bearer " + sec.create_session_token(901, "ogr_a", "a@x.com")[0]}
        tb = {"Authorization": "Bearer " + sec.create_session_token(902, "ogr_b", "b@x.com")[0]}
        for _ in range(5):
            self.assertNotEqual(self.client.get("/api/config", headers=ta).status_code, 429)
        self.assertEqual(self.client.get("/api/config", headers=ta).status_code, 429)  # A kotasını bitirdi
        self.assertNotEqual(self.client.get("/api/config", headers=tb).status_code, 429)  # B etkilenmez
        self.assertNotEqual(self.client.get("/api/config").status_code, 429)  # girişsiz ziyaretçi de

    def test_forged_token_falls_back_to_ip_budget(self):
        self.mw.burst_count = 3
        for i in range(3):
            self.client.get("/api/config", headers={"Authorization": f"Bearer sahte.{i}.token"})
        self.assertEqual(self.client.get("/api/config", headers={"Authorization": "Bearer sahte.9.token"}).status_code, 429)

    def test_static_files_do_not_consume_budget(self):
        self.mw.burst_count = 3
        for _ in range(10):
            self.assertNotEqual(self.client.get("/robots.txt").status_code, 429)
        self.assertNotEqual(self.client.get("/api/config").status_code, 429)


if __name__ == "__main__":
    unittest.main()
