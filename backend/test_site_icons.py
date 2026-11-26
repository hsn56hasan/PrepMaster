"""
Site simgeleri (Google arama sonucunda görünen favicon) ve arama sonucu açıklaması:
her sayfa 48'in katı boyutlarda PNG simge + SVG + favicon.ico sunmalı; dosyalar gerçekten var olmalı.
Giriş yapmış öğrenci ana sayfada önce tanıtımı görür ("Panelime git").
"""
import os
import re
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))
os.environ.setdefault("PREPMASTER_DB_PATH", str(BASE_DIR / "backend" / "test_site_icons.db"))
os.environ.setdefault("SECRET_KEY", "site_icons_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402

ICON_LINK = re.compile(r'<link rel="(?:icon|shortcut icon)"[^>]*href="([^"]+)"')


class TestSiteIcons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app_module.app)

    def _icons(self, html):
        return ICON_LINK.findall(html)

    def test_every_page_declares_google_friendly_icons_that_exist(self):
        for path in ("/", "/kvkk", "/admin", "/sinavlar", "/universite/itu"):
            html = self.client.get(path).text
            icons = self._icons(html)
            self.assertIn("/static/img/favicon-48x48.png?v=3", icons, path)
            self.assertIn("/static/img/favicon-96x96.png?v=3", icons, path)
            self.assertIn("/favicon.ico?v=3", icons, path)
            for href in icons:
                r = self.client.get(href)
                self.assertEqual(r.status_code, 200, f"{path}: {href}")
                self.assertTrue(r.headers["content-type"].startswith("image/"), href)

    def test_png_icons_have_declared_sizes(self):
        from PIL import Image
        for n in (48, 96):
            with Image.open(BASE_DIR / "static" / "img" / f"favicon-{n}x{n}.png") as im:
                self.assertEqual(im.size, (n, n))

    def test_search_snippet_and_footer(self):
        html = self.client.get("/").text
        desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
        self.assertLessEqual(len(desc), 160)
        self.assertIn('<footer class="pk-footer" id="auth-gate-guides" data-nosnippet>', html)
        footer = html[html.index('<footer class="pk-footer"'):html.index("</footer>")]
        self.assertNotIn("</a><a ", footer)

    def test_logged_in_visitor_sees_landing_with_panel_button(self):
        html = self.client.get("/").text
        self.assertIn('id="landing-cta-panel" data-member-only hidden onclick="enterStudentPanel()"', html)
        self.assertIn('data-guest-only onclick="landingGo(\'login\')"', html)
        js = (BASE_DIR / "static" / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("showLandingForMember();", js)
        self.assertIn("function enterStudentPanel()", js)


if __name__ == "__main__":
    unittest.main()
