"""
Güvenlik sıkılaştırması:
- Cloudflare arkasında gerçek ziyaretçi IP'si (CF-Connecting-IP) yalnızca istek Cloudflare'den geldiyse kullanılır;
  Railway adresine doğrudan gelip başlığı uyduran saldırgan hız sınırını atlatamaz.
- Şifreler 600.000 turlu PBKDF2 ile saklanır; eski 100.000 turlu özetler geçerli kalır ve girişte yükseltilir.
- Dış betikler ve Python paketleri sabit sürümlüdür.
"""
import os
import re
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))
os.environ.setdefault("PREPMASTER_DB_PATH", str(BASE_DIR / "backend" / "test_security_hardening.db"))
os.environ.setdefault("SECRET_KEY", "security_hardening_suite_secret_key_2026")

from starlette.requests import Request  # noqa: E402

import backend.app  # noqa: E402,F401  (veritabanı yolunu ve modülleri paketle aynı sırada kurar)
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402


def make_request(peer="10.0.0.5", headers=None):
    raw = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    return Request({"type": "http", "method": "GET", "path": "/", "headers": raw, "client": (peer, 12345)})


class TestClientIpBehindCloudflare(unittest.TestCase):
    def setUp(self):
        self._saved = sec.CLIENT_IP_HEADER

    def tearDown(self):
        sec.CLIENT_IP_HEADER = self._saved

    def test_railway_without_cloudflare_ignores_spoofed_cf_header(self):
        sec.CLIENT_IP_HEADER = "X-Real-IP"
        req = make_request(headers={"X-Real-IP": "85.105.10.20", "CF-Connecting-IP": "1.1.1.1"})
        self.assertEqual(sec.get_client_ip(req), "85.105.10.20")

    def test_railway_behind_cloudflare_uses_visitor_ip(self):
        sec.CLIENT_IP_HEADER = "X-Real-IP"
        req = make_request(headers={"X-Real-IP": "172.64.10.1", "CF-Connecting-IP": "85.105.10.20"})
        self.assertEqual(sec.get_client_ip(req), "85.105.10.20")
        req6 = make_request(headers={"X-Real-IP": "2606:4700::6810:1", "CF-Connecting-IP": "2a02:4780::1"})
        self.assertEqual(sec.get_client_ip(req6), "2a02:4780::1")

    def test_cloudflare_without_visitor_header_falls_back_to_upstream(self):
        sec.CLIENT_IP_HEADER = "X-Real-IP"
        req = make_request(headers={"X-Real-IP": "104.16.0.9", "CF-Connecting-IP": "bozuk"})
        self.assertEqual(sec.get_client_ip(req), "104.16.0.9")

    def test_direct_connections(self):
        sec.CLIENT_IP_HEADER = ""
        self.assertEqual(sec.get_client_ip(make_request("104.16.0.9", {"CF-Connecting-IP": "85.105.10.20"})), "85.105.10.20")
        self.assertEqual(sec.get_client_ip(make_request("85.105.10.20", {"CF-Connecting-IP": "1.1.1.1"})), "85.105.10.20")

    def test_cloudflare_ranges_are_loaded(self):
        self.assertTrue(sec._is_cloudflare("162.158.1.1"))
        self.assertFalse(sec._is_cloudflare("8.8.8.8"))
        self.assertFalse(sec._is_cloudflare("not-an-ip"))


class TestPasswordHashing(unittest.TestCase):
    def test_new_hashes_use_600k_rounds(self):
        h = sec.hash_password("Parola123!")
        self.assertTrue(h.startswith("pbkdf2:sha256:600000$"))
        self.assertTrue(sec.verify_password("Parola123!", h))
        self.assertFalse(sec.verify_password("yanlis", h))
        self.assertFalse(sec.password_needs_rehash(h))

    def test_old_hashes_still_work_and_need_rehash(self):
        old = sec.hash_password("Parola123!", iterations=100_000)
        self.assertTrue(old.startswith("pbkdf2:sha256:100000$"))
        self.assertTrue(sec.verify_password("Parola123!", old))
        self.assertTrue(sec.password_needs_rehash(old))
        self.assertTrue(sec.password_needs_rehash(""))

    def test_tampered_round_count_is_rejected(self):
        h = sec.hash_password("Parola123!", iterations=100_000)
        self.assertFalse(sec.verify_password("Parola123!", h.replace(":100000$", ":1$", 1)))

    def test_login_upgrades_old_hash(self):
        db.init_db()
        email = f"yukselt_{os.getpid()}@example.com"
        conn = db.get_db()
        with conn:
            conn.execute("DELETE FROM users WHERE email = ?", (email,))
            conn.execute(
                "INSERT INTO users (email, username, password_hash, full_name) VALUES (?, ?, ?, ?)",
                (email, f"yukselt_{os.getpid()}", sec.hash_password("Parola123!", iterations=100_000), "Eski Hash"),
            )
        conn.close()
        self.assertIsNotNone(db.authenticate_user(email, "Parola123!"))
        conn = db.get_db()
        stored = conn.execute("SELECT password_hash FROM users WHERE email = ?", (email,)).fetchone()[0]
        conn.execute("DELETE FROM users WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        self.assertTrue(stored.startswith("pbkdf2:sha256:600000$"))


class TestPinnedDependencies(unittest.TestCase):
    def test_external_scripts_are_pinned(self):
        for name in ("index.html", "kvkk.html", "admin.html"):
            html = (BASE_DIR / "static" / name).read_text(encoding="utf-8")
            self.assertNotIn("@latest", html, name)
            self.assertNotIn('src="https://cdn.tailwindcss.com"', html, name)

    def test_python_requirements_are_pinned(self):
        lines = [ln.strip() for ln in (BASE_DIR / "requirements.txt").read_text(encoding="utf-8").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
        self.assertTrue(lines)
        for ln in lines:
            self.assertRegex(ln, r"^[A-Za-z0-9_.\-\[\]]+==\d", ln)


if __name__ == "__main__":
    unittest.main()
