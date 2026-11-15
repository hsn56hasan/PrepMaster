"""
SEO, Google dizinleme, robots.txt, sitemap.xml ve üniversite rehber sayfaları testleri.
"""

import json
import os
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_seo.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "seo_suite_secret_key_2026_abcdefghijklmn"

from fastapi.testclient import TestClient
from backend.app import app
import backend.database as db
import backend.security as sec


class TestSeoEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_seo.db*"):
                p.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_seo.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def test_robots_txt(self):
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.headers["content-type"])
        self.assertIn("Disallow: /admin", res.text)
        self.assertIn("Disallow: /api/", res.text)
        self.assertIn("Allow: /sinavlar", res.text)
        self.assertIn("Sitemap:", res.text)
        self.assertIn("/sitemap.xml", res.text)

    def test_sitemap_xml_contains_all_universities(self):
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.headers["content-type"])
        root = ET.fromstring(res.text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall("sm:url/sm:loc", ns)]
        self.assertTrue(any(loc.endswith("/sinavlar") for loc in locs))
        self.assertTrue(any(loc.endswith("/kvkk") for loc in locs))
        unis = json.loads((BASE_DIR / "data" / "universities.json").read_text(encoding="utf-8"))
        for u in unis:
            self.assertTrue(
                any(loc.endswith(f"/universite/{u['id']}") for loc in locs),
                f"sitemap.xml içinde {u['id']} eksik",
            )

    def test_exams_hub_page(self):
        res = self.client.get("/sinavlar")
        self.assertEqual(res.status_code, 200)
        self.assertIn("İTÜ Proficiency", res.text)
        self.assertIn("BUEPT", res.text)
        self.assertIn("/universite/itu", res.text)
        self.assertIn("application/ld+json", res.text)

    def test_university_seo_pages_and_404(self):
        res = self.client.get("/universite/itu")
        self.assertEqual(res.status_code, 200)
        self.assertIn("İstanbul Teknik Üniversitesi", res.text)
        self.assertIn("İTÜ Proficiency", res.text)
        self.assertIn("application/ld+json", res.text)
        self.assertIn('rel="canonical"', res.text)
        self.assertIn("/?uni=itu&tab=register", res.text)

        missing = self.client.get("/universite/olmayan-universite")
        self.assertEqual(missing.status_code, 404)

    def test_index_seo_and_optional_google_verification_and_admin_noindex(self):
        home = self.client.get("/")
        self.assertEqual(home.status_code, 200)
        self.assertIn('<meta name="description"', home.text)
        self.assertIn('rel="canonical"', home.text)
        self.assertIn("application/ld+json", home.text)
        self.assertIn('href="/sinavlar"', home.text)
        self.assertIn('href="/universite/itu"', home.text)

        with mock.patch.dict(os.environ, {"GOOGLE_SITE_VERIFICATION": "verify-abc-123"}):
            verified_home = self.client.get("/")
            self.assertEqual(verified_home.status_code, 200)
            self.assertIn('<meta name="google-site-verification" content="verify-abc-123" />', verified_home.text)

        admin_res = self.client.get("/admin")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn('<meta name="robots" content="noindex, nofollow" />', admin_res.text)


if __name__ == "__main__":
    unittest.main()
