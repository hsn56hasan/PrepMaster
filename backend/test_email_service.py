"""
E-posta servisi ve .env yükleyici testleri (gerçek e-posta GÖNDERMEZ).
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

import email_service as es  # noqa: E402
import env_loader  # noqa: E402

SMTP_ENV = {
    "EMAIL_FROM": "PrepMaster <noreply@vectonis.com>",
    "SMTP_HOST": "smtp.zoho.eu",
    "SMTP_USER": "noreply@vectonis.com",
    "SMTP_PASSWORD": "uygulama-sifresi",
}


class TestEmailService(unittest.TestCase):
    def test_not_configured_without_settings(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertFalse(es.email_configured())
            self.assertFalse(es.send_email("a@b.com", "konu", "metin"))

    def test_needs_sender_address(self):
        env = {k: v for k, v in SMTP_ENV.items() if k != "EMAIL_FROM"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertFalse(es.email_configured())

    def test_smtp_ssl_465_sends_reset_code(self):
        with mock.patch.dict(os.environ, {**SMTP_ENV, "SMTP_PORT": "465"}, clear=True), \
                mock.patch.object(es.smtplib, "SMTP_SSL") as smtp_ssl:
            server = smtp_ssl.return_value.__enter__.return_value
            self.assertEqual(es.email_provider(), "smtp")
            self.assertTrue(es.send_password_reset_email("ogrenci@itu.edu.tr", "482913"))
            smtp_ssl.assert_called_once()
            self.assertEqual(smtp_ssl.call_args[0][:2], ("smtp.zoho.eu", 465))
            server.login.assert_called_once_with("noreply@vectonis.com", "uygulama-sifresi")
            msg = server.send_message.call_args[0][0]
            self.assertEqual(msg["To"], "ogrenci@itu.edu.tr")
            self.assertIn("482913", msg["Subject"])
            self.assertIn("noreply@vectonis.com", msg["From"])
            plain = msg.get_body(preferencelist=("plain",)).get_content()
            html = msg.get_body(preferencelist=("html",)).get_content()
            self.assertIn("482913", plain)
            self.assertIn("482913", html)

    def test_smtp_starttls_587(self):
        with mock.patch.dict(os.environ, {**SMTP_ENV, "SMTP_PORT": "587"}, clear=True), \
                mock.patch.object(es.smtplib, "SMTP") as smtp:
            server = smtp.return_value.__enter__.return_value
            self.assertTrue(es.send_student_otp_email("x@itu.edu.tr", "123456"))
            server.starttls.assert_called_once()
            server.login.assert_called_once()

    def test_smtp_failure_returns_false_without_raising(self):
        with mock.patch.dict(os.environ, SMTP_ENV, clear=True), \
                mock.patch.object(es.smtplib, "SMTP_SSL", side_effect=OSError("bağlantı yok")):
            self.assertFalse(es.send_password_reset_email("a@b.com", "111111"))

    def test_resend_api(self):
        env = {"EMAIL_FROM": "PrepMaster <noreply@vectonis.com>", "RESEND_API_KEY": "re_test"}
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=200, text="{}")) as post:
                self.assertEqual(es.email_provider(), "resend")
                self.assertTrue(es.send_password_reset_email("a@b.com", "654321"))
                body = post.call_args.kwargs["json"]
                self.assertEqual(body["to"], ["a@b.com"])
                self.assertIn("654321", body["text"])
                self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer re_test")

    def test_brevo_api_and_status(self):
        env = {
            "EMAIL_FROM": "PrepMaster <prepmasteryonetici@gmail.com>",
            "BREVO_API_KEY": "xkeysib-test-123",
            "SUPPORT_NOTIFY_EMAIL": "prepmasteryonetici@gmail.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=201, text='{"messageId":"1"}')) as post:
                self.assertEqual(es.email_provider(), "brevo")
                status = es.get_email_status()
                self.assertTrue(status["configured"])
                self.assertTrue(status["has_brevo_key"])
                self.assertEqual(status["support_notify_email"], "prepmasteryonetici@gmail.com")
                self.assertNotIn("xkeysib-test-123", str(status))

                ok = es.send_welcome_email("ogr@itu.edu.tr", "Ali Yılmaz", "ali123", "İTÜ")
                self.assertTrue(ok)
                self.assertEqual(post.call_args.args[0], "https://api.brevo.com/v3/smtp/email")
                self.assertEqual(post.call_args.kwargs["headers"]["api-key"], "xkeysib-test-123")
                body = post.call_args.kwargs["json"]
                self.assertEqual(body["sender"], {"email": "prepmasteryonetici@gmail.com", "name": "PrepMaster"})
                self.assertEqual(body["to"], [{"email": "ogr@itu.edu.tr"}])
                self.assertIn("ali123", body["textContent"])
                self.assertIn("İTÜ", body["htmlContent"])

    def test_support_and_access_granted_emails(self):
        env = {
            "EMAIL_FROM": "PrepMaster <prepmasteryonetici@gmail.com>",
            "BREVO_API_KEY": "xkeysib-test-456",
            "SUPPORT_NOTIFY_EMAIL": "prepmasteryonetici@gmail.com",
        }
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=201, text="{}")) as post:
                self.assertTrue(es.send_support_ticket_notification(
                    ticket_id=42,
                    category="KVKK Başvurusu",
                    student_name="Ayşe Kaya",
                    student_email="ayse@itu.edu.tr",
                    student_phone="05390001122",
                    message="Veri silme talebi",
                ))
                notify_body = post.call_args.kwargs["json"]
                self.assertEqual(notify_body["to"], [{"email": "prepmasteryonetici@gmail.com"}])
                self.assertIn("#42", notify_body["subject"])
                self.assertIn("Veri silme talebi", notify_body["textContent"])

                self.assertTrue(es.send_support_ticket_receipt("ayse@itu.edu.tr", 42, "KVKK Başvurusu"))
                self.assertTrue(es.send_access_granted_email("ayse@itu.edu.tr", "Ayşe Kaya", ["itu", "boun"]))
                access_body = post.call_args.kwargs["json"]
                self.assertIn("ITU, BOUN", access_body["textContent"])

    def test_verbose_error_on_http_failure(self):
        env = {"EMAIL_FROM": "PrepMaster <prepmasteryonetici@gmail.com>", "BREVO_API_KEY": "xkeysib-bad"}
        with mock.patch.dict(os.environ, env, clear=True):
            import httpx
            with mock.patch.object(httpx, "post", return_value=mock.Mock(status_code=401, text="Unauthorized")) as _:
                res = es.send_email_verbose("a@b.com", "Konu", "İçerik")
                self.assertFalse(res["success"])
                self.assertEqual(res["provider"], "brevo")
                self.assertIn("401", res["error"])


class TestEnvLoader(unittest.TestCase):
    def test_parses_and_does_not_override(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text('# yorum\nA_KEY=deger\nB_KEY="tirnakli deger"\nC_KEY=zaten\nbozuk satir\n', encoding="utf-8")
            with mock.patch.dict(os.environ, {"C_KEY": "ortamdaki"}, clear=False), \
                    mock.patch.object(env_loader, "_loaded", False), \
                    mock.patch.object(env_loader.sys, "argv", ["uvicorn"]):
                env_loader.load_env(p)
                self.assertEqual(os.environ["A_KEY"], "deger")
                self.assertEqual(os.environ["B_KEY"], "tirnakli deger")
                self.assertEqual(os.environ["C_KEY"], "ortamdaki")
            os.environ.pop("A_KEY", None)
            os.environ.pop("B_KEY", None)

    def test_skipped_while_testing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / ".env"
            p.write_text("TEST_SKIP_KEY=x\n", encoding="utf-8")
            with mock.patch.object(env_loader, "_loaded", False):
                env_loader.load_env(p)  # argv[0] = test_email_service.py
            self.assertNotIn("TEST_SKIP_KEY", os.environ)


class TestEmailBudget(unittest.TestCase):
    """Günlük kota: kötüye kullanımda şifre sıfırlama / doğrulama e-postaları yine gidebilmeli."""

    def setUp(self):
        es._BUDGET.update({"day": None, "total": 0, "normal": 0, "per_recipient": {}})

    def _env(self, **extra):
        env = {"EMAIL_FROM": "PrepMaster <noreply@x.com>", "BREVO_API_KEY": "xkeysib-test-sahte",
               "EMAIL_DAILY_LIMIT": "5", "EMAIL_DAILY_SOFT_LIMIT": "3", "EMAIL_PER_RECIPIENT_DAILY": "2"}
        env.update(extra)
        return mock.patch.dict(os.environ, env, clear=True)

    def test_normal_mail_stops_at_soft_limit_but_critical_still_goes(self):
        import httpx
        ok = mock.Mock(status_code=201, text="{}")
        with self._env(), mock.patch.object(httpx, "post", return_value=ok) as post:
            for i in range(3):
                self.assertTrue(es.send_email(f"k{i}@x.com", "hosgeldin", "t"))
            self.assertFalse(es.send_email("k9@x.com", "hosgeldin", "t"))  # bilgilendirme kotası doldu
            self.assertTrue(es.send_password_reset_email("ogr@x.com", "123456"))  # kritik yine gider
            self.assertTrue(es.send_student_otp_email("ogr@itu.edu.tr", "654321"))
            self.assertFalse(es.send_password_reset_email("ogr2@x.com", "111111"))  # günlük üst sınır (5)
            self.assertEqual(post.call_count, 5)

    def test_same_recipient_capped(self):
        import httpx
        ok = mock.Mock(status_code=201, text="{}")
        with self._env(EMAIL_DAILY_SOFT_LIMIT="50", EMAIL_DAILY_LIMIT="50"),                 mock.patch.object(httpx, "post", return_value=ok) as post:
            self.assertTrue(es.send_email("kurban@x.com", "a", "t"))
            self.assertTrue(es.send_email("KURBAN@x.com", "b", "t"))
            self.assertFalse(es.send_email("kurban@x.com", "c", "t"))
            self.assertEqual(post.call_count, 2)
            self.assertEqual(es.get_email_budget()["sent_normal"], 2)


if __name__ == "__main__":
    unittest.main()
