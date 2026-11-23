import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request, Depends, status, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, Response
from pydantic import BaseModel, Field, field_validator

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import (
    init_db, get_profile, update_profile, 
    save_exam_attempt, get_exam_history, 
    set_vocab_status, get_vocab_progress,
    record_mistake, resolve_mistake, delete_mistake,
    get_mistakes, get_mistake_count,
    bulk_upsert_mistakes, bulk_upsert_vocab_progress, bulk_resolve_mistakes,
    create_user, authenticate_user, verify_student, get_verification_status,
    create_student_otp, verify_student_otp,
    verify_student_by_document, unlock_university_membership, check_university_access,
    create_3ds_session, verify_3ds_code, generate_gib_receipt,
    upsert_google_user, request_password_reset, confirm_password_reset, user_exists_with_email,
    create_paytr_order, get_paytr_order, finish_paytr_order,
    record_study_day,
    admin_list_students, admin_update_student_access,
    admin_reset_student_password, admin_delete_student,
    create_support_ticket, list_support_tickets
)
from document_scanner import (
    scan_student_document, extract_text_from_bytes, SAMPLE_DOCUMENTS
)
from email_service import (
    email_configured,
    get_email_status,
    send_email_verbose,
    get_email_budget,
    send_password_reset_email,
    send_student_otp_email,
    send_welcome_email,
    send_support_ticket_notification,
    send_support_ticket_receipt,
    send_access_granted_email,
)
from paytr_service import (
    generate_paytr_iframe_token, verify_paytr_callback_hash, parse_merchant_oid,
    is_paytr_live_configured
)
from seo_pages import (
    DEFAULT_PUBLIC_URL,
    resolve_site_url,
    get_google_verification_meta,
    build_robots_txt,
    build_sitemap_xml,
    compute_counts_by_uni,
    render_exams_hub_html,
    render_university_seo_html,
)

from security import (
    SecurityHeadersMiddleware,
    DoSProtectionMiddleware,
    IS_PRODUCTION,
    ALLOWED_ORIGINS,
    rate_limiter,
    enforce_rate_limit,
    rate_limit_otp_request,
    rate_limit_otp_verify,
    rate_limit_login,
    rate_limit_register,
    rate_limit_ai_writing,
    rate_limit_ai_speaking,
    rate_limit_general,
    sanitize_text,
    get_client_ip,
    create_session_token,
    verify_session_token,
    get_current_user_from_request,
    require_current_user,
    DEMO_MODE,
)
import os
import httpx

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
MEMBERSHIP_PRICE_TRY = 50.0

# E-posta/SMS altyapısı olmadığı için bu kodlar yalnızca DEMO_MODE'da yanıtta döner.
# Aksi halde başkasının e-postasıyla kod isteyip yanıttan okumak hesabı ele geçirmeye yeterdi.
_SECRET_CODE_FIELDS = ("otp_code", "reset_code", "reset_code_sandbox", "demo_code", "sms_code", "sms_code_sandbox")


def _hide_codes(res: Dict[str, Any]) -> Dict[str, Any]:
    if DEMO_MODE:
        return res
    return {k: v for k, v in res.items() if k not in _SECRET_CODE_FIELDS}


def _require_demo(feature: str):
    if not DEMO_MODE:
        raise HTTPException(
            status_code=503,
            detail=f"{feature} henüz gerçek altyapıya bağlanmadı; yalnızca geliştirme (DEMO_MODE) ortamında çalışır."
        )


def _listening_question_map() -> Dict[str, Dict[str, Any]]:
    """
    Dinleme sorularını Hata Kasası ve sınav motorunun anladığı soru biçimine çevirir.
    Ses olmadan da çözülebilsin diye dinleme metni (transkript) sorunun başına eklenir.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for track in listening_data:
        for lq in track.get("questions", []):
            out[lq["id"]] = {
                "id": lq["id"],
                "university_id": track.get("university_id", "general"),
                "level": track.get("level", "B2"),
                "category": "Listening",
                "question": f"[Dinleme: {track.get('title', '')}]\n\n{track.get('audio_script', '')}\n\n{lq['question']}",
                "options": lq["options"],
                "correct_answer": lq["correct_answer"],
                "explanation_tr": lq.get("explanation_tr", ""),
                "explanation_en": lq.get("explanation_en", ""),
                "source": "listening",
                "track_id": track.get("id"),
            }
    return out


def _all_question_map() -> Dict[str, Dict[str, Any]]:
    q_map = {q["id"]: q for q in questions_data}
    q_map.update(_listening_question_map())
    return q_map


def _current_user_id(request: Request) -> int:
    """Oturumu zorunlu kılar ve kullanıcının hâlâ var olduğunu doğrular."""
    uid = require_current_user(request)["user_id"]
    if not get_profile(uid):
        raise HTTPException(status_code=401, detail="Hesap bulunamadı. Lütfen tekrar giriş yapın.")
    return uid


def _record_study(request: Request) -> None:
    """Giriş yapmış öğrencinin çalışma gününü seriye işler (girişsiz istekte bir şey yapmaz)."""
    token_user = get_current_user_from_request(request)
    if token_user:
        record_study_day(token_user["user_id"])


def _has_access(token_user: Optional[Dict[str, Any]], university_id: str) -> bool:
    """Giriş yapmamış kullanıcı yalnızca genel içeriği görür; kimlik her zaman token'dan gelir."""
    if not university_id or university_id in ("general", "all"):
        return True
    if not token_user:
        return False
    return check_university_access(token_user["user_id"], university_id)

