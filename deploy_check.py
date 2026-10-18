#!/usr/bin/env python3
"""
PrepMaster Production Deployment & System Integrity Verification Script
Checks datasets, audio assets, database schemas, OTP lifecycles, docker configs,
Nginx reverse proxy, network isolation, and Cloudflare/Fail2ban edge hardening.
"""

import sys
import os
import json
import sqlite3
import yaml
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
        self.check_nginx_configs()
        self.check_docker_hardening()
        self.check_fail2ban_and_edge()

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
        print("[1/8] Checking Python Environment & Dependencies...")
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
        print("\n[2/8] Checking Core Datasets Integrity...")
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
        print("\n[3/8] Checking Academic MP3 Audio Assets (static/audio)...")
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
        print("\n[4/8] Checking Database Schema & OTP Lifecycle...")
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
        print("\n[5/8] Checking Docker Orchestration Configs...")
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

    def check_nginx_configs(self):
        print("\n[6/8] Checking Nginx Reverse Proxy & Edge Security Configs...")
        nginx_conf = ROOT_DIR / "nginx" / "nginx.conf"
        default_conf = ROOT_DIR / "nginx" / "conf.d" / "default.conf"
        proxy_params = ROOT_DIR / "nginx" / "proxy_params"
        cf_ips = ROOT_DIR / "nginx" / "cloudflare_ips.conf"
        cert_file = ROOT_DIR / "nginx" / "ssl" / "prepmaster.crt"
        key_file = ROOT_DIR / "nginx" / "ssl" / "prepmaster.key"

        self.assert_check("nginx.conf exists", nginx_conf.exists(), "Missing nginx.conf")
        self.assert_check("conf.d/default.conf exists", default_conf.exists(), "Missing default.conf")
        self.assert_check("proxy_params exists", proxy_params.exists(), "Missing proxy_params")
        self.assert_check("cloudflare_ips.conf exists", cf_ips.exists(), "Missing cloudflare_ips.conf")
        self.assert_check("TLS certificate exists", cert_file.exists(), "Missing prepmaster.crt")
        self.assert_check("TLS private key exists", key_file.exists(), "Missing prepmaster.key")

        if nginx_conf.exists():
            main_text = nginx_conf.read_text(encoding="utf-8")
            self.assert_check("Rate limiting zones defined", "limit_req_zone" in main_text and "zone=api_auth" in main_text, "Missing rate limit zones")
            self.assert_check("Buffer overflow mitigation configured", "client_body_buffer_size" in main_text and "client_max_body_size" in main_text, "Missing buffer limits")
            self.assert_check("Gzip compression enabled", "gzip on;" in main_text and "gzip_types" in main_text, "Missing gzip compression")
            self.assert_check("Rate limit status HTTP 429 configured", "limit_req_status 429" in main_text, "Missing 429 status directive")

        if default_conf.exists():
            def_text = default_conf.read_text(encoding="utf-8")
            self.assert_check("HTTPS 443 SSL block configured", "listen 443 ssl" in def_text, "Missing 443 SSL server block")
            self.assert_check("HTTP to HTTPS 301 redirection", "return 301 https://$host$request_uri;" in def_text, "Missing HTTP redirect")
            self.assert_check("Modern TLS 1.2 and 1.3 enforced", "TLSv1.2 TLSv1.3" in def_text, "Insecure TLS protocols")
            self.assert_check("HSTS security header present", "Strict-Transport-Security" in def_text, "Missing HSTS header")
            self.assert_check("Static audio caching configured", "location /static/audio/" in def_text and "Accept-Ranges bytes" in def_text, "Missing audio caching")
            self.assert_check("Sensitive OTP/Auth rate limiting applied", "zone=api_auth" in def_text, "Auth endpoints not rate limited")
            self.assert_check("Bad bot / exploit scanner blocking", "sqlmap" in def_text and "nikto" in def_text, "Missing bot filter")

        if proxy_params.exists():
            pp_text = proxy_params.read_text(encoding="utf-8")
            self.assert_check("Proxy headers sanitized (X-Real-IP, Host)", "X-Real-IP" in pp_text and "X-Forwarded-Proto" in pp_text, "Incomplete proxy headers")

    def check_docker_hardening(self):
        print("\n[7/8] Checking Docker Hardening, Resource Limits & Network Isolation...")
        compose_file = ROOT_DIR / "docker-compose.yml"
        if not compose_file.exists():
            self.assert_check("docker-compose.yml parseable", False, "File missing")
            return

        try:
            with open(compose_file, "r", encoding="utf-8") as f:
                compose_data = yaml.safe_load(f)
            self.assert_check("docker-compose.yml valid YAML", True, "")
        except Exception as e:
            self.assert_check("docker-compose.yml valid YAML", False, str(e))
            return

        services = compose_data.get("services", {})
        networks = compose_data.get("networks", {})

        # Network separation
        self.assert_check("Frontend network defined", "frontend_net" in networks, "Missing frontend_net")
        self.assert_check("Backend network defined", "backend_net" in networks, "Missing backend_net")

        # Backend app isolation
        app_svc = services.get("prepmaster-app", {})
        self.assert_check("prepmaster-app service defined", bool(app_svc), "Service prepmaster-app missing")
        self.assert_check("prepmaster-app has no published host ports", "ports" not in app_svc, "Backend directly exposes ports to host!")
        self.assert_check("prepmaster-app attached to backend_net", "backend_net" in app_svc.get("networks", []), "Backend not in backend_net")

        # Nginx reverse proxy
        nginx_svc = services.get("nginx", {})
        self.assert_check("Nginx service defined", bool(nginx_svc), "Service nginx missing")
        self.assert_check("Nginx binds ports 80 and 443", "80:80" in nginx_svc.get("ports", []) and "443:443" in nginx_svc.get("ports", []), "Nginx ports missing")
        self.assert_check("Nginx bridges frontend and backend networks", "frontend_net" in nginx_svc.get("networks", []) and "backend_net" in nginx_svc.get("networks", []), "Nginx networks missing")

        # Resource limits
        app_limits = app_svc.get("deploy", {}).get("resources", {}).get("limits", {})
        self.assert_check("Backend resource limits configured", "cpus" in app_limits and "memory" in app_limits, "Missing CPU/memory limits on backend")

        nginx_limits = nginx_svc.get("deploy", {}).get("resources", {}).get("limits", {})
        self.assert_check("Nginx resource limits configured", "cpus" in nginx_limits and "memory" in nginx_limits, "Missing CPU/memory limits on nginx")

        # Security options
        self.assert_check("no-new-privileges flag configured", "no-new-privileges:true" in app_svc.get("security_opt", []), "Missing no-new-privileges")

        # Read-only volumes
        nginx_vols = nginx_svc.get("volumes", [])
        has_ro = any(":ro" in v for v in nginx_vols)
        self.assert_check("Nginx uses read-only volume mounts", has_ro, "Nginx configs not mounted read-only")

    def check_fail2ban_and_edge(self):
        print("\n[8/8] Checking Fail2ban DDoS Mitigation & Cloudflare Documentation...")
        jail_file = ROOT_DIR / "docker" / "fail2ban" / "jail.d" / "prepmaster-jail.local"
        filter_req = ROOT_DIR / "docker" / "fail2ban" / "filter.d" / "nginx-req-limit.conf"
        filter_auth = ROOT_DIR / "docker" / "fail2ban" / "filter.d" / "nginx-auth.conf"
        filter_badbots = ROOT_DIR / "docker" / "fail2ban" / "filter.d" / "nginx-badbots.conf"
        cf_doc = ROOT_DIR / "docs" / "CLOUDFLARE_EDGE_SECURITY.md"

        self.assert_check("Fail2ban jail configuration exists", jail_file.exists(), "Missing prepmaster-jail.local")
        self.assert_check("Fail2ban rate limit filter exists", filter_req.exists(), "Missing nginx-req-limit.conf")
        self.assert_check("Fail2ban auth abuse filter exists", filter_auth.exists(), "Missing nginx-auth.conf")
        self.assert_check("Fail2ban badbots filter exists", filter_badbots.exists(), "Missing nginx-badbots.conf")

        self.assert_check("Cloudflare Edge Security guide exists", cf_doc.exists(), "Missing CLOUDFLARE_EDGE_SECURITY.md")
        if cf_doc.exists():
            doc_text = cf_doc.read_text(encoding="utf-8")
            self.assert_check("Guide covers DNS Proxy (Orange Cloud)", "Orange Cloud" in doc_text, "Missing DNS proxy section")
            self.assert_check("Guide covers Under Attack Mode", "Under Attack Mode" in doc_text, "Missing Under Attack Mode")
            self.assert_check("Guide covers SSL Full (Strict)", "Full (Strict)" in doc_text, "Missing Full Strict SSL section")
            self.assert_check("Guide covers WAF & Rate Limiting", "Rate Limit" in doc_text, "Missing Rate Limiting section")


if __name__ == "__main__":
    checker = DeploymentChecker()
    success = checker.run_all()
    sys.exit(0 if success else 1)
