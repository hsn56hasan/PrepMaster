#!/usr/bin/env bash
# PrepMaster'ı sunucuya kurar ya da günceller (aynı komut; tekrar çalıştırmak güvenlidir).
#
#   sudo bash kur.sh /tmp/prepmaster.tar.gz prepmaster.com.tr
#
# - Uygulama:   /srv/prepmaster/app   (sahibi root, salt okunur)
# - Veri:       /srv/prepmaster/data  (SQLite, yalnız prepmaster kullanıcısı)
# - Yedekler:   /srv/prepmaster/yedek (her gece, 14 gün)
# - Ayarlar:    /srv/prepmaster/app/.env (ilk kurulumda üretilir, sonra KORUNUR)
# - Servis:     prepmaster.service -> 127.0.0.1:8050 (dışarıya yalnız Cloudflare Tunnel)
set -euo pipefail

PAKET="${1:-}"
ALAN="${2:-}"
KOK=/srv/prepmaster
BURASI="$(cd "$(dirname "$0")" && pwd)"

[ "$(id -u)" -eq 0 ] || { echo "sudo ile çalıştırın: sudo bash $0 <paket.tar.gz> <alan-adı>"; exit 1; }
[ -f "$PAKET" ] || { echo "Paket bulunamadı: '$PAKET'"; exit 1; }

echo "==> Gerekli paketler"
NEEDED=()
command -v sqlite3 >/dev/null || NEEDED+=(sqlite3)
python3 -c "import venv, ensurepip" 2>/dev/null || NEEDED+=(python3-venv)
if [ ${#NEEDED[@]} -gt 0 ]; then
    apt-get update -qq && apt-get install -y -qq "${NEEDED[@]}"
fi

echo "==> Kullanıcı ve klasörler"
id prepmaster >/dev/null 2>&1 || useradd --system --home-dir "$KOK" --shell /usr/sbin/nologin prepmaster
install -d -o root -g root -m 755 "$KOK"
install -d -o prepmaster -g prepmaster -m 750 "$KOK/data" "$KOK/yedek" "$KOK/log"

echo "==> Uygulama dosyaları"
YENI="$KOK/app.yeni"
rm -rf "$YENI"
mkdir -p "$YENI"
tar -xzf "$PAKET" -C "$YENI"
# Ayarlar korunur
[ -f "$KOK/app/.env" ] && cp -p "$KOK/app/.env" "$YENI/.env"
rm -rf "$KOK/app.eski"
[ -d "$KOK/app" ] && mv "$KOK/app" "$KOK/app.eski"
mv "$YENI" "$KOK/app"
chown -R root:prepmaster "$KOK/app"
chmod -R u=rwX,g=rX,o= "$KOK/app"

echo "==> Python ortamı"
[ -x "$KOK/venv/bin/python" ] || python3 -m venv "$KOK/venv"
"$KOK/venv/bin/pip" install -q --upgrade pip
"$KOK/venv/bin/pip" install -q -r "$KOK/app/requirements.txt"

ENV="$KOK/app/.env"
if [ ! -f "$ENV" ]; then
    echo "==> İlk kurulum: .env üretiliyor"
    [ -n "$ALAN" ] || { echo "İlk kurulumda alan adı gerekli: sudo bash $0 <paket> <alan-adı>"; exit 1; }
    ANAHTAR="$("$KOK/venv/bin/python" -c 'import secrets; print(secrets.token_urlsafe(48))')"
    cat > "$ENV" <<EOF
# PrepMaster canlı ayarları — GİZLİ. Yalnızca root ve prepmaster okuyabilir.
ENVIRONMENT=production
SECRET_KEY=$ANAHTAR
PREPMASTER_DB_PATH=$KOK/data/prepmaster.db
# Cloudflare Tunnel aynı makinede: gerçek istemci IP'si CF-Connecting-IP'den alınır
TRUSTED_PROXY_IPS=127.0.0.1,::1
ALLOWED_ORIGINS=https://$ALAN,https://www.$ALAN

# --- E-posta (şifre sıfırlama) ---
EMAIL_FROM="PrepMaster <noreply@$ALAN>"
SMTP_HOST=
SMTP_PORT=465
SMTP_USER=
SMTP_PASSWORD=
RESEND_API_KEY=

# --- PayTR ---
PAYTR_MERCHANT_ID=
PAYTR_MERCHANT_KEY=
PAYTR_MERCHANT_SALT=
PAYTR_TEST_MODE=1
EOF
fi
chown root:prepmaster "$ENV"
chmod 640 "$ENV"

echo "==> Servisler"
install -o root -g root -m 755 "$BURASI/prepmaster-yedek.sh" "$KOK/prepmaster-yedek.sh"
install -o root -g root -m 644 "$BURASI/prepmaster.service" /etc/systemd/system/prepmaster.service
install -o root -g root -m 644 "$BURASI/prepmaster-yedek.service" /etc/systemd/system/prepmaster-yedek.service
install -o root -g root -m 644 "$BURASI/prepmaster-yedek.timer" /etc/systemd/system/prepmaster-yedek.timer
systemctl daemon-reload
systemctl enable -q prepmaster.service prepmaster-yedek.timer
systemctl start prepmaster-yedek.timer
systemctl restart prepmaster.service

echo "==> Sağlık kontrolü"
for i in $(seq 1 30); do
    if curl -fsS http://127.0.0.1:8050/api/config >/dev/null 2>&1; then
        echo "PrepMaster çalışıyor: http://127.0.0.1:8050 (dışarıya Cloudflare Tunnel ile açılır)"
        rm -rf "$KOK/app.eski"
        exit 0
    fi
    sleep 1
done
echo "HATA: PrepMaster 30 sn'de başlamadı. Son kayıtlar:" >&2
journalctl -u prepmaster -n 40 --no-pager >&2 || true
if [ -d "$KOK/app.eski" ]; then
    echo "Önceki sürüme dönülüyor..." >&2
    rm -rf "$KOK/app.hatali" && mv "$KOK/app" "$KOK/app.hatali" && mv "$KOK/app.eski" "$KOK/app"
    systemctl restart prepmaster.service
fi
exit 1