def _filter_accessible(token_user: Optional[Dict[str, Any]], items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Kilitli üniversitelerin içeriğini listeden çıkarır (üniversite başına bir kez sorgular)."""
    cache: Dict[str, bool] = {}
    out = []
    for item in items:
        uni = item.get("university_id") or "general"
        if uni not in cache:
            cache[uni] = _has_access(token_user, uni)
        if cache[uni]:
            out.append(item)
    return out


def _require_item_access(request: Request, item: Dict[str, Any]) -> None:
    uni = item.get("university_id") or "general"
    if not _has_access(get_current_user_from_request(request), uni):
        raise HTTPException(status_code=403, detail={
            "error": "membership_required",
            "message": f"{uni.upper()} içeriği için üyelik gereklidir.",
            "university_id": uni,
            "price_try": MEMBERSHIP_PRICE_TRY,
        })

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="PrepKampüs API", version="1.2.0")

# Security Headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, etc.)
app.add_middleware(SecurityHeadersMiddleware)

# Controlled CORS configuration (Restricted origins, credentials protection, explicit methods & headers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["Retry-After"]
)

# Asıl alan adına yönlendirme (CANONICAL_HOST=prepkampus.com verilince açılır).
# Eski Railway adresi, www ve diğer alan adlarından gelen SAYFA isteklerini kalıcı olarak asıl
# adrese taşır; arama motoru aynı sitenin iki kopyasını görmez. /api/ istekleri (eski APK'lar,
# PayTR bildirimi) ve APK indirmesi YÖNLENDİRİLMEZ; yerel ve sağlık kontrolü istekleri etkilenmez.
CANONICAL_HOST = os.getenv("CANONICAL_HOST", "").strip().lower().removeprefix("https://").rstrip("/")


@app.middleware("http")
async def canonical_host_redirect(request: Request, call_next):
    if CANONICAL_HOST and request.method in ("GET", "HEAD"):
        host = (request.headers.get("x-forwarded-host") or request.headers.get("host") or "")
        host = host.split(",")[0].strip().lower().split(":")[0]
        path = request.url.path
        local = host in ("", "localhost", "127.0.0.1", "testserver") or host.startswith("192.168.")
        if (not local and host != CANONICAL_HOST and not path.startswith(("/api/", "/static/downloads/"))):
            query = request.url.query
            target = f"https://{CANONICAL_HOST}{path}" + (f"?{query}" if query else "")
            return RedirectResponse(target, status_code=301)
    return await call_next(request)


# DoS / flood koruması: en dışta çalışır, kötüye kullanan istek uygulamaya hiç ulaşmaz
app.add_middleware(DoSProtectionMiddleware)

# Load JSON datasets
def load_json(filename: str):
    file_path = DATA_DIR / filename
    if not file_path.exists():
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

universities_data = load_json("universities.json")
questions_data = load_json("questions.json")
vocabulary_data = load_json("vocabulary.json")
writing_guides_data = load_json("writing_guides.json")
listening_data = load_json("listening.json")
speaking_data = load_json("speaking.json")

@app.on_event("startup")
def startup_event():
    global universities_data, questions_data, vocabulary_data, writing_guides_data, listening_data, speaking_data
    universities_data = load_json("universities.json")
    questions_data = load_json("questions.json")
    vocabulary_data = load_json("vocabulary.json")
    writing_guides_data = load_json("writing_guides.json")
    listening_data = load_json("listening.json")
    speaking_data = load_json("speaking.json")
    init_db()
    # Günde bir otomatik veritabanı yedeği (veritabanının yanındaki backups/ klasörüne)
    try:
        from backup import start_backup_scheduler
    except ImportError:
        from backend.backup import start_backup_scheduler
    start_backup_scheduler()

# --- Models ---
class ProfileUpdateRequest(BaseModel):
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    current_level: str = Field(..., pattern=r"^(?i)(A1|A2|B1|B2|C1|C2)$")
    target_score: Optional[int] = Field(65, ge=0, le=100)

    @field_validator("university_id", "current_level", mode="before")
    @classmethod
    def sanitize_strings(cls, v):
        return sanitize_text(v, strip_tags=True)

class ExamSubmitRequest(BaseModel):
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    level: str = Field(..., max_length=10, pattern=r"^[a-zA-Z0-9]+$")
    duration_seconds: int = Field(..., ge=0, le=86400)
    answers: Dict[str, str] = Field(...) # question_id -> chosen option key (e.g. "B")
    question_times: Optional[Dict[str, int]] = Field(default_factory=dict)
    is_mistake_practice: Optional[bool] = False
    # Sınavda gösterilen TÜM soru kimlikleri. Verilirse boş bırakılanlar yanlış sayılır;
    # eskiden puan "doğru / cevaplanan" idi ve boş bırakmak puanı şişiriyordu.
    question_ids: Optional[List[str]] = Field(default=None, max_length=500)

    @field_validator("answers", mode="before")
    @classmethod
    def sanitize_answers(cls, v):
        if not isinstance(v, dict):
            return v
        cleaned = {}
        for q_id, ans in v.items():
            s_qid = sanitize_text(str(q_id), strip_tags=True, max_length=100)
            s_ans = sanitize_text(str(ans), strip_tags=True, max_length=50)
            cleaned[s_qid] = s_ans
        return cleaned

class VocabStatusRequest(BaseModel):
    status: str = Field(..., pattern=r"^(mastered|learning|unreviewed)$")

class EssayEvaluateRequest(BaseModel):
    essay: str = Field(..., min_length=1, max_length=20000)
    prompt: Optional[str] = Field("General Academic Essay", max_length=1000)
    university_id: Optional[str] = Field("general", max_length=50)
    level: Optional[str] = Field("B2", max_length=10)

    @field_validator("essay", "prompt", "university_id", "level", mode="before")
    @classmethod
    def sanitize_inputs(cls, v):
        return sanitize_text(v, strip_tags=False)

class SpeakingEvaluateRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=10000)
    task_id: Optional[str] = Field("spk_boun_01", max_length=50)
    duration_seconds: Optional[int] = Field(60, ge=1, le=3600)

    @field_validator("transcript", "task_id", mode="before")
    @classmethod
    def sanitize_inputs(cls, v):
        return sanitize_text(v, strip_tags=False)

class SyncPushRequest(BaseModel):
    """Mobilin çevrimdışıyken biriktirdiği değişiklikler (giden kutusu)."""
    profile: Optional[Dict[str, Any]] = None
    mistakes: Optional[List[Dict[str, Any]]] = Field(default=None, max_length=2000)
    resolved_mistakes: Optional[List[str]] = Field(default=None, max_length=2000)
    vocab_progress: Optional[Dict[str, str]] = None
    exam_attempts: Optional[List[Dict[str, Any]]] = Field(default=None, max_length=200)

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    university_id: Optional[str] = Field("itu", max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    student_number: Optional[str] = Field("", max_length=30, pattern=r"^[a-zA-Z0-9_-]*$")
    # Kullanıcı Sözleşmesi + Aydınlatma Metni onayı ZORUNLU; açık rıza ayrı ve isteğe bağlı
    terms_accepted: bool = False
    explicit_consent: bool = False

    @field_validator("full_name", "username", "student_number", mode="before")
    @classmethod
    def sanitize_fields(cls, v):
        return sanitize_text(v, strip_tags=True)

class LoginRequest(BaseModel):
    identifier: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("identifier", mode="before")
    @classmethod
    def sanitize_identifier(cls, v):
        return sanitize_text(v, strip_tags=True)

class StudentVerifyRequest(BaseModel):
    user_id: Optional[int] = Field(1, ge=1)
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    edu_email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    student_number: str = Field(..., min_length=4, max_length=30, pattern=r"^[a-zA-Z0-9_-]+$")
    notes: Optional[str] = Field("", max_length=500)

    @field_validator("notes", "student_number", mode="before")
    @classmethod
    def sanitize_inputs(cls, v):
        return sanitize_text(v, strip_tags=True)

class StudentOtpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    student_number: Optional[str] = Field("", max_length=30, pattern=r"^[a-zA-Z0-9_-]*$")

    @field_validator("email", "student_number", mode="before")
    @classmethod
    def sanitize_inputs(cls, v):
        return sanitize_text(v, strip_tags=True)

class StudentOtpVerifyRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    user_id: Optional[int] = Field(1, ge=1)

    @field_validator("email", "otp_code", mode="before")
    @classmethod
    def sanitize_inputs(cls, v):
        return sanitize_text(v, strip_tags=True)

class DocumentScanRequest(BaseModel):
    user_id: Optional[int] = Field(1, ge=1)
    document_text: Optional[str] = Field(None, max_length=50000)
    sample_key: Optional[str] = Field(None, max_length=50)

class Init3DSRequest(BaseModel):
    user_id: Optional[int] = Field(1, ge=1)
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    card_holder: Optional[str] = Field("Öğrenci", max_length=100)
    card_number: str = Field(..., min_length=12, max_length=30)
    expire_month: Optional[str] = Field("12", max_length=4)
    expire_year: Optional[str] = Field("28", max_length=4)
    cvv: str = Field(..., min_length=3, max_length=4)
    amount_try: Optional[float] = Field(50.0, ge=1.0)

    @field_validator("card_holder", mode="before")
    @classmethod
    def sanitize_holder(cls, v):
        return sanitize_text(v, strip_tags=True)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v):
        clean = re.sub(r"[\s-]", "", v or "")
        if not clean.isdigit() or len(clean) < 12 or len(clean) > 19:
            raise ValueError("Geçersiz kredi kartı numarası: 12-19 haneli sayısal değer olmalıdır.")
        return clean

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v):
        clean = (v or "").strip()
        if not clean.isdigit() or len(clean) < 3 or len(clean) > 4:
            raise ValueError("Geçersiz CVV kodu: 3 veya 4 haneli sayısal değer olmalıdır.")
        return clean

class UnlockMembershipRequest(BaseModel):
    user_id: Optional[int] = Field(1, ge=1)
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    card_holder: Optional[str] = Field("Öğrenci", max_length=100)
    card_number: Optional[str] = Field("**** **** **** 4242", max_length=30)
    session_id: Optional[str] = Field(None, max_length=100)
    sms_code: Optional[str] = Field(None, max_length=20)

    @field_validator("card_holder", "card_number", "session_id", "sms_code", mode="before")
    @classmethod
    def sanitize_membership_inputs(cls, v):
        if v is None:
            return None
        return sanitize_text(v, strip_tags=True)

class GoogleAuthRequest(BaseModel):
    token: Optional[str] = Field(None, max_length=2000)
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    name: Optional[str] = Field(None, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=1000)

    @field_validator("email", "name", "full_name", mode="before")
    @classmethod
    def sanitize_auth_fields(cls, v):
        if v is None:
            return None
        return sanitize_text(str(v), strip_tags=True)

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")

    @field_validator("email", mode="before")
    @classmethod
    def sanitize_email(cls, v):
        return sanitize_text(str(v), strip_tags=True)

class ResetPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    reset_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    new_password: str = Field(..., min_length=6, max_length=128)

    @field_validator("email", "reset_code", mode="before")
    @classmethod
    def sanitize_reset_fields(cls, v):
        return sanitize_text(str(v), strip_tags=True)

@app.get("/api/config")
def public_config():
    """İstemcinin hangi akışları göstereceğini bilmesi için (gizli bilgi içermez)."""
    return {
        "demo_mode": DEMO_MODE,
        "google_client_id": GOOGLE_CLIENT_ID or None,
        "paytr_configured": is_paytr_live_configured(),
        "email_configured": email_configured(),
        # "Şifremi unuttum" yalnızca kod gerçekten e-postayla gidebiliyorsa gösterilir
        "password_reset_available": email_configured() or DEMO_MODE,
        "membership_price_try": MEMBERSHIP_PRICE_TRY,
    }

# --- Authentication & Student Verification Endpoints ---
@app.post("/api/auth/register")
def register_endpoint(req: RegisterRequest, request: Request, background_tasks: BackgroundTasks, _=Depends(rate_limit_register)):
    if not req.terms_accepted:
        raise HTTPException(status_code=400, detail="Kayıt için Kullanıcı Sözleşmesi'ni kabul etmeniz ve KVKK Aydınlatma Metni'ni okumanız gerekir.")
    try:
        user = create_user(
            email=req.email,
            username=req.username,
            password=req.password,
            full_name=req.full_name,
            university_id=req.university_id or "itu",
            student_number=req.student_number or "",
            terms_accepted=True,
            explicit_consent=bool(req.explicit_consent),
        )
        token, expires_in = create_session_token(user["id"], user["username"], user["email"])
        if email_configured() and user.get("email"):
            uni = next((u for u in universities_data if u["id"] == user.get("university_id")), None)
            background_tasks.add_task(
                send_welcome_email,
                user["email"],
                user.get("full_name") or user["username"],
                user["username"],
                uni["name"] if uni else (user.get("university_id") or "").upper(),
            )
        return {
            "status": "success",
            "user": user,
            "token": token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kayıt oluşturulamadı: {str(e)}")

@app.post("/api/auth/login")
def login_endpoint(req: LoginRequest, request: Request, _=Depends(rate_limit_login)):
    enforce_rate_limit(request, scope="login_account", max_requests=5, window_seconds=60, identifier=req.identifier)
    user = authenticate_user(req.identifier, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı/e-posta veya şifre.")
    uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
    user["university"] = uni
    token, expires_in = create_session_token(user["id"], user["username"], user["email"])
    return {
        "status": "success",
        "user": user,
        "token": token,
        "token_type": "Bearer",
        "expires_in": expires_in
    }

@app.post("/api/auth/google")
def google_auth_endpoint(req: GoogleAuthRequest, request: Request):
    enforce_rate_limit(request, scope="auth_google", max_requests=10, window_seconds=60, identifier=req.email)
    display_name = req.full_name or req.name or ""
    email = req.email

    if GOOGLE_CLIENT_ID:
        # Google ID token'ını Google'a doğrulat; e-posta istemciden değil token'dan alınır.
        if not req.token:
            raise HTTPException(status_code=401, detail="Google kimlik belirteci eksik.")
        try:
            r = httpx.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": req.token}, timeout=5)
        except httpx.HTTPError:
            raise HTTPException(status_code=503, detail="Google doğrulama servisine ulaşılamadı.")
        info = r.json() if r.status_code == 200 else {}
        if (
            info.get("aud") != GOOGLE_CLIENT_ID
            or info.get("iss") not in ("accounts.google.com", "https://accounts.google.com")
            or str(info.get("email_verified")).lower() != "true"
            or not info.get("email")
        ):
            raise HTTPException(status_code=401, detail="Google kimliği doğrulanamadı.")
        email = info["email"]
        display_name = info.get("name") or display_name
    else:
        # Gerçek Google girişi yapılandırılmadıysa simülasyon yalnızca geliştirmede açıktır.
        _require_demo("Google ile giriş")

    user = upsert_google_user(email=email, name=display_name, avatar_url=req.avatar_url or "")
    uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
    user["university"] = uni
    token, expires_in = create_session_token(user["id"], user["username"], user["email"])
    return {
        "status": "success",
        "access_token": token,
        "token": token,
        "token_type": "Bearer",
        "expires_in": expires_in,
        "user": user,
        "provider": "google"
    }

@app.post("/api/auth/forgot-password")
def forgot_password_endpoint(req: ForgotPasswordRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Kayıtlı bir hesap varsa 6 haneli kodu o hesabın e-postasına gönderir.
    Yanıt, hesap olsa da olmasa da AYNIDIR (e-posta adresinin kayıtlı olup olmadığı sızmaz)
    ve kod asla yanıtta dönmez (yalnızca DEMO_MODE hariç).
    """
    enforce_rate_limit(request, scope="auth_forgot_password", max_requests=5, window_seconds=60, identifier=req.email)
    if not email_configured() and not DEMO_MODE:
        raise HTTPException(status_code=503, detail="Şifre sıfırlama şu an kullanılamıyor. Lütfen yöneticiyle iletişime geçin.")

    # Her e-posta için 60 sn bekleme — hesap olsun olmasın aynı davranış
    email_key = "forgot_cooldown:" + req.email.lower().strip()
    allowed, _, retry_after = rate_limiter.is_allowed(email_key, 1, 60)
    if not allowed:
        raise HTTPException(status_code=429, detail=f"Lütfen yeni bir kod istemeden önce {retry_after} saniye bekleyin.",
                            headers={"Retry-After": str(retry_after)})

    generic = {
        "status": "success",
        "success": True,
        "message": "Bu e-posta adresiyle kayıtlı bir hesap varsa 6 haneli bir kod gönderildi. "
                   "Gelen kutunuzu ve gereksiz (spam) klasörünü kontrol edin.",
        "cooldown_seconds": 60,
        "expires_in_seconds": 900,
    }
    if not user_exists_with_email(req.email):
        return generic

    res = request_password_reset(email=req.email)
    if not res.get("success"):
        return generic
    if email_configured():
        # Arka planda gönder: yanıt süresi hesabın var olup olmadığını ele vermesin
        background_tasks.add_task(send_password_reset_email, res["email"], res["reset_code"])
    if DEMO_MODE:
        generic.update({k: res[k] for k in ("reset_code", "reset_code_sandbox", "demo_code") if k in res})
    return generic

@app.post("/api/auth/reset-password")
def reset_password_endpoint(req: ResetPasswordRequest, request: Request):
    enforce_rate_limit(request, scope="auth_reset_password", max_requests=10, window_seconds=60, identifier=req.email)
    res = confirm_password_reset(email=req.email, reset_code=req.reset_code, new_password=req.new_password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "Şifre sıfırlama başarısız."))
    return res

