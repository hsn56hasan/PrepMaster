"""
Gerçek istemci IP'si: Cloudflare Tunnel / nginx arkasında doğru IP, doğrudan bağlantıda
uydurulmuş başlıklar yok sayılır (hız sınırı atlatılamaz, herkes tek kişi sayılmaz).
"""
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

os.environ.setdefault("SECRET_KEY", "client_ip_suite_secret_key_2026_plmoknijb")
import security as sec  # noqa: E402


def req(peer, headers=None):
    r = mock.Mock()
    r.client = mock.Mock(host=peer)
    r.headers = {k: v for k, v in (headers or {}).items()}
    return r


class TestClientIp(unittest.TestCase):
    def setUp(self):
        sec.rate_limiter.reset()

    def test_direct_connection_ignores_spoofed_headers(self):
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1,::1"}):
            r = req("203.0.113.9", {"X-Forwarded-For": "1.1.1.1", "CF-Connecting-IP": "2.2.2.2", "X-Real-IP": "3.3.3.3"})
            self.assertEqual(sec.get_client_ip(r), "203.0.113.9")

    def test_tunnel_on_localhost_uses_cloudflare_header(self):
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1,::1"}):
            self.assertEqual(sec.get_client_ip(req("127.0.0.1", {"CF-Connecting-IP": "85.10.20.30"})), "85.10.20.30")
            self.assertEqual(sec.get_client_ip(req("::1", {"X-Real-IP": "85.10.20.31"})), "85.10.20.31")

    def test_cloudflare_header_preferred_and_garbage_ignored(self):
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1"}):
            r = req("127.0.0.1", {"CF-Connecting-IP": "85.10.20.30", "X-Real-IP": "9.9.9.9"})
            self.assertEqual(sec.get_client_ip(r), "85.10.20.30")
            self.assertEqual(sec.get_client_ip(req("127.0.0.1", {"CF-Connecting-IP": "'; DROP"})), "127.0.0.1")

    def test_docker_network_can_be_trusted_by_cidr(self):
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1,172.16.0.0/12"}):
            self.assertEqual(sec.get_client_ip(req("172.18.0.5", {"X-Real-IP": "85.1.1.1"})), "85.1.1.1")
            self.assertEqual(sec.get_client_ip(req("10.0.0.5", {"X-Real-IP": "85.1.1.1"})), "10.0.0.5")

    def test_students_behind_tunnel_have_separate_rate_limits(self):
        """Tünel arkasında bir öğrencinin denemeleri diğerini kilitlememeli."""
        from fastapi import HTTPException
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1"}):
            a = req("127.0.0.1", {"CF-Connecting-IP": "85.0.0.1"})
            b = req("127.0.0.1", {"CF-Connecting-IP": "85.0.0.2"})
            for _ in range(3):
                sec.enforce_rate_limit(a, scope="t", max_requests=3, window_seconds=60)
            with self.assertRaises(HTTPException):
                sec.enforce_rate_limit(a, scope="t", max_requests=3, window_seconds=60)
            sec.enforce_rate_limit(b, scope="t", max_requests=3, window_seconds=60)  # B etkilenmez

    def test_spoofed_header_cannot_bypass_rate_limit(self):
        from fastapi import HTTPException
        with mock.patch.dict(os.environ, {"TRUSTED_PROXY_IPS": "127.0.0.1"}):
            for i in range(3):
                sec.enforce_rate_limit(req("203.0.113.9", {"X-Forwarded-For": f"10.0.0.{i}"}),
                                       scope="s", max_requests=3, window_seconds=60)
            with self.assertRaises(HTTPException):
                sec.enforce_rate_limit(req("203.0.113.9", {"X-Forwarded-For": "10.0.0.99"}),
                                       scope="s", max_requests=3, window_seconds=60)


if __name__ == "__main__":
    unittest.main()
