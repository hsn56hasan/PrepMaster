import sqlite3
import json
import hashlib
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from security import hash_password, verify_password
except ImportError:
    from backend.security import hash_password, verify_password

DB_PATH = Path(os.getenv("PREPMASTER_DB_PATH", str(Path(__file__).resolve().parent.parent / "prepmaster.db")))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            university_id TEXT DEFAULT 'itu',
            current_level TEXT DEFAULT 'B2',
            target_score INTEGER DEFAULT 65,
            streak_days INTEGER DEFAULT 1,
            last_active TEXT
        );

        INSERT OR IGNORE INTO user_profile (id, university_id, current_level, target_score, streak_days, last_active)
        VALUES (1, 'itu', 'B2', 65, 1, CURRENT_TIMESTAMP);

        -- Multi-User & Student Verification Tables --
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password_hash TEXT,
            full_name TEXT,
            university_id TEXT DEFAULT 'itu',
            student_number TEXT,
            is_verified_student INTEGER DEFAULT 0,
            verification_status TEXT DEFAULT 'unverified',
            current_level TEXT DEFAULT 'B2',
            target_score INTEGER DEFAULT 65,
            streak_days INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT DEFAULT CURRENT_TIMESTAMP
        );

        INSERT OR IGNORE INTO users (id, email, username, password_hash, full_name, university_id, student_number, is_verified_student, verification_status)
        VALUES (1, 'ogrenci@itu.edu.tr', 'ituhazirlik', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'İTÜ Hazırlık Öğrencisi', 'itu', '040220199', 1, 'verified');

        CREATE TABLE IF NOT EXISTS student_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            university_id TEXT,
            edu_email TEXT,
            student_id_number TEXT,
            verification_type TEXT DEFAULT 'edu_email',
            verification_status TEXT DEFAULT 'verified',
            notes TEXT,
            verified_at TEXT DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS exam_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            university_id TEXT,
            level TEXT,
            score REAL,
            total_questions INTEGER,
            correct_count INTEGER,
            duration_seconds INTEGER,
            answers_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS vocab_progress (
            word_id TEXT PRIMARY KEY,
            user_id INTEGER DEFAULT 1,
            status TEXT DEFAULT 'learning',
            review_count INTEGER DEFAULT 1,
            last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS question_bookmarks (
            question_id TEXT PRIMARY KEY,
            user_id INTEGER DEFAULT 1,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mistake_vault (
            question_id TEXT PRIMARY KEY,
            user_id INTEGER DEFAULT 1,
            university_id TEXT,
            level TEXT,
            category TEXT,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_answer TEXT,
            last_wrong_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            resolved_at TEXT
        );

        -- 6-Digit Email OTP Verification Table --
        CREATE TABLE IF NOT EXISTS student_otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER DEFAULT 1,
            email TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            university_id TEXT DEFAULT 'itu',
            student_number TEXT DEFAULT '',
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 5,
            is_used INTEGER DEFAULT 0, -- 0: pending, 1: verified, 2: superseded, 3: expired, 4: max attempts exceeded
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL,
            consumed_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_student_otps_email ON student_otps(email);
    """)

    # Ensure schema migrations on existing SQLite databases
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cursor.fetchall()]
    if "verification_status" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN verification_status TEXT DEFAULT 'pending'")
    if "is_verified_student" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN is_verified_student INTEGER DEFAULT 0")
    if "unlocked_universities" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN unlocked_universities TEXT DEFAULT '[\"itu\", \"general\"]'")
    if "verified_university" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN verified_university TEXT DEFAULT 'itu'")

    cursor.execute("PRAGMA table_info(student_verifications)")
    s_cols = [r[1] for r in cursor.fetchall()]
    if "verification_status" not in s_cols:
        conn.execute("ALTER TABLE student_verifications ADD COLUMN verification_status TEXT DEFAULT 'pending'")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS university_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            university_id TEXT,
            price_try REAL DEFAULT 50.0,
            payment_reference TEXT,
            card_last_four TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

# Auto-initialize on import
init_db()

def get_profile(user_id: int = 1) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, username, full_name, university_id, current_level, target_score, streak_days, 
               is_verified_student, verification_status, student_number, last_active,
               unlocked_universities, verified_university
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    if row:
        conn.close()
        data = dict(row)
        import json
        raw_unlocked = data.get("unlocked_universities")
        unlocked = []
        if isinstance(raw_unlocked, str):
            try:
                unlocked = json.loads(raw_unlocked)
            except Exception:
                unlocked = []
        elif isinstance(raw_unlocked, list):
            unlocked = raw_unlocked

        primary_uni = data.get("verified_university") or data.get("university_id") or "itu"
        if primary_uni not in unlocked:
            unlocked.append(primary_uni)
        if "general" not in unlocked:
            unlocked.append("general")

        data["unlocked_universities"] = unlocked
        data["verified_university"] = primary_uni
        return data

    # Fallback to legacy user_profile
    cursor.execute("SELECT university_id, current_level, target_score, streak_days, last_active FROM user_profile WHERE id = 1")
    legacy = cursor.fetchone()
    conn.close()
    if legacy:
        data = dict(legacy)
        data["is_verified_student"] = 1
        data["verification_status"] = "verified"
        data["student_number"] = "040220199"
        data["unlocked_universities"] = ["itu", "general"]
        data["verified_university"] = "itu"
        return data

    return {
        "id": 1,
        "email": "ogrenci@itu.edu.tr",
        "username": "ituhazirlik",
        "full_name": "İTÜ Hazırlık Öğrencisi",
        "university_id": "itu",
        "current_level": "B2",
        "target_score": 65,
        "streak_days": 1,
        "is_verified_student": 1,
        "verification_status": "verified",
        "student_number": "040220199",
        "unlocked_universities": ["itu", "general"],
        "verified_university": "itu",
        "last_active": datetime.now().isoformat()
    }

def update_profile(university_id: str, current_level: str, target_score: int, user_id: int = 1) -> Dict[str, Any]:
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE users 
            SET university_id = ?, current_level = ?, target_score = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (university_id, current_level, target_score, user_id))
        conn.execute("""
            UPDATE user_profile 
            SET university_id = ?, current_level = ?, target_score = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (university_id, current_level, target_score))
    conn.close()
    return get_profile(user_id)

def create_user(email: str, username: str, password: str, full_name: str, university_id: str = "itu", student_number: str = "") -> Dict[str, Any]:
    import json
    conn = get_db()
    pw_hash = hash_password(password)
    initial_unlocked = json.dumps([university_id, "general"])
    with conn:
        cursor = conn.execute("""
            INSERT INTO users (email, username, password_hash, full_name, university_id, student_number, is_verified_student, verification_status, unlocked_universities, verified_university)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'pending', ?, ?)
        """, (email.lower().strip(), username.strip(), pw_hash, full_name.strip(), university_id, student_number.strip(), initial_unlocked, university_id))
        user_id = cursor.lastrowid
    conn.close()
    return get_profile(user_id)

def authenticate_user(identifier: str, password: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    ident = identifier.lower().strip()
    cursor.execute("""
        SELECT id, email, username, password_hash, full_name, university_id, current_level, target_score, 
               is_verified_student, verification_status, unlocked_universities, verified_university
        FROM users 
        WHERE LOWER(email) = ? OR LOWER(username) = ?
    """, (ident, ident))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    stored_hash = row["password_hash"]
    if not verify_password(password, stored_hash):
        conn.close()
        return None

    # Transparently upgrade legacy SHA-256 hash to PBKDF2
    if not stored_hash.startswith("pbkdf2:"):
        upgraded_hash = hash_password(password)
        with conn:
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (upgraded_hash, row["id"]))

    user_dict = dict(row)
    user_dict.pop("password_hash", None)
    conn.close()

    import json
    raw_unlocked = user_dict.get("unlocked_universities")
    unlocked = []
    if isinstance(raw_unlocked, str):
        try:
            unlocked = json.loads(raw_unlocked)
        except Exception:
            unlocked = []
    elif isinstance(raw_unlocked, list):
        unlocked = raw_unlocked

    primary = user_dict.get("verified_university") or user_dict.get("university_id") or "itu"
    if primary not in unlocked:
        unlocked.append(primary)
    if "general" not in unlocked:
        unlocked.append("general")

    user_dict["unlocked_universities"] = unlocked
    user_dict["verified_university"] = primary
    return user_dict

def verify_student(user_id: int, university_id: str, edu_email: str, student_number: str, doc_note: str = "") -> Dict[str, Any]:
    conn = get_db()
    is_valid_edu = edu_email.lower().endswith(".edu.tr") or edu_email.lower().endswith(".edu") or len(student_number) >= 6
    status = "verified" if is_valid_edu else "pending"
    is_verified_int = 1 if status == "verified" else 0

    with conn:
        conn.execute("""
            INSERT INTO student_verifications (user_id, university_id, edu_email, student_id_number, verification_status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, university_id, edu_email, student_number, status, doc_note))
        conn.execute("""
            UPDATE users 
            SET university_id = ?, student_number = ?, is_verified_student = ?, verification_status = ?
            WHERE id = ?
        """, (university_id, student_number, is_verified_int, status, user_id))
    conn.close()

    return {
        "user_id": user_id,
        "university_id": university_id,
        "is_verified": is_verified_int == 1,
        "verification_status": status,
        "message": "Öğrenci kaydınız başarıyla doğrulandı!" if status == "verified" else "Öğrenci belgeniz incelemeye alındı."
    }

def get_verification_status(user_id: int = 1) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, full_name, university_id, student_number, is_verified_student, verification_status FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"id": user_id, "is_verified_student": 1, "verification_status": "verified"}

def verify_student_by_document(user_id: int, matched_uni_id: str, student_number: str = "", barcode: str = "", doc_snippet: str = "") -> Dict[str, Any]:
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT unlocked_universities, email, full_name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    email = row["email"] if row else ""
    raw_unlocked = row["unlocked_universities"] if row else None

    unlocked = ["general"]
    if raw_unlocked:
        try:
            unlocked = json.loads(raw_unlocked)
        except Exception:
            unlocked = ["general"]

    if matched_uni_id not in unlocked:
        unlocked.append(matched_uni_id)

    with conn:
        conn.execute("""
            UPDATE users 
            SET university_id = ?,
                verified_university = ?,
                is_verified_student = 1,
                verification_status = 'verified',
                student_number = CASE WHEN ? != '' THEN ? ELSE student_number END,
                unlocked_universities = ?
            WHERE id = ?
        """, (matched_uni_id, matched_uni_id, student_number, student_number, json.dumps(unlocked), user_id))

        conn.execute("""
            INSERT INTO student_verifications (user_id, university_id, edu_email, student_id_number, verification_type, verification_status, notes)
            VALUES (?, ?, ?, ?, 'document_scan', 'verified', ?)
        """, (user_id, matched_uni_id, email, student_number, f"Barcode: {barcode} | Snippet: {doc_snippet[:100]}"))

    conn.close()
    return {
        "success": True,
        "university_id": matched_uni_id,
        "is_verified": True,
        "verification_status": "verified",
        "unlocked_universities": unlocked,
        "message": f"Tebrikler! Belgeniz başarıyla tarandı ve {matched_uni_id.upper()} hazırlık programı hesabınıza otomatik olarak tanımlandı."
    }

def unlock_university_membership(user_id: int, university_id: str, card_holder: str = "", card_last_four: str = "4242", price_try: float = 50.0) -> Dict[str, Any]:
    import json
    import uuid
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT unlocked_universities FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    raw_unlocked = row["unlocked_universities"] if row else None
    unlocked = ["general"]
    if raw_unlocked:
        try:
            unlocked = json.loads(raw_unlocked)
        except Exception:
            unlocked = ["general"]

    if university_id not in unlocked:
        unlocked.append(university_id)

    ref = f"PAY-50TL-{uuid.uuid4().hex[:8].upper()}"
    with conn:
        conn.execute("""
            UPDATE users 
            SET unlocked_universities = ?
            WHERE id = ?
        """, (json.dumps(unlocked), user_id))

        conn.execute("""
            INSERT INTO university_purchases (user_id, university_id, price_try, payment_reference, card_last_four)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, university_id, price_try, ref, card_last_four[-4:] if card_last_four else "4242"))

    conn.close()
    return {
        "success": True,
        "unlocked_university": university_id,
        "unlocked_universities": unlocked,
        "price_try": price_try,
        "reference": ref,
        "message": f"{university_id.upper()} hazırlık sınavları ve deneme testleri 50 TL karşılığında başarıyla açıldı!"
    }

