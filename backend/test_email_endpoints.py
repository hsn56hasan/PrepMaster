"""
E-posta endpoint ve arka plan bildirimi entegrasyon testleri.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_email_endpoints.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "email_endpoints_suite_secret_key_2026_abcd"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec


class TestEmailEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_email_endpoints.db*"):
                p.unlink()
        db.init_db()
        cls.client = TestClient(app)
        cls._saved_admin_pw = app_module.ADMIN_PASSWORD
        if not app_module.ADMIN_PASSWORD:
            app_module.ADMIN_PASSWORD = "TestAdminEmailPass2026!"

    @classmethod
    def tearDownClass(cls):
        app_module.ADMIN_PASSWORD = cls._saved_admin_pw
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_email_endpoints.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def _admin_headers(self):
        res = self.client.post("/api/admin/login", json={
            "username": app_module.ADMIN_USERNAME,
            "password": app_module.ADMIN_PASSWORD,
        })
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['token']}"}

    def test_admin_email_endpoints_require_admin_auth(self):
        self.assertEqual(self.client.get("/api/admin/email/status").status_code, 401)
        self.assertEqual(self.client.post("/api/admin/email/test", json={"to_email": "a@b.com"}).status_code, 401)

        reg = self.client.post("/api/auth/register", json={"terms_accepted": True, 
            "email": "plain_student@example.com",
            "username": "plain_student_mail",
            "password": "Parola123!",
            "full_name": "Normal Ogrenci",
            "university_id": "itu",
        })
        self.assertEqual(reg.status_code, 200, reg.text)
        student_headers = {"Authorization": f"Bearer {reg.json()['token']}"}
        self.assertEqual(self.client.get("/api/admin/email/status", headers=student_headers).status_code, 403)
        self.assertEqual(self.client.post("/api/admin/email/test", json={"to_email": "a@b.com"}, headers=student_headers).status_code, 403)

    def test_config_and_admin_email_status_and_live_test(self):
        admin_h = self._admin_headers()

        with mock.patch.dict(os.environ, {}, clear=True):
            cfg = self.client.get("/api/config").json()
            self.assertFalse(cfg["email_configured"])
            st = self.client.get("/api/admin/email/status", headers=admin_h)
            self.assertEqual(st.status_code, 200)
            self.assertFalse(st.json()["configured"])
            fail_res = self.client.post("/api/admin/email/test", json={"to_email": "prepmasteryonetici@gmail.com"}, headers=admin_h)
            self.assertEqual(fail_res.status_code, 503)

        env = {
            "EMAIL_FROM": "PrepMaster <prepmasteryonetici@gmail.com>",
            "BREVO_API_KEY": "xkeysib-live-mock",
            "SUPPORT_NOTIFY_EMAIL": "prepmasteryonetici@gmail.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=201, text='{"messageId":"ok"}')) as post:
                cfg = self.client.get("/api/config").json()
                self.assertTrue(cfg["email_configured"])

                st = self.client.get("/api/admin/email/status", headers=admin_h).json()
                self.assertTrue(st["configured"])
                self.assertEqual(st["provider"], "brevo")
                self.assertEqual(st["support_notify_email"], "prepmasteryonetici@gmail.com")

                test_res = self.client.post("/api/admin/email/test", json={"to_email": "prepmasteryonetici@gmail.com"}, headers=admin_h)
                self.assertEqual(test_res.status_code, 200, test_res.text)
                body = test_res.json()
                self.assertTrue(body["success"])
                self.assertEqual(body["provider"], "brevo")
                self.assertEqual(post.call_count, 1)

    def test_register_support_and_access_grant_trigger_emails(self):
        admin_h = self._admin_headers()
        env = {
            "EMAIL_FROM": "PrepMaster <prepmasteryonetici@gmail.com>",
            "BREVO_API_KEY": "xkeysib-bg-mock",
            "SUPPORT_NOTIFY_EMAIL": "prepmasteryonetici@gmail.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=201, text="{}")) as post:
                reg = self.client.post("/api/auth/register", json={"terms_accepted": True, 
                    "email": "mail_ogr@itu.edu.tr",
                    "username": "mail_ogr_test",
                    "password": "Parola123!",
                    "full_name": "Mail Ogrenci",
                    "university_id": "itu",
                })
                self.assertEqual(reg.status_code, 200, reg.text)
                uid = reg.json()["user"]["id"]
                ogr_h = {"Authorization": "Bearer " + reg.json()["token"]}
                subjects = [c.kwargs["json"]["subject"] for c in post.call_args_list]
                self.assertTrue(any("Hoş Geldin" in s for s in subjects), subjects)

                post.reset_mock()
                ticket = self.client.post("/api/support/ticket", json={
                    "category": "Ödeme & Fatura İşlemleri",
                    "full_name": "Mail Ogrenci",
                    "email": "baska-biri@example.com",
                    "phone": "05398381887",
                    "message": "Erişim kontrolü istiyorum.",
                }, headers=ogr_h)
                self.assertEqual(ticket.status_code, 200, ticket.text)
                # 1 bildirim (yöneticiye) + 1 alındı onayı — formdaki adrese DEĞİL, hesabın adresine
                self.assertEqual(post.call_count, 2)
                recipients = [c.kwargs["json"]["to"][0]["email"] for c in post.call_args_list]
                self.assertIn("prepmasteryonetici@gmail.com", recipients)
                self.assertIn("mail_ogr@itu.edu.tr", recipients)
                self.assertNotIn("baska-biri@example.com", recipients)

                # Giriş yapmamış ziyaretçi: yalnız yöneticiye bildirim, yazdığı adrese e-posta gitmez
                post.reset_mock()
                anon = self.client.post("/api/support/ticket", json={
                    "category": "<a href=x>tikla</a>",
                    "full_name": "Ziyaretci",
                    "email": "kurban@example.com",
                    "message": "Spam denemesi metni.",
                })
                self.assertEqual(anon.status_code, 200, anon.text)
                recipients = [c.kwargs["json"]["to"][0]["email"] for c in post.call_args_list]
                self.assertEqual(recipients, ["prepmasteryonetici@gmail.com"])
                self.assertTrue(post.call_args.kwargs["json"]["subject"].endswith("Genel Destek"))

                post.reset_mock()
                acc = self.client.post(f"/api/admin/students/{uid}/access", json={
                    "unlocked_universities": ["general", "itu", "boun"],
                    "primary_university_id": "itu",
                    "is_verified": True,
                }, headers=admin_h)
                self.assertEqual(acc.status_code, 200, acc.text)
                self.assertEqual(post.call_count, 1)
                self.assertEqual(post.call_args.kwargs["json"]["to"][0]["email"], "mail_ogr@itu.edu.tr")


if __name__ == "__main__":
    unittest.main()