@app.get("/api/auth/me")
def current_user_endpoint(request: Request):
    token_user = require_current_user(request)
    target_id = token_user["user_id"]
    user = get_profile(target_id)
    uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
    user["university"] = uni
    user["authenticated_via"] = "bearer_token"
    return user

@app.post("/api/student/verify")
def student_verify_endpoint(req: StudentVerifyRequest, request: Request):
    token_user = require_current_user(request)
    res = verify_student(
        user_id=token_user["user_id"],
        university_id=req.university_id,
        edu_email=req.edu_email,
        student_number=req.student_number,
        doc_note=req.notes or ""
    )
    return res

@app.post("/api/student/request-otp")
def student_request_otp_endpoint(req: StudentOtpRequest, request: Request, background_tasks: BackgroundTasks,
                                 _=Depends(rate_limit_otp_request)):
    require_current_user(request)
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Geçerli bir e-posta adresi giriniz.")
    enforce_rate_limit(request, scope="otp_request_email", max_requests=3, window_seconds=60, identifier=req.email)
    if not email_configured() and not DEMO_MODE:
        raise HTTPException(status_code=503, detail="E-posta doğrulaması şu an kullanılamıyor.")
    # Kod yalnızca üniversite adreslerine gönderilir (rastgele adreslere e-posta atılamasın)
    if not DEMO_MODE and not req.email.lower().strip().endswith(".edu.tr"):
        raise HTTPException(status_code=400, detail="Lütfen .edu.tr uzantılı üniversite e-postanızı girin.")
    res = create_student_otp(email=req.email, student_number=req.student_number or "")
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "OTP kodu oluşturulamadı."))
    if email_configured() and res.get("otp_code"):
        background_tasks.add_task(send_student_otp_email, res["email"], res["otp_code"])
    return _hide_codes(res)

@app.post("/api/student/verify-otp")
def student_verify_otp_endpoint(req: StudentOtpVerifyRequest, request: Request, _=Depends(rate_limit_otp_verify)):
    if not req.email or not req.otp_code:
        raise HTTPException(status_code=400, detail="E-posta ve 6 haneli doğrulama kodunu eksiksiz giriniz.")
    enforce_rate_limit(request, scope="otp_verify_email", max_requests=5, window_seconds=60, identifier=req.email)
    token_user = require_current_user(request)
    res = verify_student_otp(email=req.email, otp_code=req.otp_code, user_id=token_user["user_id"])
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "Doğrulama başarısız."))
    return res


@app.get("/api/student/status")
def student_status_endpoint(request: Request):
    return get_verification_status(require_current_user(request)["user_id"])

@app.get("/api/student/sample-documents")
def get_sample_documents():
    return {
        k: {
            "key": k,
            "title": f"{k.upper()} E-Devlet Öğrenci Belgesi Örneği",
            "content": v.strip()
        } for k, v in SAMPLE_DOCUMENTS.items()
    }

async def _process_scanned_document(doc_text: str, filename: str, target_user_id: int):
    if not doc_text or len(doc_text.strip()) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Öğrenci belgesi metni okunamadı. Lütfen geçerli bir PDF yükleyin veya E-Devlet barkodlu metni yapıştırın."
        )

    scan_res = scan_student_document(doc_text, filename)
    if not scan_res.get("success"):
        raise HTTPException(
            status_code=400,
            detail=scan_res.get("error", "Öğrenci belgesinde tanınan bir üniversite tespit edilemedi.")
        )

    matched_uni = scan_res["matched_university_id"]
    db_res = verify_student_by_document(
        user_id=target_user_id,
        matched_uni_id=matched_uni,
        student_number=scan_res.get("student_number", ""),
        barcode=scan_res.get("document_barcode", ""),
        doc_snippet=scan_res.get("matched_snippet", "")
    )

    uni_obj = next((u for u in universities_data if u["id"] == matched_uni), None)

    return {
        "success": True,
        "matched_university_id": matched_uni,
        "matched_university_name": scan_res.get("matched_university_name", matched_uni),
        "university": uni_obj,
        "student_name": scan_res.get("student_name", ""),
        "faculty": scan_res.get("faculty", ""),
        "department": scan_res.get("department", ""),
        "student_number": scan_res.get("student_number", ""),
        "document_barcode": scan_res.get("document_barcode", ""),
        "is_active_student": scan_res.get("is_active_student", True),
        "confidence": scan_res.get("confidence", "high"),
        "verification_checks": scan_res.get("verification_checks", {}),
        "unlocked_universities": db_res.get("unlocked_universities", [matched_uni, "general"]),
        "message": scan_res.get("message", "Belgeniz başarıyla tarandı ve onaylandı.")
    }

@app.post("/api/student/scan-document")
async def scan_student_document_endpoint(req: DocumentScanRequest, request: Request):
    target_user_id = require_current_user(request)["user_id"]

    doc_text = ""
    filename = ""

    if req.sample_key:
        # Örnek belgeler herkese açık; bunlarla doğrulama yalnızca demoda yapılabilir.
        _require_demo("Örnek belge ile doğrulama")
    if req.sample_key and req.sample_key in SAMPLE_DOCUMENTS:
        doc_text = SAMPLE_DOCUMENTS[req.sample_key]
        filename = f"{req.sample_key}_edevlet.txt"
    elif req.document_text:
        doc_text = req.document_text
        filename = "uploaded_text.txt"

    return await _process_scanned_document(doc_text, filename, target_user_id)

@app.post("/api/student/upload-document")
async def upload_student_document_endpoint(
    request: Request,
    file: UploadFile = File(...),
):
    target_user_id = require_current_user(request)["user_id"]

    filename = file.filename or "belge.pdf"
    content = await file.read()
    doc_text = extract_text_from_bytes(content, filename)
    return await _process_scanned_document(doc_text, filename, target_user_id)

@app.post("/api/membership/3d-init")
def init_3ds_payment_endpoint(req: Init3DSRequest, request: Request):
    # Simüle 3D Secure: SMS'i banka değil sunucu üretiyor; gerçek ödeme PayTR iFrame ile alınır.
    _require_demo("Simüle 3D Secure ödeme")
    target_id = require_current_user(request)["user_id"]

    session_data = create_3ds_session(
        user_id=target_id,
        university_id=req.university_id,
        card_holder=req.card_holder or "Öğrenci",
        card_number=req.card_number,
        amount_try=MEMBERSHIP_PRICE_TRY
    )
    return _hide_codes(session_data)

@app.post("/api/membership/unlock")
def unlock_membership_endpoint(req: UnlockMembershipRequest, request: Request):
    # Canlıda üyelik YALNIZCA PayTR'nin imzalı bildirimiyle (/api/payment/paytr/callback) açılır.
    _require_demo("Simüle ödeme ile üyelik açma")
    target_id = require_current_user(request)["user_id"]

    # Ödeme oturumu olmadan kilit açılamaz (eskiden session_id gönderilmezse 3DS atlanıyordu).
    if not req.session_id or not req.sms_code:
        raise HTTPException(status_code=400, detail="3D Secure oturum kimliği ve SMS doğrulama kodu zorunludur.")
    verify_res = verify_3ds_code(req.session_id, req.sms_code)
    if not verify_res.get("success"):
        raise HTTPException(status_code=400, detail=verify_res.get("detail", "3D Secure SMS doğrulaması başarısız."))
    session_info = verify_res.get("session", {})
    # Oturum, bu kullanıcıya ve bu üniversiteye ait olmalı.
    if session_info.get("user_id") != target_id or session_info.get("university_id") != req.university_id:
        raise HTTPException(status_code=403, detail="Bu ödeme oturumu size veya bu üniversiteye ait değil.")
    card_holder = session_info.get("card_holder") or "Öğrenci"
    card_last_four = (session_info.get("card_number_masked") or "0000")[-4:]

    res = unlock_university_membership(
        user_id=target_id,
        university_id=req.university_id,
        card_holder=card_holder,
        card_last_four=card_last_four,
        price_try=MEMBERSHIP_PRICE_TRY,
        session_id=req.session_id
    )
    return res

@app.get("/api/membership/check")
def check_membership_endpoint(university_id: str, request: Request):
    has_access = _has_access(get_current_user_from_request(request), university_id)
    return {
        "university_id": university_id,
        "has_access": has_access,
        "price_try": 50.0,
        "requires_membership": not has_access
    }


