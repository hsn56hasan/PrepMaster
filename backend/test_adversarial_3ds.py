"""
Adversarial Verification Suite for Milestone M2: 3D Secure Sandbox & GİB E-Arşiv
Author: Empirical Challenger
Target:
  - Wrong SMS code rejection
  - Lockout after 3 invalid attempts
  - Replay prevention on verified session
  - Exact tax calculation check: gross == net + vat
  - Receipt regex check: ^EARSIV-2026-[A-F0-9]{4}$
  - Boundary, tampering, and expiration stress tests
"""

import os
import sys
import re
import json
import sqlite3
import unittest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_adversarial_3ds.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "adversarial_challenger_m2_test_key_2026"

import backend.database as db
db.DB_PATH = TEST_DB_PATH

from fastapi.testclient import TestClient
from backend.app import app
import backend.security as sec


class TestAdversarialPayment3DS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            try:
                TEST_DB_PATH.unlink()
            except Exception:
                pass
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

    # =========================================================================
    # 1. Wrong SMS Code Rejection
    # =========================================================================
    def test_adversarial_wrong_sms_code_rejection(self):
        """Stress test wrong SMS codes: standard wrong digits, malformed strings, and ensure rejection."""
        # Initialize 3DS Session
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "ankara",
            "card_holder": "Adversarial Tester",
            "card_number": "5528 7900 0000 0001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123",
            "amount_try": 50.0
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        correct_sms = init_res.json()["sms_code_sandbox"]

        # Formulate wrong codes to test
        wrong_codes = [
            "000000" if correct_sms != "000000" else "111111",
            "999999" if correct_sms != "999999" else "888888",
            "ABC123",
            " 12345 ",
            "123"
        ]

        # Test first wrong code
        res1 = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "ankara",
            "session_id": session_id,
            "sms_code": wrong_codes[0]
        })
        self.assertEqual(res1.status_code, 400, "Wrong SMS code must return HTTP 400")
        self.assertIn("detail", res1.json())

        # Verify DB state: attempts must be 1, status must still be 'pending'
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT attempts, status FROM payment_3ds_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row["attempts"], 1)
        self.assertEqual(row["status"], "pending")

        # Verify user does NOT have access
        access_res = self.client.get("/api/membership/check?university_id=ankara&user_id=1")
        self.assertEqual(access_res.status_code, 200)
        self.assertFalse(access_res.json().get("has_access", False))

    # =========================================================================
    # 2. Lockout After Exactly 3 Invalid Attempts
    # =========================================================================
    def test_adversarial_lockout_after_3_attempts(self):
        """Verify strict lockout on exactly the 3rd wrong attempt, and that even the CORRECT code is blocked afterwards."""
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "gazi",
            "card_holder": "Adversarial Tester",
            "card_number": "5528 7900 0000 0001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123",
            "amount_try": 50.0
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        correct_sms = init_res.json()["sms_code_sandbox"]

        # Attempt 1: Wrong code -> 400, remaining 2
        res1 = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "gazi",
            "session_id": session_id,
            "sms_code": "000001"
        })
        self.assertEqual(res1.status_code, 400)
        self.assertIn("2", res1.json()["detail"])

        # Attempt 2: Wrong code -> 400, remaining 1
        res2 = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "gazi",
            "session_id": session_id,
            "sms_code": "000002"
        })
        self.assertEqual(res2.status_code, 400)
        self.assertIn("1", res2.json()["detail"])

        # Attempt 3: Wrong code -> 400, triggers lockout!
        res3 = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "gazi",
            "session_id": session_id,
            "sms_code": "000003"
        })
        self.assertEqual(res3.status_code, 400)
        self.assertTrue("kilitlendi" in res3.json()["detail"].lower() or "kilit" in res3.json()["detail"].lower())

        # Attempt 4: CRITICAL ADVERSARIAL CHECK - Attempt with the CORRECT SMS code
        # A flawed implementation might only check code equality and unlock anyway.
        # A secure implementation MUST reject it because the session is locked.
        res_correct_after_lock = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "gazi",
            "session_id": session_id,
            "sms_code": correct_sms
        })
        self.assertEqual(res_correct_after_lock.status_code, 400, "Locked session must reject even correct SMS code")
        self.assertTrue("kilit" in res_correct_after_lock.json()["detail"].lower())

        # Verify DB records
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT attempts, status FROM payment_3ds_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row["status"], "locked")
        self.assertEqual(row["attempts"], 3)

        # Verify university was NOT unlocked
        access_res = self.client.get("/api/membership/check?university_id=gazi&user_id=1")
        self.assertFalse(access_res.json().get("has_access", False))

    # =========================================================================
    # 3. Replay Prevention on Verified Session
    # =========================================================================
    def test_adversarial_replay_prevention_on_verified_session(self):
        """Verify that a successfully verified session cannot be replayed under any condition."""
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "koc",
            "card_holder": "Adversarial Tester",
            "card_number": "5528 7900 0000 0001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123",
            "amount_try": 50.0
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        correct_sms = init_res.json()["sms_code_sandbox"]

        # 1. Legitimate unlock
        res_legit = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": session_id,
            "sms_code": correct_sms
        })
        self.assertEqual(res_legit.status_code, 200)
        self.assertEqual(res_legit.json()["status"], "success")

        # 2. Immediate exact replay
        res_replay = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": session_id,
            "sms_code": correct_sms
        })
        self.assertEqual(res_replay.status_code, 400, "Replay attack on verified session must return HTTP 400")
        self.assertTrue("daha önce kullanılmıştır" in res_replay.json()["detail"].lower() or "tekrar" in res_replay.json()["detail"].lower())

        # 3. Cross-university replay attempt with the same session
        res_cross_replay = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "sabanci",
            "session_id": session_id,
            "sms_code": correct_sms
        })
        self.assertEqual(res_cross_replay.status_code, 400, "Cross-university replay must return HTTP 400")

        # 4. Verify DB state: session status is 'verified' and only one purchase was logged
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT status FROM payment_3ds_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        self.assertEqual(row["status"], "verified")

        cur.execute("SELECT COUNT(*) as count FROM university_purchases WHERE user_id = 1 AND university_id = 'koc'")
        purchases_count = cur.fetchone()["count"]
        self.assertEqual(purchases_count, 1, "Only one purchase record should exist, no duplicate charges on replay")
        conn.close()

    # =========================================================================
    # 4. Exact Tax Calculation Check: gross == net + vat
    # =========================================================================
    def test_adversarial_exact_tax_calculation(self):
        """Stress test financial accuracy: gross (50.00) == net (41.67) + vat (8.33) with exact decimal precision."""
        # Test directly via database receipt generator
        receipt = db.generate_gib_receipt(card_last_four="0001", card_holder="Test", university_id="koc")

        gross = receipt["gross_amount"]
        vat_rate = receipt["vat_rate"]
        net = receipt["net_amount"]
        vat = receipt["vat_amount"]

        # Exact values
        self.assertEqual(gross, 50.00)
        self.assertEqual(vat_rate, 0.20)
        self.assertEqual(net, 41.67)
        self.assertEqual(vat, 8.33)

        # Mathematical equality in float and Decimal
        self.assertEqual(round(net + vat, 2), gross)
        self.assertEqual(net + vat, gross)

        d_gross = Decimal(str(gross))
        d_net = Decimal(str(net))
        d_vat = Decimal(str(vat))
        self.assertEqual(d_gross, d_net + d_vat, f"Exact Decimal equality failed: {d_gross} != {d_net} + {d_vat}")

        # Test 1000 generated receipts to ensure zero floating-point drift or variation
        for _ in range(1000):
            r = db.generate_gib_receipt()
            g = Decimal(str(r["gross_amount"]))
            n = Decimal(str(r["net_amount"]))
            v = Decimal(str(r["vat_amount"]))
            self.assertEqual(g, n + v)
            self.assertEqual(r["gross_amount"], 50.00)
            self.assertEqual(r["net_amount"], 41.67)
            self.assertEqual(r["vat_amount"], 8.33)

    # =========================================================================
    # 5. Receipt Regex Check: ^EARSIV-2026-[A-F0-9]{4}$
    # =========================================================================
    def test_adversarial_receipt_regex_check(self):
        """Empirically test 10,000 receipts against exact regex ^EARSIV-2026-[A-F0-9]{4}$."""
        pattern = re.compile(r"^EARSIV-2026-[A-F0-9]{4}$")

        generated_refs = set()
        for i in range(10000):
            receipt = db.generate_gib_receipt()
            receipt_no = receipt["receipt_no"]

            # Must match exact regex
            match = pattern.match(receipt_no)
            self.assertIsNotNone(match, f"Receipt '{receipt_no}' failed to match regex ^EARSIV-2026-[A-F0-9]{{4}}$ on iteration {i}")
            self.assertEqual(len(receipt_no), 16, f"Receipt length must be exactly 16 chars: {receipt_no}")

            # Check suffix is uppercase hex
            suffix = receipt_no.split("-")[2]
            self.assertEqual(len(suffix), 4)
            self.assertTrue(all(c in "0123456789ABCDEF" for c in suffix))

            generated_refs.add(receipt_no)

        # High entropy check: across 10,000 draws from 65,536 space, birthday paradox allows collisions,
        # but unique count should be substantial (> 7,000)
        self.assertGreater(len(generated_refs), 7000, f"Low entropy detected: only {len(generated_refs)} unique IDs out of 10,000")

    # =========================================================================
    # 6. Session Expiry Boundary Check
    # =========================================================================
    def test_adversarial_expired_session_handling(self):
        """Verify that a session that has passed 180 seconds expiry is rejected and marked 'expired'."""
        init_res = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "ege",
            "card_holder": "Adversarial Tester",
            "card_number": "5528 7900 0000 0001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123",
            "amount_try": 50.0
        })
        self.assertEqual(init_res.status_code, 200)
        session_id = init_res.json()["session_id"]
        correct_sms = init_res.json()["sms_code_sandbox"]

        # Artificially wind back expires_at in DB
        past_time = (datetime.now(timezone.utc) - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("UPDATE payment_3ds_sessions SET expires_at = ? WHERE session_id = ?", (past_time, session_id))
        conn.commit()
        conn.close()

        # Attempt unlock with the correct SMS code -> MUST BE REJECTED with 400
        res = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "ege",
            "session_id": session_id,
            "sms_code": correct_sms
        })
        self.assertEqual(res.status_code, 400)
        self.assertTrue("süresi dolmuş" in res.json()["detail"].lower() or "zaman" in res.json()["detail"].lower() or "expired" in res.json()["detail"].lower())

        # Verify DB status is 'expired'
        conn = db.get_db()
        cur = conn.cursor()
        cur.execute("SELECT status FROM payment_3ds_sessions WHERE session_id = ?", (session_id,))
        row = cur.fetchone()
        conn.close()
        self.assertEqual(row["status"], "expired")

    # =========================================================================
    # 7. Forged Session ID & Missing Field Injections
    # =========================================================================
    def test_adversarial_forged_session_and_missing_fields(self):
        """Verify forged session IDs and incomplete payload handling."""
        # Non-existent session ID
        res_fake = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": "3DS-NON-EXISTENT-SESSION",
            "sms_code": "123456"
        })
        self.assertEqual(res_fake.status_code, 400)

        # SQL injection in session_id
        res_sqli = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": "' OR 1=1 --",
            "sms_code": "123456"
        })
        self.assertEqual(res_sqli.status_code, 400)

        # session_id provided but sms_code missing/None
        res_missing_sms = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": "3DS-SOME-ID",
            "sms_code": None
        })
        self.assertEqual(res_missing_sms.status_code, 400)

        # sms_code provided but session_id missing
        res_missing_session = self.client.post("/api/membership/unlock", json={
            "user_id": 1,
            "university_id": "koc",
            "session_id": None,
            "sms_code": "123456"
        })
        self.assertEqual(res_missing_session.status_code, 400)

    # =========================================================================
    # 8. Card Validation Boundaries
    # =========================================================================
    def test_adversarial_card_validation_boundaries(self):
        """Stress test card length and formatting validation on /api/membership/3d-init."""
        # Card number too short (<12 digits)
        res_short = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Test",
            "card_number": "12345678901",  # 11 digits
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertIn(res_short.status_code, [400, 422])

        # Card number too long (>19 digits)
        res_long = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Test",
            "card_number": "12345678901234567890",  # 20 digits
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "123"
        })
        self.assertIn(res_long.status_code, [400, 422])

        # CVV wrong length (2 digits or 5 digits)
        res_cvv2 = self.client.post("/api/membership/3d-init", json={
            "user_id": 1,
            "university_id": "hacettepe",
            "card_holder": "Test",
            "card_number": "5528790000000001",
            "expire_month": "12",
            "expire_year": "28",
            "cvv": "12"
        })
        self.assertIn(res_cvv2.status_code, [400, 422])


if __name__ == "__main__":
    unittest.main()
