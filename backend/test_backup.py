"""
Veritabanı yedeği testleri: yedek geçerli ve tutarlı, eskiler silinir, indirme yalnız yöneticiye açık.
"""
import gzip
import os
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_backup.db"
os.environ["PREPMASTER_DB_PATH"] = str(TEST_DB_PATH)
os.environ["SECRET_KEY"] = "backup_suite_secret_key_2026_qwertyuiopasdf"
os.environ["BACKUP_DISABLED"] = "1"

from fastapi.testclient import TestClient
from backend.app import app
import backend.app as app_module
import backend.database as db
import backend.backup as backup
import backend.security as sec


class TestBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p in BASE_DIR.joinpath("backend").glob("test_backup.db*"):
            p.unlink()
        db.init_db()
        cls.client = TestClient(app)
        cls._saved_pw = app_module.ADMIN_PASSWORD
        app_module.ADMIN_PASSWORD = "BackupTestAdminPass2026!x"

    @classmethod
    def tearDownClass(cls):
        app_module.ADMIN_PASSWORD = cls._saved_pw
        import shutil
        shutil.rmtree(backup.backup_dir(), ignore_errors=True)
        for p in BASE_DIR.joinpath("backend").glob("test_backup.db*"):
            try:
                p.unlink()
            except Exception:
                pass

    def setUp(self):
        sec.rate_limiter.reset()

    def _restore(self, gz_path):
        out = Path(tempfile.mkdtemp()) / "geri.db"
        with gzip.open(gz_path, "rb") as f_in, open(out, "wb") as f_out:
            f_out.write(f_in.read())
        return sqlite3.connect(out)

    def test_backup_is_consistent_copy(self):
        db.create_user("yedek@example.com", "yedekci", "Parola123!", "Yedek Test", terms_accepted=True)
        gz = backup.create_backup()
        self.assertTrue(gz.exists())
        con = self._restore(gz)
        self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        self.assertEqual(con.execute("SELECT COUNT(*) FROM users WHERE username='yedekci'").fetchone()[0], 1)
        con.close()

    def test_daily_backup_once_per_day_and_prunes_old(self):
        first = backup.daily_backup_if_needed()
        self.assertIsNotNone(first)
        self.assertIsNone(backup.daily_backup_if_needed())  # aynı gün ikinci kez alınmaz
        old = backup.backup_dir() / "prepmaster-eski.db.gz"
        old.write_bytes(b"x")
        t = time.time() - 30 * 86400
        os.utime(old, (t, t))
        backup.prune_backups(keep_days=7)
        self.assertFalse(old.exists())
        self.assertTrue(first.exists())

    def test_download_requires_admin(self):
        self.assertEqual(self.client.get("/api/admin/backup").status_code, 401)
        student = sec.create_session_token(5, "ogr", "o@x.com")[0]
        self.assertIn(self.client.get("/api/admin/backup", headers={"Authorization": "Bearer " + student}).status_code, (401, 403))
        tok = self.client.post("/api/admin/login", json={"username": "admin", "password": app_module.ADMIN_PASSWORD}).json()["token"]
        res = self.client.get("/api/admin/backup", headers={"Authorization": "Bearer " + tok})
        self.assertEqual(res.status_code, 200, res.text[:200])
        self.assertEqual(res.content[:2], b"\x1f\x8b")  # gzip
        self.assertIn("prepmaster-yedek-", res.headers.get("content-disposition", ""))

    def test_dockerfile_healthcheck_uses_public_endpoint(self):
        df = (BASE_DIR / "Dockerfile").read_text(encoding="utf-8")
        cmd = df[df.index("HEALTHCHECK"):].split(chr(10) + chr(10))[0]
        self.assertIn("/api/config", cmd)
        self.assertNotIn("/api/student/status", cmd)
        self.assertEqual(self.client.get("/api/config").status_code, 200)


if __name__ == "__main__":
    unittest.main()