class PayTRTokenRequest(BaseModel):
    university_id: str = Field(..., max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    # PayTR müşteri telefonu zorunlu tutuyor (dolandırıcılık kontrolü)
    user_phone: str = Field(..., min_length=10, max_length=20)
    # Ön Bilgilendirme + Mesafeli Satış Sözleşmesi + cayma hakkı istisnası onayı (Yönetmelik md. 7, 15/ğ)
    pre_info_accepted: bool = False

    @field_validator("user_phone")
    @classmethod
    def normalize_phone(cls, v):
        digits = re.sub(r"\D", "", v or "")
        if digits.startswith("90") and len(digits) == 12:
            digits = "0" + digits[2:]
        if len(digits) == 10 and digits.startswith("5"):
            digits = "0" + digits
        if not re.fullmatch(r"05\d{9}", digits):
            raise ValueError("Geçerli bir cep telefonu girin (05XX XXX XX XX).")
        return digits


def _payer_ip(request: Request) -> str:
    """PayTR gerçek müşteri IP'sini ister; güvenilir aracı kuralları get_client_ip'te."""
    return get_client_ip(request)


def _paytr_result_url(request: Request, outcome: str) -> str:
    base = str(request.base_url).rstrip("/")
    proto = (request.headers.get("X-Forwarded-Proto") or "").strip()
    if proto in ("http", "https") and base.startswith(("http://", "https://")):
        base = proto + "://" + base.split("://", 1)[1]
    return f"{base}/odeme-sonuc?durum={outcome}"


@app.post("/api/payment/paytr/token")
def create_paytr_token_endpoint(req: PayTRTokenRequest, request: Request):
    """
    PayTR iFrame ödemesini başlatır: bir 'pending' sipariş açar ve PayTR'den ödeme sayfası
    token'ı alır. Kart bilgisi hiçbir zaman bu sunucuya gelmez; PayTR'nin penceresinde girilir.
    Kilit burada AÇILMAZ — yalnızca PayTR'nin imzalı bildirimi (/callback) açar.
    """
    target_id = _current_user_id(request)
    if not req.pre_info_accepted:
        raise HTTPException(status_code=400, detail="Ödemeden önce Ön Bilgilendirme Formu ve Mesafeli Satış Sözleşmesi'ni onaylamanız gerekir.")
    if not is_paytr_live_configured():
        raise HTTPException(status_code=503, detail="Ödeme altyapısı henüz yapılandırılmadı.")
    if not any(u["id"] == req.university_id for u in universities_data) or req.university_id == "general":
        raise HTTPException(status_code=400, detail="Bilinmeyen üniversite.")
    if check_university_access(target_id, req.university_id):
        raise HTTPException(status_code=400, detail="Bu üniversitenin içeriği hesabınızda zaten açık.")

    profile = get_profile(target_id)
    email = (profile.get("email") or "").strip()
    if not email or not email.isascii():
        raise HTTPException(status_code=400, detail="Ödeme için hesabınızdaki e-posta adresi Türkçe karakter içermemeli.")

    res = generate_paytr_iframe_token(
        user_id=target_id,
        university_id=req.university_id,
        email=email,
        user_name=(profile.get("full_name") or profile.get("username") or "PrepKampus Ogrencisi")[:60],
        user_ip=_payer_ip(request),
        price_try=MEMBERSHIP_PRICE_TRY,
        user_phone=req.user_phone,
        ok_url=_paytr_result_url(request, "basarili"),
        fail_url=_paytr_result_url(request, "basarisiz"),
    )
    if res.get("status") != "success":
        raise HTTPException(status_code=400, detail=res.get("reason", "PayTR ödeme sayfası açılamadı."))
    create_paytr_order(res["merchant_oid"], target_id, req.university_id, int(round(MEMBERSHIP_PRICE_TRY * 100)))
    return {
        "merchant_oid": res["merchant_oid"],
        "iframe_url": res["iframe_url"],
        "amount_try": MEMBERSHIP_PRICE_TRY,
    }


@app.get("/api/payment/paytr/orders/{merchant_oid}")
def paytr_order_status_endpoint(merchant_oid: str, request: Request):
    """Web, ödeme penceresi açıkken bunu sorar; kilit açıldı mı burada görünür."""
    uid = _current_user_id(request)
    order = get_paytr_order(merchant_oid[:64])
    if not order or order["user_id"] != uid:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı.")
    profile = get_profile(uid)
    return {
        "merchant_oid": order["merchant_oid"],
        "university_id": order["university_id"],
        "status": order["status"],
        "unlocked_universities": profile.get("unlocked_universities", []),
    }


@app.post("/api/payment/paytr/callback")
async def paytr_webhook_callback_endpoint(request: Request):
    """
    PayTR Resmi Bildirim URL (Webhook Adım 2):
    PayTR sunucusundan gelen POST isteğini HMAC-SHA256 ile doğrular,
    ödemesi onaylanan üniversitenin kilidini açar ve 'OK' yanıtı döner.
    """
    form = await request.form()
    merchant_oid = str(form.get("merchant_oid", ""))
    status_val = str(form.get("status", ""))
    total_amount = str(form.get("total_amount", ""))
    received_hash = str(form.get("hash", ""))

    if not verify_paytr_callback_hash(merchant_oid, status_val, total_amount, received_hash):
        raise HTTPException(status_code=400, detail="PAYTR notification failed: bad hash")

    # Bildirim imzalı; artık PayTR'ye her durumda "OK" dönülür (aksi halde tekrar tekrar gönderir).
    order = get_paytr_order(merchant_oid)
    if not order:
        return PlainTextResponse("OK")  # bizim açmadığımız sipariş: hiçbir hesaba dokunma

    paid_kurus = int(total_amount) if total_amount.isdigit() else 0
    if status_val == "success":
        if paid_kurus < order["amount_kurus"]:
            finish_paytr_order(merchant_oid, "amount_mismatch", paid_kurus, "Ödenen tutar sipariş tutarından düşük")
        elif finish_paytr_order(merchant_oid, "success", paid_kurus):
            # Yalnızca 'pending' -> 'success' geçişini yapan bildirim kilidi açar (tekrarlar açmaz)
            unlock_university_membership(
                user_id=order["user_id"],
                university_id=order["university_id"],
                card_holder="PayTR Sanal POS",
                card_last_four="PAYT",
                price_try=paid_kurus / 100.0,
                session_id=merchant_oid,
            )
    else:
        reason = f'{form.get("failed_reason_code", "")} {form.get("failed_reason_msg", "")}'.strip()
        finish_paytr_order(merchant_oid, "failed", paid_kurus, reason)

    return PlainTextResponse("OK")



# --- API Routes ---
@app.get("/api/universities")
def get_universities():
    return universities_data

@app.get("/api/universities/{uni_id}")
def get_university_by_id(uni_id: str):
    for u in universities_data:
        if u["id"] == uni_id:
            return u
    raise HTTPException(status_code=404, detail="University not found")

@app.get("/api/profile")
def get_user_profile(request: Request):
    profile = get_profile(_current_user_id(request))
    # attach university details
    uni = next((u for u in universities_data if u["id"] == profile.get("university_id")), universities_data[0])
    profile["university"] = uni
    return profile

@app.post("/api/profile")
def update_user_profile(req: ProfileUpdateRequest, request: Request):
    uid = _current_user_id(request)
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    if req.current_level.upper() not in valid_levels:
        raise HTTPException(status_code=400, detail="Invalid level. Must be one of: A1, A2, B1, B2, C1, C2")
    if not any(u["id"] == req.university_id for u in universities_data):
        raise HTTPException(status_code=400, detail="Bilinmeyen üniversite.")
    return update_profile(uid, req.university_id, req.current_level.upper(), req.target_score or 65)

@app.get("/api/questions")
def get_questions(
    request: Request,
    university_id: Optional[str] = None,
    level: Optional[str] = None,
    category: Optional[str] = None,
    strict_uni: bool = False,
):
    token_user = get_current_user_from_request(request)
    if university_id and university_id not in ["all", "general"]:
        if not _has_access(token_user, university_id):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "membership_required",
                    "message": f"{university_id.upper()} hazırlık sorularını çözmek için 50 TL üyelik gereklidir.",
                    "university_id": university_id,
                    "price_try": 50.0
                }
            )

    filtered = questions_data
    if university_id and university_id != "all":
        if strict_uni or university_id == "general":
            filtered = [q for q in filtered if q["university_id"] == university_id]
        else:
            # Üniversiteye özel sorular en başta, ardından genel havuz
            uni_only = [q for q in filtered if q["university_id"] == university_id]
            gen_only = [q for q in filtered if q["university_id"] == "general"]
            filtered = uni_only + gen_only
    else:
        # "all" eskiden kilitli üniversitelerin sorularını da döndürüyordu.
        filtered = [q for q in filtered if _has_access(token_user, q["university_id"])]
    if level and level != "all":
        filtered = [q for q in filtered if q["level"].upper() == level.upper()]
    if category and category != "all":
        filtered = [q for q in filtered if q.get("category", "").lower() == category.lower()]
    return filtered

@app.get("/api/vocabulary")
def get_vocabulary(
    request: Request,
    level: Optional[str] = None,
    search: Optional[str] = None
):
    token_user = get_current_user_from_request(request)
    progress = get_vocab_progress(token_user["user_id"]) if token_user else {}
    result = []
    clean_search = sanitize_text(search, strip_tags=True, max_length=100) if search else None
    for item in vocabulary_data:
        entry = dict(item)
        entry["status"] = progress.get(item["id"], "unreviewed")
        if level and level != "all" and item["level"].upper() != level.upper():
            continue
        if clean_search:
            query = clean_search.lower()
            if (query not in item["word"].lower() and 
                query not in item["meaning_tr"].lower() and 
                query not in item["definition_en"].lower()):
                continue
        result.append(entry)
    return result

