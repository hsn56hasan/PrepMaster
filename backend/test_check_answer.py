"""
check_answer: doğru cevap karşılaştırmasının tek yerde toplanması (zemin düzeltmesi, 26.11.2026).

Eskiden aynı karşılaştırma üç ayrı yerde kopyalanmıştı: dinleme cevabı, sınav gönderimi ve
alıştırma cevabı. Dinleme ile alıştırma uçları cevabı büyük harfe çeviriyordu, sınav gönderimi
ise çevirmiyordu. Pydantic deseni küçük harfli şık anahtarını da kabul ettiği için
(^[A-Ea-e]$), küçük harf gönderen bir istemci alıştırmada doğru sayılırken aynı soruda sınavda
yanlış sayılıyordu. Artık üç uç da backend.app.check_answer kullanıyor; bu testler o
davranışı kilitler.
"""

import json
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_check_answer.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "check_answer_suite_secret_key_2026_prepkampus"

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app, check_answer  # noqa: E402
import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402

DATA = BASE_DIR / "data"
QUESTIONS = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
LISTENING = json.loads((DATA / "listening.json").read_text(encoding="utf-8"))


def wrong_key_of(question):
    """Sorunun doğru şıkkı dışındaki ilk şık anahtarı."""
    return next(o["key"] for o in question["options"] if o["key"] != question["correct_answer"])


class TestCheckAnswerBirim(unittest.TestCase):
    """Fonksiyonun kendi kuralları."""

    def test_buyuk_harf_dogru_cevap(self):
        self.assertTrue(check_answer({"correct_answer": "B"}, "B"))

    def test_kucuk_harf_de_dogru_sayilir(self):
        """Asıl düzeltilen hata: küçük harfli şık anahtarı da doğrudur."""
        self.assertTrue(check_answer({"correct_answer": "B"}, "b"))

    def test_bastaki_sondaki_bosluk_onemsiz(self):
        self.assertTrue(check_answer({"correct_answer": "C"}, "  c  "))

    def test_yanlis_sik(self):
        self.assertFalse(check_answer({"correct_answer": "A"}, "D"))

    def test_bos_cevap_yanlis(self):
        self.assertFalse(check_answer({"correct_answer": "A"}, None))
        self.assertFalse(check_answer({"correct_answer": "A"}, ""))
        self.assertFalse(check_answer({"correct_answer": "A"}, "   "))

    def test_dogru_cevap_alani_yoksa_yanlis(self):
        """Şıksız soru tipleri (BUEPT kısa cevap, eşleştirme) için çökmemeli."""
        self.assertFalse(check_answer({}, "A"))
        self.assertFalse(check_answer({"correct_answer": None}, "A"))

    def test_dogru_cevap_kucuk_harfle_saklanmissa(self):
        """Veri tarafı küçük harfle gelse bile karşılaştırma iki yönlü normalleşir."""
        self.assertTrue(check_answer({"correct_answer": "d"}, "D"))


