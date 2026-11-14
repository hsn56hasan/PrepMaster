"""
PrepMaster Comprehensive Security & Defense Suite
Includes:
- Thread-safe sliding window rate limiter (Brute Force & DoS defense)
- Security Headers Middleware (CSP, HSTS, X-Content-Type-Options, etc.)
- Controlled CORS configuration
- Input Sanitization & XSS protection
- Cryptographic Password Hashing (PBKDF2-HMAC-SHA256 with per-user salt + legacy migration)
- Session Token & JWT Authentication (with expiration and constant-time HMAC validation)
"""

import os
import re
import json
import time

# .env dosyasını (varsa) diğer her şeyden önce yükle: SECRET_KEY, DEMO_MODE, e-posta ayarları
try:
    import env_loader  # noqa: F401
except ImportError:  # "backend.security" olarak içe aktarıldığında
    from backend import env_loader  # noqa: F401
import base64
import hmac
import hashlib
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple, Any

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# -----------------------------------------------------------------------------
# 1. Environment & Cryptographic Configuration
# -----------------------------------------------------------------------------
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Depoda/örnek dosyalarda bir zamanlar yayımlanmış değerler: bunlarla imzalanan
# token'ları herkes üretebilir, bu yüzden hiçbir ortamda kabul edilmez.
_KNOWN_PUBLIC_SECRETS = {
    "",
    "prepmaster_secure_jwt_secret_change_in_production_2026",
    "prepmaster_salt_2026",
    "change_me",
}

# DEMO_MODE=1 yalnızca geliştirme içindir: e-posta/SMS altyapısı olmadığından
# doğrulama kodlarını yanıtta döndürür ve simüle ödeme/Google girişine izin verir.
DEMO_MODE = os.getenv("DEMO_MODE", "0").strip().lower() in ("1", "true", "yes")
if DEMO_MODE and IS_PRODUCTION:
    raise RuntimeError(
        "DEMO_MODE=1 üretim ortamında (ENVIRONMENT=production) kullanılamaz: "
        "doğrulama kodlarını istemciye açar ve ödemesiz üyelik açtırır."
    )

_env_secret = os.getenv("SECRET_KEY", "").strip()
if _env_secret in _KNOWN_PUBLIC_SECRETS or len(_env_secret) < 32:
    if IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY tanımlı değil, çok kısa (<32 karakter) ya da depoda yayımlanmış bir değer. "
            "Üretmek için: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
        )
    # Geliştirmede her açılışta rastgele anahtar: oturumlar yeniden başlatınca düşer.
    _env_secret = secrets.token_urlsafe(48)
    print("[security] UYARI: SECRET_KEY ayarlı değil; geçici rastgele anahtar kullanılıyor.")
SECRET_KEY = _env_secret

# Yalnızca eski SHA-256 parolalarını doğrulamak için; yeni parolalar PBKDF2 + kişiye özel tuz kullanır.
# Boş değer tuzsuz SHA-256 demek olurdu (ör. seed kullanıcının "123456" hash'i eşleşirdi), bu yüzden "or".
LEGACY_SALT = os.getenv("PASSWORD_SALT") or "prepmaster_salt_2026"
SESSION_EXPIRY_HOURS = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))

# CORS Allowed Origins
RAW_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8050,http://127.0.0.1:8050")
ALLOWED_ORIGINS = [orig.strip() for orig in RAW_ORIGINS.split(",") if orig.strip()]
# Ensure local development hosts are supported if not specified
for dev_origin in ["http://localhost:8050", "http://127.0.0.1:8050", "http://localhost:3000"]:
    if dev_origin not in ALLOWED_ORIGINS:
        ALLOWED_ORIGINS.append(dev_origin)