@app.post("/api/vocabulary/{word_id}/status")
def update_word_status(word_id: str, req: VocabStatusRequest, request: Request):
    uid = _current_user_id(request)
    _record_study(request)
    if req.status not in ["mastered", "learning", "unreviewed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    set_vocab_status(uid, word_id[:100], req.status)
    return {"status": "ok", "word_id": word_id, "new_status": req.status}

@app.get("/api/writing-guides")
def get_writing_guides(level: Optional[str] = None):
    if level and level != "all":
        lvl_upper = level.upper()
        matched = [g for g in writing_guides_data if g.get("level", "").upper() == lvl_upper]
        if matched:
            return matched
        if lvl_upper == "A1":
            return [g for g in writing_guides_data if g.get("level", "").upper() == "A2"]
    return writing_guides_data

@app.get("/api/listening")
def get_listening_list(
    request: Request,
    university_id: Optional[str] = None,
    level: Optional[str] = None,
    type: Optional[str] = None,
    strict_uni: bool = False,
):
    results = listening_data
    if university_id and university_id != "all":
        if strict_uni or university_id == "general":
            results = [item for item in results if item.get("university_id") == university_id]
        else:
            uni_only = [item for item in results if item.get("university_id") == university_id]
            gen_only = [item for item in results if item.get("university_id") == "general"]
            results = uni_only + gen_only
    if type and type != "all":
        results = [item for item in results if item.get("type") == type]
    if level and level != "all":
        lvl_upper = level.upper()
        lvl_matches = [item for item in results if item.get("level", "").upper() == lvl_upper]
        if lvl_matches:
            results = lvl_matches
        elif lvl_upper == "A1":
            a2_matches = [item for item in results if item.get("level", "").upper() == "A2"]
            if a2_matches:
                results = a2_matches
    # Kilitli üniversitelerin dinleme sınavları yalnız erişimi olanlara (eskiden herkese açıktı)
    return _filter_accessible(get_current_user_from_request(request), results)

@app.get("/api/listening/{item_id}")
def get_listening_detail(item_id: str, request: Request):
    for item in listening_data:
        if item["id"] == item_id:
            _require_item_access(request, item)
            return item
    raise HTTPException(status_code=404, detail="Listening item not found")

class ListeningAnswerRequest(BaseModel):
    question_id: str = Field(..., max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    chosen_answer: str = Field(..., max_length=5, pattern=r"^[A-Ea-e]$")


@app.post("/api/listening/answer")
def listening_answer_endpoint(req: ListeningAnswerRequest, request: Request):
    """
    Dinlemede verilen tek bir cevabı işler: yanlışsa Hata Kasası'na yazar, doğruysa kasadan düşer.
    Eskiden bu iş /api/exam/submit'e gönderiliyordu; dinleme soruları orada tanınmadığı için
    yanlış kasaya hiç düşmüyor, üstüne %0'lık sahte bir deneme kaydı açılıyordu.
    """
    uid = _current_user_id(request)
    q = _listening_question_map().get(req.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Dinleme sorusu bulunamadı.")
    _record_study(request)
    chosen = req.chosen_answer.upper()
    is_correct = chosen == q["correct_answer"]
    if is_correct:
        resolve_mistake(uid, q["id"])
    else:
        record_mistake(
            user_id=uid,
            question_id=q["id"],
            university_id=q["university_id"],
            level=q["level"],
            category="Listening",
            wrong_answer=chosen,
        )
    return {"question_id": q["id"], "is_correct": is_correct, "correct_answer": q["correct_answer"]}


@app.post("/api/writing/evaluate")
def evaluate_essay_endpoint(req: EssayEvaluateRequest, request: Request, _=Depends(rate_limit_ai_writing)):
    _record_study(request)
    import re
    text = req.essay.strip()
    words = re.findall(r"\b[A-Za-z0-9'-]+\b", text)
    word_count = len(words)
    
    if word_count < 30:
        return {
            "overall_score": 25,
            "estimated_cefr": "A1/A2",
            "word_count": word_count,
            "paragraph_count": 1,
            "is_passing": False,
            "task_achievement_score": 8,
            "coherence_cohesion_score": 6,
            "lexical_resource_score": 6,
            "grammatical_range_score": 5,
            "feedback_summary_tr": "Yazılan metin üniversite sınavı için çok kısa. En az 200-250 kelimelik bir akademik kompozisyon gereklidir.",
            "strengths_tr": ["Denemeye başlanmış olması."],
            "improvements_tr": [
                "Giriş, en az 2 gelişme ve 1 sonuç paragrafı oluşturun.",
                "Kelime sayısını en az 250 seviyesine çıkarın.",
                "Fikirlerinizi 'For example', 'Consequently' gibi bağlaçlarla destekleyin."
            ],
            "detected_transitions": [],
            "detected_academic_words": [],
            "informal_words_found": []
        }
        
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    para_count = len(paragraphs)
    
    # 1. Task Achievement (max 25)
    # Target: 250-400 words, at least 3-4 paragraphs, clear intro/conclusion
    ta_score = 0
    if word_count >= 250:
        ta_score += 15
    elif word_count >= 180:
        ta_score += 10
    elif word_count >= 120:
        ta_score += 6
    else:
        ta_score += 3
        
    if para_count in [3, 4, 5]:
        ta_score += 7
    elif para_count >= 2:
        ta_score += 4
    else:
        ta_score += 2
        
    # Check intro stance markers
    first_para = paragraphs[0].lower() if paragraphs else ""
    has_thesis = any(phrase in first_para for phrase in ["in my opinion", "this essay will", "i believe", "in my view", "it is argued", "firstly", "two main"])
    if has_thesis:
        ta_score += 3
    ta_score = min(25, max(5, ta_score))
    
    # 2. Coherence & Cohesion (max 25)
    transitions_catalog = [
        "furthermore", "moreover", "in addition", "additionally", "consequently",
        "as a result", "therefore", "thus", "on the other hand", "in contrast",
        "nevertheless", "nonetheless", "firstly", "secondly", "thirdly",
        "for instance", "for example", "to illustrate", "in conclusion", "to sum up",
        "in particular", "specifically", "subsequently", "despite", "although"
    ]
    text_lower = text.lower()
    found_transitions = [t for t in transitions_catalog if t in text_lower]
    cc_score = min(25, max(6, len(found_transitions) * 3 + (5 if para_count >= 3 else 0)))
    
    # 3. Lexical Resource (max 25)
    academic_keywords = [
        "significant", "significantly", "demonstrate", "illustrate", "crucial",
        "essential", "fundamental", "mitigate", "phenomenon", "consequence",
        "substantial", "implement", "perspective", "evident", "facilitate",
        "comprehensive", "implication", "predominant", "indicate", "perception",
        "correlation", "diminish", "enhance", "advocate", "prevalent", "framework",
        "infrastructure", "inevitable", "profound", "diversity", "sustainable"
    ]
    found_academic = [w for w in academic_keywords if w in text_lower]
    
    informal_keywords = ["a lot of", "lots of", "gonna", "wanna", "kids", "stuff", "thing", "really good", "bad", "huge"]
    found_informal = [w for w in informal_keywords if w in text_lower]
    
    lex_score = min(25, max(6, 8 + len(found_academic) * 2 - len(found_informal) * 2))
    
    # 4. Grammatical Range & Accuracy (max 25)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    avg_sentence_len = round(word_count / max(len(sentences), 1), 1)
    
    complex_connectors = ["although", "whereas", "while", "even though", "since", "unless", "provided that", "because"]
    found_complex = sum(1 for c in complex_connectors if c in text_lower)
    
    # Passive indicators
    passive_markers = ["is considered", "are considered", "was found", "were found", "has been", "have been", "is believed", "can be seen", "be implemented"]
    has_passive = sum(1 for p in passive_markers if p in text_lower)
    
    grammar_score = 10
    if 12 <= avg_sentence_len <= 26:
        grammar_score += 6
    if found_complex >= 2:
        grammar_score += 5
    if has_passive >= 1:
        grammar_score += 4
    grammar_score = min(25, max(6, grammar_score))
    
    overall = ta_score + cc_score + lex_score + grammar_score
    
    if overall >= 85:
        cefr = "C1 (Mastery)"
    elif overall >= 70:
        cefr = "B2 (Vantage - Hazırlık Muafiyet Barajı)"
    elif overall >= 55:
        cefr = "B1 (Threshold)"
    else:
        cefr = "A2 (Elementary)"
        
    is_passing = overall >= 65
    
    strengths = []
    if ta_score >= 18:
        strengths.append(f"Gelişmiş kelime hacmi ({word_count} kelime) ve net kompozisyon yapısı.")
    if found_transitions:
        strengths.append(f"Geçiş bağlaçlarının zengin kullanımı ({', '.join(found_transitions[:4])} vb.).")
    if found_academic:
        strengths.append(f"Akademik kelime dağarcığı kullanımı ({', '.join(found_academic[:4])}).")
    if found_complex >= 2:
        strengths.append("Bileşik ve karmaşık cümle yapıları (complex sentence structures).")
    if not strengths:
        strengths.append("Temel fikir akışı sağlanmış.")
        
    improvements = []
    if word_count < 220:
        improvements.append(f"Kelime sayısı hedefin altında ({word_count}/250). Argümanlarınızı örnek ve nedenlerle genişletin.")
    if para_count < 4:
        improvements.append("Paragraf ayrımını belirginleştirin (Giriş, 2 Gelişme, 1 Sonuç).")
    if not has_thesis:
        improvements.append("Giriş paragrafının sonuna açık bir Tez Cümlesi (Thesis Statement) ekleyin.")
    if len(found_transitions) < 4:
        improvements.append("Paragraflar ve fikirler arasında 'Furthermore', 'Consequently', 'On the contrary' gibi akademik bağlaçlar kullanın.")
    if found_informal:
        improvements.append(f"Resmi olmayan ifadelerden kaçının ({', '.join(found_informal)} yerine akademik alternatifler seçin).")
    if not improvements:
        improvements.append("Zaman kiplerini ve özne-yüklem uyumunu (subject-verb agreement) kontrol ederek C2 düzeyine yaklaşabilirsiniz.")
        
    return {
        "overall_score": overall,
        "estimated_cefr": cefr,
        "is_passing": is_passing,
        "word_count": word_count,
        "paragraph_count": para_count,
        "avg_sentence_length": avg_sentence_len,
        "task_achievement_score": ta_score,
        "coherence_cohesion_score": cc_score,
        "lexical_resource_score": lex_score,
        "grammatical_range_score": grammar_score,
        "detected_transitions": found_transitions,
        "detected_academic_words": found_academic,
        "informal_words_found": found_informal,
        "strengths_tr": strengths,
        "improvements_tr": improvements
    }

@app.post("/api/exam/submit")
def submit_exam(req: ExamSubmitRequest, request: Request):
    uid = _current_user_id(request)
    _record_study(request)
    q_map = _all_question_map()
    correct_count = 0
    results_detail = []
    category_times = {} # category -> list of seconds
    
    question_times = req.question_times or {}
    answers = {k: v for k, v in req.answers.items() if v}

    # Puanın paydası: gösterilen sorular (verildiyse), yoksa cevaplananlar.
    presented = [qid for qid in (req.question_ids or list(answers.keys())) if qid in q_map]
    presented = list(dict.fromkeys(presented + [qid for qid in answers if qid in q_map]))
    if not presented:
        # Tanınan soru yoksa (ör. dinleme soruları) sahte bir %0 deneme kaydı açma.
        raise HTTPException(status_code=400, detail="Gönderilen cevaplar tanınan bir soruya ait değil.")

    for q_id in presented:
        q = q_map[q_id]
        chosen_key = answers.get(q_id)

        is_correct = (chosen_key == q["correct_answer"])
        time_spent = question_times.get(q_id, 0)
        category = q.get("category", "General")
        
        if category not in category_times:
            category_times[category] = []
        if time_spent > 0:
            category_times[category].append(time_spent)
            
        if is_correct:
            correct_count += 1
            # If resolved in mistake practice or regular test
            resolve_mistake(uid, q_id)
        elif chosen_key:
            # Save into mistake vault (boş bırakılan soru kasaya yazılmaz, ama yanlış sayılır)
            record_mistake(
                user_id=uid,
                question_id=q_id,
                university_id=q.get("university_id", req.university_id),
                level=q.get("level", req.level),
                category=category,
                wrong_answer=chosen_key
            )
            
        results_detail.append({
            "question_id": q_id,
            "category": category,
            "level": q.get("level", req.level),
            "question_text": q["question"],
            "chosen_answer": chosen_key,
            "correct_answer": q["correct_answer"],
            "is_correct": is_correct,
            "time_spent": time_spent,
            "explanation_tr": q.get("explanation_tr", ""),
            "options": q["options"]
        })
    
    total_answered = len(presented)
    score_percentage = round((correct_count / max(total_answered, 1)) * 100, 1)
    avg_time = round(req.duration_seconds / max(total_answered, 1), 1) if total_answered > 0 else 0
    
    # Calculate category time summary
    cat_summary = {}
    for cat, times in category_times.items():
        if times:
            cat_summary[cat] = {
                "avg_seconds": round(sum(times) / len(times), 1),
                "total_seconds": sum(times),
                "question_count": len(times)
            }
            
    # Find slowest and fastest questions
    timed_questions = [(q["question_id"], q["time_spent"]) for q in results_detail if q["time_spent"] > 0]
    slowest_q = max(timed_questions, key=lambda x: x[1]) if timed_questions else None
    fastest_q = min(timed_questions, key=lambda x: x[1]) if timed_questions else None
    time_traps = [q for q in results_detail if q["time_spent"] >= 90]
    
    attempt_id = save_exam_attempt(
        user_id=uid,
        university_id=req.university_id,
        level=req.level,
        score=score_percentage,
        total_questions=total_answered,
        correct_count=correct_count,
        duration_seconds=req.duration_seconds,
        answers=req.answers
    )
    
    return {
        "attempt_id": attempt_id,
        "score": score_percentage,
        "total_questions": total_answered,
        "correct_count": correct_count,
        "wrong_count": total_answered - correct_count,
        "duration_seconds": req.duration_seconds,
        "time_analytics": {
            "avg_time_per_question": avg_time,
            "category_summary": cat_summary,
            "slowest_question": {"id": slowest_q[0], "seconds": slowest_q[1]} if slowest_q else None,
            "fastest_question": {"id": fastest_q[0], "seconds": fastest_q[1]} if fastest_q else None,
            "time_traps_count": len(time_traps)
        },
        "details": results_detail
    }

# --- Mistake Vault Endpoints ---
@app.get("/api/mistakes")
def get_mistake_vault(request: Request, is_resolved: bool = False):
    mistakes = get_mistakes(_current_user_id(request), is_resolved=is_resolved)
    q_map = _all_question_map()
    
    enriched = []
    for m in mistakes:
        q = q_map.get(m["question_id"])
        if q:
            item = dict(m)
            item["question_details"] = q
            enriched.append(item)
    return enriched

@app.post("/api/mistakes/{question_id}/resolve")
def resolve_mistake_endpoint(question_id: str, request: Request):
    resolve_mistake(_current_user_id(request), question_id)
    return {"status": "ok", "question_id": question_id}

class PracticeAnswerRequest(BaseModel):
    question_id: str = Field(..., max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    chosen_answer: str = Field(..., max_length=5, pattern=r"^[A-Ea-e]$")

@app.post("/api/practice/answer")
def practice_answer_endpoint(req: PracticeAnswerRequest, request: Request):
    """
    Kur alıştırmalarında verilen tekil cevabı işler:
    Yanlışsa Hata Defterine (Mistake Vault) kaydeder, doğruysa kasadan çözer.
    """
    uid = _current_user_id(request)
    q = _all_question_map().get(req.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Alıştırma sorusu bulunamadı.")
    _record_study(request)
    chosen = req.chosen_answer.upper()
    is_correct = chosen == q["correct_answer"]
    if is_correct:
        resolve_mistake(uid, q["id"])
    else:
        record_mistake(
            user_id=uid,
            question_id=q["id"],
            university_id=q.get("university_id", "general"),
            level=q.get("level", "B2"),
            category=q.get("category", "Grammar"),
            wrong_answer=chosen,
        )
    return {"question_id": q["id"], "is_correct": is_correct, "correct_answer": q["correct_answer"]}

@app.delete("/api/mistakes/{question_id}")
def delete_mistake_endpoint(question_id: str, request: Request):
    delete_mistake(_current_user_id(request), question_id)
    return {"status": "ok", "question_id": question_id}

@app.get("/api/exam/history")
def exam_history(request: Request):
    return get_exam_history(_current_user_id(request))

@app.get("/api/stats")
def get_overall_stats(request: Request):
    uid = _current_user_id(request)
    profile = get_profile(uid)
    history = get_exam_history(uid, limit=50)
    vocab_progress = get_vocab_progress(uid)
    unresolved_mistakes = get_mistake_count(uid)
    
    mastered_vocab = sum(1 for status in vocab_progress.values() if status == "mastered")
    total_vocab = len(vocabulary_data)
    
    total_exams = len(history)
    avg_score = round(sum(h["score"] for h in history) / total_exams, 1) if total_exams > 0 else 0
    
    return {
        "profile": profile,
        "mastered_vocab": mastered_vocab,
        "total_vocab": total_vocab,
        "unresolved_mistakes": unresolved_mistakes,
        "total_exams_taken": total_exams,
        "average_exam_score": avg_score,
        "recent_exams": history[:5]
    }

@app.get("/api/speaking")
def get_speaking_tasks(
    request: Request,
    university_id: Optional[str] = None,
    level: Optional[str] = None,
    strict_uni: bool = False,
):
    results = speaking_data
    if university_id and university_id != "all":
        if strict_uni or university_id == "general":
            results = [t for t in results if t.get("university_id") == university_id]
        else:
            uni_only = [t for t in results if t.get("university_id") == university_id]
            gen_only = [t for t in results if t.get("university_id") == "general"]
            results = uni_only + gen_only
    if level and level != "all":
        lvl_upper = level.upper()
        lvl_matches = [t for t in results if t.get("level", "").upper() == lvl_upper]
        if lvl_matches:
            results = lvl_matches
        elif lvl_upper == "A1":
            a2_matches = [t for t in results if t.get("level", "").upper() == "A2"]
            if a2_matches:
                results = a2_matches
    return _filter_accessible(get_current_user_from_request(request), results)

@app.get("/api/speaking/{task_id}")
def get_speaking_task(task_id: str, request: Request):
    task = next((t for t in speaking_data if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Speaking task not found")
    _require_item_access(request, task)
    return task

@app.post("/api/speaking/evaluate")
def evaluate_speaking(req: SpeakingEvaluateRequest, request: Request, _=Depends(rate_limit_ai_speaking)):
    _record_study(request)
    text = (req.transcript or "").strip()
    words = re.findall(r"\b[A-Za-z']+\b", text)
    word_count = len(words)
    duration = max(req.duration_seconds or 60, 15)
    wpm = round((word_count / duration) * 60, 1)

    task = next((t for t in speaking_data if t["id"] == req.task_id), None)
    text_lower = text.lower()

    # 1. Fluency & Speaking Rate (max 25)
    # Target rate: 110 - 150 words per minute for academic fluency
    if 100 <= wpm <= 160:
        fluency_score = 23
    elif 80 <= wpm < 100 or 160 < wpm <= 180:
        fluency_score = 19
    elif 50 <= wpm < 80:
        fluency_score = 14
    else:
        fluency_score = max(6, min(10, int(wpm / 10)))

    # 2. Lexical Resource / Academic Vocabulary (max 25)
    academic_keywords = [
        "fundamental", "significant", "mitigate", "consequently", "furthermore",
        "paradigm", "infrastructure", "mobility", "autonomy", "subsidize",
        "intermittency", "biodiversity", "unprecedented", "catalyze", "proliferation",
        "perspective", "crucial", "sustainable", "inevitably", "comprehensive"
    ]
    detected_academic = [w for w in academic_keywords if w in text_lower]
    if task and "key_vocabulary" in task:
        for kw in task["key_vocabulary"]:
            if kw.lower() in text_lower and kw.lower() not in detected_academic:
                detected_academic.append(kw.lower())

    lexical_score = min(25, max(8, 10 + len(detected_academic) * 3))

    # 3. Grammatical Range & Structure (max 25)
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 3]
    connectors = ["although", "because", "while", "furthermore", "however", "therefore", "in addition", "for instance", "as a result"]
    detected_connectors = [c for c in connectors if c in text_lower]
    grammar_score = min(25, max(8, 10 + len(detected_connectors) * 3 + (4 if len(sentences) >= 3 else 0)))

    # 4. Task Achievement & Guiding Questions (max 25)
    guiding_hits = 0
    if task and "guiding_questions" in task:
        for gq in task["guiding_questions"]:
            gq_keywords = [w.lower() for w in re.findall(r"\b[A-Za-z]{4,}\b", gq)]
            hits = sum(1 for kw in gq_keywords if kw in text_lower)
            if hits >= 2:
                guiding_hits += 1
    task_score = min(25, max(8, 12 + guiding_hits * 4 + (5 if word_count >= 80 else 0)))

    overall = fluency_score + lexical_score + grammar_score + task_score

    if overall >= 85:
        cefr = "C1 (Advanced Fluency)"
    elif overall >= 70:
        cefr = "B2 (Vantage - Muafiyet Yeterli)"
    elif overall >= 55:
        cefr = "B1 (Independent)"
    else:
        cefr = "A2 (Developing)"

    strengths = []
    improvements = []

    if fluency_score >= 20:
        strengths.append(f"Akıcı konuşma temposu ({wpm} kelime/dk) sınav standartlarına çok uygun.")
    else:
        improvements.append(f"Konuşma temponuz {wpm} kelime/dk. Hazırlık sınavlarında ideal tempo 110-150 kelime/dk aralığıdır.")

    if len(detected_academic) >= 3:
        strengths.append(f"Akademik kelime kullanımı zengin ({', '.join(detected_academic[:4])}).")
    else:
        improvements.append("Konuşmanızda daha fazla akademik bağlaç ve konu ile ilgili terim (AWL) kullanmaya özen gösterin.")

    if len(detected_connectors) >= 2:
        strengths.append("Fikir geçişleri bağlaçlarla desteklenmiş.")
    else:
        improvements.append("Cümlelerinizi 'Furthermore', 'Consequently', 'On the other hand' gibi bağlaçlarla bağlayın.")

    return {
        "word_count": word_count,
        "speaking_rate_wpm": wpm,
        "overall_score": overall,
        "cefr_level": cefr,
        "is_passing": overall >= 65,
        "scores": {
            "fluency_and_coherence": fluency_score,
            "lexical_resource": lexical_score,
            "grammatical_range": grammar_score,
            "task_achievement": task_score
        },
        "detected_academic_words": detected_academic,
        "detected_transitions": detected_connectors,
        "strengths_tr": strengths,
        "improvements_tr": improvements,
        "model_transcript": task.get("model_answer_transcript") if task else ""
    }

# --- Cloud Sync Endpoints (Web-Mobile Two-Way Sync) ---
@app.get("/api/sync/pull")
def sync_pull(request: Request):
    """Öğrencinin sunucudaki güncel hâli; web ve mobil aynı veriyi buradan alır."""
    uid = _current_user_id(request)
    profile = get_profile(uid)
    mistakes = get_mistakes(uid)
    vocab_progress = get_vocab_progress(uid)
    exam_history = get_exam_history(uid, limit=100)
    
    return {
        "profile": profile,
        "mistakes": mistakes,
        "vocab_progress": vocab_progress,
        "exam_history": exam_history,
        "server_timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/sync/push")
def sync_push(req: SyncPushRequest, request: Request):
    """
    Mobilin çevrimdışı giden kutusunu uygular. Sıra önemli: önce yeni yanlışlar,
    sonra çözülenler (aynı soru çevrimdışıyken önce yanlış sonra doğru yapıldıysa çözülmüş kalır).
    """
    uid = _current_user_id(request)
    updates = {"profile_updated": False, "mistakes_synced": 0, "mistakes_resolved": 0,
               "vocab_synced": 0, "exams_saved": 0}

    if req.profile:
        current = get_profile(uid)
        uni = str(req.profile.get("university_id") or current.get("university_id") or "itu")
        if not any(u["id"] == uni for u in universities_data):
            uni = current.get("university_id") or "itu"
        level = str(req.profile.get("current_level") or current.get("current_level") or "B2").upper()
        if level not in ("A1", "A2", "B1", "B2", "C1", "C2"):
            level = current.get("current_level") or "B2"
        try:
            target = int(req.profile.get("target_score") or current.get("target_score") or 65)
        except (TypeError, ValueError):
            target = 65
        update_profile(uid, uni, level, max(0, min(100, target)))
        updates["profile_updated"] = True

    # Telefonda çevrimdışı çalışıldıysa bugün seriye işlensin
    if req.mistakes or req.resolved_mistakes or req.vocab_progress or req.exam_attempts:
        record_study_day(uid)

    if req.mistakes:
        updates["mistakes_synced"] = bulk_upsert_mistakes(uid, req.mistakes)

    if req.resolved_mistakes:
        updates["mistakes_resolved"] = bulk_resolve_mistakes(uid, req.resolved_mistakes)

    if req.vocab_progress:
        updates["vocab_synced"] = bulk_upsert_vocab_progress(uid, req.vocab_progress)

    if req.exam_attempts:
        for ea in req.exam_attempts:
            save_exam_attempt(
                user_id=uid,
                university_id=str(ea.get("university_id", "itu"))[:50],
                level=str(ea.get("level", "B2"))[:10],
                score=max(0.0, min(100.0, float(ea.get("score") or 0))),
                total_questions=max(0, int(ea.get("total_questions") or 0)),
                correct_count=max(0, int(ea.get("correct_count") or 0)),
                duration_seconds=max(0, int(ea.get("duration_seconds") or 0)),
                answers=ea.get("answers") if isinstance(ea.get("answers"), dict) else {},
                created_at=str(ea["created_at"])[:19].replace("T", " ") if ea.get("created_at") else None,
            )
            updates["exams_saved"] += 1
            
    return {"status": "success", "synced": updates, "timestamp": datetime.utcnow().isoformat()}

# --- Mock Exam Mode (Full University Trial Exam) ---
@app.get("/api/exam/mock/{university_id}")
def generate_mock_exam(university_id: str, request: Request, level: Optional[str] = None):
    if not _has_access(get_current_user_from_request(request), university_id):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "membership_required",
                "message": f"{university_id.upper()} hazırlık sınavları kilitlidir. Bu üniversitenin denemelerini çözmek için 50 TL üyelik gereklidir.",
                "university_id": university_id,
                "price_try": 50.0
            }
        )

    uni = next((u for u in universities_data if u["id"] == university_id), universities_data[0])
    target_level = (level or "B2").upper()

    # 1. Select questions strictly from THIS university's 180-question pool (30 per level)
    uni_all_questions = [q for q in questions_data if q.get("university_id") == university_id]
    uni_exact_level = [q for q in uni_all_questions if q.get("level", "").upper() == target_level]

    adjacent_order = {
        "A1": ["A2", "B1", "B2", "C1", "C2"],
        "A2": ["A1", "B1", "B2", "C1", "C2"],
        "B1": ["B2", "A2", "C1", "A1", "C2"],
        "B2": ["B1", "C1", "A2", "C2", "A1"],
        "C1": ["B2", "C2", "B1", "A2", "A1"],
        "C2": ["C1", "B2", "B1", "A2", "A1"]
    }
    uni_adj_questions = []
    for adj_lvl in adjacent_order.get(target_level, ["B1", "C1"]):
        uni_adj_questions.extend([q for q in uni_all_questions if q.get("level", "").upper() == adj_lvl])

    random.shuffle(uni_exact_level)
    random.shuffle(uni_adj_questions)
    combined_uni = uni_exact_level + uni_adj_questions

    if len(combined_uni) < 30:
        gen_supp = [q for q in questions_data if q.get("university_id") == "general" and q.get("level", "").upper() == target_level]
        random.shuffle(gen_supp)
        combined_uni.extend(gen_supp)

    final_questions = combined_uni[:30]

    # 2. Select matching listening track for THIS university and target_level
    lis_track = next((lt for lt in listening_data if lt.get("university_id") == university_id and lt.get("level", "").upper() == target_level), None)
    if not lis_track:
        lis_track = next((lt for lt in listening_data if lt.get("university_id") == university_id), None)
    if not lis_track:
        lis_track = next((lt for lt in listening_data if lt.get("level", "").upper() == target_level), listening_data[0] if listening_data else None)

    # 3. Select matching essay prompt for target_level
    essay_guide = next((wg for wg in writing_guides_data if wg.get("level", "").upper() == target_level), None)
    if not essay_guide and target_level == "A1":
        essay_guide = next((wg for wg in writing_guides_data if wg.get("level", "").upper() == "A2"), None)
    if not essay_guide:
        essay_guide = writing_guides_data[0] if writing_guides_data else None

    # 4. Select matching speaking prompt for THIS university and target_level
    spk_task = next((st for st in speaking_data if st.get("university_id") == university_id and st.get("level", "").upper() == target_level), None)
    if not spk_task:
        spk_task = next((st for st in speaking_data if st.get("university_id") == university_id), None)
    if not spk_task:
        spk_task = next((st for st in speaking_data if st.get("level", "").upper() == target_level), speaking_data[0] if speaking_data else None)

    return {
        "university": uni,
        "level": target_level,
        "exam_title": f"{uni.get('name')} ({uni.get('exam_name')}) • {target_level} Deneme Sınavı",
        "duration_minutes": uni.get("duration_minutes", 120),
        "passing_score": uni.get("passing_score", 60),
        "sections": {
            "multiple_choice": final_questions,
            "listening": lis_track,
            "writing_prompt": essay_guide,
            "speaking_prompt": spk_task
        }
    }

# --- Student Summary Report Card (PDF/Print View) ---
@app.get("/api/report/summary")
def get_student_report_summary(request: Request):
    uid = _current_user_id(request)
    profile = get_profile(uid)
    history = get_exam_history(uid, limit=50)
    mistakes = get_mistakes(uid, is_resolved=False)
    vocab_progress = get_vocab_progress(uid)
    
    total_exams = len(history)
    avg_score = round(sum(h["score"] for h in history) / total_exams, 1) if total_exams > 0 else 0
    mastered_count = sum(1 for s in vocab_progress.values() if s == "mastered")
    
    # Group mistakes by category
    category_counts = {}
    for m in mistakes:
        cat = m.get("category", "General")
        category_counts[cat] = category_counts.get(cat, 0) + 1
        
    uni = next((u for u in universities_data if u["id"] == profile.get("university_id")), universities_data[0])
    passing_score = uni.get("passing_score", 60)
    is_ready = avg_score >= passing_score and len(mistakes) <= 5
    
    return {
        "student_profile": profile,
        "target_university": uni,
        "readiness_status": "Muafiyete Hazır (Geçer Not)" if is_ready else "Geliştirilmeli (Eksik Konular Var)",
        "readiness_color": "emerald" if is_ready else "amber",
        "average_score": avg_score,
        "passing_score": passing_score,
        "total_exams_taken": total_exams,
        "unresolved_mistakes_count": len(mistakes),
        "mistakes_by_category": category_counts,
        "mastered_vocabulary_count": mastered_count,
        "total_vocabulary_count": len(vocabulary_data),
        "mistake_details": mistakes[:15],
        "generated_at": datetime.utcnow().strftime("%d.%m.%Y %H:%M")
    }


# --- PayTR ödeme sonucu sayfası (PayTR penceresi buraya yönlendirir) ---
@app.get("/odeme-sonuc")
def payment_result_page():
    return FileResponse(STATIC_DIR / "odeme-sonuc.html", media_type="text/html")


# --- Mobil Uygulama (Android APK) İndirme & Bilgi Uç Noktaları ---
def _resolve_apk_path() -> Optional[Path]:
    candidates = [
        STATIC_DIR / "downloads" / "PrepKampus-Android.apk",
        BASE_DIR / "mobile" / "build" / "app" / "outputs" / "flutter-apk" / "app-release.apk",
        BASE_DIR / "mobile" / "build" / "app" / "outputs" / "flutter-apk" / "app-arm64-v8a-release.apk",
        BASE_DIR / "mobile" / "build" / "app" / "outputs" / "flutter-apk" / "app-debug.apk",
    ]
    for path in candidates:
        if path.exists() and path.is_file():
            return path
    return None


@app.get("/api/mobile-app/info")
def get_mobile_app_info():
    apk_path = _resolve_apk_path()
    size_bytes = apk_path.stat().st_size if apk_path else 0
    size_mb = round(size_bytes / (1024 * 1024), 1) if size_bytes else 42.8
    return {
        "available": apk_path is not None,
        "app_name": "PrepKampüs Mobil (Android)",
        "version": "1.4.0",
        "build_type": "Release (ARM64)",
        "filename": "PrepKampus-v1.4-Android.apk",
        "size_mb": size_mb,
        "min_android": "Android 8.0+ (API 26+)",
        "download_url": "/api/download/apk",
        "features": [
            "Web hesabınızla anlık Bulut Senkronizasyon (Kaldığınız yerden devam)",
            "İnternetsiz (Offline) Kelime Kartları ve Gramer Pratik Modu",
            "26 Üniversite Muafiyet Deneme Sınavı (30 Soru/Kur) & 24 Akademik Dinleme (MP3)",
            "E-Devlet Öğrenci Belgesi Tarama ve AI Writing / Speaking Değerlendirme"
        ]
    }


@app.get("/api/download/apk")
def download_android_apk():
    apk_path = _resolve_apk_path()
    if not apk_path:
        raise HTTPException(
            status_code=404,
            detail="Android APK paketi şu an hazırlanıyor. Lütfen birkaç dakika sonra tekrar deneyin veya tarayıcıdan 'Ana Ekrana Ekle' (PWA) özelliğini kullanın."
        )
    return FileResponse(
        path=apk_path,
        media_type="application/vnd.android.package-archive",
        filename="PrepKampus-v1.4-Android.apk",
        headers={
            "Content-Disposition": 'attachment; filename="PrepKampus-v1.4-Android.apk"',
            "Cache-Control": "public, max-age=3600"
        }
    )


# --- Bağımsız Yönetici Paneli (Admin) API & Arayüz Uç Noktaları ---
import hmac as _hmac

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin").strip()
# Üretimde şifre YALNIZCA ortam değişkeninden gelir: koddaki varsayılan (depoda herkese açık)
# şifre canlıda asla kabul edilmez. Geliştirmede kolaylık için varsayılan kalır.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip() or ("" if IS_PRODUCTION else "PrepMasterAdmin2026!")


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=80)
    password: str = Field(..., min_length=1, max_length=128)


class AdminStudentAccessRequest(BaseModel):
    unlocked_universities: List[str] = Field(default_factory=lambda: ["general"])
    primary_university_id: Optional[str] = Field(None, max_length=50)
    is_verified: Optional[bool] = None
    student_number: Optional[str] = Field(None, max_length=40)
    admin_note: Optional[str] = Field("", max_length=300)


class AdminPasswordResetRequest(BaseModel):
    new_password: str = Field(..., min_length=6, max_length=128)


def _require_admin(request: Request) -> Dict[str, Any]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yönetici oturumu gerekli."
        )
    payload = verify_session_token(auth_header.split(" ", 1)[1].strip())
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu işlem yalnızca sistem yöneticileri içindir."
        )
    return payload


@app.post("/api/admin/login")
def admin_login_endpoint(req: AdminLoginRequest, request: Request):
    enforce_rate_limit(request, scope="admin_login", max_requests=8, window_seconds=60, identifier=req.username)
    # Kaba kuvvete karşı ikinci kat: aynı IP saatte en fazla 30 yönetici giriş denemesi
    enforce_rate_limit(request, scope="admin_login_hourly", max_requests=30, window_seconds=3600)
    if not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Yönetici paneli yapılandırılmamış (ADMIN_PASSWORD ortam değişkeni eksik)."
        )
    user_ok = _hmac.compare_digest(req.username.strip().encode("utf-8"), ADMIN_USERNAME.encode("utf-8"))
    pass_ok = _hmac.compare_digest(req.password.encode("utf-8"), ADMIN_PASSWORD.encode("utf-8"))
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yönetici kullanıcı adı veya şifre hatalı."
        )
    token, expires_in = create_session_token(
        user_id=0,
        username=ADMIN_USERNAME,
        email="admin@prepmaster.local",
        role="admin",
        expires_in_hours=12
    )
    return {
        "success": True,
        "token": token,
        "expires_in": expires_in,
        "admin": {
            "username": ADMIN_USERNAME,
            "role": "admin"
        }
    }


