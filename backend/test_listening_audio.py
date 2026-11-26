"""Dinleme sesi boru hattı: ses alan adı DÖRT yerde de aynı olmalı.

Gerçek bir hatadan doğdu (26.11.2026): MP3'ler Cloudflare R2'ye taşındıktan sonra ses
çalmadı, çünkü backend'in CSP başlığındaki `media-src` yalnızca 'self' idi. Tarayıcı
sesi sessizce engelledi; sunucu tarafında hiçbir hata görünmedi.

Alan adı şu dört yerde geçiyor ve biri değişip diğeri unutulursa ses yine sessizce
kesilir - bu testler o dördünü birbirine bağlar:
  1. backend/security.py           -> CSP media-src (tarayıcı izni)
  2. data/listening.json           -> audio_url alanları (sesin adresi)
  3. static/js/listening.js        -> AUDIO_IZINLI_URL kalıbı (istemci beyaz listesi)
  4. nginx/conf.d/default.conf     -> ters vekil sunucunun CSP'si (kendi sunucuya kurulumda)
"""

import json
import os
import re
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_listening_audio.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "listening_audio_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402
from backend.security import AUDIO_HOST  # noqa: E402
import backend.database as db  # noqa: E402

LISTENING = json.loads((BASE_DIR / "data" / "listening.json").read_text(encoding="utf-8"))
LISTENING_JS = (BASE_DIR / "static" / "js" / "listening.js").read_text(encoding="utf-8")
NGINX_CONF = (BASE_DIR / "nginx" / "conf.d" / "default.conf").read_text(encoding="utf-8")


class TestSesAlanAdiTutarliligi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app)

    def test_csp_ses_alan_adina_izin_veriyor(self):
        """Asıl hata buydu: media-src yalnızca 'self' olunca ses sessizce engellenir."""
        res = self.client.get("/api/universities")
        csp = res.headers.get("Content-Security-Policy", "")
        media = next((p.strip() for p in csp.split(";") if p.strip().startswith("media-src")), "")
        self.assertTrue(media, "CSP'de media-src direktifi yok.")
        self.assertIn(AUDIO_HOST, media,
                      f"media-src ses alan adını ({AUDIO_HOST}) içermiyor: {media}")

    def test_audio_urller_izinli_alan_adini_kullaniyor(self):
        """Veri ile CSP aynı alan adını göstermeli."""
        yabanci = []
        for t in LISTENING:
            u = (t.get("audio_url") or "").strip()
            if not u or u.startswith("/static/audio/"):
                continue
            if not u.startswith(AUDIO_HOST + "/"):
                yabanci.append((t["id"], u))
        self.assertEqual(yabanci, [], f"CSP'nin izin vermediği alan adından ses: {yabanci[:5]}")

    def test_istemci_beyaz_listesi_ayni_alan_adini_tasiyor(self):
        """listening.js içindeki AUDIO_IZINLI_URL kalıbı CSP ile aynı alan adını kullanmalı."""
        self.assertIn("AUDIO_IZINLI_URL", LISTENING_JS,
                      "listening.js içinde beyaz liste kalıbı bulunamadı.")
        alan = AUDIO_HOST.replace("https://", "").replace(".", r"\.")
        self.assertIn(alan, LISTENING_JS,
                      f"listening.js beyaz listesi {AUDIO_HOST} alan adını içermiyor.")

    def test_nginx_csp_de_ayni_alan_adina_izin_veriyor(self):
        """Kendi sunucusuna kurulumda nginx'in CSP'si de sesi engellememeli."""
        satirlar = [s for s in NGINX_CONF.splitlines() if "media-src" in s]
        self.assertTrue(satirlar, "nginx yapılandırmasında media-src bulunamadı.")
        for s in satirlar:
            self.assertIn(AUDIO_HOST, s, f"nginx media-src ses alan adını içermiyor: {s.strip()}")

    def test_audio_urller_icerik_ozetli_ve_mp3(self):
        """Dosya adı <id>.<hash8>.mp3 kalıbında olmalı; nginx 90 gün immutable önbellek veriyor,
        özetsiz ad aynı adla yeniden üretimde aylarca eski sesi servis ettirir."""
        kalip = re.compile(r"^[A-Za-z0-9_-]+\.[0-9a-f]{8}\.mp3$")
        bozuk = []
        for t in LISTENING:
            u = (t.get("audio_url") or "").strip()
            if not u:
                continue
            ad = u.rsplit("/", 1)[-1]
            if not kalip.match(ad):
                bozuk.append((t["id"], ad))
        self.assertEqual(bozuk, [], f"İçerik özetli olmayan ses dosyası adları: {bozuk[:5]}")

    def test_api_audio_url_alanini_gonderiyor(self):
        """Ayıklama (_public_listening_track) audio_url'i düşürmemeli."""
        res = self.client.get("/api/listening?university_id=general")
        self.assertEqual(res.status_code, 200, res.text)
        parcalar = res.json()
        self.assertTrue(parcalar, "Genel havuzda dinleme parçası dönmedi.")
        urlsuz = [t["id"] for t in parcalar if not t.get("audio_url")]
        self.assertEqual(urlsuz, [], f"audio_url'i düşen parçalar: {urlsuz[:5]}")


if __name__ == "__main__":
    unittest.main()
