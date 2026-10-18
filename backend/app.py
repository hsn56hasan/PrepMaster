import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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
    bulk_upsert_mistakes, bulk_upsert_vocab_progress,
    create_user, authenticate_user, verify_student, get_verification_status,
    create_student_otp, verify_student_otp
)

from security import (
    SecurityHeadersMiddleware,
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
    create_session_token,
    verify_session_token,
    get_current_user_from_request
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="PrepMaster API", version="1.2.0")

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
    profile: Optional[Dict[str, Any]] = None
    mistakes: Optional[List[Dict[str, Any]]] = None
    vocab_progress: Optional[Dict[str, str]] = None
    exam_attempts: Optional[List[Dict[str, Any]]] = None

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=6, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=100)
    university_id: Optional[str] = Field("itu", max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    student_number: Optional[str] = Field("", max_length=30, pattern=r"^[a-zA-Z0-9_-]*$")

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

# --- Authentication & Student Verification Endpoints ---
@app.post("/api/auth/register")
def register_endpoint(req: RegisterRequest, request: Request, _=Depends(rate_limit_register)):
    try:
        user = create_user(
            email=req.email,
            username=req.username,
            password=req.password,
            full_name=req.full_name,
            university_id=req.university_id or "itu",
            student_number=req.student_number or ""
        )
        token, expires_in = create_session_token(user["id"], user["username"], user["email"])
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

@app.get("/api/auth/me")
def current_user_endpoint(request: Request, user_id: int = 1):
    token_user = get_current_user_from_request(request)
    target_id = token_user["user_id"] if token_user else user_id
    user = get_profile(target_id)
    uni = next((u for u in universities_data if u["id"] == user.get("university_id")), universities_data[0])
    user["university"] = uni
    if token_user:
        user["authenticated_via"] = "bearer_token"
    return user

@app.post("/api/student/verify")
def student_verify_endpoint(req: StudentVerifyRequest):
    res = verify_student(
        user_id=req.user_id or 1,
        university_id=req.university_id,
        edu_email=req.edu_email,
        student_number=req.student_number,
        doc_note=req.notes or ""
    )
    return res

@app.post("/api/student/request-otp")
def student_request_otp_endpoint(req: StudentOtpRequest, request: Request, _=Depends(rate_limit_otp_request)):
    if not req.email or "@" not in req.email:
        raise HTTPException(status_code=400, detail="Geçerli bir e-posta adresi giriniz.")
    enforce_rate_limit(request, scope="otp_request_email", max_requests=3, window_seconds=60, identifier=req.email)
    res = create_student_otp(email=req.email, student_number=req.student_number or "")
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "OTP kodu oluşturulamadı."))
    return res

@app.post("/api/student/verify-otp")
def student_verify_otp_endpoint(req: StudentOtpVerifyRequest, request: Request, _=Depends(rate_limit_otp_verify)):
    if not req.email or not req.otp_code:
        raise HTTPException(status_code=400, detail="E-posta ve 6 haneli doğrulama kodunu eksiksiz giriniz.")
    enforce_rate_limit(request, scope="otp_verify_email", max_requests=5, window_seconds=60, identifier=req.email)
    res = verify_student_otp(email=req.email, otp_code=req.otp_code, user_id=req.user_id or 1)
    if not res.get("success"):
        raise HTTPException(status_code=400, detail=res.get("detail", "Doğrulama başarısız."))
    return res


@app.get("/api/student/status")
def student_status_endpoint(user_id: int = 1):
    return get_verification_status(user_id)



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
def get_user_profile():
    profile = get_profile()
    # attach university details
    uni = next((u for u in universities_data if u["id"] == profile.get("university_id")), universities_data[0])
    profile["university"] = uni
    return profile

@app.post("/api/profile")
def update_user_profile(req: ProfileUpdateRequest):
    valid_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    if req.current_level.upper() not in valid_levels:
        raise HTTPException(status_code=400, detail="Invalid level. Must be one of: A1, A2, B1, B2, C1, C2")
    return update_profile(req.university_id, req.current_level.upper(), req.target_score or 65)

@app.get("/api/questions")
def get_questions(
    university_id: Optional[str] = None,
    level: Optional[str] = None,
    category: Optional[str] = None
):
    filtered = questions_data
    if university_id and university_id != "all":
        # match specific university or general questions
        filtered = [q for q in filtered if q["university_id"] in [university_id, "general"]]
    if level and level != "all":
        filtered = [q for q in filtered if q["level"].upper() == level.upper()]
    if category and category != "all":
        filtered = [q for q in filtered if q.get("category", "").lower() == category.lower()]
    return filtered