@app.get("/api/admin/students")
def admin_get_students_endpoint(
    request: Request,
    search: str = Query("", max_length=120),
    university_id: str = Query("", max_length=50),
    verification: str = Query("", max_length=30)
):
    _require_admin(request)
    res = admin_list_students(
        search=search,
        university_filter=university_id,
        verification_filter=verification
    )
    res["universities"] = universities_data
    return res


@app.post("/api/admin/students/{target_user_id}/access")
def admin_update_student_access_endpoint(
    target_user_id: int,
    req: AdminStudentAccessRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    _require_admin(request)
    res = admin_update_student_access(
        user_id=target_user_id,
        unlocked_universities=req.unlocked_universities,
        primary_university_id=req.primary_university_id,
        is_verified=req.is_verified,
        student_number=req.student_number,
        admin_note=req.admin_note or ""
    )
    if not res.get("success"):
        raise HTTPException(status_code=404, detail=res.get("detail", "Öğrenci güncellenemedi."))
    if email_configured() and res.get("is_verified"):
        prof = get_profile(target_user_id)
        if prof.get("email"):
            background_tasks.add_task(
                send_access_granted_email,
                prof["email"],
                prof.get("full_name") or prof.get("username") or "",
                res.get("unlocked_universities", []),
            )
    return res


@app.post("/api/admin/students/{target_user_id}/reset-password")
def admin_reset_student_password_endpoint(
    target_user_id: int,
    req: AdminPasswordResetRequest,
    request: Request
):
    _require_admin(request)
    res = admin_reset_student_password(user_id=target_user_id, new_password=req.new_password)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "Şifre güncellenemedi."))
    return res


