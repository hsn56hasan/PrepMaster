"""
Writing dosya yükleme (/api/writing/extract-pdf): yalnızca PDF kabul edilir (fotoğraflar tarayıcıda okunur),
giriş zorunludur, metinsiz/bozuk PDF anlaşılır hata döner.
"""
import os
import sys
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend"))

TEST_DB_PATH = BASE_DIR / "backend" / "test_writing_upload.db"
os.environ.setdefault("PREPMASTER_DB_PATH", str(TEST_DB_PATH))
os.environ.setdefault("SECRET_KEY", "writing_upload_suite_secret_key_2026")

from fastapi.testclient import TestClient  # noqa: E402

import backend.app as app_module  # noqa: E402
import backend.database as db  # noqa: E402
import backend.security as sec  # noqa: E402

URL = "/api/writing/extract-pdf"


def make_pdf(text: str = "") -> bytes:
    """Tek sayfalık, isteğe bağlı metin içeren geçerli bir PDF üretir."""
    stream = (f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET" if text else "").encode("latin-1")
    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = b"%PDF-1.4\n"
    offsets = []
    for i, obj in enumerate(objs, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + obj + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for off in offsets:
        out += b"%010d 00000 n \n" % off
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs) + 1, xref)
    return out


PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64


class TestWritingUpload(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.init_db()
        cls.client = TestClient(app_module.app)
        name = f"yazi_{os.getpid()}"
        res = cls.client.post("/api/auth/register", json={
            "terms_accepted": True, "email": f"{name}@example.com", "username": name,
            "password": "Parola123!", "full_name": "Yazı Test", "university_id": "itu",
        })
        assert res.status_code == 200, res.text
        cls.h = {"Authorization": f"Bearer {res.json()['token']}"}

    @classmethod
    def tearDownClass(cls):
        if Path(db.DB_PATH) == TEST_DB_PATH:
            for p in BASE_DIR.joinpath("backend").glob("test_writing_upload.db*"):
                try:
                    p.unlink()
                except Exception:
                    pass

    def setUp(self):
        sec.rate_limiter.reset()

    def post(self, data: bytes, name="essay.pdf", ctype="application/pdf", headers=None):
        return self.client.post(URL, files={"file": (name, data, ctype)}, headers=self.h if headers is None else headers)

    def test_requires_login(self):
        self.assertEqual(self.post(make_pdf("Hello"), headers={}).status_code, 401)

    def test_text_pdf_is_extracted(self):
        essay = "Renewable energy is important because it reduces pollution in modern cities"
        r = self.post(make_pdf(essay))
        self.assertEqual(r.status_code, 200, r.text)
        body = r.json()
        self.assertIn("Renewable energy is important", body["text"])
        self.assertEqual(body["pages"], 1)
        self.assertEqual(body["word_count"], len(essay.split()))

    def test_only_pdf_is_accepted(self):
        # Uzantı ve içerik türü PDF dese de içerik PDF değilse reddedilir
        self.assertEqual(self.post(PNG_BYTES, name="essay.pdf").status_code, 415)
        self.assertEqual(self.post(PNG_BYTES, name="photo.png", ctype="image/png").status_code, 415)
        self.assertEqual(self.post(b"Just some essay text", name="essay.txt", ctype="text/plain").status_code, 415)
        self.assertEqual(self.post(b"MZ\x90\x00", name="virus.exe", ctype="application/octet-stream").status_code, 415)

    def test_pdf_without_text_and_broken_pdf(self):
        r = self.post(make_pdf(""))
        self.assertEqual(r.status_code, 422)
        self.assertIn("fotoğraf", r.json()["detail"])
        self.assertEqual(self.post(b"%PDF-1.4\nbozuk dosya").status_code, 422)

    def test_upload_size_limit_allows_10mb_path(self):
        self.assertIn(URL, sec.UPLOAD_PATHS)


if __name__ == "__main__":
    unittest.main()
