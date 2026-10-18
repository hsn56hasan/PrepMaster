#!/usr/bin/env python3
"""
PrepMaster Production Deployment & System Integrity Verification Script
Checks datasets, audio assets, database schemas, OTP lifecycles, and docker configs.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PASS = "[PASS]"
FAIL = "[FAIL]"


class DeploymentChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.checks_passed = 0

    def assert_check(self, description: str, condition: bool, err_msg: str):
        if condition:
            print(f"  \033[92m{PASS}\033[0m {description}")
            self.checks_passed += 1
        else:
            print(f"  \033[91m{FAIL}\033[0m {description}: {err_msg}")
            self.errors.append(f"{description}: {err_msg}")

    def run_all(self):
        print("\n=======================================================")
        print("  PrepMaster Production Pre-Flight & Integrity Check")
        print("=======================================================\n")

        self.check_environment()
        self.check_datasets()
        self.check_audio_assets()
        self.check_database_and_otp()
        self.check_docker_configs()

        print("\n-------------------------------------------------------")
        print(f"Total Checks Passed: {self.checks_passed}")
        if self.errors:
            print(f"\033[91mFAILED with {len(self.errors)} error(s):\033[0m")
            for err in self.errors:
                print(f"  - {err}")
            return False
        else:
            print("\033[92mALL DEPLOYMENT & INTEGRITY CHECKS PASSED SUCCESSFULLY!\033[0m")
            return True

    def check_environment(self):
        print("[1/5] Checking Python Environment & Dependencies...")
        self.assert_check("Python 3.10+ runtime", sys.version_info >= (3, 10), f"Found {sys.version}")

        try:
            import fastapi
            self.assert_check("FastAPI installed", True, "")
        except ImportError:
            self.assert_check("FastAPI installed", False, "Missing fastapi")

        try:
            import uvicorn
            self.assert_check("Uvicorn installed", True, "")
        except ImportError:
            self.assert_check("Uvicorn installed", False, "Missing uvicorn")

        try:
            import pydantic
            self.assert_check("Pydantic installed", True, "")
        except ImportError:
            self.assert_check("Pydantic installed", False, "Missing pydantic")

    def check_datasets(self):
        print("\n[2/5] Checking Core Datasets Integrity...")
        data_dir = ROOT_DIR / "data"

        # Questions
        q_file = data_dir / "questions.json"
        if q_file.exists():
            with open(q_file, "r", encoding="utf-8") as f:
                questions = json.load(f)
            self.assert_check("Questions count >= 105", len(questions) >= 105, f"Found {len(questions)}")
        else:
            self.assert_check("questions.json exists", False, "File missing")

        # Vocabulary
        v_file = data_dir / "vocabulary.json"
        if v_file.exists():
            with open(v_file, "r", encoding="utf-8") as f:
                vocab = json.load(f)
            self.assert_check("Vocabulary count >= 110", len(vocab) >= 110, f"Found {len(vocab)}")
        else:
            self.assert_check("vocabulary.json exists", False, "File missing")

        # Listening
        l_file = data_dir / "listening.json"
        if l_file.exists():
            with open(l_file, "r", encoding="utf-8") as f:
                tracks = json.load(f)
            self.assert_check("Listening tracks count == 8", len(tracks) == 8, f"Found {len(tracks)}")
        else:
            self.assert_check("listening.json exists", False, "File missing")

        # Speaking
        s_file = data_dir / "speaking.json"
        if s_file.exists():
            with open(s_file, "r", encoding="utf-8") as f:
                speaking = json.load(f)
            self.assert_check("Speaking tasks count >= 6", len(speaking) >= 6, f"Found {len(speaking)}")
        else:
            self.assert_check("speaking.json exists", False, "File missing")

    def check_audio_assets(self):
        print("\n[3/5] Checking Academic MP3 Audio Assets (static/audio)...")
        audio_dir = ROOT_DIR / "static" / "audio"
        self.assert_check("Audio directory exists", audio_dir.exists() and audio_dir.is_dir(), "Directory missing")

        expected_tracks = [
            "track_1.mp3", "track_2.mp3", "track_3.mp3", "track_4.mp3",
            "track_5.mp3", "track_6.mp3", "track_7.mp3", "track_8.mp3",
            "lis_buept_01.mp3", "lis_itu_01.mp3", "lis_odtu_01.mp3", "lis_bilkent_01.mp3",
            "lis_buept_02.mp3", "lis_bilkent_02.mp3", "lis_odtu_02.mp3", "lis_itu_02.mp3"
        ]

        found_count = 0
        for track_name in expected_tracks:
            track_path = audio_dir / track_name
            if track_path.exists() and track_path.stat().st_size > 50000:
                found_count += 1

        self.assert_check(f"High-fidelity MP3 tracks ({found_count}/{len(expected_tracks)})", found_count == len(expected_tracks), f"Found {found_count}")

    def check_database_and_otp(self):
        print("\n[4/5] Checking Database Schema & OTP Lifecycle...")
        from backend.database import init_db, get_db, create_student_otp, verify_student_otp

        init_db()
        conn = get_db()
        cursor = conn.cursor()

        tables = ["student_otps", "users", "mistake_vault", "exam_attempts", "student_verifications", "vocab_progress"]
        for tbl in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tbl}'")
            self.assert_check(f"Table '{tbl}' exists in SQLite", cursor.fetchone() is not None, "Missing table")
        conn.close()


        # OTP cycle test
        test_email = "deploy_test@itu.edu.tr"
        otp_res = create_student_otp(test_email, "040220999")
        self.assert_check("Create student OTP", otp_res.get("success") is True, str(otp_res))

        code = otp_res.get("otp_code")
        # Test wrong code
        fail_verify = verify_student_otp(test_email, "000000")
        self.assert_check("Reject invalid OTP code", fail_verify.get("success") is False, "Accepted wrong OTP")

        # Test valid code
        succ_verify = verify_student_otp(test_email, code)
        self.assert_check("Verify valid OTP code", succ_verify.get("success") is True, str(succ_verify))

    def check_docker_configs(self):
        print("\n[5/5] Checking Docker Orchestration Configs...")
        dockerfile = ROOT_DIR / "Dockerfile"
        compose_file = ROOT_DIR / "docker-compose.yml"
        env_example = ROOT_DIR / ".env.example"

        self.assert_check("Dockerfile exists", dockerfile.exists(), "Missing Dockerfile")
        if dockerfile.exists():
            content = dockerfile.read_text(encoding="utf-8")
            self.assert_check("Dockerfile has HEALTHCHECK", "HEALTHCHECK" in content, "Missing HEALTHCHECK")
            self.assert_check("Dockerfile has non-root user", "USER prepmaster" in content, "Missing non-root user")

        self.assert_check("docker-compose.yml exists", compose_file.exists(), "Missing docker-compose.yml")
        if compose_file.exists():
            content = compose_file.read_text(encoding="utf-8")
            self.assert_check("docker-compose has volume persistence", "prepmaster_data" in content, "Missing persistent volume")

        self.assert_check(".env.example exists", env_example.exists(), "Missing .env.example")

if __name__ == "__main__":
    checker = DeploymentChecker()
    success = checker.run_all()
    sys.exit(0 if success else 1)
