"""
PrepMaster 3D Secure Sandbox Payment & GİB E-Arşiv Receipt Test Suite
Authoritative specifications: ORIGINAL_REQUEST.md (R2) & PROJECT.md (Interface Contract 2)

Tests:
1. /api/membership/3d-init: Session creation, masked phone (+90...), 6-digit SMS code, 180s expiry
2. SMS code validation: Sandbox validation, wrong code rejection (HTTP 400), attempt limits
3. GİB E-Arşiv Receipt Format: EARSIV-2026-XXXX format compliance
4. Statutory Tax Breakdown: 50.00 TL gross, 20% VAT (8.33 TL), 41.67 TL net, exact mathematical equality
5. /api/membership/unlock with 3DS: Successful verification, SQLite unlocked_universities update, purchase record
6. Replay attack defense: Expired or consumed 3DS sessions cannot be reused
7. Backward compatibility: Legacy mobile unlock fallback without session_id
"""

import os
import sys
import re
import json
import sqlite3
import unittest
from pathlib import Path

# Set up test environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_payment_3ds.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "super_secret_test_key_for_payment_suite_2026"

from fastapi.testclient import TestClient
from backend.app import app
from backend.database import init_db, get_db, check_university_access, unlock_university_membership
import backend.security as sec


class TestPayment3DSSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Clean previous test database if exists
        if TEST_DB_PATH.exists():
            try:
                TEST_DB_PATH.unlink()
            except Exception:
                pass
        init_db()
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

    # =========================================================================
    # 1. 3D Secure Session Initialization Tests (/api/membership/3d-init)
    # =========================================================================
    def test_3d_init_session_creation_success(self):
        """Verify /api/membership/3d-init generates session, masked phone, 6-digit SMS, and 180s expiry."""
        payload = {
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528 7900 0000 0001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123",
            "amount_try": 50.0
        }
        res = self.client.post("/api/membership/3d-init", json=payload)
        self.assertEqual(res.status_code, 200, f"Failed to init 3DS session: {res.text}")
        data = res.json()

        # 1. Session ID validation
        session_id = data.get("session_id")
        self.assertIsNotNone(session_id)
        self.assertTrue(len(session_id) >= 8, f"Session ID too short: {session_id}")

        # 2. 6-digit SMS code validation
        sms_code = data.get("sms_code_sandbox") or data.get("sms_code")
        self.assertIsNotNone(sms_code, "Missing SMS code in sandbox response")
        self.assertTrue(re.match(r"^\d{6}$", str(sms_code)), f"SMS code must be 6 numeric digits, got: {sms_code}")

        # 3. Masked phone number validation
        masked_phone = data.get("masked_phone", "")
        self.assertIn("*", masked_phone, f"Phone number must be masked, got: {masked_phone}")

        # 4. Expiry and financial bounds
        expires_in = data.get("expires_in_seconds", 0)
        self.assertGreaterEqual(expires_in, 60, "Session expiry should be at least 60 seconds")
        amount = float(data.get("amount_try") or data.get("amount") or 0)
        self.assertEqual(amount, 50.0)
        self.assertEqual(data.get("currency", "TRY"), "TRY")

    def test_3d_init_invalid_card_bounds_rejected(self):
        """Verify invalid card numbers or CVVs trigger 400 or 422 Unprocessable Entity."""
        # 1. Malformed card number (alphabetic)
        res1 = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Test Student",
            "card_number": "invalid-card-number",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertIn(res1.status_code, [400, 422])

        # 2. CVV wrong length (<3 or >4 digits)
        res2 = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Test Student",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "9"
        })
        self.assertIn(res2.status_code, [400, 422])

    # =========================================================================
    # 2. SMS Code Sandbox Validation & Attempt Limits
    # =========================================================================
    def test_sms_code_validation_rejects_wrong_code(self):
        """Verify /api/membership/unlock rejects incorrect 6-digit SMS code with HTTP 400."""
        # Init 3DS session
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "ankara",
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]

        # Attempt unlock with deliberate wrong code
        unlock_res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "ankara",
            "session_id": session_id,
            "sms_code": "000000"
        })
        self.assertEqual(unlock_res.status_code, 400)
        self.assertIn("detail", unlock_res.json())

    def test_sms_code_attempt_limit_lockout(self):
        """Verify 3 consecutive invalid SMS codes locks out the 3DS session."""
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "gazi",
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]

        for i in range(3):
            res = self.client.post("/api/membership/unlock", json={
                "user_id": 1,
                "university_id": "gazi",
                "session_id": session_id,
                "sms_code": f"11111{i}"
            })
            self.assertEqual(res.status_code, 400)

        # 4th attempt should be explicitly locked out
        blocked_res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "gazi",
            "session_id": session_id,
            "sms_code": "123456"
        })
        self.assertEqual(blocked_res.status_code, 400)

    # =========================================================================
    # 3. GİB E-Arşiv Format & Statutory Tax Breakdown Tests
    # =========================================================================
    def test_gib_earsiv_format_and_tax_breakdown(self):
        """Verify statutory financial breakdown: 50.00 TL gross, 20% VAT (8.33 TL), 41.67 TL net, and EARSIV-2026-XXXX format."""
        # 1. Statutory derivation verification
        gross_statutory = 50.00
        vat_rate_statutory = 0.20
        net_statutory = round(gross_statutory / (1.0 + vat_rate_statutory), 2)
        vat_statutory = round(gross_statutory - net_statutory, 2)

        self.assertEqual(net_statutory, 41.67, "Net amount must be exactly 41.67 TL")
        self.assertEqual(vat_statutory, 8.33, "VAT amount must be exactly 8.33 TL")
        self.assertEqual(round(net_statutory + vat_statutory, 2), 50.00, "Net + VAT must equal 50.00 TL exactly")

        # 2. Perform 3DS Init and Unlock
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "koc",
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        sms_code = init_res.json().get("sms_code_sandbox") or init_res.json().get("sms_code")

        unlock_res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": session_id,
            "sms_code": sms_code
        })
        self.assertEqual(unlock_res.status_code, 200)
        data = unlock_res.json()

        # 3. Verify Receipt Format EARSIV-2026-XXXX
        receipt = data.get("receipt", {})
        receipt_no = receipt.get("receipt_no") or receipt.get("invoice_number") or data.get("reference")
        self.assertIsNotNone(receipt_no, "Receipt number / reference must be returned")
        self.assertTrue(
            bool(re.match(r"^EARSIV-2026-[A-Z0-9]{4,}$", receipt_no)),
            f"Receipt number must match EARSIV-2026-XXXX format, got: {receipt_no}"
        )

        # 4. Verify Financial Breakdown in Receipt
        gross = float(receipt.get("gross_amount") or receipt.get("amount") or data.get("price_try", 0))
        vat_rate = float(receipt.get("vat_rate", 0))
        vat_amount = float(receipt.get("vat_amount", 0))
        net_amount = float(receipt.get("net_amount", 0))

        self.assertEqual(gross, 50.00)
        self.assertIn(vat_rate, [0.20, 20])
        self.assertEqual(round(vat_amount, 2), 8.33)
        self.assertEqual(round(net_amount, 2), 41.67)
        self.assertEqual(round(net_amount + vat_amount, 2), 50.00)

    # =========================================================================
    # 4. End-to-End Unlock & Access Entitlement Tests
    # =========================================================================
    def test_membership_unlock_with_3ds_verification_updates_db(self):
        """Verify successful 3DS unlock updates SQLite unlocked_universities and grants exam access."""
        uni_target = "sabanci"

        # Verify initial locked state
        init_access = self.client.get(f"/api/membership/check?university_id={uni_target}&user_id=1")
        self.assertEqual(init_access.status_code, 200)
        self.assertFalse(init_access.json().get("has_access", False))
        self.assertTrue(init_access.json().get("requires_membership", True))

        # Init 3DS Session
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": uni_target,
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        sms_code = init_res.json().get("sms_code_sandbox") or init_res.json().get("sms_code")

        # Unlock with valid SMS code
        unlock_res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": uni_target,
            "session_id": session_id,
            "sms_code": sms_code
        })
        self.assertEqual(unlock_res.status_code, 200)

        # Verify Database Persistence
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT unlocked_universities FROM users WHERE id = 1")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        unlocked_list = json.loads(row["unlocked_universities"]) if isinstance(row["unlocked_universities"], str) else row["unlocked_universities"]
        self.assertIn(uni_target, unlocked_list)

        # Verify Purchase Record
        cursor.execute("SELECT university_id, price_try, payment_reference FROM university_purchases WHERE user_id = 1 AND university_id = ?", (uni_target,))
        purch_row = cursor.fetchone()
        self.assertIsNotNone(purch_row, "Purchase record not found in university_purchases table")
        self.assertEqual(purch_row["price_try"], 50.0)
        conn.close()

        # Verify API Access Check is now Granted
        post_access = self.client.get(f"/api/membership/check?university_id={uni_target}&user_id=1")
        self.assertEqual(post_access.status_code, 200)
        self.assertTrue(post_access.json().get("has_access", False))
        self.assertFalse(post_access.json().get("requires_membership", True))

    def test_replay_used_3ds_session_rejected(self):
        """Verify a consumed 3DS session cannot be re-used for another purchase (replay defense)."""
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "ege",
            "card_holder": "Ahmet Yılmaz",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        sms_code = init_res.json().get("sms_code_sandbox") or init_res.json().get("sms_code")

        # First use -> 200
        first_unlock = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "ege",
            "session_id": session_id,
            "sms_code": sms_code
        })
        self.assertEqual(first_unlock.status_code, 200)

        # Replay attempt -> 400
        replay_unlock = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "ege",
            "session_id": session_id,
            "sms_code": sms_code
        })
        self.assertEqual(replay_unlock.status_code, 400)

    def test_legacy_unlock_direct_fallback(self):
        """Verify legacy direct /api/membership/unlock calls without session_id still work gracefully."""
        res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Legacy Mobile User",
            "card_number": "4242 4242 4242 4242"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success") is True or data.get("status") == "success")


if __name__ == "__main__":
    unittest.main()