class TestUclardaTutarlilik(unittest.TestCase):
    """Üç uç da aynı kuralı uygulamalı."""

    @classmethod
    def setUpClass(cls):
        for p in BASE_DIR.joinpath("backend").glob("test_check_answer.db*"):
            p.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        for p in BASE_DIR.joinpath("backend").glob("test_check_answer.db*"):
            try:
                p.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False

    def _register(self, username):
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True,
            "email": f"{username}@example.com",
            "username": username,
            "password": "Parola123!",
            "full_name": "Test Ogrenci",
            "university_id": "general",
        })
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['token']}"}

    def test_sinav_gonderiminde_kucuk_harf_dogru_sayilir(self):
        """Regresyon: /api/exam/submit eskiden küçük harfi yanlış sayıyordu."""
        auth = self._register("sinavkucuk")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        res = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 30,
            "answers": {q["id"]: q["correct_answer"].lower()},
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        self.assertEqual(body["correct_count"], 1, "Küçük harfli doğru cevap yanlış sayıldı.")
        self.assertEqual(body["score"], 100.0)
        # Doğru cevap hata defterine düşmemeli
        self.assertEqual(self.client.get("/api/mistakes", headers=auth).json(), [])

    def test_sinav_gonderiminde_yanlis_cevap_hala_yanlis(self):
        auth = self._register("sinavyanlis")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        res = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 30,
            "answers": {q["id"]: wrong_key_of(q).lower()},
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["correct_count"], 0)
        self.assertTrue(any(m["question_id"] == q["id"]
                            for m in self.client.get("/api/mistakes", headers=auth).json()))

    def test_alistirma_ucunda_kucuk_harf_dogru_sayilir(self):
        auth = self._register("alistirma")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        res = self.client.post("/api/practice/answer", json={
            "question_id": q["id"], "chosen_answer": q["correct_answer"].lower(),
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertTrue(res.json()["is_correct"])

    def test_dinleme_ucunda_kucuk_harf_dogru_sayilir(self):
        auth = self._register("dinleme")
        track = LISTENING[0]
        lq = track["questions"][0]
        res = self.client.post("/api/listening/answer", json={
            "question_id": lq["id"], "chosen_answer": lq["correct_answer"].lower(),
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertTrue(res.json()["is_correct"])

    def test_uc_uc_ayni_soruda_ayni_sonucu_verir(self):
        """Aynı soruya aynı cevap, alıştırma ile sınavda farklı sonuç vermemeli."""
        auth = self._register("tutarli")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        for key in (q["correct_answer"], q["correct_answer"].lower()):
            pratik = self.client.post("/api/practice/answer", json={
                "question_id": q["id"], "chosen_answer": key,
            }, headers=auth).json()["is_correct"]
            sinav = self.client.post("/api/exam/submit", json={
                "university_id": "general", "level": q["level"], "duration_seconds": 10,
                "answers": {q["id"]: key},
            }, headers=auth).json()["correct_count"] == 1
            self.assertEqual(pratik, sinav, f"'{key}' cevabı iki uçta farklı sonuç verdi.")
            self.assertTrue(pratik)


class TestCevapAnahtariSizmasin(unittest.TestCase):
    """Soruyu DAĞITAN uçlar cevap anahtarını göndermemeli.

    Olumsuz iddialar: bu testler olmadan ayıklama ilk yeniden düzenlemede sessizce
    geri gelir ve hiçbir şey uyarmaz. Cevabı DEĞERLENDİREN uçların anahtarı cevaptan
    SONRA döndürmeye devam ettiği de ayrıca doğrulanır (fazla ayıklama da bir hatadır).
    """

    ANAHTAR_ALANLARI = ("correct_answer", "explanation_tr", "explanation_en")

    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app)

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False

    def _anahtar_var_mi(self, soru):
        return [a for a in self.ANAHTAR_ALANLARI if a in soru]

    def test_deneme_paketi_coktan_secmeli_anahtarsiz(self):
        res = self.client.get("/api/exam/mock/general")
        self.assertEqual(res.status_code, 200, res.text)
        sorular = res.json()["sections"]["multiple_choice"]
        self.assertTrue(sorular, "Deneme paketi boş döndü, test anlamsız olur.")
        for q in sorular:
            self.assertEqual(self._anahtar_var_mi(q), [], f"{q.get('id')} cevap anahtarı taşıyor.")
            self.assertTrue(q.get("options"), "Şıklar düşmemeli, yalnızca anahtar düşmeli.")

    def test_deneme_paketi_dinleme_bolumu_anahtarsiz_ve_transkriptsiz(self):
        res = self.client.get("/api/exam/mock/general")
        track = res.json()["sections"].get("listening")
        if not track:
            self.skipTest("Bu üniversite için deneme paketinde dinleme bölümü yok.")
        self.assertNotIn("audio_script", track,
                         "Deneme paketindeki dinleme bölümünü hiçbir istemci okumuyor; transkript gitmemeli.")
        for q in track.get("questions", []):
            self.assertEqual(self._anahtar_var_mi(q), [])

    def test_deneme_paketi_model_cevaplari_tasimaz(self):
        bolumler = self.client.get("/api/exam/mock/general").json()["sections"]
        for ad in ("writing_prompt", "speaking_prompt"):
            bolum = bolumler.get(ad)
            if not bolum:
                continue
            for alan in ("model_essay", "annotated_strengths", "model_band_score", "model_answer_transcript"):
                self.assertNotIn(alan, bolum, f"{ad} içinde {alan} gidiyor.")

    def test_konusma_gorevleri_model_cevap_tasimaz(self):
        res = self.client.get("/api/speaking")
        self.assertEqual(res.status_code, 200, res.text)
        gorevler = res.json()
        self.assertTrue(gorevler, "Konuşma görevi listesi boş döndü.")
        for g in gorevler:
            self.assertNotIn("model_answer_transcript", g, f"{g.get('id')} model cevabı taşıyor.")

    def test_dinleme_detayi_anahtarsiz_ama_ses_metni_korunur(self):
        track = next((t for t in LISTENING if t.get("university_id") == "general"), None)
        if not track:
            self.skipTest("Genel havuzda dinleme parçası yok.")
        res = self.client.get(f"/api/listening/{track['id']}")
        self.assertEqual(res.status_code, 200, res.text)
        body = res.json()
        for q in body.get("questions", []):
            self.assertEqual(self._anahtar_var_mi(q), [])
        self.assertIn("audio_script", body,
                      "audio_script sesin kaynağı; düşürülürse parçaların çoğu sessiz kalır.")

    def test_sinav_sonucu_dogru_cevabi_hala_donuyor(self):
        """Fazla ayıklama kontrolü: cevaptan SONRA anahtar dönmeye devam etmeli."""
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": "sonuc@example.com", "username": "sonuc",
            "password": "Parola123!", "full_name": "Test Ogrenci", "university_id": "general",
        })
        self.assertEqual(res.status_code, 200, res.text)
        auth = {"Authorization": f"Bearer {res.json()['token']}"}
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        sonuc = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 20,
            "answers": {q["id"]: wrong_key_of(q)},
        }, headers=auth)
        self.assertEqual(sonuc.status_code, 200, sonuc.text)
        detay = sonuc.json()["details"][0]
        self.assertIn("correct_answer", detay, "Sınav sonucunda doğru cevap gösterilmeye devam etmeli.")

    def test_ayiklama_sunucunun_kendi_puanlamasini_bozmaz(self):
        """Kopya yerine yerinde silme yapılsaydı bu test düşerdi."""
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": "kopya@example.com", "username": "kopya",
            "password": "Parola123!", "full_name": "Test Ogrenci", "university_id": "general",
        })
        auth = {"Authorization": f"Bearer {res.json()['token']}"}
        # Önce deneme paketi çekilir (ayıklama bu çağrıda çalışır)
        self.client.get("/api/exam/mock/general")
        q = next(x for x in QUESTIONS if x["university_id"] == "general")
        # Sonra aynı soru doğru cevaplanır: sunucu hala doğru cevabı biliyor olmalı
        body = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 20,
            "answers": {q["id"]: q["correct_answer"]},
        }, headers=auth).json()
        self.assertEqual(body["correct_count"], 1,
                         "Ayıklama global soru verisini bozmuş: sunucu doğru cevabı kaybetti.")
        self.assertIn("correct_answer", QUESTIONS[0], "Bellekteki kaynak veri değişmemeli.")


if __name__ == "__main__":
    unittest.main()
