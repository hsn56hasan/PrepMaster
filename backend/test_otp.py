import unittest
import os
import sys
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Setup temporary test database
os.environ["PREPMASTER_DB_PATH"] = str(Path(__file__).resolve().parent / "test_prepmaster.db")

from backend.database import init_db, create_student_otp, verify_student_otp, get_db

class TestStudentOTP(unittest.TestCase):
    def setUp(self):
        init_db()

    def tearDown(self):
        test_db = Path(__file__).resolve().parent / "test_prepmaster.db"
        if test_db.exists():
            try:
                test_db.unlink()
            except Exception:
                pass

    def test_otp_flow_success(self):
        email = "student@itu.edu.tr"
        gen = create_student_otp(email, "040220999")
        self.assertTrue(gen["success"])
        self.assertEqual(len(gen["otp_code"]), 6)
        self.assertEqual(gen["cooldown_seconds"], 60)

        # Verify correct code
        ver = verify_student_otp(email, gen["otp_code"])
        self.assertTrue(ver["success"])
        self.assertEqual(ver["verification_status"], "verified")

    def test_otp_cooldown(self):
        email = "cooldown@boun.edu.tr"
        gen1 = create_student_otp(email, "12345")
        self.assertTrue(gen1["success"])

        # Immediate second request should be rate-limited
        gen2 = create_student_otp(email, "12345")
        self.assertFalse(gen2["success"])
        self.assertIn("bekleyin", gen2["detail"])

    def test_otp_invalid_code(self):
        email = "invalid@metu.edu.tr"
        gen = create_student_otp(email, "54321")
        self.assertTrue(gen["success"])

        # Wrong code
        ver = verify_student_otp(email, "000000")
        self.assertFalse(ver["success"])
        self.assertIn("Kalan deneme", ver["detail"])

if __name__ == "__main__":
    unittest.main()
