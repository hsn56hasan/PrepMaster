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


class TestDinlemeNotlari(unittest.TestCase):
    """Not tutarak dinlemede alınan notlar kullanıcıya özel ve kalıcı olmalı."""

    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app)

    def setUp(self):
        import backend.security as sec
        sec.rate_limiter.reset()

    def _kayit(self, kullanici):
        # Test veritabanı diskte kalabildiği için her koşuda benzersiz kullanıcı üret.
        import uuid
        kullanici = f"{kullanici}_{uuid.uuid4().hex[:8]}"
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True,
            "email": f"{kullanici}@example.com",
            "username": kullanici,
            "password": "Parola123!",
            "full_name": "Test Ogrenci",
            "university_id": "general",
        })
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['token']}"}

    def test_notlar_giris_istiyor(self):
        self.assertEqual(
            self.client.post("/api/listening/notes",
                             json={"track_id": "lis_general_a1_01", "notes": "x"}).status_code, 401)
        self.assertEqual(self.client.get("/api/listening/notes/lis_general_a1_01").status_code, 401)

    def test_not_kaydedilir_ve_geri_okunur(self):
        auth = self._kayit("notalan")
        metin = "- Confirmation bias: Wason 1960\n- Framing: Kahneman & Tversky"
        r = self.client.post("/api/listening/notes",
                             json={"track_id": "lis_general_b1_01", "notes": metin}, headers=auth)
        self.assertEqual(r.status_code, 200, r.text)
        g = self.client.get("/api/listening/notes/lis_general_b1_01", headers=auth)
        self.assertEqual(g.status_code, 200, g.text)
        self.assertEqual(g.json()["notes"], metin)

    def test_ayni_parcaya_tekrar_yazmak_uzerine_yazar(self):
        auth = self._kayit("notguncelle")
        for metin in ("ilk hali", "ikinci hali"):
            self.client.post("/api/listening/notes",
                             json={"track_id": "lis_general_b1_02", "notes": metin}, headers=auth)
        g = self.client.get("/api/listening/notes/lis_general_b1_02", headers=auth)
        self.assertEqual(g.json()["notes"], "ikinci hali")

    def test_notlar_kullaniciya_ozel(self):
        a = self._kayit("notlar_a")
        b = self._kayit("notlar_b")
        self.client.post("/api/listening/notes",
                         json={"track_id": "lis_general_c1_01", "notes": "A'nin notu"}, headers=a)
        self.assertEqual(
            self.client.get("/api/listening/notes/lis_general_c1_01", headers=b).json()["notes"], "")
        self.assertEqual(
            self.client.get("/api/listening/notes/lis_general_c1_01", headers=a).json()["notes"], "A'nin notu")

    def test_kaydedilmemis_parca_bos_doner(self):
        auth = self._kayit("notyok")
        g = self.client.get("/api/listening/notes/lis_general_c2_04", headers=auth)
        self.assertEqual(g.status_code, 200)
        self.assertEqual(g.json()["notes"], "")

    def test_html_temizlenir(self):
        auth = self._kayit("nothtml")
        self.client.post("/api/listening/notes",
                         json={"track_id": "lis_general_a2_01",
                               "notes": "<script>alert(1)</script>onemli not"}, headers=auth)
        notlar = self.client.get("/api/listening/notes/lis_general_a2_01", headers=auth).json()["notes"]
        self.assertNotIn("<script", notlar.lower())
        self.assertIn("onemli not", notlar)

    def test_gecersiz_parca_kimligi_reddedilir(self):
        auth = self._kayit("notgecersiz")
        # Tek parçalık ama desene uymayan kimlik uca ulaşır ve 400 alır
        self.assertEqual(self.client.get("/api/listening/notes/abc.def", headers=auth).status_code, 400)
        # Yol kaçışı denemesi hiç uca ulaşmadan reddedilir (404/400 fark etmez, 200 OLMAMALI)
        self.assertNotEqual(self.client.get("/api/listening/notes/..%2Fetc", headers=auth).status_code, 200)
        r = self.client.post("/api/listening/notes",
                             json={"track_id": "kotu/kimlik", "notes": "x"}, headers=auth)
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()
