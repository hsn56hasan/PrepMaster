"""
PayTR iFrame ödemesi testleri (gerçek PayTR'ye GİTMEZ).

PayTR'nin get-token servisi sahte yanıtla taklit edilir; bildirimler (callback) gerçek
PayTR'nin yaptığı gibi mağaza anahtarı + tuzuyla HMAC-SHA256 imzalanır.
"""

import base64
import hashlib
import hmac
import io
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_paytr.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "paytr_suite_secret_key_2026_zxcvbnmasdfgh"
os.environ["PAYTR_MERCHANT_ID"] = "123456"
os.environ["PAYTR_MERCHANT_KEY"] = "test_merchant_key_abc"
os.environ["PAYTR_MERCHANT_SALT"] = "test_merchant_salt_xyz"
os.environ["PAYTR_TEST_MODE"] = "1"
os.environ["TRUSTED_PROXY_IPS"] = "testclient"  # test istemcisi aracı (tünel) rolünde

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec
import paytr_service

KEY = b"test_merchant_key_abc"
SALT = "test_merchant_salt_xyz"


def sign(oid, status, total):
    return base64.b64encode(hmac.new(KEY, f"{oid}{SALT}{status}{total}".encode(), hashlib.sha256).digest()).decode()


class FakePaytr:
    """paytr_service içindeki urllib.request.urlopen'ı taklit eder; gönderilen formu yakalar."""

    def __init__(self, reply=None):
        self.reply = reply or {"status": "success", "token": "tok_abc123"}
        self.forms = []

    def __call__(self, req, timeout=None):
        from urllib.parse import parse_qs
        self.forms.append({k: v[0] for k, v in parse_qs(req.data.decode()).items()})
        return io.BytesIO(json.dumps(self.reply).encode())


