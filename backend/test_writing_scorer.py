"""Yazma puanlayıcısının BUGÜNKÜ davranışını çivileyen karakterizasyon testleri.

Neden: `/api/writing/evaluate` kural tabanlı puanlama yapıyor ve bugüne kadar HİÇ testi
yoktu. Integrated Writing ile beşinci bir ölçüt (kaynak sentezi) eklenecek ve ölçüt
ağırlıkları değişecek. Bu testler, değişiklik yapılırken nelerin bilinçsizce kaydığını
gösterir: buradaki sayılar "doğru" olduğu için değil, BUGÜN ÜRETİLEN değerler olduğu için
yazılmıştır. Puanlama bilerek değiştirilirse bu dosya da bilerek güncellenmelidir.

Ölçülen sürüm: 26.11.2026, dört ölçüt (her biri en çok 25 puan).
"""

import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_writing_scorer.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "writing_scorer_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

from backend.app import app  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402

KISA = "This is a short text."

ORTA = (
    "In my opinion, universities should invest in renewable energy.\n"
    "Firstly, solar panels demonstrate a significant reduction in costs. "
    "For example, a comprehensive study indicates substantial savings.\n"
    "Furthermore, although the initial investment is high, the consequence is evident. "
    "Therefore, the framework has been implemented in many campuses.\n"
    "In conclusion, this perspective is crucial and sustainable."
)

UZUN = ORTA + ("\nMoreover, the implication of this phenomenon is profound because it can be seen "
               "in diversity of outcomes. Nevertheless, lots of kids think it is a huge thing. " * 6)

# Yanıt sözleşmesi: istemciler (static/js/writing_ai.js ve mobil) bu alanları okuyor.
BEKLENEN_ALANLAR = {
    "overall_score", "estimated_cefr", "is_passing", "word_count", "paragraph_count",
    "avg_sentence_length", "task_achievement_score", "coherence_cohesion_score",
    "lexical_resource_score", "grammatical_range_score", "detected_transitions",
    "detected_academic_words", "informal_words_found", "strengths_tr", "improvements_tr",
}


class TestYazmaPuanlayici(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app)

    def setUp(self):
        sec.rate_limiter.reset()

    def _puanla(self, metin, **ek):
        govde = {"essay": metin}
        govde.update(ek)
        res = self.client.post("/api/writing/evaluate", json=govde)
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()

    # ------------------------------------------------------------ sabit çıktılar
    def test_cok_kisa_metin_sabit_yanit_doner(self):
        """30 kelimenin altında erken dönüş var; değerleri sabit."""
        d = self._puanla(KISA)
        self.assertEqual(d["overall_score"], 25)
        self.assertEqual(d["estimated_cefr"], "A1/A2")
        self.assertFalse(d["is_passing"])
        self.assertEqual(d["word_count"], 5)
        self.assertEqual(d["paragraph_count"], 1)
        self.assertEqual(d["task_achievement_score"], 8)
        self.assertEqual(d["coherence_cohesion_score"], 6)
        self.assertEqual(d["lexical_resource_score"], 6)
        self.assertEqual(d["grammatical_range_score"], 5)
        self.assertEqual(d["detected_transitions"], [])
        self.assertEqual(d["detected_academic_words"], [])
        self.assertEqual(d["informal_words_found"], [])

    def test_orta_metin_bugunku_puanlar(self):
        d = self._puanla(ORTA)
        self.assertEqual(d["word_count"], 54)
        self.assertEqual(d["paragraph_count"], 4)
        self.assertEqual(d["task_achievement_score"], 13)
        self.assertEqual(d["coherence_cohesion_score"], 23)
        self.assertEqual(d["lexical_resource_score"], 25)
        self.assertEqual(d["grammatical_range_score"], 14)
        self.assertEqual(d["overall_score"], 75)
        self.assertTrue(d["is_passing"])
        self.assertEqual(d["informal_words_found"], [])

    def test_uzun_metin_bugunku_puanlar(self):
        d = self._puanla(UZUN)
        self.assertEqual(d["word_count"], 216)
        self.assertEqual(d["paragraph_count"], 10)
        self.assertEqual(d["task_achievement_score"], 17)
        self.assertEqual(d["coherence_cohesion_score"], 25)
        self.assertEqual(d["lexical_resource_score"], 25)
        self.assertEqual(d["grammatical_range_score"], 25)
        self.assertEqual(d["overall_score"], 92)
        self.assertEqual(d["estimated_cefr"], "C1 (Mastery)")
        # Gayri resmi ifadeler yakalanıyor
        self.assertEqual(set(d["informal_words_found"]), {"lots of", "kids", "thing", "huge"})

    # ------------------------------------------------------------ sözleşme
    def test_yanit_alanlari_tam(self):
        d = self._puanla(ORTA)
        self.assertEqual(set(d.keys()), BEKLENEN_ALANLAR,
                         "Yanıt sözleşmesi değişti; istemciler bu alanları okuyor.")

    def test_genel_puan_dort_olcutun_toplami(self):
        """Bu ilişki Integrated Writing ile beşinci ölçüt eklenirse DEĞİŞECEK."""
        for metin in (ORTA, UZUN):
            d = self._puanla(metin)
            toplam = (d["task_achievement_score"] + d["coherence_cohesion_score"]
                      + d["lexical_resource_score"] + d["grammatical_range_score"])
            self.assertEqual(d["overall_score"], toplam)

    def test_her_olcut_en_cok_25(self):
        for metin in (KISA, ORTA, UZUN):
            d = self._puanla(metin)
            for alan in ("task_achievement_score", "coherence_cohesion_score",
                         "lexical_resource_score", "grammatical_range_score"):
                self.assertLessEqual(d[alan], 25, f"{alan} 25'i aştı")
                self.assertGreaterEqual(d[alan], 0)

    def test_ayni_girdi_ayni_cikti(self):
        self.assertEqual(self._puanla(ORTA), self._puanla(ORTA))

    def test_gecme_esigi_65(self):
        self.assertFalse(self._puanla(KISA)["is_passing"])   # 25
        self.assertTrue(self._puanla(ORTA)["is_passing"])    # 75

    # ------------------------------------------------------------ bilinen boşluklar
    def test_universite_seviye_ve_konu_SU_AN_yok_sayiliyor(self):
        """BİLİNEN EKSİK: uç yalnızca essay'i okuyor.

        İstek modelinde prompt, university_id ve level alanları var ama puanlamaya hiç
        girmiyor; yani İTÜ'nün 300-350 kelime sınırı ile başka bir üniversitenin kuralı
        aynı sonucu veriyor. Integrated Writing bu alanları kullanmaya başlayınca bu test
        BİLEREK güncellenmeli - kazara kırılmasın diye buraya yazıldı.
        """
        a = self._puanla(ORTA, university_id="itu", level="C1", prompt="Konu A")
        b = self._puanla(ORTA, university_id="boun", level="A1", prompt="Konu B")
        self.assertEqual(a, b, "Artık üniversiteye göre puanlanıyorsa bu testi güncelleyin.")

    def test_uc_SU_AN_giris_istemiyor(self):
        """BİLİNEN EKSİK: kimlik doğrulaması yok, tek koruma hız sınırı.

        Ücretli bir model (EVREN) bağlanmadan önce giriş zorunlu hale getirilmeli;
        o yapıldığında bu test bilerek güncellenecek.
        """
        res = self.client.post("/api/writing/evaluate", json={"essay": ORTA})
        self.assertEqual(res.status_code, 200,
                         "Uç artık giriş istiyorsa bu testi güncelleyin.")


if __name__ == "__main__":
    unittest.main()
