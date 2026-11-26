"""
Yönetici paneli: genel bakış, siparişler, destek durumu, izinler ve CSV dışa aktarma, site duyurusu,
soru gizleme/düzeltme, öğrenci ayrıntısı, tam hesap silme ve yönetici işlem kaydı.
"""
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_yonetici_paneli.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "yonetici_paneli_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402


class TestAdminPanel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        app_module.init_admin_tables()
        cls.client = TestClient(app_module.app)
        cls._saved_pw = app_module.ADMIN_PASSWORD
        app_module.ADMIN_PASSWORD = "AdminPanelTestPass2026!x"
        cls.suffix = str(os.getpid())

    @classmethod
    def tearDownClass(cls):
        app_module.ADMIN_PASSWORD = cls._saved_pw
        app_module.rebuild_questions_data()
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_yonetici_paneli.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def admin(self):
        res = self.client.post("/api/admin/login", json={"username": app_module.ADMIN_USERNAME, "password": app_module.ADMIN_PASSWORD})
        self.assertEqual(res.status_code, 200, res.text)
        return {"Authorization": f"Bearer {res.json()['token']}"}

    def student(self, name):
        name = f"{name}_{self.suffix}"
        res = self.client.post("/api/auth/register", json={
            "terms_accepted": True, "privacy_notice_ack": True, "marketing_consent": True,
            "email": f"{name}@example.com", "username": name, "password": "Parola123!",
            "full_name": "=Formül Deneme", "university_id": "itu",
        })
        self.assertEqual(res.status_code, 200, res.text)
        d = res.json()
        return d["user"]["id"], {"Authorization": f"Bearer {d['token']}"}

    def test_every_new_endpoint_requires_admin(self):
        _, student_h = self.student("yetkisiz")
        endpoints = [
            ("get", "/api/admin/overview"), ("get", "/api/admin/orders"), ("get", "/api/admin/tickets"),
            ("get", "/api/admin/consents"), ("get", "/api/admin/export/students.csv"),
            ("get", "/api/admin/export/marketing-consents.csv"), ("get", "/api/admin/export/orders.csv"),
            ("get", "/api/admin/announcement"), ("get", "/api/admin/questions"), ("get", "/api/admin/audit-log"),
            ("get", "/api/admin/students/1"),
        ]
        for method, url in endpoints:
            self.assertEqual(getattr(self.client, method)(url).status_code, 401, url)
            self.assertIn(getattr(self.client, method)(url, headers=student_h).status_code, (401, 403), url)
        self.assertIn(self.client.put("/api/admin/announcement", json={"enabled": True, "text": "x"}, headers=student_h).status_code, (401, 403))
        self.assertIn(self.client.put("/api/admin/questions/q_itu_a1_01", json={"hidden": True}, headers=student_h).status_code, (401, 403))

    def test_overview_orders_and_student_detail(self):
        uid, _ = self.student("ozet")
        db.create_paytr_order(f"PMTEST{self.suffix}", uid, "itu", 5000)
        db.finish_paytr_order(f"PMTEST{self.suffix}", "success", 5000, "")
        h = self.admin()
        ov = self.client.get("/api/admin/overview", headers=h).json()
        self.assertGreaterEqual(ov["users"]["total"], 1)
        self.assertGreaterEqual(ov["revenue"]["total_try"], 50.0)
        self.assertEqual(len(ov["daily"]), 14)
        self.assertGreater(ov["content"]["questions"], 11000)
        orders = self.client.get("/api/admin/orders?status=success", headers=h).json()["orders"]
        self.assertTrue(any(o["merchant_oid"] == f"PMTEST{self.suffix}" and o["amount_try"] == 50.0 for o in orders))
        detail = self.client.get(f"/api/admin/students/{uid}", headers=h).json()
        self.assertEqual(detail["user"]["id"], uid)
        self.assertNotIn("password_hash", detail["user"])
        self.assertEqual(detail["orders"][0]["status"], "success")
        self.assertTrue(any(c["doc_key"] for c in detail["consents"]))
        self.assertEqual(self.client.get("/api/admin/students/999999", headers=h).status_code, 404)

    def test_ticket_status_and_note(self):
        res = db.create_support_ticket("Paketim açılmadı", category="Ödeme & Fatura İşlemleri", full_name="Test", email="t@example.com")
        tid = res["ticket_id"]
        h = self.admin()
        r = self.client.patch(f"/api/admin/tickets/{tid}", json={"status": "answered", "admin_note": "E-postayla cevaplandı"}, headers=h)
        self.assertEqual(r.status_code, 200, r.text)
        t = next(x for x in self.client.get("/api/admin/tickets", headers=h).json()["tickets"] if x["id"] == tid)
        self.assertEqual((t["status"], t["admin_note"]), ("answered", "E-postayla cevaplandı"))
        self.assertEqual(self.client.patch(f"/api/admin/tickets/{tid}", json={"status": "silindi"}, headers=h).status_code, 400)
        self.assertEqual(self.client.patch("/api/admin/tickets/999999", json={"status": "closed"}, headers=h).status_code, 404)

    def test_csv_exports_escape_formulas(self):
        self.student("csv")
        h = self.admin()
        r = self.client.get("/api/admin/export/students.csv", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/csv", r.headers["content-type"])
        self.assertIn("'=Formül Deneme", r.text)
        self.assertNotIn("password_hash", r.text)
        m = self.client.get("/api/admin/export/marketing-consents.csv", headers=h)
        self.assertIn(f"csv_{self.suffix}@example.com", m.text)
        self.assertGreaterEqual(self.client.get("/api/admin/consents", headers=h).json()["marketing_count"], 1)

    def test_announcement_flow(self):
        h = self.admin()
        self.assertEqual(self.client.put("/api/admin/announcement", json={"enabled": True, "text": "x", "link_url": "javascript:alert(1)"}, headers=h).status_code, 422)
        r = self.client.put("/api/admin/announcement", json={"enabled": True, "text": " Ocak denemeleri yayında ", "tone": "success", "link_url": "/sinavlar", "link_text": "Gör"}, headers=h)
        self.assertEqual(r.status_code, 200, r.text)
        pub = self.client.get("/api/site/announcement").json()
        self.assertEqual((pub["enabled"], pub["text"], pub["tone"]), (True, "Ocak denemeleri yayında", "success"))
        self.client.put("/api/admin/announcement", json={"enabled": False, "text": "kapalı"}, headers=h)
        self.assertEqual(self.client.get("/api/site/announcement").json(), {"enabled": False})

    def test_question_hide_and_fix(self):
        h = self.admin()
        qid = "q_itu_a1_01"
        original = next(q for q in app_module.questions_raw if q["id"] == qid)
        wrong = next(o["key"] for o in original["options"] if o["key"] != original["correct_answer"])
        try:
            r = self.client.put(f"/api/admin/questions/{qid}", json={"correct_answer": "Z"}, headers=h)
            self.assertEqual(r.status_code, 422)
            r = self.client.put(f"/api/admin/questions/{qid}", json={"correct_answer": wrong, "explanation_tr": "Düzeltildi.", "note": "Öğrenci bildirdi"}, headers=h)
            self.assertEqual(r.status_code, 200, r.text)
            served = next(q for q in app_module.questions_data if q["id"] == qid)
            self.assertEqual((served["correct_answer"], served["explanation_tr"]), (wrong, "Düzeltildi."))
            listed = self.client.get(f"/api/admin/questions?search={qid}", headers=h).json()
            self.assertEqual(listed["questions"][0]["correct_answer"], wrong)
            self.assertEqual(listed["questions"][0]["_original"]["correct_answer"], original["correct_answer"])

            self.client.put(f"/api/admin/questions/{qid}", json={"hidden": True}, headers=h)
            self.assertFalse(any(q["id"] == qid for q in app_module.questions_data))
            self.assertEqual(self.client.get("/api/admin/questions?state=hidden", headers=h).json()["questions"][0]["id"], qid)
            self.assertEqual(self.client.put("/api/admin/questions/yok-boyle-soru", json={"hidden": True}, headers=h).status_code, 404)
        finally:
            self.client.put(f"/api/admin/questions/{qid}", json={"hidden": False}, headers=h)
        restored = next(q for q in app_module.questions_data if q["id"] == qid)
        self.assertEqual(restored["correct_answer"], original["correct_answer"])

    def test_delete_removes_personal_progress_and_is_logged(self):
        uid, sh = self.student("silinecek")
        db.bump_daily_activity(uid, answered=3, correct=2)
        db.record_lesson_result(uid, "a1-01", "A1", 10, 13, 10)
        h = self.admin()
        self.assertEqual(self.client.delete(f"/api/admin/students/{uid}", headers=h).status_code, 200)
        conn = db.get_db()
        for table in ("users", "daily_activity", "lesson_progress"):
            col = "id" if table == "users" else "user_id"
            self.assertEqual(conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} = ?", (uid,)).fetchone()[0], 0, table)
        conn.close()
        log = self.client.get("/api/admin/audit-log", headers=h).json()["entries"]
        self.assertTrue(any(e["action"] == "student_delete" and e["target"] == str(uid) for e in log))


if __name__ == "__main__":
    unittest.main()