class TestPaytr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_PATH.exists():
            try:
                TEST_DB_PATH.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False
        self.fake = FakePaytr()
        p = mock.patch.object(paytr_service.urllib.request, "urlopen", self.fake)
        p.start()
        self.addCleanup(p.stop)

    def _register(self, username):
        res = self.client.post("/api/auth/register", json={"terms_accepted": True, 
            "email": f"{username}@example.com", "username": username, "password": "Parola123!",
            "full_name": "Test Öğrenci", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    def _start(self, auth, uni="boun", phone="0532 123 45 67"):
        return self.client.post("/api/payment/paytr/token", json={"university_id": uni, "user_phone": phone, "pre_info_accepted": True},
                                headers={**auth, "CF-Connecting-IP": "88.1.2.3"})

    def _callback(self, oid, status="success", total="5000", sig=None):
        return self.client.post("/api/payment/paytr/callback", data={
            "merchant_oid": oid, "status": status, "total_amount": total,
            "hash": sig or sign(oid, status, total),
            "failed_reason_code": "" if status == "success" else "2",
            "failed_reason_msg": "" if status == "success" else "Yetersiz bakiye",
        })

    def _order(self, oid, auth):
        return self.client.get(f"/api/payment/paytr/orders/{oid}", headers=auth).json()

    # ------------------------------------------------------------------ başlatma
    def test_start_sends_correct_fields_to_paytr_and_opens_pending_order(self):
        uid, auth = self._register("odeyen1")
        res = self._start(auth)
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["iframe_url"], "https://www.paytr.com/odeme/guvenli/tok_abc123")
        form = self.fake.forms[0]
        self.assertEqual(form["merchant_id"], "123456")
        self.assertEqual(form["payment_amount"], "5000")
        self.assertEqual(form["user_ip"], "88.1.2.3")
        self.assertEqual(form["user_phone"], "05321234567")
        self.assertEqual(form["email"], "odeyen1@example.com")
        self.assertEqual(form["debug_on"], "0")
        self.assertTrue(form["merchant_ok_url"].endswith("/odeme-sonuc?durum=basarili"))
        self.assertTrue(form["merchant_fail_url"].endswith("/odeme-sonuc?durum=basarisiz"))
        self.assertNotIn("card", " ".join(form.keys()))
        # PayTR token imzası doğru hesaplanmış mı (PayTR'nin resmi sırası)
        hash_str = (f"{form['merchant_id']}{form['user_ip']}{form['merchant_oid']}{form['email']}"
                    f"{form['payment_amount']}{form['user_basket']}{form['no_installment']}"
                    f"{form['max_installment']}{form['currency']}{form['test_mode']}")
        expected = base64.b64encode(hmac.new(KEY, hash_str.encode() + SALT.encode(), hashlib.sha256).digest()).decode()
        self.assertEqual(form["paytr_token"], expected)
        order = self._order(body["merchant_oid"], auth)
        self.assertEqual(order["status"], "pending")
        self.assertFalse(db.check_university_access(uid, "boun"))

    def test_start_requires_login_valid_phone_and_locked_university(self):
        self.assertEqual(self.client.post("/api/payment/paytr/token",
                                          json={"university_id": "boun", "user_phone": "05321234567"}).status_code, 401)
        uid, auth = self._register("odeyen2")
        self.assertEqual(self._start(auth, phone="12345").status_code, 422)
        self.assertEqual(self._start(auth, uni="hogwarts").status_code, 400)
        db.unlock_university_membership(uid, "koc")
        self.assertEqual(self._start(auth, uni="koc").status_code, 400)  # zaten açık
        self.assertEqual(self.fake.forms, [])

    def test_disabled_without_merchant_keys(self):
        _, auth = self._register("anahtarsiz")
        with mock.patch.object(app_module, "is_paytr_live_configured", return_value=False):
            self.assertEqual(self._start(auth).status_code, 503)

    def test_paytr_rejection_is_reported_and_no_order_left(self):
        _, auth = self._register("reddedilen")
        self.fake.reply = {"status": "failed", "reason": "Gecersiz telefon"}
        res = self._start(auth)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Gecersiz telefon", res.text)

    # ------------------------------------------------------------------ bildirim
    def test_signed_success_callback_unlocks_once(self):
        uid, auth = self._register("odeyen3")
        oid = self._start(auth).json()["merchant_oid"]
        for _ in range(3):  # PayTR aynı bildirimi birden çok kez gönderebilir
            r = self._callback(oid)
            self.assertEqual((r.status_code, r.text), (200, "OK"))
        self.assertTrue(db.check_university_access(uid, "boun"))
        self.assertEqual(self._order(oid, auth)["status"], "success")
        conn = db.get_db()
        n = conn.execute("SELECT COUNT(*) FROM university_purchases WHERE user_id = ? AND university_id = 'boun'",
                         (uid,)).fetchone()[0]
        conn.close()
        self.assertEqual(n, 1, "Tekrarlanan bildirim ikinci bir satın alma kaydı açmamalı")

    def test_failed_callback_does_not_unlock(self):
        uid, auth = self._register("odeyen4")
        oid = self._start(auth).json()["merchant_oid"]
        self.assertEqual(self._callback(oid, status="failed", total="5000").text, "OK")
        self.assertFalse(db.check_university_access(uid, "boun"))
        self.assertEqual(self._order(oid, auth)["status"], "failed")
        # Başarısız siparişe sonradan gelen "success" kilidi açmaz
        self._callback(oid, status="success")
        self.assertFalse(db.check_university_access(uid, "boun"))

    def test_underpaid_callback_does_not_unlock(self):
        uid, auth = self._register("odeyen5")
        oid = self._start(auth).json()["merchant_oid"]
        self._callback(oid, total="100")
        self.assertFalse(db.check_university_access(uid, "boun"))
        self.assertEqual(self._order(oid, auth)["status"], "amount_mismatch")

    def test_installment_total_above_price_unlocks(self):
        uid, auth = self._register("taksitli")
        oid = self._start(auth).json()["merchant_oid"]
        self._callback(oid, total="5300")  # vade farkıyla daha yüksek tutar
        self.assertTrue(db.check_university_access(uid, "boun"))

    def test_bad_signature_rejected(self):
        uid, auth = self._register("odeyen6")
        oid = self._start(auth).json()["merchant_oid"]
        r = self._callback(oid, sig="uydurma-imza")
        self.assertEqual(r.status_code, 400)
        self.assertFalse(db.check_university_access(uid, "boun"))
        self.assertEqual(self._order(oid, auth)["status"], "pending")

    def test_signed_callback_for_unknown_order_touches_nobody(self):
        uid, _ = self._register("odeyen7")
        oid = f"PMU{uid}XBOUNX1700000000XDEADBEEF"  # biçimi doğru ama bizim açmadığımız sipariş
        r = self._callback(oid)
        self.assertEqual(r.text, "OK")
        self.assertFalse(db.check_university_access(uid, "boun"))

    def test_order_status_only_visible_to_owner(self):
        _, a = self._register("sahip")
        _, b = self._register("meraklı".replace("ı", "i"))
        oid = self._start(a).json()["merchant_oid"]
        self.assertEqual(self.client.get(f"/api/payment/paytr/orders/{oid}", headers=b).status_code, 404)

    # ------------------------------------------------------------------ sonuç sayfası
    def test_result_page_can_be_framed_by_paytr_only(self):
        r = self.client.get("/odeme-sonuc?durum=basarili")
        self.assertEqual(r.status_code, 200)
        self.assertIn("frame-ancestors 'self' https://www.paytr.com", r.headers["Content-Security-Policy"])
        self.assertEqual(r.headers["X-Frame-Options"], "SAMEORIGIN")
        main = self.client.get("/")
        self.assertIn("frame-ancestors 'none'", main.headers["Content-Security-Policy"])
        self.assertIn("frame-src https://www.paytr.com", main.headers["Content-Security-Policy"])
        self.assertEqual(main.headers["X-Frame-Options"], "DENY")

    # ------------------------------------------------------------------ ödeme öncesi onay
    def test_payment_requires_pre_information_consent_and_records_it(self):
        _, auth = self._register("onaysiz")
        res = self.client.post("/api/payment/paytr/token",
                               json={"university_id": "boun", "user_phone": "05321234567"}, headers=auth)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(self.fake.forms, [], "Onay olmadan PayTR'ye gidilmemeli")
        oid = self._start(auth).json()["merchant_oid"]
        self.assertIsNotNone(db.get_paytr_order(oid)["pre_info_accepted_at"])


if __name__ == "__main__":
    unittest.main()
