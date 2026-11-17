"""
PrepMaster/.env dosyasını ortam değişkenlerine yükler (ek paket gerektirmez).

- Ortamda zaten tanımlı bir değişkenin üzerine YAZMAZ (Docker/sistem ayarı önceliklidir).
- Satır biçimi: ANAHTAR=deger  (# ile başlayan satırlar yorum; tırnaklar soyulur)
- Birden fazla kez çağrılması güvenlidir.
"""
import os
import sys
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
_loaded = False


def load_env(path: Path = _ENV_PATH) -> None:
    global _loaded
    if _loaded:
        return
    _loaded = True
    # Testler gerçek .env'i (gerçek SMTP şifresi vb.) okumasın: test çalıştırılırken atla.
    argv0 = sys.argv[0] if sys.argv else ""
    script = os.path.basename(argv0)
    is_unittest_cli = argv0.endswith(" -m unittest")
    if os.getenv("PREPMASTER_SKIP_DOTENV") or script.startswith("test_") or is_unittest_cli or "pytest" in sys.modules:
        return
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


load_env()
