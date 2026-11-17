"""
Veritabanı yedekleri.

- Günlük otomatik yedek: veritabanının yanındaki `backups/` klasörüne (Railway'de /data/backups),
  son BACKUP_KEEP_DAYS (varsayılan 7) gün tutulur. Hatalı bir güncelleme ya da yanlışlıkla silinen
  veriye karşı korur; ANCAK aynı diskte durduğu için diskin kendisi kaybolursa onlar da gider.
- Bu yüzden yönetici panelinden "Yedeği İndir" ile bilgisayara düzenli kopya alınmalıdır.

SQLite'ın kendi yedekleme API'si kullanılır: uygulama çalışırken tutarlı kopya alır (WAL dahil).
"""
import gzip
import logging
import os
import shutil
import sqlite3
import tempfile
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

log = logging.getLogger("prepmaster.backup")


def _db_path() -> Path:
    try:
        from database import DB_PATH  # type: ignore
    except ImportError:  # backend.database olarak yüklendiyse
        from backend.database import DB_PATH  # type: ignore
    return Path(DB_PATH)


def backup_dir() -> Path:
    return _db_path().parent / "backups"


def _istanbul_today() -> str:
    return (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y%m%d")


def create_backup(target_dir: Optional[Path] = None, name: Optional[str] = None) -> Path:
    """Tutarlı, gzip'li bir yedek oluşturur ve yolunu döner. Bütünlük kontrolünden geçmezse hata verir."""
    src_path = _db_path()
    target_dir = Path(target_dir or backup_dir())
    target_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name = name or f"prepmaster-{stamp}.db"

    fd, tmp_name = tempfile.mkstemp(suffix=".db", dir=str(target_dir))
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        src = sqlite3.connect(str(src_path), timeout=30)
        dst = sqlite3.connect(str(tmp))
        with dst:
            src.backup(dst)
        ok = dst.execute("PRAGMA integrity_check").fetchone()[0]
        dst.close()
        src.close()
        if ok != "ok":
            raise RuntimeError(f"Yedek bütünlük kontrolünden geçmedi: {ok}")
        out = target_dir / (name + ".gz")
        with open(tmp, "rb") as f_in, gzip.open(out, "wb", compresslevel=6) as f_out:
            shutil.copyfileobj(f_in, f_out)
        return out
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass


def prune_backups(keep_days: Optional[int] = None) -> int:
    keep_days = keep_days if keep_days is not None else int(os.getenv("BACKUP_KEEP_DAYS", "7") or 7)
    d = backup_dir()
    if not d.exists():
        return 0
    cutoff = time.time() - keep_days * 86400
    removed = 0
    for f in d.glob("prepmaster-*.db.gz"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    return removed


def daily_backup_if_needed() -> Optional[Path]:
    """Bugün (İstanbul) için yedek yoksa alır."""
    d = backup_dir()
    today = _istanbul_today()
    if d.exists() and any(f.name.startswith(f"prepmaster-daily-{today}") for f in d.glob("*.gz")):
        return None
    out = create_backup(name=f"prepmaster-daily-{today}.db")
    prune_backups()
    log.info("Günlük yedek alındı: %s", out)
    return out


_started = False


def start_backup_scheduler(interval_seconds: int = 3600) -> None:
    """Arka planda saatte bir kontrol eder; günde bir yedek alır. BACKUP_DISABLED=1 ile kapatılır."""
    global _started
    if _started or os.getenv("BACKUP_DISABLED", "").strip() == "1":
        return
    _started = True

    def loop():
        time.sleep(30)  # açılışta veritabanı göçlerinin bitmesini bekle
        while True:
            try:
                daily_backup_if_needed()
            except Exception as exc:  # yedek hatası uygulamayı durdurmamalı
                log.error("Günlük yedek alınamadı: %s", exc)
            time.sleep(interval_seconds)

    threading.Thread(target=loop, name="prepmaster-backup", daemon=True).start()
