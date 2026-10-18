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
SECRET_KEY = os.getenv("SECRET_KEY", "prepmaster_secure_jwt_secret_change_in_production_2026")
LEGACY_SALT = os.getenv("PASSWORD_SALT", "prepmaster_salt_2026")
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
    def __init__(self, cleanup_interval_seconds: int = 300):
        self._history: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = cleanup_interval_seconds

    def is_allowed(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int, int]:
        """
        Check if request under `key` is allowed.
        Returns:
            (allowed: bool, current_count: int, retry_after_seconds: int)
        """
        now = time.time()
        with self._lock:
            # Periodic cleanup
            if now - self._last_cleanup > self._cleanup_interval:
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
            else:
                self._history.clear()

    def _cleanup(self, now: float):
        self._last_cleanup = now
        expired_keys = []
        for k, v in self._history.items():
            if not v or v[-1] < (now - 3600):
                expired_keys.append(k)
        for k in expired_keys:
            del self._history[k]


# Global rate limiter instance
rate_limiter = SlidingWindowRateLimiter()


def get_client_ip(request: Request) -> str:
    """
    Extract the client's real IP address, handling proxies/load balancers safely.
    """
    # Check X-Forwarded-For header
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Leftmost entry is the initial client
        parts = [p.strip() for p in forwarded.split(",")]
        if parts and parts[0]:
            return parts[0]

    # Check X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to direct client host
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


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

        # 1. Content-Security-Policy
        # Permissive enough for embedded Tailwind CDN, Lucide, Google Fonts, and audio Blobs
        # Strict enough to block unauthorized script injection and framing
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://unpkg.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: https://cdn-icons-png.flaticon.com",
            "media-src 'self' blob: data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 2. Strict-Transport-Security (1 year HSTS)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        # 3. MIME sniffing defense
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 4. Clickjacking defense
        response.headers["X-Frame-Options"] = "DENY"

        # 5. Cross-site leakage defense
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 6. Legacy XSS filter activation
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 7. Hardware & feature permissions
        response.headers["Permissions-Policy"] = "camera=(), microphone=(self), geolocation=()"

        return response


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

# Synchronize sys.modules so both 'security' and 'backend.security' point to this identical module singleton
import sys
if __name__ in sys.modules:
    sys.modules["security"] = sys.modules[__name__]
    sys.modules["backend.security"] = sys.modules[__name__]