# -----------------------------------------------------------------------------
# 2. In-Memory Sliding Window Rate Limiter (Brute-Force & DoS Defense)
# -----------------------------------------------------------------------------
class SlidingWindowRateLimiter:
    """
    Thread-safe in-memory sliding window rate limiter.
    Accurately tracks request frequency per sliding time window.
    Automatically purges expired keys to prevent memory exhaustion.
    """
    def __init__(self, cleanup_interval_seconds: int = 300, max_keys: int = 100_000):
        self._history: Dict[str, List[float]] = {}
        self._bans: Dict[str, float] = {}          # anahtar -> yasak bitiş zamanı (epoch)
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = cleanup_interval_seconds
        self._max_keys = max_keys

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """
        Check if request under `key` is allowed.
        Returns:
            (allowed: bool, current_count: int, retry_after_seconds: int)
        """
        now = time.time()
        with self._lock:
            # Periodic cleanup (ya da bellek tavanı aşıldıysa hemen): çok sayıda sahte IP ile
            # sözlüğü şişirip belleği tüketme saldırısına karşı.
            if now - self._last_cleanup > self._cleanup_interval or len(self._history) > self._max_keys:
                self._cleanup(now)

            timestamps = self._history.get(key, [])
            cutoff = now - window_seconds
            # Keep only hits inside the sliding window
            timestamps = [t for t in timestamps if t > cutoff]

            if len(timestamps) >= max_requests:
                earliest = timestamps[0]
                retry_after = max(1, int(window_seconds - (now - earliest)))
                self._history[key] = timestamps
                return False, len(timestamps), retry_after

            timestamps.append(now)
            self._history[key] = timestamps
            return True, len(timestamps), 0

    def reset(self, key: Optional[str] = None):
        """Reset rate limits (useful for testing or manual administrative unlock)."""
        with self._lock:
            if key:
                self._history.pop(key, None)
                self._bans.pop(key, None)
            else:
                self._history.clear()
                self._bans.clear()

    # --- Geçici yasaklama (tekrar tekrar sınırı aşan IP'ler) ---
    def ban(self, key: str, seconds: int) -> None:
        with self._lock:
            self._bans[key] = time.time() + seconds

    def ban_remaining(self, key: str) -> int:
        """Yasak sürüyorsa kalan saniye, yoksa 0."""
        with self._lock:
            until = self._bans.get(key)
            if not until:
                return 0
            remaining = until - time.time()
            if remaining <= 0:
                self._bans.pop(key, None)
                return 0
            return max(1, int(remaining))

    def _cleanup(self, now: float):
        self._last_cleanup = now
        over_cap = len(self._history) > self._max_keys
        # Normalde 1 saatten eski anahtarlar silinir; bellek tavanı aşıldıysa 2 dakikadan eskiler.
        horizon = 120 if over_cap else 3600
        expired_keys = [k for k, v in self._history.items() if not v or v[-1] < (now - horizon)]
        for k in expired_keys:
            del self._history[k]
        if len(self._history) > self._max_keys:
            # Hâlâ fazlaysa en eski yarısını at (saldırı altında bellek sınırlı kalsın)
            ordered = sorted(self._history.items(), key=lambda kv: kv[1][-1] if kv[1] else 0)
            for k, _ in ordered[: len(ordered) // 2]:
                del self._history[k]
        for k in [k for k, until in self._bans.items() if until < now]:
            del self._bans[k]


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()


# Gerçek istemci IP'sini taşıyan başlıklara YALNIZCA bu adreslerden gelen isteklerde güvenilir.
# Varsayılan: aynı makinedeki aracı (Cloudflare Tunnel / nginx). Docker'da nginx konteynerinin
# adresi/ağı eklenmeli, ör. TRUSTED_PROXY_IPS=127.0.0.1,::1,172.16.0.0/12
import ipaddress as _ipaddress


def _trusted_proxies():
    raw = os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1,::1")
    nets, names = [], set()
    for part in (p.strip() for p in raw.split(",")):
        if not part:
            continue
        try:
            nets.append(_ipaddress.ip_network(part, strict=False))
        except ValueError:
            names.add(part)  # IP olmayan değerler (ör. testlerdeki "testclient") birebir eşleşir
    return nets, names


def _is_trusted_proxy(host: str) -> bool:
    nets, names = _trusted_proxies()
    if host in names:
        return True
    try:
        addr = _ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(addr in n for n in nets)


# Railway'de konteynere dışarıdan YALNIZCA Railway'in kenar (edge) vekili üzerinden ulaşılır ve
# vekil, gerçek istemci IP'sini X-Real-IP başlığına yazar. Vekilin kendi adresi her istekte
# farklı bir iç ağ adresi olabildiğinden TRUSTED_PROXY_IPS ile eşleştirmek yerine bu başlığa
# doğrudan güvenilir. Başka bir barındırmada CLIENT_IP_HEADER ile açıkça ayarlanabilir.
_ON_RAILWAY = bool(os.getenv("RAILWAY_ENVIRONMENT_ID") or os.getenv("RAILWAY_ENVIRONMENT"))
CLIENT_IP_HEADER = os.getenv("CLIENT_IP_HEADER", "X-Real-IP" if _ON_RAILWAY else "").strip()


def get_client_ip(request: Request) -> str:
    """
    İsteğin gerçek istemci IP'si (hız sınırı ve PayTR için).

    - CLIENT_IP_HEADER ayarlıysa (Railway'de otomatik X-Real-IP) o başlık kullanılır.
    - Doğrudan bağlanan adres güvenilir bir aracı DEĞİLSE o adres kullanılır; başlıklara
      bakılmaz (X-Forwarded-For'u herkes uydurabilir, hız sınırını atlatmak için kullanılırdı).
    - Güvenilir aracıdan geldiyse: Cloudflare'in yazdığı CF-Connecting-IP, yoksa nginx'in
      yazdığı X-Real-IP kullanılır. (Eskiden tünel arkasında herkes 127.0.0.1 görünecek ve
      bir öğrencinin yanlış şifreleri herkesi kilitleyecekti.)
    """
    peer = request.client.host if request.client and request.client.host else "127.0.0.1"
    if CLIENT_IP_HEADER:
        value = (request.headers.get(CLIENT_IP_HEADER) or "").split(",")[0].strip()
        if value:
            try:
                return str(_ipaddress.ip_address(value))
            except ValueError:
                pass
        return peer
    if not _is_trusted_proxy(peer):
        return peer
    for header in ("CF-Connecting-IP", "X-Real-IP"):
        value = (request.headers.get(header) or "").strip()
        if value:
            try:
                return str(_ipaddress.ip_address(value))
            except ValueError:
                continue
    return peer


def enforce_rate_limit(
    request: Request,
    scope: str,
    max_requests: int,
    window_seconds: int,
    identifier: Optional[str] = None
):
    """
    Enforces dual-layer rate limiting:
    1. By Client IP (prevents volume attacks / endpoint flooding)
    2. By User Identifier/Email (prevents distributed credential stuffing / targeted OTP spam)
    """
    client_ip = get_client_ip(request)

    # 1. Check IP rate limit
    ip_key = f"rl:ip:{scope}:{client_ip}"
    allowed, count, retry_after = rate_limiter.is_allowed(ip_key, max_requests, window_seconds)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Çok fazla istek yapıldı ({scope}). Lütfen {retry_after} saniye sonra tekrar deneyin.",
            headers={"Retry-After": str(retry_after)}
        )

    # 2. Check Identifier rate limit if provided
    if identifier:
        clean_id = identifier.lower().strip()
        id_key = f"rl:id:{scope}:{clean_id}"
        id_allowed, id_count, id_retry = rate_limiter.is_allowed(id_key, max_requests, window_seconds)
        if not id_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Bu hesap/hedef için çok fazla deneme yapıldı. Lütfen {id_retry} saniye sonra tekrar deneyin.",
                headers={"Retry-After": str(id_retry)}
            )


