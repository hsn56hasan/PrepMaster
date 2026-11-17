"""
"Hemen" düzeltmeleri için regresyon testleri (14.11.2026, YOL-HARITASI #1-#7).
"""

import collections
import json
import os
import sys
import unittest
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_quick_fixes.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "quick_fixes_suite_secret_key_2026_abcdefgh"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.security as sec

DATA = BASE_DIR / "data"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class TestQuickFixes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if TEST_DB_PATH.exists():
            TEST_DB_PATH.unlink()
        db.init_db()
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        if TEST_DB_PATH.exists():
            try:
                TEST_DB_PATH.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()
        app_module.DEMO_MODE = False

    def _register(self, username):
        res = self.client.post("/api/auth/register", json={"terms_accepted": True, 
            "email": f"{username}@example.com", "username": username, "password": "Parola123!",
            "full_name": "Test Ogrenci", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    # #2 Cevap anahtarı dengeli
    def test_answer_keys_balanced(self):
        for name, items in (("questions", load("questions.json")),
                            ("listening", [q for t in load("listening.json") for q in t["questions"]])):
            dist = collections.Counter(q["correct_answer"] for q in items)
            top_share = max(dist.values()) / len(items)
            self.assertLess(top_share, 0.35, f"{name}: tek bir harf çok baskın {dict(dist)}")
            for q in items:
                self.assertIn(q["correct_answer"], [o["key"] for o in q["options"]], q["id"])
                keys = [o["key"] for o in q["options"]]
                self.assertEqual(keys, sorted(keys), q["id"])

    def test_mobile_data_matches_backend_data(self):
        for name in ("questions.json", "listening.json", "speaking.json"):
            self.assertEqual((DATA / name).read_bytes(),
                             (BASE_DIR / "mobile" / "assets" / "data" / name).read_bytes(), name)

    # #3 Sahte fatura bilgisi yok
    def test_payment_summary_is_not_a_fake_invoice(self):
        r = db.generate_gib_receipt()
        for field in ("tax_office", "tax_number", "gib_status"):
            self.assertNotIn(field, r)
        self.assertTrue(r["receipt_no"].startswith("PM-"))
        self.assertIn("fatura değildir", r["document_type"])
        html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
        for fake in ("8930491823", "Mecidiyeköy", "GİB E-Arşiv Fatura Sistemi Onaylı", "HAZİNE VE MALİYE"):
            self.assertNotIn(fake, html)

    # #4 Seri
    def test_streak_counts_consecutive_days(self):
        uid, auth = self._register("serici")
        self.assertEqual(db.get_profile(uid)["streak_days"], 0)
        self.assertEqual(db.record_study_day(uid), 1)
        self.assertEqual(db.record_study_day(uid), 1)  # aynı gün ikinci kez artmaz
        conn = db.get_db()
        yesterday = (db._istanbul_today() - timedelta(days=1)).isoformat()
        conn.execute("UPDATE users SET streak_days = 4, last_study_date = ? WHERE id = ?", (yesterday, uid))
        conn.commit()
        conn.close()
        self.assertEqual(db.record_study_day(uid), 5)  # dün çalıştı -> +1
        conn = db.get_db()
        old = (db._istanbul_today() - timedelta(days=3)).isoformat()
        conn.execute("UPDATE users SET streak_days = 9, last_study_date = ? WHERE id = ?", (old, uid))
        conn.commit()
        conn.close()
        self.assertEqual(db.get_profile(uid)["streak_days"], 0)  # bozulmuş seri 0 görünür
        self.assertEqual(db.record_study_day(uid), 1)

    def test_stats_show_logged_in_users_streak(self):
        uid, auth = self._register("istatistikci")
        q = load("questions.json")[0]
        self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": q["level"], "duration_seconds": 30,
            "answers": {q["id"]: q["correct_answer"]},
        }, headers=auth)
        res = self.client.get("/api/stats", headers=auth).json()
        self.assertEqual(res["profile"]["id"], uid)
        self.assertEqual(res["profile"]["streak_days"], 1)

    # #5 Deneme
    def test_mock_exam_is_randomized(self):
        _, auth = self._register("denemeci")
        seen = set()
        for _ in range(6):
            data = self.client.get("/api/exam/mock/general?level=B2", headers=auth).json()
            mc = data["sections"]["multiple_choice"] if "sections" in data else data.get("multiple_choice")
            if mc is None:
                mc = next(v for v in data.values() if isinstance(v, dict) and "multiple_choice" in v)["multiple_choice"]
            seen.add(tuple(q["id"] for q in mc))
        self.assertGreater(len(seen), 1, "Her deneme aynı soruları aynı sırayla getiriyor")

    def test_unanswered_questions_count_as_wrong(self):
        _, auth = self._register("boscu")
        qs = [q for q in load("questions.json") if q["university_id"] == "general"][:4]
        res = self.client.post("/api/exam/submit", json={
            "university_id": "general", "level": "B2", "duration_seconds": 60,
            "answers": {qs[0]["id"]: qs[0]["correct_answer"]},
            "question_ids": [q["id"] for q in qs],
        }, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["score"], 25.0)  # eskiden 100.0 idi

    # #6 Dinleme yanlışları Hata Kasası'na
    def test_listening_mistake_goes_to_vault_without_fake_attempt(self):
        track = load("listening.json")[0]
        lq = track["questions"][0]
        wrong = next(o["key"] for o in lq["options"] if o["key"] != lq["correct_answer"])
        uid, auth = self._register("dinleyici")
        before = len(db.get_exam_history(uid, limit=1000))
        res = self.client.post("/api/listening/answer", json={"question_id": lq["id"], "chosen_answer": wrong}, headers=auth)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertFalse(res.json()["is_correct"])
        vault = self.client.get("/api/mistakes", headers=auth).json()
        item = next((m for m in vault if m["question_id"] == lq["id"]), None)
        self.assertIsNotNone(item, "Dinleme yanlışı Hata Kasası'nda görünmüyor")
        self.assertIn(track["title"], item["question_details"]["question"])
        self.assertEqual(len(db.get_exam_history(uid, limit=1000)), before, "Sahte deneme kaydı açıldı")
        # doğru cevap kasadan düşürür
        self.client.post("/api/listening/answer", json={"question_id": lq["id"], "chosen_answer": lq["correct_answer"]}, headers=auth)
        self.assertFalse(any(m["question_id"] == lq["id"] for m in self.client.get("/api/mistakes", headers=auth).json()))

    def test_exam_submit_with_only_unknown_ids_creates_no_attempt(self):
        uid, auth = self._register("bilinmeyenci")
        before = len(db.get_exam_history(uid, limit=1000))
        res = self.client.post("/api/exam/submit", json={
            "university_id": "boun", "level": "C1", "duration_seconds": 60, "answers": {"yok-boyle-soru": "A"},
        }, headers=auth)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(len(db.get_exam_history(uid, limit=1000)), before)

    # #7 ODTÜ kimliği
    def test_no_orphan_odtu_university_id(self):
        uni_ids = {u["id"] for u in load("universities.json")}
        for name in ("questions.json", "listening.json", "speaking.json"):
            for item in load(name):
                self.assertIn(item["university_id"], uni_ids | {"general"}, f"{name}: {item['id']}")

    # #1 app.js tanımsız fonksiyon atamaz
    def test_app_js_exports_are_defined(self):
        import re
        js_dir = BASE_DIR / "static" / "js"
        src = "\n".join(p.read_text(encoding="utf-8") for p in js_dir.glob("*.js"))
        app_js = (js_dir / "app.js").read_text(encoding="utf-8")
        for name in re.findall(r"^window\.\w+ = (\w+);", app_js, re.M):
            self.assertRegex(src, rf"(function\s+{name}\b|(const|let|var)\s+{name}\s*=)", name)

    # #8 Yönetici panelinden açılan üniversiteler giriş-çıkış sonrası kaybolmaz & tüm kayıtlar listelenir
    def test_admin_university_grants_persist_after_logout_login(self):
        uid, auth = self._register("kalici_ogrenci")
        all_unis = ["general"] + [u["id"] for u in load("universities.json")]
        # Modal üzerinde is_verified=False kalsa bile 26 okul açıldığında doğrulanmış ve kalıcı olmalı
        upd = db.admin_update_student_access(
            user_id=uid,
            unlocked_universities=all_unis,
            primary_university_id="boun",
            is_verified=False,
        )
        self.assertTrue(upd["success"])
        self.assertTrue(upd["is_verified"])
        self.assertEqual(set(upd["unlocked_universities"]), set(all_unis))

        # Çıkış yapıp tekrar giriş yaptığında (/api/auth/login + /api/profile) 26 okul açık kalmalı
        login_res = self.client.post("/api/auth/login", json={
            "identifier": "kalici_ogrenci",
            "password": "Parola123!",
        })
        self.assertEqual(login_res.status_code, 200, login_res.text)
        login_user = login_res.json()["user"]
        self.assertEqual(login_user["is_verified_student"], 1)
        self.assertEqual(login_user["verification_status"], "verified")
        self.assertEqual(set(login_user["unlocked_universities"]), set(all_unis))

        new_auth = {"Authorization": f"Bearer {login_res.json()['token']}"}
        prof = self.client.get("/api/profile", headers=new_auth).json()
        self.assertEqual(set(prof["unlocked_universities"]), set(all_unis))

        # Tüm kayıtlı öğrenciler (aktif/çevrimdışı fark etmeksizin) admin listesinde görünmeli
        admin_list = db.admin_list_students()["students"]
        usernames = {s["username"] for s in admin_list}
        self.assertIn("kalici_ogrenci", usernames)
        self.assertIn("deneme", usernames)

    # Kayıt onayları: sözleşme zorunlu, açık rıza isteğe bağlı; ikisi de zamanla kaydedilir
    def test_register_requires_terms_and_records_consents(self):
        base = {"username": "onaycu", "password": "Parola123!", "full_name": "Onay Test", "university_id": "itu"}
        r = self.client.post("/api/auth/register", json={**base, "email": "onaycu@example.com"})
        self.assertEqual(r.status_code, 400)
        r = self.client.post("/api/auth/register", json={**base, "email": "onaycu@example.com", "terms_accepted": True})
        self.assertEqual(r.status_code, 200, r.text)
        conn = db.get_db()
        row = conn.execute("SELECT terms_accepted_at, explicit_consent_at FROM users WHERE username='onaycu'").fetchone()
        conn.close()
        self.assertIsNotNone(row["terms_accepted_at"])
        self.assertIsNone(row["explicit_consent_at"])
        r = self.client.post("/api/auth/register", json={**base, "username": "onaycu2", "email": "onaycu2@example.com",
                                                          "terms_accepted": True, "explicit_consent": True})
        self.assertEqual(r.status_code, 200, r.text)
        conn = db.get_db()
        row = conn.execute("SELECT explicit_consent_at FROM users WHERE username='onaycu2'").fetchone()
        conn.close()
        self.assertIsNotNone(row["explicit_consent_at"])

    def test_registration_checkboxes_start_unchecked(self):
        html = (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")
        import re
        for cid in ("reg-kvkk-consent", "reg-explicit-consent", "paytr-pre-info"):
            tag = re.search(r'<input[^>]*id="%s"[^>]*>' % cid, html)
            self.assertIsNotNone(tag, cid)
            self.assertNotIn("checked", tag.group(0), cid)

    # İçerik denetimi (15.11): mekanik hatalar geri gelmesin
    def test_content_mechanical_issues_fixed(self):
        import re
        for name in ("questions.json", "listening.json", "speaking.json"):
            raw = (DATA / name).read_text(encoding="utf-8")
            self.assertNotIn("随机", raw, name)
            self.assertNotIn("proficiency proficiency", raw.lower(), name)
        qs = load("questions.json")
        for q in qs:
            if "encountered severe" in q["question"]:
                correct = next(o["text"] for o in q["options"] if o["key"] == q["correct_answer"])
                self.assertEqual(correct, "nevertheless", q["id"])
        # Şablon sorularda doğru şıkkın yeri soru numarasından tahmin edilemesin
        by_slot = collections.defaultdict(collections.Counter)
        for q in qs:
            m = re.match(r"^q_[a-z_]+_(?:a1|a2|b1|b2|c1|c2)_(\d+)$", q["id"])
            if m:
                by_slot[m.group(1)][q["correct_answer"]] += 1
        for slot, c in by_slot.items():
            self.assertLess(max(c.values()) / sum(c.values()), 0.5, f"soru #{slot}: {dict(c)}")


if __name__ == "__main__":
    unittest.main()
