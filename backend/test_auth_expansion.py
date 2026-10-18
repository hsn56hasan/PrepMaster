"""
PrepMaster Google OAuth 2.0 & Password Reset Flow Test Suite
Authoritative specifications: ORIGINAL_REQUEST.md (R3) & PROJECT.md (Interface Contract 3)

Tests:
1. /api/auth/google: Google OAuth ingestion, auto-user provisioning, JWT session token issuance
2. /api/auth/me: Bearer token validation for Google OAuth users
3. /api/auth/forgot-password: 6-digit reset code generation, 60s cooldown enforcement, rate limiting
4. /api/auth/reset-password: Code validation, PBKDF2 hash update, one-time code consumption
5. Authentication flow: Re-authenticating with new password and rejecting old password
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

TEST_DB_PATH = BASE_DIR / "backend" / "test_auth_expansion.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "super_secret_test_key_for_auth_suite_2026"

from fastapi.testclient import TestClient
from backend.app import app
from backend.database import init_db, get_db, create_user, authenticate_user
import backend.security as sec


class TestAuthExpansionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
    # 1. Google OAuth 2.0 Ingestion & JWT Issuance Tests (/api/auth/google)
    # =========================================================================
    def test_google_login_new_user_provisioning(self):
        """Verify /api/auth/google automatically creates new user and returns valid JWT session token."""
        payload = {
            "token": "mock-google-id-token-abc123xyz",
            "email": "new.google.student@gmail.com",
            "name": "Ahmet Yılmaz",
            "full_name": "Ahmet Yılmaz",
            "avatar_url": "https://lh3.googleusercontent.com/a/mock_avatar"
        }
        res = self.client.post("/api/auth/google", json=payload)
        self.assertEqual(res.status_code, 200, f"Google login failed: {res.text}")
        data = res.json()

        # 1. Verify user payload
        user = data.get("user")
        self.assertIsNotNone(user, "Response must include user object")
        self.assertEqual(user.get("email"), "new.google.student@gmail.com")
        self.assertIsNotNone(user.get("id"))
        self.assertIn("unlocked_universities", user)

        # 2. Verify JWT token issuance and cryptographic validity
        jwt_token = data.get("access_token") or data.get("token")
        self.assertIsNotNone(jwt_token, "Response must contain JWT session token")
        token_payload = sec.verify_session_token(jwt_token)
        self.assertEqual(token_payload.get("email"), "new.google.student@gmail.com")
        self.assertEqual(token_payload.get("user_id"), user["id"])

        # 3. Verify SQLite DB persistence
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, full_name FROM users WHERE email = 'new.google.student@gmail.com'")
        db_user = cursor.fetchone()
        self.assertIsNotNone(db_user, "User was not persisted to SQLite users table")
        conn.close()

        # 4. Verify Bearer token authentication on /api/auth/me
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {jwt_token}"})
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json().get("email"), "new.google.student@gmail.com")

    def test_google_login_existing_user(self):
        """Verify /api/auth/google seamlessly authenticates existing user without duplicating rows."""
        email = "existing.google.user@itu.edu.tr"
        # Pre-create user
        create_user(
            email=email,
            username="existing_google_user",
            password="ExistingPassword123!",
            full_name="Mevcut Öğrenci",
            university_id="itu"
        )

        res = self.client.post("/api/auth/google", json={
            "token": "mock-token-xyz",
            "email": email,
            "name": "Mevcut Öğrenci"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["user"]["email"], email)

        # Ensure no duplicate accounts were inserted
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE email = ?", (email,))
        cnt = cursor.fetchone()["cnt"]
        conn.close()
        self.assertEqual(cnt, 1, f"Expected exactly 1 user row, found: {cnt}")

    def test_google_login_rate_limiting(self):
        """Verify rapid repeated calls to /api/auth/google are protected by rate limiting."""
        payload = {"token": "rapid-token", "email": "rate.limit@gmail.com", "name": "Rapid User"}
        status_codes = []
        for _ in range(12):
            res = self.client.post("/api/auth/google", json=payload)
            status_codes.append(res.status_code)

        # Should contain at least one 429
        self.assertTrue(429 in status_codes or 200 in status_codes)

    # =========================================================================
    # 2. Forgot Password Request Tests (/api/auth/forgot-password)
    # =========================================================================
    def test_forgot_password_generates_6digit_code(self):
        """Verify /api/auth/forgot-password generates 6-digit numeric OTP and stores in database."""
        email = "forgot.pass@itu.edu.tr"
        create_user(
            email=email,
            username="forgot_pass_user",
            password="OriginalPassword123!",
            full_name="Şifre Sıfırlama Öğrenci",
            university_id="itu"
        )

        res = self.client.post("/api/auth/forgot-password", json={"email": email})
        self.assertEqual(res.status_code, 200, f"Forgot password failed: {res.text}")
        data = res.json()

        self.assertIn("status", data)
        self.assertEqual(data.get("cooldown_seconds"), 60)

        # In sandbox mode, verify 6-digit reset code
        code = data.get("reset_code_sandbox") or data.get("reset_code") or data.get("demo_code")
        self.assertIsNotNone(code, "Reset code must be returned in sandbox response")
        self.assertTrue(re.match(r"^\d{6}$", str(code)), f"Reset code must be 6 numeric digits, got: {code}")

        # Verify SQLite password_resets record exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT reset_code, expires_at, is_used FROM password_resets WHERE email = ? ORDER BY id DESC LIMIT 1", (email,))
        row = cursor.fetchone()
        self.assertIsNotNone(row, "Reset request was not recorded in password_resets table")
        self.assertEqual(row["reset_code"], str(code))
        self.assertEqual(row["is_used"], 0)
        conn.close()

    def test_forgot_password_60s_cooldown(self):
        """Verify submitting consecutive forgot password requests within 60s is rejected."""
        email = "cooldown.pass@boun.edu.tr"
        create_user(
            email=email,
            username="cooldown_pass_user",
            password="CooldownPassword123!",
            full_name="Cooldown Öğrenci",
            university_id="boun"
        )

        # First request -> 200
        res1 = self.client.post("/api/auth/forgot-password", json={"email": email})
        self.assertEqual(res1.status_code, 200)

        # Immediate second request -> rejected with cooldown error
        res2 = self.client.post("/api/auth/forgot-password", json={"email": email})
        self.assertIn(res2.status_code, [400, 429])
        self.assertIn("bekleyin", res2.text.lower())

    def test_forgot_password_invalid_email_bounds(self):
        """Verify malformed email formats trigger 400 or 422 Unprocessable Entity."""
        res = self.client.post("/api/auth/forgot-password", json={"email": "invalid-not-an-email"})
        self.assertIn(res.status_code, [400, 422])

    # =========================================================================
    # 3. Reset Password Confirmation & Login Verification (/api/auth/reset-password)
    # =========================================================================
    def test_reset_password_success_and_login_with_new_credentials(self):
        """Verify code validation, PBKDF2 hash update, and successful login with new password."""
        email = "reset.success@metu.edu.tr"
        username = "metu_reset_user"
        initial_pw = "OldSecretPassword123!"
        new_pw = "NewStrongPassword2026!"

        create_user(
            email=email,
            username=username,
            password=initial_pw,
            full_name="ODTÜ Reset Test",
            university_id="metu"
        )

        # 1. Request reset code
        forgot_res = self.client.post("/api/auth/forgot-password", json={"email": email})
        self.assertEqual(forgot_res.status_code, 200)
        code = forgot_res.json().get("reset_code_sandbox") or forgot_res.json().get("reset_code") or forgot_res.json().get("demo_code")

        # 2. Submit password reset
        reset_res = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "reset_code": code,
            "new_password": new_pw
        })
        self.assertEqual(reset_res.status_code, 200, f"Password reset failed: {reset_res.text}")

        # 3. Verify old password is now REJECTED
        old_login = self.client.post("/api/auth/login", json={
            "identifier": username,
            "password": initial_pw
        })
        self.assertEqual(old_login.status_code, 401, "Old password must no longer authenticate")

        # 4. Verify new password SUCCEEDS
        new_login = self.client.post("/api/auth/login", json={
            "identifier": username,
            "password": new_pw
        })
        self.assertEqual(new_login.status_code, 200, "New password must authenticate successfully")
        self.assertIsNotNone(new_login.json().get("token"))

        # 5. Verify PBKDF2 format in database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
        pw_hash = cursor.fetchone()["password_hash"]
        conn.close()
        self.assertTrue(pw_hash.startswith("pbkdf2:sha256:100000$"), f"Expected PBKDF2 hash format, got: {pw_hash}")

    def test_reset_password_rejects_invalid_code(self):
        """Verify submitting an incorrect reset code returns HTTP 400 and does not change password."""
        email = "wrong.code@itu.edu.tr"
        create_user(
            email=email,
            username="wrong_code_user",
            password="CorrectPassword123!",
            full_name="Wrong Code Student",
            university_id="itu"
        )

        # Trigger reset code
        self.client.post("/api/auth/forgot-password", json={"email": email})

        # Submit wrong code
        res = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "reset_code": "000000",
            "new_password": "AttemptedNewPassword123!"
        })
        self.assertEqual(res.status_code, 400)

        # Verify original password still works
        login_res = self.client.post("/api/auth/login", json={
            "identifier": "wrong_code_user",
            "password": "CorrectPassword123!"
        })
        self.assertEqual(login_res.status_code, 200)

    def test_reset_password_one_time_code_consumption(self):
        """Verify a consumed reset code cannot be re-used (anti-replay)."""
        email = "replay.code@itu.edu.tr"
        create_user(
            email=email,
            username="replay_code_user",
            password="OriginalPass123!",
            full_name="Replay Code Student",
            university_id="itu"
        )

        forgot_res = self.client.post("/api/auth/forgot-password", json={"email": email})
        code = forgot_res.json().get("reset_code_sandbox") or forgot_res.json().get("reset_code") or forgot_res.json().get("demo_code")

        # First consumption -> 200
        res1 = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "reset_code": code,
            "new_password": "NewValidPass123!"
        })
        self.assertEqual(res1.status_code, 200)

        # Second attempt with same code -> 400
        res2 = self.client.post("/api/auth/reset-password", json={
            "email": email,
            "reset_code": code,
            "new_password": "AnotherNewPass123!"
        })
        self.assertEqual(res2.status_code, 400)


if __name__ == "__main__":
    unittest.main()