def check_university_access(user_id: int, university_id: str) -> bool:
    if not university_id or university_id in ["general", "all"]:
        return True
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT university_id, verified_university, unlocked_universities FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return True

    # If it's their own registered / verified university, it's 100% free!
    if row["university_id"] == university_id or row["verified_university"] == university_id:
        return True

    raw_unlocked = row["unlocked_universities"]
    if raw_unlocked:
        try:
            unlocked = json.loads(raw_unlocked)
            if university_id in unlocked:
                return True
        except Exception:
            pass
    return False


def save_exam_attempt(university_id: str, level: str, score: float, total_questions: int, 
                      correct_count: int, duration_seconds: int, answers: Dict[str, Any]) -> int:
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            INSERT INTO exam_attempts (university_id, level, score, total_questions, correct_count, duration_seconds, answers_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (university_id, level, score, total_questions, correct_count, duration_seconds, json.dumps(answers)))
        attempt_id = cursor.lastrowid
    conn.close()
    return attempt_id

def get_exam_history(limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, university_id, level, score, total_questions, correct_count, duration_seconds, created_at
        FROM exam_attempts 
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_vocab_status(word_id: str, status: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO vocab_progress (word_id, status, review_count, last_reviewed)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(word_id) DO UPDATE SET
                status = excluded.status,
                review_count = review_count + 1,
                last_reviewed = CURRENT_TIMESTAMP
        """, (word_id, status))
    conn.close()

def get_vocab_progress() -> Dict[str, str]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word_id, status FROM vocab_progress")
    rows = cursor.fetchall()
    conn.close()
    return {r["word_id"]: r["status"] for r in rows}

def record_mistake(question_id: str, university_id: str, level: str, category: str, wrong_answer: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO mistake_vault (question_id, university_id, level, category, wrong_count, last_wrong_answer, last_wrong_at, is_resolved)
            VALUES (?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, 0)
            ON CONFLICT(question_id) DO UPDATE SET
                wrong_count = wrong_count + 1,
                last_wrong_answer = excluded.last_wrong_answer,
                last_wrong_at = CURRENT_TIMESTAMP,
                is_resolved = 0,
                resolved_at = NULL
        """, (question_id, university_id, level, category, wrong_answer))
    conn.close()

def resolve_mistake(question_id: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE mistake_vault 
            SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
            WHERE question_id = ?
        """, (question_id,))
    conn.close()

def delete_mistake(question_id: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM mistake_vault WHERE question_id = ?", (question_id,))
    conn.close()

def get_mistakes(is_resolved: bool = False) -> List[Dict[str, Any]]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT question_id, university_id, level, category, wrong_count, last_wrong_answer, last_wrong_at, is_resolved, resolved_at
        FROM mistake_vault
        WHERE is_resolved = ?
        ORDER BY last_wrong_at DESC
    """, (1 if is_resolved else 0,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_mistake_count() -> int:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM mistake_vault WHERE is_resolved = 0")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] if row else 0

def bulk_upsert_mistakes(mistakes: List[Dict[str, Any]]) -> int:
    conn = get_db()
    inserted = 0
    with conn:
        for m in mistakes:
            qid = m.get("question_id")
            if not qid:
                continue
            conn.execute("""
                INSERT INTO mistake_vault (question_id, university_id, level, category, wrong_count, last_wrong_answer, last_wrong_at, is_resolved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(question_id) DO UPDATE SET
                    wrong_count = MAX(mistake_vault.wrong_count, excluded.wrong_count),
                    last_wrong_answer = excluded.last_wrong_answer,
                    last_wrong_at = excluded.last_wrong_at,
                    is_resolved = excluded.is_resolved
            """, (
                qid, 
                m.get("university_id", "general"),
                m.get("level", "B2"),
                m.get("category", "General"),
                m.get("wrong_count", 1),
                m.get("last_wrong_answer", ""),
                m.get("last_wrong_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
                1 if m.get("is_resolved") else 0
            ))
            inserted += 1
    conn.close()
    return inserted

def bulk_upsert_vocab_progress(vocab_map: Dict[str, str]) -> int:
    conn = get_db()
    count = 0
    with conn:
        for word_id, status in vocab_map.items():
            conn.execute("""
                INSERT INTO vocab_progress (word_id, status, last_reviewed)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(word_id) DO UPDATE SET
                    status = excluded.status,
                    review_count = vocab_progress.review_count + 1,
                    last_reviewed = CURRENT_TIMESTAMP
            """, (word_id, status))
            count += 1
    conn.close()
    return count

def create_student_otp(email: str, student_number: str = "") -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT created_at FROM student_otps
        WHERE email = ? AND is_used = 0
        ORDER BY id DESC LIMIT 1
    """, (email.lower(),))
    row = cursor.fetchone()
    now = datetime.now(timezone.utc)
    if row and row["created_at"]:
        try:
            created_time = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            diff = (now - created_time).total_seconds()
            if diff < 60:
                remaining = 60 - int(diff)
                conn.close()
                return {"success": False, "cooldown": remaining, "detail": f"Lütfen yeni bir kod istemeden önce {remaining} saniye bekleyin."}
        except Exception:
            pass

    otp_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = (now + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO student_otps (email, student_number, otp_code, created_at, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (email.lower(), student_number, otp_code, created_at_str, expires_at))
    conn.commit()
    conn.close()

    return {
        "success": True,
        "email": email.lower(),
        "otp_code": otp_code,
        "cooldown_seconds": 60,
        "expires_in_seconds": 300,
        "message": f"6 haneli doğrulama kodu {email} adresine gönderildi."
    }

def verify_student_otp(email: str, otp_code: str, user_id: int = 1) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


    cursor.execute("""
        SELECT id, otp_code, attempts, expires_at, is_used, student_number
        FROM student_otps
        WHERE email = ? AND is_used = 0
        ORDER BY id DESC LIMIT 1
    """, (email.lower(),))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "detail": "Aktif bir doğrulama kodu bulunamadı. Lütfen yeni bir kod talep edin."}

    otp_id = row["id"]
    expected_code = row["otp_code"]
    attempts = row["attempts"]
    expires_at = row["expires_at"]

    if attempts >= 5:
        conn.close()
        return {"success": False, "detail": "Çok fazla hatalı deneme yaptınız. Lütfen yeni bir kod talep edin."}

    if expires_at and now > expires_at:
        conn.close()
        return {"success": False, "detail": "Doğrulama kodunun 5 dakikalık süresi dolmuştur. Lütfen yeni bir kod talep edin."}

    if otp_code.strip() != expected_code:
        cursor.execute("UPDATE student_otps SET attempts = attempts + 1 WHERE id = ?", (otp_id,))
        conn.commit()
        remaining_attempts = 5 - (attempts + 1)
        conn.close()
        return {"success": False, "detail": f"Geçersiz doğrulama kodu. Kalan deneme hakkı: {remaining_attempts}"}

    cursor.execute("UPDATE student_otps SET is_used = 1 WHERE id = ?", (otp_id,))
    cursor.execute("""
        UPDATE users 
        SET is_verified_student = 1, verification_status = 'verified'
        WHERE id = ? OR email = ?
    """, (user_id, email.lower()))
    cursor.execute("""
        INSERT INTO student_verifications (user_id, university_id, edu_email, student_id_number, verification_type, verification_status, notes)
        VALUES (?, 'itu', ?, ?, 'otp_email', 'verified', '6-digit OTP verification successful')
    """, (user_id, email.lower(), row["student_number"] or ""))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "verification_status": "verified",
        "message": "Tebrikler! Öğrenci e-postanız ve hesabınız başarıyla doğrulandı."
    }