@app.delete("/api/admin/students/{target_user_id}")
def admin_delete_student_endpoint(target_user_id: int, request: Request):
    _require_admin(request)
    res = admin_delete_student(user_id=target_user_id)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "Öğrenci silinemedi."))
    return res


@app.get("/admin")
def serve_admin_panel():
    return FileResponse(STATIC_DIR / "admin.html", media_type="text/html")


# --- Destek & KVKK Yasal Belgeler Uç Noktaları ---
SUPPORT_CONTACT_INFO = {
    "email": "destek@prepkampus.com",
    "phone": "05398381887",
    "phone_display": "0539 838 18 87",
    "phone_intl": "+905398381887",
    "whatsapp_url": "https://wa.me/905398381887",
    "data_controller": "Hasan Toprakcı",
    "platform": "PrepKampüs - Üniversite Hazırlık & Muafiyet Platformu",
    "kvkk_url": "/kvkk",
    "documents": [
        {"id": "kvkk-aydinlatma", "code": "PM-KVKK-01", "title": "6698 Sayılı KVKK Aydınlatma Metni"},
        {"id": "acik-riza", "code": "PM-KVKK-02", "title": "Açık Rıza Beyanı Metni"},
        {"id": "gizlilik-cerez", "code": "PM-KVKK-03", "title": "Gizlilik, Veri Güvenliği ve Çerez Politikası"},
        {"id": "kullanici-sozlesmesi", "code": "PM-HUKUK-04", "title": "Kullanıcı Sözleşmesi ve Hizmet Koşulları"},
        {"id": "kvkk-basvuru", "code": "PM-KVKK-05", "title": "KVKK Madde 11 Veri Sahibi Başvuru Formu"},
    ],
}