def make_rate_limiter_dependency(scope: str, max_requests: int, window_seconds: int):
    """
    FastAPI Depends() factory for standard IP-based rate limiting.
    """
    async def _rate_limiter_dep(request: Request):
        enforce_rate_limit(request, scope, max_requests, window_seconds)
    return _rate_limiter_dep


# Preset rate limiters for endpoints
rate_limit_otp_request = make_rate_limiter_dependency("otp_request", max_requests=5, window_seconds=60)
rate_limit_otp_verify = make_rate_limiter_dependency("otp_verify", max_requests=10, window_seconds=60)
rate_limit_login = make_rate_limiter_dependency("auth_login", max_requests=5, window_seconds=60)
rate_limit_register = make_rate_limiter_dependency("auth_register", max_requests=5, window_seconds=60)
rate_limit_ai_writing = make_rate_limiter_dependency("ai_writing", max_requests=10, window_seconds=60)
rate_limit_ai_speaking = make_rate_limiter_dependency("ai_speaking", max_requests=10, window_seconds=60)
rate_limit_general = make_rate_limiter_dependency("general", max_requests=120, window_seconds=60)


# -----------------------------------------------------------------------------
# 3. Security Headers Middleware
# -----------------------------------------------------------------------------
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injects essential OWASP recommended security headers on all responses:
    - Content-Security-Policy (CSP)
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options (nosniff)
    - X-Frame-Options (DENY)
    - Referrer-Policy
    - X-XSS-Protection
    - Permissions-Policy
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        is_payment_result = request.url.path == "/odeme-sonuc"

        # 1. Content-Security-Policy
        # Permissive enough for embedded Tailwind CDN, Lucide, Google Fonts, and audio Blobs
        # Strict enough to block unauthorized script injection and framing
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com https://www.paytr.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: https://cdn-icons-png.flaticon.com",
            "media-src 'self' blob: data:",
            "connect-src 'self'",
            # PayTR ödeme penceresi (kart bilgisi yalnızca orada girilir)
            "frame-src https://www.paytr.com",
            # PayTR penceresi ödeme sonrası /odeme-sonuc sayfasını kendi içinde açar
            "frame-ancestors 'self' https://www.paytr.com" if is_payment_result else "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 2. Strict-Transport-Security (1 year HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 3. MIME sniffing defense
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. Clickjacking defense
        if is_payment_result:
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response.headers["X-Frame-Options"] = "DENY"

        # 5. Cross-site leakage defense
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Legacy XSS filter activation
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 7. Hardware & feature permissions
        response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"

        return response


