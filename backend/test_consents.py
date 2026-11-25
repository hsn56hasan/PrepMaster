"""
Kayıt onayları (KVKK): ayrı beyanlar, zorunlu/isteğe bağlı ayrımı, sürümlü onay geçmişi,
eski istemci (Android v2.1, tek kutu) uyumu ve ticari ileti onayının geri çekilmesi.
"""
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_consents.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "consents_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402


class TestRegistrationConsents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app_module.app)
        cls.suffix = str(os.getpid())

    @classmethod
    def tearDownClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_consents.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def _payload(self, name, **extra):
        username = f"{name}_{self.suffix}"
        body = {"email": f"{username}@example.com", "username": username, "password": "Parola123!",
                "full_name": "Onay Test", "university_id": "itu"}
        body.update(extra)
        return body

    def test_terms_required(self):
        r = self.client.post("/api/auth/register", json=self._payload("onay_yok", privacy_notice_ack=True))
        self.assertEqual(r.status_code, 400)
        self.assertIn("Kullanıcı Sözleşmesi", r.json()["detail"])

    def test_privacy_notice_false_rejected(self):
        r = self.client.post("/api/auth/register", json=self._payload("aydinlatma_yok", terms_accepted=True, privacy_notice_ack=False))
        self.assertEqual(r.status_code, 400)
        self.assertIn("Aydınlatma", r.json()["detail"])

    def test_separate_declarations_are_logged_with_versions(self):
        r = self.client.post("/api/auth/register", json=self._payload(
            "ayri_beyan", terms_accepted=True, privacy_notice_ack=True, marketing_consent=False))
        self.assertEqual(r.status_code, 200, r.text)
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        c = self.client.get("/api/consents", headers=h).json()
        self.assertFalse(c["marketing_consent"])
        self.assertIsNotNone(c["terms_accepted_at"])
        self.assertIsNotNone(c["privacy_notice_ack_at"])
        keys = {(x["doc_key"], x["action"], x["channel"]) for x in c["history"]}
        self.assertIn(("kullanici_sozlesmesi", "accepted", "web"), keys)
        self.assertIn(("aydinlatma_metni", "acknowledged", "web"), keys)
        self.assertNotIn("ticari_ileti", {x["doc_key"] for x in c["history"]})
        self.assertEqual({x["doc_version"] for x in c["history"]}, {app_module.LEGAL_VERSIONS["kullanici_sozlesmesi"]})

    def test_marketing_is_optional_and_can_be_withdrawn(self):
        r = self.client.post("/api/auth/register", json=self._payload(
            "ileti", terms_accepted=True, privacy_notice_ack=True, marketing_consent=True))
        self.assertEqual(r.status_code, 200, r.text)
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        self.assertTrue(self.client.get("/api/consents", headers=h).json()["marketing_consent"])
        w = self.client.post("/api/consents/marketing", json={"granted": False}, headers=h)
        self.assertEqual(w.status_code, 200)
        c = self.client.get("/api/consents", headers=h).json()
        self.assertFalse(c["marketing_consent"])
        actions = [x["action"] for x in c["history"] if x["doc_key"] == "ticari_ileti"]
        self.assertEqual(actions[:2], ["withdrawn", "granted"])  # en yeni önce

    def test_legacy_client_single_checkbox_still_registers(self):
        # Android v2.1: yalnızca terms_accepted (+ isteğe bağlı explicit_consent) gönderir
        r = self.client.post("/api/auth/register", json=self._payload("eski_apk", terms_accepted=True, explicit_consent=True))
        self.assertEqual(r.status_code, 200, r.text)
        h = {"Authorization": f"Bearer {r.json()['token']}"}
        hist = self.client.get("/api/consents", headers=h).json()["history"]
        channels = {x["doc_key"]: x["channel"] for x in hist}
        self.assertEqual(channels["kullanici_sozlesmesi"], "legacy-combined")
        self.assertEqual(channels["aydinlatma_metni"], "legacy-combined")
        self.assertIn("acik_riza", channels)

    def test_consent_endpoints_require_login(self):
        self.assertEqual(self.client.get("/api/consents").status_code, 401)
        self.assertEqual(self.client.post("/api/consents/marketing", json={"granted": True}).status_code, 401)


if __name__ == "__main__":
    unittest.main()