SUPPORT_CATEGORIES = {
    "Üniversite Erişim & Paket Tanımlama",
    "E-Devlet Öğrenci Belgesi Doğrulama",
    "Ödeme & Fatura İşlemleri",
    "Teknik Destek / Şifre İşlemleri",
    "KVKK Veri Sahibi / Hesap Silme Başvurusu",
    "Genel Destek",
}


class SupportTicketRequest(BaseModel):
    category: str = Field("general", max_length=60)
    full_name: Optional[str] = Field("", max_length=100)
    email: Optional[str] = Field("", max_length=120)
    phone: Optional[str] = Field("", max_length=40)
    message: str = Field(..., min_length=5, max_length=4000)

    @field_validator("category", "full_name", "email", "phone", "message", mode="before")
    @classmethod
    def _clean(cls, v):
        return sanitize_text(v, strip_tags=True)


@app.get("/api/support/info")
def get_support_info_endpoint():
    return SUPPORT_CONTACT_INFO


@app.post("/api/support/ticket")
def submit_support_ticket_endpoint(
    req: SupportTicketRequest,
    request: Request,
    background_tasks: BackgroundTasks,
):
    enforce_rate_limit(request, scope="support_ticket", max_requests=6, window_seconds=60)
    # Günlük tavan: bir IP günde en fazla 20 talep açabilir (seri gönderimle e-posta kotası tükenmesin)
    enforce_rate_limit(request, scope="support_ticket_daily", max_requests=20, window_seconds=86400)
    token_user = get_current_user_from_request(request)
    uid = token_user["user_id"] if token_user else None
    # Kategori serbest metin değil: e-posta konusuna/şablonuna yabancı metin (ör. bağlantı) girmesin
    category = req.category if req.category in SUPPORT_CATEGORIES else "Genel Destek"
    account_email = ""
    if token_user:
        profile = get_profile(uid) or {}
        account_email = (profile.get("email") or "").strip()
    sender_name = req.full_name or (token_user.get("username", "") if token_user else "")
    sender_email = req.email or account_email
    res = create_support_ticket(
        message=req.message,
        category=category,
        full_name=sender_name,
        email=sender_email,
        phone=req.phone or "",
        user_id=uid,
    )
    if email_configured() and res.get("ticket_id"):
        background_tasks.add_task(
            send_support_ticket_notification,
            res["ticket_id"],
            category,
            sender_name,
            sender_email,
            req.phone or "",
            req.message,
        )
        # "Alındı" e-postası YALNIZCA giriş yapmış öğrencinin kendi hesap adresine gider.
        # Eskiden formda yazılan her adrese gidiyordu: herkes formu başkalarına e-posta
        # göndermek (spam) ve günlük kotayı bitirmek için kullanabiliyordu.
        if account_email and "@" in account_email:
            background_tasks.add_task(
                send_support_ticket_receipt,
                account_email,
                res["ticket_id"],
                category,
            )
    return res


class AdminTestEmailRequest(BaseModel):
    to_email: Optional[str] = Field("", max_length=120)


@app.get("/api/admin/backup")
def admin_backup_download_endpoint(request: Request, background_tasks: BackgroundTasks):
    """
    Yönetici için anlık, tutarlı veritabanı yedeği indirir (gzip). Railway diski kaybolursa
    sunucudaki otomatik yedekler de gider; bu yüzden düzenli olarak bilgisayara indirilmelidir.
    """
    _require_admin(request)
    enforce_rate_limit(request, scope="admin_backup", max_requests=6, window_seconds=3600)
    import tempfile as _tempfile
    try:
        from backup import create_backup
    except ImportError:
        from backend.backup import create_backup
    tmp_dir = Path(_tempfile.mkdtemp(prefix="pm-yedek-"))
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M")
    out = create_backup(target_dir=tmp_dir, name=f"prepmaster-yedek-{stamp}.db")
    background_tasks.add_task(lambda: __import__("shutil").rmtree(tmp_dir, ignore_errors=True))
    return FileResponse(out, media_type="application/gzip", filename=out.name)


@app.get("/api/admin/email/status")
def admin_email_status_endpoint(request: Request):
    _require_admin(request)
    return {**get_email_status(), "budget": get_email_budget()}


@app.post("/api/admin/email/test")
def admin_test_email_endpoint(req: AdminTestEmailRequest, request: Request):
    _require_admin(request)
    target = (req.to_email or "prepmasteryonetici@gmail.com").strip()
    if "@" not in target:
        raise HTTPException(status_code=400, detail="Geçerli bir hedef e-posta adresi giriniz.")
    result = send_email_verbose(
        to=target,
        priority="kritik",
        subject="PrepKampüs E-Posta Altyapısı Canlı Testi",
        text=(
            "Merhaba Hasan,\n\n"
            "PrepKampüs e-posta gönderim altyapısı başarıyla çalışıyor!\n"
            "Şifre sıfırlama, .edu.tr doğrulama kodları, hoş geldin mailleri ve destek bildirimleri aktif."
        ),
        html=(
            '<p style="color:#334155;font-size:14px">Merhaba <b>Hasan</b>,</p>'
            '<p style="color:#065f46;font-size:14px;background:#ecfdf5;border:1px solid #a7f3d0;padding:12px 16px;border-radius:12px">'
            '✓ PrepKampüs e-posta gönderim altyapısı canlı sunucuda başarıyla çalışıyor!</p>'
            '<p style="color:#475569;font-size:13px">Şifre sıfırlama, .edu.tr OTP doğrulama, hoş geldin mailleri ve Destek/KVKK bildirimleri aktif durumdadır.</p>'
        ),
    )
    if not result.get("success"):
        raise HTTPException(status_code=503, detail=result.get("error") or "Test e-postası gönderilemedi.")
    return result


@app.get("/api/admin/support-tickets")
def admin_get_support_tickets_endpoint(request: Request):
    _require_admin(request)
    return {"tickets": list_support_tickets(limit=100)}


@app.get("/kvkk")
@app.get("/destek")
def serve_kvkk_page():
    return FileResponse(STATIC_DIR / "kvkk.html", media_type="text/html")


@app.get("/robots.txt", response_class=PlainTextResponse)
def serve_robots_txt(request: Request):
    return PlainTextResponse(build_robots_txt(resolve_site_url(request)))


@app.get("/sitemap.xml")
def serve_sitemap_xml(request: Request):
    xml = build_sitemap_xml(resolve_site_url(request), universities_data)
    return Response(content=xml, media_type="application/xml")


@app.get("/sinavlar", response_class=HTMLResponse)
def serve_exams_hub(request: Request):
    counts = compute_counts_by_uni(questions_data, listening_data, speaking_data)
    html_str = render_exams_hub_html(resolve_site_url(request), universities_data, counts)
    return HTMLResponse(content=html_str)


@app.get("/universite/{uni_id}", response_class=HTMLResponse)
def serve_university_seo_page(uni_id: str, request: Request):
    uni = next((u for u in universities_data if u.get("id") == uni_id), None)
    if not uni:
        raise HTTPException(status_code=404, detail="Üniversite bulunamadı.")
    counts = compute_counts_by_uni(questions_data, listening_data, speaking_data)
    html_str = render_university_seo_html(
        resolve_site_url(request),
        uni,
        universities_data,
        counts.get(uni_id, {"questions": 0, "listening": 0, "speaking": 0}),
    )
    return HTMLResponse(content=html_str)


# --- Static files ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index(request: Request):
    verif_meta = get_google_verification_meta()
    env_site = os.getenv("SITE_URL", "").strip().rstrip("/")
    if verif_meta or (env_site and env_site != DEFAULT_PUBLIC_URL):
        html_str = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        if env_site:
            html_str = html_str.replace(DEFAULT_PUBLIC_URL, env_site)
        if verif_meta:
            html_str = html_str.replace("</head>", f"  {verif_meta}\n</head>", 1)
        return HTMLResponse(content=html_str)
    return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8050, reload=True)