# -----------------------------------------------------------------------------
# 3a. DoS / Flood Koruması (saf ASGI ara katmanı)
# -----------------------------------------------------------------------------
def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


class _BodyTooLarge(Exception):
    pass


class DoSProtectionMiddleware:
    """
    Tek bir istemcinin sunucuyu boğmasını engeller:
      1. IP başına genel istek sınırı (tüm yollar) ve daha sıkı /api/ sınırı
      2. Kısa süreli patlama (burst) sınırı: saniyeler içinde yüzlerce istek
      3. Sınırı tekrar tekrar aşan IP'ye geçici yasak (istek uygulamaya hiç ulaşmaz)
      4. İstek gövdesi boyut sınırı (büyük gövdeyle bellek tüketme saldırısı -> 413)

    Not: Bu katman tek kaynaklı kötüye kullanımı ve kaba kuvveti durdurur. Binlerce farklı
    IP'den gelen hacimsel DDoS ağ kenarında (Railway edge / Cloudflare) karşılanmalıdır.
    """

    def __init__(self, app):
        self.app = app
        self.api_per_min = _env_int("DOS_API_REQUESTS_PER_MIN", 240)
        self.all_per_min = _env_int("DOS_TOTAL_REQUESTS_PER_MIN", 600)
        self.burst_count = _env_int("DOS_BURST_REQUESTS", 60)
        self.burst_window = _env_int("DOS_BURST_WINDOW_SECONDS", 5)
        self.strikes_to_ban = _env_int("DOS_STRIKES_BEFORE_BAN", 5)
        self.ban_seconds = _env_int("DOS_BAN_SECONDS", 600)
        self.max_body = _env_int("DOS_MAX_BODY_BYTES", 2 * 1024 * 1024)
        self.max_upload = _env_int("DOS_MAX_UPLOAD_BYTES", 10 * 1024 * 1024)

    @staticmethod
    async def _reject(send, status_code: int, detail: str, retry_after: Optional[int] = None):
        body = json.dumps({"detail": detail}, ensure_ascii=False).encode("utf-8")
        headers = [
            (b"content-type", b"application/json; charset=utf-8"),
            (b"content-length", str(len(body)).encode()),
        ]
        if retry_after:
            headers.append((b"retry-after", str(retry_after).encode()))
        await send({"type": "http.response.start", "status": status_code, "headers": headers})
        await send({"type": "http.response.body", "body": body})

    def _strike(self, ip: str) -> None:
        """Sınır aşımı sayılır; kısa sürede çok aşım olursa IP geçici olarak yasaklanır."""
        allowed, _, _ = rate_limiter.is_allowed(f"dos:strike:{ip}", self.strikes_to_ban, 300)
        if not allowed:
            rate_limiter.ban(f"dos:ban:{ip}", self.ban_seconds)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        path = scope.get("path", "")
        peer = scope.get("client")[0] if scope.get("client") else ""
        ip = get_client_ip(request)

        # Konteynerin kendi sağlık kontrolü (127.0.0.1, vekil başlığı yok) sınırlanmaz
        is_local_healthcheck = peer in ("127.0.0.1", "::1") and not (
            CLIENT_IP_HEADER and request.headers.get(CLIENT_IP_HEADER)
        )

        if not is_local_healthcheck:
            # 1) Yasaklı IP: hiçbir işlem yapmadan reddet
            banned_for = rate_limiter.ban_remaining(f"dos:ban:{ip}")
            if banned_for:
                return await self._reject(
                    send, 429,
                    f"Çok fazla istek gönderildiği için erişiminiz geçici olarak durduruldu. "
                    f"{banned_for} saniye sonra tekrar deneyin.",
                    banned_for,
                )

            # 2) Patlama, genel ve API sınırları
            checks = [
                (f"dos:burst:{ip}", self.burst_count, self.burst_window),
                (f"dos:all:{ip}", self.all_per_min, 60),
            ]
            if path.startswith("/api/"):
                checks.append((f"dos:api:{ip}", self.api_per_min, 60))
            for key, limit, window in checks:
                allowed, _, retry_after = rate_limiter.is_allowed(key, limit, window)
                if not allowed:
                    self._strike(ip)
                    return await self._reject(
                        send, 429,
                        f"Çok fazla istek yapıldı. Lütfen {retry_after} saniye sonra tekrar deneyin.",
                        retry_after,
                    )

        # 3) Gövde boyutu sınırı
        limit = self.max_upload if path == "/api/student/upload-document" else self.max_body
        headers = dict(scope.get("headers") or [])
        raw_len = headers.get(b"content-length")
        if raw_len is not None:
            try:
                declared = int(raw_len)
            except ValueError:
                return await self._reject(send, 400, "Geçersiz Content-Length başlığı.")
            if declared > limit:
                return await self._reject(
                    send, 413, f"İstek gövdesi çok büyük (en fazla {limit // (1024 * 1024)} MB)."
                )

        received = 0
        response_started = False

        async def limited_receive():
            nonlocal received
            message = await receive()
            if message.get("type") == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise _BodyTooLarge()
            return message

        async def tracking_send(message):
            nonlocal response_started
            if message.get("type") == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracking_send)
        except _BodyTooLarge:
            if not response_started:
                await self._reject(
                    send, 413, f"İstek gövdesi çok büyük (en fazla {limit // (1024 * 1024)} MB)."
                )


