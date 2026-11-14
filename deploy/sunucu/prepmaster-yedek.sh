#!/usr/bin/env bash
# PrepMaster veritabanının günlük yedeği (prepmaster-yedek.timer her gece çalıştırır).
# SQLite'ın kendi yedekleme komutu kullanılır: çalışan uygulamayı durdurmadan tutarlı kopya alır.
set -euo pipefail

DB=/srv/prepmaster/data/prepmaster.db
HEDEF=/srv/prepmaster/yedek
SAKLA_GUN=14

[ -f "$DB" ] || { echo "Veritabanı yok: $DB"; exit 0; }
mkdir -p "$HEDEF"
DOSYA="$HEDEF/prepmaster-$(date +%Y%m%d-%H%M%S).db"

sqlite3 "$DB" ".backup '$DOSYA'"
# Yedeğin bozuk olmadığını doğrula
if [ "$(sqlite3 "$DOSYA" 'PRAGMA integrity_check;')" != "ok" ]; then
    echo "HATA: yedek bütünlük kontrolünden geçmedi: $DOSYA" >&2
    rm -f "$DOSYA"
    exit 1
fi
gzip -9 "$DOSYA"
chmod 600 "$DOSYA.gz"

# Eski yedekleri sil
find "$HEDEF" -name 'prepmaster-*.db.gz' -mtime +"$SAKLA_GUN" -delete

echo "Yedek alındı: $DOSYA.gz ($(du -h "$DOSYA.gz" | cut -f1))"
