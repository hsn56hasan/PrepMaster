"""
PrepMaster Comprehensive Security Test Suite
Tests:
1. Brute Force & DoS Defense (Sliding Window Rate Limiter for OTP, Auth, and AI endpoints)
2. Security Headers Middleware (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, etc.)
3. CORS Hardening & Credential Protection
4. Input Validation & Sanitization (SQL Injection immunity, XSS sanitization, Pydantic bounds & regex)
5. Token & Session Security (PBKDF2 with dynamic salt, legacy migration, JWT generation & expiry)
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Set test environment
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_security.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "super_secret_test_key_for_security_suite_2026"
os.environ["ALLOWED_ORIGINS"] = "http://localhost:8050,http://127.0.0.1:8050"

from fastapi.testclient import TestClient
from backend.app import app
from backend.database import init_db, get_db, create_user, authenticate_user
import backend.security as sec


class TestSecuritySuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
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
        # Reset rate limiter memory before each test
        sec.rate_limiter.reset()

    # =========================================================================
    # 1. Brute Force & DoS Defense Tests
    # =========================================================================
    def test_rate_limit_request_otp(self):
        """Verify /api/student/request-otp blocks excessive requests with HTTP 429."""
        email = "dos_test@itu.edu.tr"
        for i in range(3):
            res = self.client.post("/api/student/request-otp", json={"email": email, "student_number": "123456"})
            self.assertIn(res.status_code, [200, 400])

        # 4th request within 1 minute should trigger rate limit (max 3 per email)
        res_blocked = self.client.post("/api/student/request-otp", json={"email": email, "student_number": "123456"})
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Retry-After", res_blocked.headers)
        self.assertIn("Çok fazla", res_blocked.json().get("detail", ""))

    def test_rate_limit_verify_otp(self):
        """Verify /api/student/verify-otp rate limits brute-force guessing."""
        email = "brute_otp@itu.edu.tr"
        for i in range(5):
            res = self.client.post("/api/student/verify-otp", json={"email": email, "otp_code": "111111", "user_id": 1})
            self.assertIn(res.status_code, [400, 200])

        # 6th attempt should trigger 429
        blocked = self.client.post("/api/student/verify-otp", json={"email": email, "otp_code": "111111", "user_id": 1})
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Retry-After", blocked.headers)

    def test_rate_limit_login_brute_force(self):
        """Verify /api/auth/login blocks credential stuffing / brute-force."""
        for i in range(5):
            res = self.client.post("/api/auth/login", json={"identifier": "victim_student", "password": f"wrong_{i}"})
            self.assertEqual(res.status_code, 401)

        # 6th login attempt should be rate-limited
        blocked = self.client.post("/api/auth/login", json={"identifier": "victim_student", "password": "wrong"})
        self.assertEqual(blocked.status_code, 429)
        self.assertIn("Retry-After", blocked.headers)

    def test_rate_limit_ai_evaluation_endpoints(self):
        """Verify AI endpoints are protected against compute exhaustion DoS."""
        essay_payload = {
            "essay": "Education is essential for academic development and future research. " * 15,
            "prompt": "Test Prompt",
            "level": "B2"
        }
        for i in range(10):
            res = self.client.post("/api/writing/evaluate", json=essay_payload)
            self.assertEqual(res.status_code, 200)

        # 11th request should be rate-limited
        res_blocked = self.client.post("/api/writing/evaluate", json=essay_payload)
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Retry-After", res_blocked.headers)

    # =========================================================================
    # 2. Security Headers Middleware Tests
    # =========================================================================
    def test_security_headers_present(self):
        """Verify all essential OWASP security headers are present on responses."""
        res = self.client.get("/api/universities")
        self.assertEqual(res.status_code, 200)

        # 1. Content Security Policy
        csp = res.headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'none'", csp)

        # 2. Strict Transport Security
        hsts = res.headers.get("Strict-Transport-Security", "")
        self.assertIn("max-age=31536000", hsts)
        self.assertIn("includeSubDomains", hsts)

        # 3. MIME Sniffing Defense
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")

        # 4. Clickjacking Defense
        self.assertEqual(res.headers.get("X-Frame-Options"), "DENY")

        # 5. Referrer Policy
        self.assertEqual(res.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")

        # 6. Legacy XSS Protection
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")

    # =========================================================================
    # 3. CORS Hardening Tests
    # =========================================================================
    def test_cors_allowed_origin(self):
        """Verify authorized origin is accepted with credentials."""
        res = self.client.options(
            "/api/universities",
            headers={
                "Origin": "http://localhost:8050",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertEqual(res.headers.get("Access-Control-Allow-Origin"), "http://localhost:8050")
        self.assertEqual(res.headers.get("Access-Control-Allow-Credentials"), "true")

    def test_cors_disallowed_origin(self):
        """Verify unauthorized external origin is not mirrored in Access-Control-Allow-Origin."""
        res = self.client.options(
            "/api/universities",
            headers={
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        self.assertNotEqual(res.headers.get("Access-Control-Allow-Origin"), "http://malicious-site.com")
        self.assertNotEqual(res.headers.get("Access-Control-Allow-Origin"), "*")

    # =========================================================================
    # 4. Input Validation & Sanitization Tests
    # =========================================================================
    def test_xss_sanitization(self):
        """Verify XSS payloads are stripped or neutralized in models."""
        malicious_script = "<script>alert('XSS')</script>John Doe"
        sanitized = sec.sanitize_text(malicious_script, strip_tags=True)
        self.assertEqual(sanitized, "John Doe")

        img_xss = '<img src=x onerror="alert(1)">'
        sanitized_img = sec.sanitize_text(img_xss, strip_tags=False)
        self.assertNotIn("onerror=", sanitized_img)
        self.assertIn("data-blocked=", sanitized_img)

        js_uri = '<a href="javascript:alert(1)">Click</a>'
        sanitized_js = sec.sanitize_text(js_uri, strip_tags=False)
        self.assertNotIn("javascript:", sanitized_js)

    def test_pydantic_validation_bounds(self):
        """Verify oversized or malformed inputs trigger 422 Unprocessable Entity."""
        # 1. Invalid email regex
        res1 = self.client.post("/api/auth/register", json={
            "email": "not-an-email",
            "username": "validuser",
            "password": "validpassword",
            "full_name": "Valid Name"
        })
        self.assertEqual(res1.status_code, 422)

        # 2. Password too short (<6 characters)
        res2 = self.client.post("/api/auth/register", json={
            "email": "valid@itu.edu.tr",
            "username": "validuser",
            "password": "123",
            "full_name": "Valid Name"
        })
        self.assertEqual(res2.status_code, 422)

        # 3. Invalid OTP code (alphabetic or wrong length)
        res3 = self.client.post("/api/student/verify-otp", json={
            "email": "student@itu.edu.tr",
            "otp_code": "abcdef"
        })
        self.assertEqual(res3.status_code, 422)

        # 4. Essay exceeds length bounds (>20,000 chars)
        res4 = self.client.post("/api/writing/evaluate", json={
            "essay": "A" * 25000
        })
        self.assertEqual(res4.status_code, 422)

    def test_sql_injection_defense(self):
        """Verify parameterized queries completely prevent SQL injection attacks."""
        conn = get_db()
        cursor = conn.cursor()

        # SQL Injection attempt in authentication
        sqli_payload = "' OR '1'='1"
        res = authenticate_user(sqli_payload, "any_password")
        self.assertIsNone(res)

        # Test parameterized execution safely preserves quotes without executing
        cursor.execute("SELECT id FROM users WHERE username = ?", (sqli_payload,))
        row = cursor.fetchone()
        self.assertIsNone(row)
        conn.close()

    # =========================================================================
    # 5. Token & Session Security Tests
    # =========================================================================
    def test_pbkdf2_password_hashing_and_dynamic_salt(self):
        """Verify passwords are hashed with PBKDF2 and random cryptographic salts."""
        raw_pw = "MySecureP@ssword2026"
        hash1 = sec.hash_password(raw_pw)
        hash2 = sec.hash_password(raw_pw)

        # Verify PBKDF2 format
        self.assertTrue(hash1.startswith("pbkdf2:sha256:100000$"))
        # Verify dynamic salt ensures different hashes for the same password
        self.assertNotEqual(hash1, hash2)

        # Verify verification works for both
        self.assertTrue(sec.verify_password(raw_pw, hash1))
        self.assertTrue(sec.verify_password(raw_pw, hash2))
        self.assertFalse(sec.verify_password("WrongPassword", hash1))

    def test_legacy_password_verification_and_auto_migration(self):
        """Verify legacy salted SHA-256 hashes still verify and auto-upgrade on login."""
        import hashlib
        legacy_salt = sec.LEGACY_SALT
        legacy_pw = "LegacyPass123"
        legacy_hash = hashlib.sha256((legacy_pw + legacy_salt).encode("utf-8")).hexdigest()

        # Insert a user with legacy hash
        conn = get_db()
        with conn:
            conn.execute("""
                INSERT OR REPLACE INTO users (id, email, username, password_hash, full_name, university_id, is_verified_student)
                VALUES (999, 'legacy@itu.edu.tr', 'legacyuser', ?, 'Legacy Student', 'itu', 1)
            """, (legacy_hash,))
        conn.close()

        # Authenticate should succeed using legacy fallback
        user = authenticate_user("legacyuser", legacy_pw)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "legacyuser")

        # Database hash should now be automatically upgraded to PBKDF2!
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE id = 999")
        new_hash = cursor.fetchone()["password_hash"]
        conn.close()

        self.assertTrue(new_hash.startswith("pbkdf2:sha256:100000$"))
        # Verify user can still authenticate with the upgraded PBKDF2 hash
        user_again = authenticate_user("legacyuser", legacy_pw)
        self.assertIsNotNone(user_again)

    def test_jwt_session_token_lifecycle(self):
        """Verify JWT generation, Bearer verification, expiration, and signature tampering."""
        token, expires_in = sec.create_session_token(
            user_id=1,
            username="ituhazirlik",
            email="ogrenci@itu.edu.tr",
            expires_in_hours=2
        )
        self.assertEqual(expires_in, 7200)

        # 1. Valid token verification
        payload = sec.verify_session_token(token)
        self.assertEqual(payload["username"], "ituhazirlik")
        self.assertEqual(payload["user_id"], 1)

        # 2. Tampered token rejection
        tampered = token[:-4] + "abcd"
        with self.assertRaises(Exception):
            sec.verify_session_token(tampered)

        # 3. Expired token rejection
        expired_token, _ = sec.create_session_token(
            user_id=1,
            username="ituhazirlik",
            email="ogrenci@itu.edu.tr",
            expires_in_hours=-1 # Already expired 1 hour ago
        )
        with self.assertRaises(Exception):
            sec.verify_session_token(expired_token)

    def test_auth_me_bearer_token(self):
        """Verify /api/auth/me authenticates via Authorization: Bearer <token>."""
        token, _ = sec.create_session_token(
            user_id=1,
            username="ituhazirlik",
            email="ogrenci@itu.edu.tr"
        )
        res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["username"], "ituhazirlik")
        self.assertEqual(data.get("authenticated_via"), "bearer_token")


if __name__ == "__main__":
    unittest.main()