@app.get("/api/vocabulary")
def get_vocabulary(
    level: Optional[str] = None,
    search: Optional[str] = None
):
    progress = get_vocab_progress()
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
def update_word_status(word_id: str, req: VocabStatusRequest):
    if req.status not in ["mastered", "learning", "unreviewed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    set_vocab_status(word_id, req.status)
    return {"status": "ok", "word_id": word_id, "new_status": req.status}

@app.get("/api/writing-guides")
def get_writing_guides():
    return writing_guides_data

@app.get("/api/listening")
def get_listening_list(
    university_id: Optional[str] = None,
    level: Optional[str] = None,
    type: Optional[str] = None
):
    results = []
    for item in listening_data:
        if university_id and university_id != "all" and item.get("university_id") != university_id:
            continue
        if level and level != "all" and item.get("level", "").upper() != level.upper():
            continue
        if type and type != "all" and item.get("type") != type:
            continue
        results.append(item)
    return results

@app.get("/api/listening/{item_id}")
def get_listening_detail(item_id: str):
    for item in listening_data:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Listening item not found")

@app.post("/api/writing/evaluate")
def evaluate_essay_endpoint(req: EssayEvaluateRequest, _=Depends(rate_limit_ai_writing)):
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
def submit_exam(req: ExamSubmitRequest):
    q_map = {q["id"]: q for q in questions_data}
    correct_count = 0
    results_detail = []
    category_times = {} # category -> list of seconds
    
    question_times = req.question_times or {}
    
    for q_id, chosen_key in req.answers.items():
        q = q_map.get(q_id)
        if not q:
            continue
        
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
            resolve_mistake(q_id)
        else:
            # Save into mistake vault
            record_mistake(
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
    
    total_answered = len(req.answers)
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
def get_mistake_vault(is_resolved: bool = False):
    mistakes = get_mistakes(is_resolved=is_resolved)
    q_map = {q["id"]: q for q in questions_data}
    
    enriched = []
    for m in mistakes:
        q = q_map.get(m["question_id"])
        if q:
            item = dict(m)
            item["question_details"] = q
            enriched.append(item)
    return enriched

@app.post("/api/mistakes/{question_id}/resolve")
def resolve_mistake_endpoint(question_id: str):
    resolve_mistake(question_id)
    return {"status": "ok", "question_id": question_id}

@app.delete("/api/mistakes/{question_id}")
def delete_mistake_endpoint(question_id: str):
    delete_mistake(question_id)
    return {"status": "ok", "question_id": question_id}

@app.get("/api/exam/history")
def exam_history():
    return get_exam_history()

@app.get("/api/stats")
def get_overall_stats():
    profile = get_profile()
    history = get_exam_history(limit=50)
    vocab_progress = get_vocab_progress()
    unresolved_mistakes = get_mistake_count()
    
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

# --- Speaking Simulator Endpoints ---
@app.get("/api/speaking")
def get_speaking_tasks(university_id: Optional[str] = None):
    if university_id:
        return [t for t in speaking_data if t.get("university_id") == university_id or t.get("university_id") == "general"]
    return speaking_data

@app.get("/api/speaking/{task_id}")
def get_speaking_task(task_id: str):
    task = next((t for t in speaking_data if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Speaking task not found")
    return task

@app.post("/api/speaking/evaluate")
def evaluate_speaking(req: SpeakingEvaluateRequest, _=Depends(rate_limit_ai_speaking)):
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
def sync_pull():
    profile = get_profile()
    mistakes = get_mistakes()
    vocab_progress = get_vocab_progress()
    exam_history = get_exam_history(limit=100)
    
    return {
        "profile": profile,
        "mistakes": mistakes,
        "vocab_progress": vocab_progress,
        "exam_history": exam_history,
        "server_timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/sync/push")
def sync_push(req: SyncPushRequest):
    updates = {"profile_updated": False, "mistakes_synced": 0, "vocab_synced": 0, "exams_saved": 0}
    
    if req.profile:
        update_profile(
            university_id=req.profile.get("university_id", "itu"),
            current_level=req.profile.get("current_level", "B2"),
            target_score=req.profile.get("target_score", 65)
        )
        updates["profile_updated"] = True
        
    if req.mistakes:
        updates["mistakes_synced"] = bulk_upsert_mistakes(req.mistakes)
        
    if req.vocab_progress:
        updates["vocab_synced"] = bulk_upsert_vocab_progress(req.vocab_progress)
        
    if req.exam_attempts:
        for ea in req.exam_attempts:
            save_exam_attempt(
                university_id=ea.get("university_id", "itu"),
                level=ea.get("level", "B2"),
                score=ea.get("score", 0),
                total_questions=ea.get("total_questions", 0),
                correct_count=ea.get("correct_count", 0),
                duration_seconds=ea.get("duration_seconds", 0),
                answers=ea.get("answers", {})
            )
            updates["exams_saved"] += 1
            
    return {"status": "success", "synced": updates, "timestamp": datetime.utcnow().isoformat()}

# --- Mock Exam Mode (Full University Trial Exam) ---
@app.get("/api/exam/mock/{university_id}")
def generate_mock_exam(university_id: str):
    uni = next((u for u in universities_data if u["id"] == university_id), universities_data[0])
    
    # 1. Select matching university questions
    uni_questions = [q for q in questions_data if q.get("university_id") == university_id]
    if len(uni_questions) < 10:
        # supplement with general B2/C1 questions
        supp = [q for q in questions_data if q.get("university_id") != university_id and q.get("level") in ["B2", "C1"]]
        uni_questions.extend(supp[:(15 - len(uni_questions))])
    
    # 2. Select matching listening track
    lis_track = next((lt for lt in listening_data if lt.get("university_id") == university_id), listening_data[0] if listening_data else None)
    
    # 3. Select matching essay prompt
    essay_guide = next((wg for wg in writing_guides_data if wg.get("university_id") == university_id), writing_guides_data[0] if writing_guides_data else None)
    
    # 4. Select matching speaking prompt
    spk_task = next((st for st in speaking_data if st.get("university_id") == university_id), speaking_data[0] if speaking_data else None)
    
    return {
        "university": uni,
        "exam_title": f"{uni.get('name')} Tam Deneme Sınavı",
        "duration_minutes": uni.get("duration_minutes", 120),
        "passing_score": uni.get("passing_score", 60),
        "sections": {
            "multiple_choice": uni_questions[:15],
            "listening": lis_track,
            "writing_prompt": essay_guide,
            "speaking_prompt": spk_task
        }
    }

# --- Student Summary Report Card (PDF/Print View) ---
@app.get("/api/report/summary")
def get_student_report_summary():
    profile = get_profile()
    history = get_exam_history(limit=50)
    mistakes = get_mistakes(is_resolved=False)
    vocab_progress = get_vocab_progress()
    
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


# --- Static files ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8050, reload=True)