# -----------------------------------------------------------------------------
# 4. Input Sanitization & XSS Defense
# -----------------------------------------------------------------------------
def sanitize_text(value: Optional[str], strip_tags: bool = False, max_length: Optional[int] = None) -> str:
    """
    Sanitizes arbitrary text input to prevent XSS and control character injection.
    - Strips NULL bytes (\\x00)
    - Removes dangerous executable blocks (<script>...</script>, <iframe>...</iframe>, etc.)
    - Removes orphaned dangerous tags
    - Neutralizes event handlers (onerror=, onclick=, etc.)
    - Neutralizes javascript: URI protocols
    - Optionally strips all remaining HTML tags
    - Truncates to max_length if specified
    """
    if value is None:
        return ""

    # Remove null bytes
    val = str(value).replace("\x00", "")

    # 1. Remove complete executable blocks (including inner script body)
    val = re.sub(
        r"<\s*(script|iframe|object|embed|style|meta|link|svg|applet)[^>]*>.*?</\s*\1\s*>",
        "",
        val,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 2. Remove any remaining or unclosed dangerous tags
    val = re.sub(
        r"<\s*/?\s*(script|iframe|object|embed|style|meta|link|svg|applet)[^>]*>",
        "",
        val,
        flags=re.IGNORECASE
    )

    # 3. Neutralize inline event handlers and pseudo protocols
    val = re.sub(r"\bon\w+\s*=", "data-blocked=", val, flags=re.IGNORECASE)
    val = re.sub(r"javascript\s*:", "blocked:", val, flags=re.IGNORECASE)

    # 4. Strip all remaining HTML tags if requested
    if strip_tags:
        val = re.sub(r"<[^>]*>", "", val)

    val = val.strip()
    if max_length and len(val) > max_length:
        val = val[:max_length]
    return val


# -----------------------------------------------------------------------------
# 5. Password Hashing & Salt Security (PBKDF2-HMAC-SHA256 + Legacy Fallback)
# -----------------------------------------------------------------------------
def hash_password(password: str, salt: Optional[str] = None) -> str:
    """
    Hashes password using PBKDF2-HMAC-SHA256 with 100,000 iterations and
    a cryptographically secure per-user salt.
    Format: pbkdf2:sha256:100000$<salt>$<hash>
    """
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    )
    return f"pbkdf2:sha256:100000${salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verifies a password against stored hash with constant-time equality.
    Supports:
    1. PBKDF2-HMAC-SHA256 with dynamic salt (preferred standard)
    2. Legacy SHA-256 salted hash (for backwards compatibility with existing users)
    """
    if not stored_hash:
        return False

    # Check for PBKDF2 format
    if stored_hash.startswith("pbkdf2:sha256:"):
        parts = stored_hash.split("$")
        if len(parts) == 3:
            salt = parts[1]
            expected_hex = parts[2]
            computed_hex = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt.encode("utf-8"),
                100000
            ).hex()
            return hmac.compare_digest(computed_hex, expected_hex)

    # Legacy SHA-256 salted fallback
    legacy_hash = hashlib.sha256((password + LEGACY_SALT).encode("utf-8")).hexdigest()
    if hmac.compare_digest(legacy_hash, stored_hash):
        return True

    return False


# -----------------------------------------------------------------------------
# 6. Session Token & JWT Authentication Engine
# -----------------------------------------------------------------------------
def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def create_session_token(
    user_id: int,
    username: str,
    email: str,
    role: str = "student",
    expires_in_hours: Optional[int] = None
) -> Tuple[str, int]:
    """
    Generates a secure, signed session JWT.
    Returns (token_string, expires_in_seconds).
    """
    hours = expires_in_hours or SESSION_EXPIRY_HOURS
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=hours)

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }

    h_bytes = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_bytes = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{h_bytes}.{p_bytes}"

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()
    sig_b64 = _b64url_encode(signature)

    token = f"{message}.{sig_b64}"
    expires_in_seconds = int(hours * 3600)
    return token, expires_in_seconds


def verify_session_token(token: str) -> Dict[str, Any]:
    """
    Validates HMAC signature and checks token expiration.
    Returns token payload dict or raises HTTPException(401).
    """
    if not token or not isinstance(token, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum belirteci (token) eksik.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    parts = token.strip().split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz oturum belirteci formatı.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    header_b64, payload_b64, sig_b64 = parts
    message = f"{header_b64}.{payload_b64}"

    # Verify signature
    expected_sig = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256
    ).digest()
    expected_sig_b64 = _b64url_encode(expected_sig)

    if not hmac.compare_digest(sig_b64, expected_sig_b64):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Geçersiz veya değiştirilmiş oturum belirteci.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum yükü çözülemedi.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check expiration
    exp = payload.get("exp")
    if not exp or time.time() > exp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Oturum süresi dolmuş. Lütfen tekrar giriş yapın.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return payload


def get_current_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """
    Extracts authenticated user payload from 'Authorization: Bearer <token>' header
    or returns None if unauthenticated.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1].strip()
    try:
        return verify_session_token(token)
    except HTTPException:
        return None


def require_current_user(request: Request) -> Dict[str, Any]:
    """
    Kullanıcı kimliği YALNIZCA imzalı oturum token'ından alınır.
    İstek gövdesindeki/sorgudaki user_id'ye asla güvenilmez.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bu işlem için giriş yapmanız gerekiyor.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    payload = verify_session_token(auth_header.split(" ", 1)[1].strip())
    try:
        payload["user_id"] = int(payload.get("user_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz oturum.")
    return payload

# Synchronize sys.modules so both 'security' and 'backend.security' point to this identical module singleton
import sys
if __name__ in sys.modules:
    sys.modules["security"] = sys.modules[__name__]
    sys.modules["backend.security"] = sys.modules[__name__]
