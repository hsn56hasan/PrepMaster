import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import (
    init_db, get_profile, update_profile, 
    save_exam_attempt, get_exam_history, 
    set_vocab_status, get_vocab_progress,
    record_mistake, resolve_mistake, delete_mistake,
    get_mistakes, get_mistake_count
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="PrepMaster API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.on_event("startup")
def startup_event():
    init_db()

# --- Models ---
class ProfileUpdateRequest(BaseModel):
    university_id: str
    current_level: str
    target_score: Optional[int] = 65

class ExamSubmitRequest(BaseModel):
    university_id: str
    level: str
    duration_seconds: int
    answers: Dict[str, str] # question_id -> chosen option key (e.g. "B")
    question_times: Optional[Dict[str, int]] = {} # question_id -> seconds spent
    is_mistake_practice: Optional[bool] = False

class VocabStatusRequest(BaseModel):
    status: str # "mastered" or "learning"

class EssayEvaluateRequest(BaseModel):
    essay: str
    prompt: Optional[str] = "General Academic Essay"
    university_id: Optional[str] = "general"
    level: Optional[str] = "B2"

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
    for item in vocabulary_data:
        entry = dict(item)
        entry["status"] = progress.get(item["id"], "unreviewed")
        if level and level != "all" and item["level"].upper() != level.upper():
            continue
        if search:
            query = search.lower()
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
def evaluate_essay_endpoint(req: EssayEvaluateRequest):
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

# --- Static files ---
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8050, reload=True)
