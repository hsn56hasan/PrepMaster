import sqlite3
import json
import hashlib
import os
import secrets
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, timezone

import re
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from security import hash_password, verify_password
except ImportError:
    from backend.security import hash_password, verify_password

_DEFAULT_DB_PATH = (
    Path("/data/prepmaster.db")
    if Path("/data").is_dir()
    else (Path(__file__).resolve().parent.parent / "prepmaster.db")
)
DB_PATH = Path(os.getenv("PREPMASTER_DB_PATH", str(_DEFAULT_DB_PATH)))

def get_db():
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    # timeout: aynı anda yazan iki istek "database is locked" yerine kısa süre beklesin
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

_PER_USER_TABLES = {
    # tablo: (yeni şema, kopyalanacak sütunlar)
    "vocab_progress": (
        """CREATE TABLE vocab_progress (
            user_id INTEGER NOT NULL,
            word_id TEXT NOT NULL,
            status TEXT DEFAULT 'learning',
            review_count INTEGER DEFAULT 1,
            last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, word_id)
        )""",
        ["word_id", "status", "review_count", "last_reviewed"],
    ),
    "question_bookmarks": (
        """CREATE TABLE question_bookmarks (
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, question_id)
        )""",
        ["question_id", "note", "created_at"],
    ),
    "mistake_vault": (
        """CREATE TABLE mistake_vault (
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            university_id TEXT,
            level TEXT,
            category TEXT,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_answer TEXT,
            last_wrong_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            resolved_at TEXT,
            PRIMARY KEY (user_id, question_id)
        )""",
        ["question_id", "university_id", "level", "category", "wrong_count",
         "last_wrong_answer", "last_wrong_at", "is_resolved", "resolved_at"],
    ),
}


def _migrate_per_user_tables(conn) -> None:
    """
    Eski şemada (anahtar yalnızca kelime/soru kimliği) duran tabloları
    (user_id, kimlik) anahtarlı şemaya taşır. Eski satırlar kendi user_id'leriyle
    (çoğu varsayılan 1) korunur. Göçten önce veritabanının bir yedeği alınır.
    """
    pending = []
    for table in _PER_USER_TABLES:
        info = conn.execute(f"PRAGMA table_info({table})").fetchall()
        if not info:
            continue  # tablo yok: CREATE IF NOT EXISTS yeni şemayla kuracak
        pk_cols = [r[1] for r in sorted(info, key=lambda r: r[5]) if r[5] > 0]
        if pk_cols[:1] != ["user_id"]:
            pending.append(table)
    if not pending:
        return

    if DB_PATH.exists() and DB_PATH.stat().st_size > 0:
        backup = DB_PATH.with_name(DB_PATH.name + ".yedek-kullanici-gocu-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
        # SQLite'ın kendi yedekleme API'si: WAL günlüğündeki veriler de yedeğe girer
        conn.commit()
        dst = sqlite3.connect(backup)
        with dst:
            conn.backup(dst)
        dst.close()

    with conn:
        for table in pending:
            new_sql, cols = _PER_USER_TABLES[table]
            old_cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
            copy_cols = [c for c in cols if c in old_cols]
            conn.execute(f"ALTER TABLE {table} RENAME TO {table}__eski")
            conn.execute(new_sql)
            user_expr = "COALESCE(user_id, 1)" if "user_id" in old_cols else "1"
            col_list = ", ".join(copy_cols)
            conn.execute(
                f"INSERT OR IGNORE INTO {table} (user_id, {col_list}) "
                f"SELECT {user_expr}, {col_list} FROM {table}__eski"
            )
            conn.execute(f"DROP TABLE {table}__eski")


def init_db():
    conn = get_db()
    # WAL: okumalar yazmayı beklemez, eşzamanlı öğrencilerde kilitlenme azalır (dosyaya kalıcı yazılır)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    _migrate_per_user_tables(conn)
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

        -- Kullanıcı bazlı ilerleme tabloları: anahtar (user_id, kayıt_id).
        -- Eskiden anahtar yalnızca kelime/soru kimliğiydi ve tüm öğrenciler aynı satırı paylaşıyordu.
        CREATE TABLE IF NOT EXISTS vocab_progress (
            user_id INTEGER NOT NULL,
            word_id TEXT NOT NULL,
            status TEXT DEFAULT 'learning',
            review_count INTEGER DEFAULT 1,
            last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, word_id)
        );

        CREATE TABLE IF NOT EXISTS question_bookmarks (
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, question_id)
        );

        CREATE TABLE IF NOT EXISTS mistake_vault (
            user_id INTEGER NOT NULL,
            question_id TEXT NOT NULL,
            university_id TEXT,
            level TEXT,
            category TEXT,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_answer TEXT,
            last_wrong_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            resolved_at TEXT,
            PRIMARY KEY (user_id, question_id)
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
        conn.execute("ALTER TABLE users ADD COLUMN unlocked_universities TEXT DEFAULT '[\"general\"]'")
    if "verified_university" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN verified_university TEXT")
    # Onay kayıtları: kullanıcı sözleşmesi (zorunlu) ve açık rıza (isteğe bağlı) ne zaman verildi
    if "terms_accepted_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN terms_accepted_at TEXT")
    if "explicit_consent_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN explicit_consent_at TEXT")
    if "last_study_date" not in cols:
        # Seri için İstanbul takvim günü (YYYY-MM-DD); last_active'ten ayrı tutulur
        # çünkü last_active profil güncellemesinde de değişiyor.
        conn.execute("ALTER TABLE users ADD COLUMN last_study_date TEXT")

    all_26_unis_json = json.dumps([
        "general", "itu", "boun", "metu", "bilkent", "ytu", "hacettepe",
        "ankara", "gazi", "ege", "koc", "sabanci", "marmara", "istanbul",
        "cerrahpasa", "dokuz_eylul", "iyte", "anadolu", "eskisehir_teknik",
        "gebze_teknik", "akdeniz", "cukurova", "uludag", "ozyegin",
        "bahcesehir", "yeditepe", "tobb"
    ])
    conn.execute("""
        INSERT OR IGNORE INTO users
        (email, username, password_hash, full_name, university_id, student_number,
         is_verified_student, verification_status, verified_university, unlocked_universities)
        VALUES (?, ?, ?, ?, ?, ?, 1, 'verified', ?, ?)
    """, (
        "toprakcihasan5@gmail.com",
        "Hasan",
        "pbkdf2:sha256:100000$18ebd2a7479259eb01c558ec811410cb$be5a705d2cd170cf46b14e0373b7e5047f3e395bc9fe4dae1cac889534db5f45",
        "Hasan Toprakcı",
        "ankara",
        "2024091823",
        "ankara",
        json.dumps(["general", "ankara"]),
    ))
    conn.execute("""
        INSERT OR IGNORE INTO users
        (email, username, password_hash, full_name, university_id, student_number,
         is_verified_student, verification_status, verified_university, unlocked_universities)
        VALUES (?, ?, ?, ?, ?, ?, 1, 'verified', ?, ?)
    """, (
        "deneme@prepmaster.test",
        "deneme",
        "pbkdf2:sha256:100000$f3905b1dbf6046be6015f5aedb24251d$50f81ef115dc8ee19bf36e88a03eeb30788bbda53792b430611967b8a5c5ae83",
        "Deneme Öğrenci",
        "itu",
        "20260001",
        "itu",
        all_26_unis_json,
    ))
    conn.execute("""
        UPDATE users
        SET unlocked_universities = ?,
            is_verified_student = 1,
            verification_status = 'verified',
            verified_university = COALESCE(verified_university, university_id, 'itu')
        WHERE LOWER(username) = 'deneme'
          AND (unlocked_universities IS NULL OR LENGTH(unlocked_universities) < 40)
    """, (all_26_unis_json,))

    cursor.execute("PRAGMA table_info(student_verifications)")
    s_cols = [r[1] for r in cursor.fetchall()]
    if "verification_status" not in s_cols:
        conn.execute("ALTER TABLE student_verifications ADD COLUMN verification_status TEXT DEFAULT 'pending'")

    cursor.execute("PRAGMA table_info(exam_attempts)")
    ea_cols = [r[1] for r in cursor.fetchall()]
    if ea_cols and "user_id" not in ea_cols:
        conn.execute("ALTER TABLE exam_attempts ADD COLUMN user_id INTEGER DEFAULT 1")

    conn.executescript("""
        -- PayTR siparişleri: kilit yalnızca imzalı bildirim gelince ve sipariş
        -- 'pending' iken BİR KEZ açılır (PayTR aynı bildirimi birden çok kez gönderebilir).
        CREATE TABLE IF NOT EXISTS paytr_orders (
            merchant_oid TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            university_id TEXT NOT NULL,
            amount_kurus INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',   -- pending | success | failed | amount_mismatch
            total_amount_kurus INTEGER,
            failed_reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,
            pre_info_accepted_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_paytr_orders_user ON paytr_orders(user_id);

        CREATE TABLE IF NOT EXISTS university_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            university_id TEXT,
            price_try REAL DEFAULT 50.0,
            payment_reference TEXT,
            card_last_four TEXT,
            gib_receipt_no TEXT,
            tax_amount REAL DEFAULT 8.33,
            net_amount REAL DEFAULT 41.67,
            currency TEXT DEFAULT 'TRY',
            receipt_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    cursor.execute("PRAGMA table_info(university_purchases)")
    p_cols = [r[1] for r in cursor.fetchall()]
    if "gib_receipt_no" not in p_cols:
        conn.execute("ALTER TABLE university_purchases ADD COLUMN gib_receipt_no TEXT")
    if "tax_amount" not in p_cols:
        conn.execute("ALTER TABLE university_purchases ADD COLUMN tax_amount REAL DEFAULT 8.33")
    if "net_amount" not in p_cols:
        conn.execute("ALTER TABLE university_purchases ADD COLUMN net_amount REAL DEFAULT 41.67")
    if "currency" not in p_cols:
        conn.execute("ALTER TABLE university_purchases ADD COLUMN currency TEXT DEFAULT 'TRY'")
    if "receipt_json" not in p_cols:
        conn.execute("ALTER TABLE university_purchases ADD COLUMN receipt_json TEXT")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS payment_3ds_sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER DEFAULT 1,
            university_id TEXT NOT NULL,
            card_holder TEXT,
            card_number_masked TEXT,
            amount_try REAL DEFAULT 50.0,
            sms_code TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 3,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_3ds_sessions_user ON payment_3ds_sessions(user_id);")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            reset_code TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            max_attempts INTEGER DEFAULT 5,
            is_used INTEGER DEFAULT 0,
            used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            expires_at TEXT NOT NULL
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_password_resets_email ON password_resets(email);")

    cursor.execute("PRAGMA table_info(password_resets)")
    pr_cols = [r[1] for r in cursor.fetchall()]
    if "is_used" not in pr_cols:
        conn.execute("ALTER TABLE password_resets ADD COLUMN is_used INTEGER DEFAULT 0")
    if "used" not in pr_cols:
        conn.execute("ALTER TABLE password_resets ADD COLUMN used INTEGER DEFAULT 0")

    if "kvkk_accepted_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN kvkk_accepted_at TEXT")
        conn.execute("UPDATE users SET kvkk_accepted_at = COALESCE(created_at, CURRENT_TIMESTAMP) WHERE kvkk_accepted_at IS NULL")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            category TEXT DEFAULT 'general',
            message TEXT NOT NULL,
            status TEXT DEFAULT 'open',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    conn.close()

# Auto-initialize on import
init_db()

def get_profile(user_id: int) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, email, username, full_name, university_id, current_level, target_score, streak_days, 
               is_verified_student, verification_status, student_number, last_active,
               unlocked_universities, verified_university, last_study_date
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

        # Yalnızca belgeyle DOĞRULANMIŞ üniversite açık sayılır (check_university_access ile aynı kural);
        # kayıtta seçilen university_id tek başına kilidi açmaz.
        is_ver = bool(data.get("is_verified_student") == 1 or data.get("verification_status") == "verified")
        verified_uni = data.get("verified_university") or (data.get("university_id") if is_ver else None)
        if verified_uni and verified_uni not in unlocked:
            unlocked.append(verified_uni)
        if "general" not in unlocked:
            unlocked.append("general")

        data["unlocked_universities"] = unlocked
        data["verified_university"] = verified_uni
        data["streak_days"] = _effective_streak(data.get("streak_days"), data.get("last_study_date"))
        return data

    conn.close()
    # Kullanıcı yok: eskiden burada uydurma "doğrulanmış İTÜ öğrencisi" dönüyordu.
    return {}

def _istanbul_today():
    # Türkiye'de yaz saati yok: UTC+3 sabit.
    return (datetime.now(timezone.utc) + timedelta(hours=3)).date()


def _effective_streak(streak, last_study_date) -> int:
    """Dün ya da bugün çalışılmadıysa seri bozulmuştur: 0 gösterilir."""
    if not last_study_date:
        return 0
    try:
        last = datetime.strptime(str(last_study_date)[:10], "%Y-%m-%d").date()
    except ValueError:
        return 0
    if (_istanbul_today() - last).days > 1:
        return 0
    return int(streak or 0)


def record_study_day(user_id: int) -> int:
    """
    Kullanıcının bugün çalıştığını kaydeder ve güncel seriyi döndürür.
    Aynı gün tekrar çağrılırsa değişmez; dün çalıştıysa +1; daha eskiyse 1'den başlar.
    """
    today = _istanbul_today()
    conn = get_db()
    row = conn.execute("SELECT streak_days, last_study_date FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return 0
    streak = int(row["streak_days"] or 0)
    last = None
    if row["last_study_date"]:
        try:
            last = datetime.strptime(str(row["last_study_date"])[:10], "%Y-%m-%d").date()
        except ValueError:
            last = None
    if last == today:
        conn.close()
        return max(streak, 1)
    streak = streak + 1 if last == today - timedelta(days=1) else 1
    with conn:
        conn.execute("UPDATE users SET streak_days = ?, last_study_date = ? WHERE id = ?",
                     (streak, today.isoformat(), user_id))
    conn.close()
    return streak


def update_profile(user_id: int, university_id: str, current_level: str, target_score: int) -> Dict[str, Any]:
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE users 
            SET university_id = ?, current_level = ?, target_score = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (university_id, current_level, target_score, user_id))
    conn.close()
    return get_profile(user_id)

def create_user(email: str, username: str, password: str, full_name: str, university_id: str = "itu", student_number: str = "",
                terms_accepted: bool = False, explicit_consent: bool = False) -> Dict[str, Any]:
    import json
    conn = get_db()
    pw_hash = hash_password(password)
    # Kayıtta seçilen üniversite belgeyle doğrulanana kadar ücretsiz açılmaz.
    initial_unlocked = json.dumps(["general"])
    with conn:
        cursor = conn.execute("""
            INSERT INTO users (email, username, password_hash, full_name, university_id, student_number, is_verified_student, verification_status, unlocked_universities, verified_university)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'pending', ?, ?)
        """, (email.lower().strip(), username.strip(), pw_hash, full_name.strip(), university_id, student_number.strip(), initial_unlocked, None))
        user_id = cursor.lastrowid
        conn.execute("""
            UPDATE users SET
                terms_accepted_at = CASE WHEN ? THEN CURRENT_TIMESTAMP END,
                explicit_consent_at = CASE WHEN ? THEN CURRENT_TIMESTAMP END
            WHERE id = ?
        """, (1 if terms_accepted else 0, 1 if explicit_consent else 0, user_id))
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

    # Transparently upgrade legacy SHA-256 hash to PBKDF2 and update last_active
    with conn:
        if not stored_hash.startswith("pbkdf2:"):
            upgraded_hash = hash_password(password)
            conn.execute(
                "UPDATE users SET password_hash = ?, last_active = CURRENT_TIMESTAMP WHERE id = ?",
                (upgraded_hash, row["id"])
            )
        else:
            conn.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))

    user_id = row["id"]
    conn.close()

    profile = get_profile(user_id)
    if profile:
        return profile

    user_dict = dict(row)
    user_dict.pop("password_hash", None)
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

def generate_gib_receipt(card_last_four: str = "4242", card_holder: str = "Öğrenci", university_id: str = "general") -> Dict[str, Any]:
    """
    Ödeme ÖZETİ üretir — resmi fatura DEĞİLDİR.
    Eskiden uydurma vergi dairesi/numarası ve "GİB E-Arşiv onaylı" ibaresiyle
    fatura gibi gösteriliyordu; gerçek para alınırken bu yanıltıcı ve yasal risk.
    Gerçek e-Arşiv faturası GİB portalı veya bir entegratör üzerinden ayrıca kesilmelidir.
    """
    seq = secrets.token_hex(2).upper()
    receipt_no = f"PM-2026-{seq}"
    gross_amount = 50.00
    vat_rate = 0.20
    net_amount = round(gross_amount / (1.0 + vat_rate), 2)
    vat_amount = round(gross_amount - net_amount, 2)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "receipt_no": receipt_no,
        "invoice_number": receipt_no,
        "gross_amount": gross_amount,
        "amount": gross_amount,
        "vat_rate": vat_rate,
        "vat_amount": vat_amount,
        "net_amount": net_amount,
        "currency": "TRY",
        "payment_date": now_iso,
        "date": now_iso,
        "card_last_four": (card_last_four or "4242")[-4:],
        "card_holder": card_holder or "Öğrenci",
        "payment_method": "3D Secure Sanal POS (Mastercard/Visa)",
        "university_id": university_id,
        "document_type": "Ödeme özeti (fatura değildir)",
        "description": f"PrepKampüs Hazırlık Sınav Paketi - {university_id.upper()}"
    }

def create_3ds_session(user_id: int, university_id: str, card_holder: str = "", card_number: str = "", amount_try: float = 50.0) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    session_id = f"3DS-{secrets.token_hex(8).upper()}"
    sms_code = f"{secrets.randbelow(900000) + 100000}"
    now = datetime.now(timezone.utc)
    created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")
    expires_at_str = (now + timedelta(seconds=180)).strftime("%Y-%m-%d %H:%M:%S")

    clean_card = re.sub(r"[\s-]", "", card_number or "")
    last_four = clean_card[-4:] if len(clean_card) >= 4 else "0001"
    masked_card = f"**** **** **** {last_four}"
    masked_phone = "+90 (532) *** ** 42"

    cursor.execute("""
        INSERT INTO payment_3ds_sessions (
            session_id, user_id, university_id, card_holder, card_number_masked,
            amount_try, sms_code, attempts, max_attempts, status, created_at, expires_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 3, 'pending', ?, ?)
    """, (
        session_id, user_id, university_id, card_holder or "Öğrenci", masked_card,
        amount_try, sms_code, created_at_str, expires_at_str
    ))
    conn.commit()
    conn.close()

    return {
        "status": "success",
        "success": True,
        "session_id": session_id,
        "masked_phone": masked_phone,
        "sms_code": sms_code,
        "sms_code_sandbox": sms_code,
        "expires_in_seconds": 180,
        "amount_try": amount_try,
        "amount": amount_try,
        "currency": "TRY",
        "university_id": university_id,
        "message": "3D Secure SMS doğrulama kodu telefonunuza iletildi."
    }

def verify_3ds_code(session_id: str, sms_code: str) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id, user_id, university_id, card_holder, card_number_masked,
               amount_try, sms_code, attempts, max_attempts, status, expires_at
        FROM payment_3ds_sessions
        WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "detail": "Geçersiz veya bulunamayan 3D Secure oturumu."}

    status = row["status"]
    attempts = row["attempts"]
    max_attempts = row["max_attempts"] if row["max_attempts"] is not None else 3
    expires_at = row["expires_at"]
    expected_code = row["sms_code"]

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    if status == "verified":
        conn.close()
        return {"success": False, "detail": "Bu 3D Secure oturumu daha önce kullanılmıştır (tekrar kullanılamaz)."}

    if status == "locked" or attempts >= max_attempts:
        cursor.execute("UPDATE payment_3ds_sessions SET status = 'locked' WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return {"success": False, "detail": "Çok fazla hatalı SMS doğrulama kodu girildi. Oturum kilitlendi."}

    if expires_at and now > expires_at:
        cursor.execute("UPDATE payment_3ds_sessions SET status = 'expired' WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return {"success": False, "detail": "3D Secure SMS doğrulama kodunun süresi dolmuştur. Lütfen yeniden deneyin."}

    # Validate code
    if sms_code.strip() != expected_code.strip():
        new_attempts = attempts + 1
        new_status = "locked" if new_attempts >= max_attempts else "pending"
        cursor.execute("UPDATE payment_3ds_sessions SET attempts = ?, status = ? WHERE session_id = ?", (new_attempts, new_status, session_id))
        conn.commit()
        conn.close()
        if new_attempts >= max_attempts:
            return {"success": False, "detail": "Çok fazla hatalı SMS doğrulama kodu girildi. Oturum kilitlendi."}
        remaining = max_attempts - new_attempts
        return {"success": False, "detail": f"Geçersiz SMS doğrulama kodu. Kalan hak: {remaining}"}

    # Valid code -> Mark verified
    cursor.execute("UPDATE payment_3ds_sessions SET status = 'verified' WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
    return {"success": True, "session": dict(row)}

def unlock_university_membership(
    user_id: int,
    university_id: str,
    card_holder: str = "",
    card_last_four: str = "4242",
    price_try: float = 50.0,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    import json
    receipt = generate_gib_receipt(card_last_four=card_last_four, card_holder=card_holder, university_id=university_id)
    ref = receipt["receipt_no"]

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

    with conn:
        conn.execute("""
            UPDATE users 
            SET unlocked_universities = ?
            WHERE id = ?
        """, (json.dumps(unlocked), user_id))

        conn.execute("""
            INSERT INTO university_purchases (
                user_id, university_id, price_try, payment_reference, card_last_four,
                gib_receipt_no, tax_amount, net_amount, currency, receipt_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            university_id,
            price_try,
            ref,
            card_last_four[-4:] if card_last_four else "4242",
            receipt["receipt_no"],
            receipt["vat_amount"],
            receipt["net_amount"],
            receipt["currency"],
            json.dumps(receipt)
        ))

    conn.close()
    return {
        "status": "success",
        "success": True,
        "message": "Ödeme onaylandı ve üniversite erişimi açıldı.",
        "unlocked_university": university_id,
        "university_id": university_id,
        "unlocked_universities": unlocked,
        "price_try": price_try,
        "reference": ref,
        "invoice_number": ref,
        "receipt": receipt
    }

def check_university_access(user_id: int, university_id: str) -> bool:
    if not university_id or university_id in ["general", "all"]:
        return True
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT university_id, verified_university, unlocked_universities,
               is_verified_student, verification_status
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        # Var olmayan kullanıcı hiçbir kilitli içeriğe erişemez.
        return False

    is_ver = bool(row["is_verified_student"] == 1 or row["verification_status"] == "verified")
    verified_uni = row["verified_university"] or (row["university_id"] if is_ver else None)
    if verified_uni == university_id:
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


def save_exam_attempt(user_id: int, university_id: str, level: str, score: float, total_questions: int,
                      correct_count: int, duration_seconds: int, answers: Dict[str, Any],
                      created_at: Optional[str] = None) -> int:
    conn = get_db()
    with conn:
        cursor = conn.execute("""
            INSERT INTO exam_attempts (user_id, university_id, level, score, total_questions, correct_count,
                                       duration_seconds, answers_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
        """, (user_id, university_id, level, score, total_questions, correct_count, duration_seconds,
              json.dumps(answers), created_at))
        attempt_id = cursor.lastrowid
    conn.close()
    return attempt_id


def get_exam_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    conn = get_db()
    rows = conn.execute("""
        SELECT id, university_id, level, score, total_questions, correct_count, duration_seconds, created_at
        FROM exam_attempts
        WHERE user_id = ?
        ORDER BY id DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_vocab_status(user_id: int, word_id: str, status: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO vocab_progress (user_id, word_id, status, review_count, last_reviewed)
            VALUES (?, ?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, word_id) DO UPDATE SET
                status = excluded.status,
                review_count = review_count + 1,
                last_reviewed = CURRENT_TIMESTAMP
        """, (user_id, word_id, status))
    conn.close()


def get_vocab_progress(user_id: int) -> Dict[str, str]:
    conn = get_db()
    rows = conn.execute("SELECT word_id, status FROM vocab_progress WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return {r["word_id"]: r["status"] for r in rows}


def record_mistake(user_id: int, question_id: str, university_id: str, level: str, category: str,
                   wrong_answer: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            INSERT INTO mistake_vault (user_id, question_id, university_id, level, category, wrong_count,
                                       last_wrong_answer, last_wrong_at, is_resolved)
            VALUES (?, ?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP, 0)
            ON CONFLICT(user_id, question_id) DO UPDATE SET
                wrong_count = wrong_count + 1,
                last_wrong_answer = excluded.last_wrong_answer,
                last_wrong_at = CURRENT_TIMESTAMP,
                is_resolved = 0,
                resolved_at = NULL
        """, (user_id, question_id, university_id, level, category, wrong_answer))
    conn.close()


def resolve_mistake(user_id: int, question_id: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE mistake_vault
            SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND question_id = ?
        """, (user_id, question_id))
    conn.close()


def delete_mistake(user_id: int, question_id: str) -> None:
    conn = get_db()
    with conn:
        conn.execute("DELETE FROM mistake_vault WHERE user_id = ? AND question_id = ?", (user_id, question_id))
    conn.close()


def get_mistakes(user_id: int, is_resolved: bool = False) -> List[Dict[str, Any]]:
    conn = get_db()
    rows = conn.execute("""
        SELECT question_id, university_id, level, category, wrong_count, last_wrong_answer, last_wrong_at,
               is_resolved, resolved_at
        FROM mistake_vault
        WHERE user_id = ? AND is_resolved = ?
        ORDER BY last_wrong_at DESC
    """, (user_id, 1 if is_resolved else 0)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_mistake_count(user_id: int) -> int:
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS cnt FROM mistake_vault WHERE user_id = ? AND is_resolved = 0",
                       (user_id,)).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def bulk_upsert_mistakes(user_id: int, mistakes: List[Dict[str, Any]]) -> int:
    """
    Mobilin çevrimdışıyken biriktirdiği YENİ yanlışları ekler. Çözülmüş bir hatayı
    yeniden açar (öğrenci soruyu tekrar yanlış yaptı); asla "çözüldü" olarak işaretlemez —
    çözme işlemleri ayrı listeyle (resolved_mistakes) gelir.
    """
    conn = get_db()
    count = 0
    with conn:
        for m in mistakes:
            qid = str(m.get("question_id") or "")[:100]
            if not qid:
                continue
            conn.execute("""
                INSERT INTO mistake_vault (user_id, question_id, university_id, level, category, wrong_count,
                                           last_wrong_answer, last_wrong_at, is_resolved)
                VALUES (?, ?, ?, ?, ?, 1, ?, COALESCE(?, CURRENT_TIMESTAMP), 0)
                ON CONFLICT(user_id, question_id) DO UPDATE SET
                    wrong_count = mistake_vault.wrong_count + 1,
                    last_wrong_answer = excluded.last_wrong_answer,
                    last_wrong_at = excluded.last_wrong_at,
                    is_resolved = 0,
                    resolved_at = NULL
            """, (
                user_id, qid,
                str(m.get("university_id") or "general")[:50],
                str(m.get("level") or "B2")[:10],
                str(m.get("category") or "General")[:100],
                str(m.get("last_wrong_answer") or "")[:5],
                m.get("last_wrong_at"),
            ))
            count += 1
    conn.close()
    return count


def bulk_resolve_mistakes(user_id: int, question_ids: List[str]) -> int:
    conn = get_db()
    count = 0
    with conn:
        for qid in question_ids:
            cur = conn.execute("""
                UPDATE mistake_vault SET is_resolved = 1, resolved_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND question_id = ? AND is_resolved = 0
            """, (user_id, str(qid)[:100]))
            count += cur.rowcount
    conn.close()
    return count


def bulk_upsert_vocab_progress(user_id: int, vocab_map: Dict[str, str]) -> int:
    conn = get_db()
    count = 0
    with conn:
        for word_id, status in vocab_map.items():
            if status not in ("mastered", "learning", "unreviewed"):
                continue
            conn.execute("""
                INSERT INTO vocab_progress (user_id, word_id, status, last_reviewed)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, word_id) DO UPDATE SET
                    status = excluded.status,
                    review_count = vocab_progress.review_count + 1,
                    last_reviewed = CURRENT_TIMESTAMP
            """, (user_id, str(word_id)[:100], status))
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


def upsert_google_user(email: str, name: str = "", avatar_url: str = "") -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    clean_email = email.lower().strip()
    cursor.execute("SELECT id, full_name FROM users WHERE LOWER(email) = ?", (clean_email,))
    row = cursor.fetchone()

    if row:
        user_id = row["id"]
        if name and (not row["full_name"] or row["full_name"] == "İTÜ Hazırlık Öğrencisi"):
            with conn:
                conn.execute("""
                    UPDATE users
                    SET full_name = ?, last_active = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (name.strip(), user_id))
        conn.close()
        return get_profile(user_id)

    # User does not exist, provision a new user
    raw_prefix = clean_email.split("@")[0]
    clean_username = re.sub(r"[^a-zA-Z0-9_]", "_", raw_prefix)[:30] or "student"

    cursor.execute("SELECT id FROM users WHERE LOWER(username) = ?", (clean_username.lower(),))
    if cursor.fetchone():
        clean_username = f"{clean_username}_{secrets.token_hex(2)}"

    display_name = name.strip() if name and name.strip() else clean_username
    initial_unlocked = json.dumps(["general"])
    dummy_oauth_hash = f"oauth2:google:{secrets.token_hex(16)}"

    with conn:
        cur = conn.execute("""
            INSERT INTO users (
                email, username, password_hash, full_name, university_id, 
                student_number, is_verified_student, verification_status, 
                unlocked_universities, verified_university
            )
            VALUES (?, ?, ?, ?, 'itu', '', 0, 'pending', ?, NULL)
        """, (clean_email, clean_username, dummy_oauth_hash, display_name, initial_unlocked))
        new_user_id = cur.lastrowid

    conn.close()
    return get_profile(new_user_id)


def create_paytr_order(merchant_oid: str, user_id: int, university_id: str, amount_kurus: int) -> None:
    """Sipariş, ödeme öncesi onay (ön bilgilendirme + cayma istisnası) alındıktan sonra açılır; onay zamanı saklanır."""
    conn = get_db()
    cols = {r[1] for r in conn.execute("PRAGMA table_info(paytr_orders)").fetchall()}
    if "pre_info_accepted_at" not in cols:
        conn.execute("ALTER TABLE paytr_orders ADD COLUMN pre_info_accepted_at TEXT")
    with conn:
        conn.execute("""
            INSERT INTO paytr_orders (merchant_oid, user_id, university_id, amount_kurus, status, pre_info_accepted_at)
            VALUES (?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        """, (merchant_oid, user_id, university_id, amount_kurus))
    conn.close()


def get_paytr_order(merchant_oid: str) -> Optional[Dict[str, Any]]:
    conn = get_db()
    row = conn.execute("SELECT * FROM paytr_orders WHERE merchant_oid = ?", (merchant_oid,)).fetchone()
    conn.close()
    return dict(row) if row else None


def finish_paytr_order(merchant_oid: str, new_status: str, total_amount_kurus: Optional[int],
                       failed_reason: str = "") -> bool:
    """
    Siparişi 'pending'den new_status'e taşır. Yalnızca bu çağrı taşıdıysa True döner;
    böylece aynı bildirim ikinci kez geldiğinde kilit ikinci kez açılmaz.
    """
    conn = get_db()
    with conn:
        cur = conn.execute("""
            UPDATE paytr_orders
            SET status = ?, total_amount_kurus = ?, failed_reason = ?, updated_at = CURRENT_TIMESTAMP
            WHERE merchant_oid = ? AND status = 'pending'
        """, (new_status, total_amount_kurus, failed_reason[:300], merchant_oid))
        changed = cur.rowcount == 1
    conn.close()
    return changed


def user_exists_with_email(email: str) -> bool:
    conn = get_db()
    row = conn.execute("SELECT 1 FROM users WHERE LOWER(email) = ?", (email.lower().strip(),)).fetchone()
    conn.close()
    return row is not None


def request_password_reset(email: str) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    clean_email = email.lower().strip()

    # Cooldown check: enforce 60s cooldown per email
    cursor.execute("""
        SELECT created_at FROM password_resets
        WHERE LOWER(email) = ? AND (is_used = 0 OR used = 0)
        ORDER BY id DESC LIMIT 1
    """, (clean_email,))
    row = cursor.fetchone()
    now = datetime.now(timezone.utc)
    if row and row["created_at"]:
        try:
            created_time = datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
            diff = (now - created_time).total_seconds()
            if diff < 60:
                remaining = 60 - int(diff)
                conn.close()
                return {
                    "success": False,
                    "cooldown": True,
                    "remaining_seconds": remaining,
                    "detail": f"Lütfen yeni bir kod istemeden önce {remaining} saniye bekleyin."
                }
        except Exception:
            pass

    reset_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = (now + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
    created_at_str = now.strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        conn.execute("""
            INSERT INTO password_resets (email, reset_code, attempts, max_attempts, is_used, used, created_at, expires_at)
            VALUES (?, ?, 0, 5, 0, 0, ?, ?)
        """, (clean_email, reset_code, created_at_str, expires_at))

    conn.close()
    return {
        "status": "success",
        "success": True,
        "email": clean_email,
        "reset_code": reset_code,
        "reset_code_sandbox": reset_code,
        "demo_code": reset_code,
        "cooldown_seconds": 60,
        "expires_in_seconds": 900,
        "message": "Şifre sıfırlama kodu e-posta adresinize gönderildi."
    }


def confirm_password_reset(email: str, reset_code: str, new_password: str) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    clean_email = email.lower().strip()
    clean_code = str(reset_code).strip()

    cursor.execute("""
        SELECT id, reset_code, attempts, max_attempts, is_used, used, expires_at
        FROM password_resets
        WHERE LOWER(email) = ?
        ORDER BY id DESC LIMIT 1
    """, (clean_email,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return {"success": False, "detail": "Aktif bir şifre sıfırlama kodu bulunamadı."}

    # Anti-replay: one-time consumption check
    if row["is_used"] != 0 or row["used"] != 0:
        conn.close()
        return {"success": False, "detail": "Bu şifre sıfırlama kodu daha önce kullanılmıştır veya geçersizdir."}

    max_att = row["max_attempts"] if row["max_attempts"] is not None else 5
    if row["attempts"] >= max_att:
        conn.close()
        return {"success": False, "detail": "Çok fazla hatalı kod denemesi yapıldı. Lütfen yeni bir kod talep edin."}

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if row["expires_at"] and now_str > row["expires_at"]:
        conn.close()
        return {"success": False, "detail": "Şifre sıfırlama kodunun süresi dolmuştur. Lütfen yeni bir kod talep edin."}

    if clean_code != row["reset_code"].strip():
        with conn:
            conn.execute("UPDATE password_resets SET attempts = attempts + 1 WHERE id = ?", (row["id"],))
        conn.close()
        return {"success": False, "detail": "Geçersiz şifre sıfırlama kodu."}

    # Code is valid! Update user password and mark code used
    pw_hash = hash_password(new_password)
    with conn:
        conn.execute("UPDATE password_resets SET is_used = 1, used = 1 WHERE id = ?", (row["id"],))
        conn.execute("UPDATE users SET password_hash = ? WHERE LOWER(email) = ?", (pw_hash, clean_email))

    conn.close()
    return {
        "status": "success",
        "success": True,
        "message": "Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz."
    }


# =============================================================================
# YÖNETİCİ PANELİ (ADMIN) VERİTABANI İŞLEMLERİ
# =============================================================================

def admin_list_students(
    search: str = "",
    university_filter: str = "",
    verification_filter: str = ""
) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, username, full_name, university_id, student_number,
               is_verified_student, verification_status, verified_university,
               unlocked_universities, current_level, target_score, streak_days,
               created_at, last_active
        FROM users
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()

    # Sınav istatistiklerini tek sorguda topla
    exam_map = {}
    try:
        cursor.execute("""
            SELECT COALESCE(user_id, 1) as uid, COUNT(*) as exam_count, ROUND(AVG(score), 1) as avg_score
            FROM exam_attempts
            GROUP BY COALESCE(user_id, 1)
        """)
        exam_map = {r["uid"]: {"exam_count": r["exam_count"], "avg_score": r["avg_score"] or 0.0} for r in cursor.fetchall()}
    except Exception:
        exam_map = {}

    # Son doğrulama kayıtlarını topla
    verif_map = {}
    try:
        cursor.execute("""
            SELECT user_id, university_id, edu_email, student_id_number, verification_type,
                   verification_status, notes, verified_at
            FROM student_verifications
            ORDER BY id ASC
        """)
        for vr in cursor.fetchall():
            verif_map[vr["user_id"]] = dict(vr)
    except Exception:
        verif_map = {}

    # Satın alma istatistikleri
    total_purchases = 0
    total_revenue = 0.0
    try:
        cursor.execute("SELECT COUNT(*) as cnt, COALESCE(SUM(price_try), 0) as rev FROM university_purchases")
        p_row = cursor.fetchone()
        total_purchases = p_row["cnt"] if p_row else 0
        total_revenue = round(float(p_row["rev"] or 0.0), 2) if p_row else 0.0
    except Exception:
        pass

    students = []
    verified_total = 0
    unverified_total = 0
    total_exams_all = sum(v["exam_count"] for v in exam_map.values())

    q = (search or "").strip().lower()
    uni_f = (university_filter or "").strip().lower()
    ver_f = (verification_filter or "").strip().lower()

    for r in rows:
        u = dict(r)
        is_ver = bool(u.get("is_verified_student") == 1 or u.get("verification_status") == "verified")
        if is_ver:
            verified_total += 1
        else:
            unverified_total += 1

        try:
            unlocked = json.loads(u.get("unlocked_universities") or '["general"]')
            if not isinstance(unlocked, list):
                unlocked = ["general"]
        except Exception:
            unlocked = ["general"]

        if is_ver and u.get("verified_university") and u["verified_university"] not in unlocked:
            unlocked.append(u["verified_university"])
        if "general" not in unlocked:
            unlocked.append("general")

        u["unlocked_universities"] = unlocked
        u["is_verified"] = is_ver
        u["exam_count"] = exam_map.get(u["id"], {}).get("exam_count", 0)
        u["avg_score"] = exam_map.get(u["id"], {}).get("avg_score", 0.0)
        u["latest_verification"] = verif_map.get(u["id"])

        # Filtreleme
        if q:
            haystack = " ".join([
                str(u.get("full_name") or ""),
                str(u.get("username") or ""),
                str(u.get("email") or ""),
                str(u.get("student_number") or ""),
                str(u.get("university_id") or "")
            ]).lower()
            if q not in haystack:
                continue

        if uni_f and uni_f != "all":
            if (u.get("university_id") or "").lower() != uni_f and uni_f not in [x.lower() for x in unlocked]:
                continue

        if ver_f == "verified" and not is_ver:
            continue
        if ver_f == "unverified" and is_ver:
            continue

        students.append(u)

    conn.close()
    return {
        "summary": {
            "total_students": len(rows),
            "verified_students": verified_total,
            "unverified_students": unverified_total,
            "total_exams_completed": total_exams_all,
            "total_purchases": total_purchases,
            "total_revenue_try": total_revenue
        },
        "students": students
    }


def admin_update_student_access(
    user_id: int,
    unlocked_universities: List[str],
    primary_university_id: Optional[str] = None,
    is_verified: Optional[bool] = None,
    student_number: Optional[str] = None,
    admin_note: str = ""
) -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"success": False, "detail": "Öğrenci kaydı bulunamadı."}

    current = dict(row)

    # Temiz üniversite listesi oluştur
    clean_unlocked = []
    for uid in (unlocked_universities or []):
        s = str(uid).strip().lower()
        if s and s not in clean_unlocked:
            clean_unlocked.append(s)
    if "general" not in clean_unlocked:
        clean_unlocked.append("general")

    new_uni_id = (primary_university_id or current.get("university_id") or "itu").strip().lower()
    new_stu_no = student_number.strip() if student_number is not None else (current.get("student_number") or "")

    # Yönetici öğrenciye herhangi bir üniversite paketi tanımladıysa (general dışında),
    # öğrenci hesabı otomatik olarak doğrulanmış kabul edilir ki giriş-çıkış yaptığında
    # belge doğrulama kapısına takılmasın ve tanımlanan üniversiteler kalıcı olarak açık kalsın.
    has_granted_unis = any(u != "general" for u in clean_unlocked)

    if is_verified is None:
        if has_granted_unis:
            ver_int = 1
            ver_status = "verified"
            ver_uni = current.get("verified_university") or new_uni_id
        else:
            ver_int = current.get("is_verified_student", 0)
            ver_status = current.get("verification_status", "unverified")
            ver_uni = current.get("verified_university")
    elif is_verified or has_granted_unis:
        ver_int = 1
        ver_status = "verified"
        ver_uni = new_uni_id
        if new_uni_id not in clean_unlocked:
            clean_unlocked.append(new_uni_id)
    else:
        ver_int = 0
        ver_status = "unverified"
        ver_uni = None

    with conn:
        conn.execute("""
            UPDATE users
            SET university_id = ?,
                student_number = ?,
                is_verified_student = ?,
                verification_status = ?,
                verified_university = ?,
                unlocked_universities = ?
            WHERE id = ?
        """, (
            new_uni_id,
            new_stu_no,
            ver_int,
            ver_status,
            ver_uni,
            json.dumps(clean_unlocked),
            user_id
        ))

        if is_verified is not None:
            note_txt = admin_note.strip() or (
                f"Yönetici paneli üzerinden {'onaylandı' if is_verified else 'onay kaldırıldı'}. "
                f"Açık okullar: {', '.join(clean_unlocked)}"
            )
            conn.execute("""
                INSERT INTO student_verifications
                (user_id, university_id, edu_email, student_id_number, verification_type, verification_status, notes)
                VALUES (?, ?, ?, ?, 'admin_panel', ?, ?)
            """, (
                user_id,
                new_uni_id,
                current.get("email") or "",
                new_stu_no,
                ver_status,
                note_txt
            ))

    conn.close()
    return {
        "success": True,
        "user_id": user_id,
        "university_id": new_uni_id,
        "is_verified": bool(ver_int == 1),
        "verification_status": ver_status,
        "unlocked_universities": clean_unlocked,
        "student_number": new_stu_no,
        "message": "Öğrenci üniversite erişim yetkileri ve doğrulama durumu güncellendi."
    }


def admin_reset_student_password(user_id: int, new_password: str) -> Dict[str, Any]:
    if not new_password or len(new_password.strip()) < 6:
        return {"success": False, "detail": "Yeni şifre en az 6 karakter olmalıdır."}
    conn = get_db()
    row = conn.execute("SELECT id, email, full_name FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return {"success": False, "detail": "Öğrenci bulunamadı."}

    pw_hash = hash_password(new_password.strip())
    with conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (pw_hash, user_id))
    conn.close()
    return {
        "success": True,
        "message": f"{row['full_name'] or row['email']} adlı öğrencinin şifresi güncellendi."
    }


def admin_delete_student(user_id: int) -> Dict[str, Any]:
    if user_id == 1:
        return {"success": False, "detail": "Varsayılan sistem öğrenci hesabı (ID: 1) silinemez."}
    conn = get_db()
    row = conn.execute("SELECT id, full_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return {"success": False, "detail": "Öğrenci bulunamadı."}

    with conn:
        conn.execute("DELETE FROM student_verifications WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM exam_attempts WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM vocab_progress WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM question_bookmarks WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM mistake_vault WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.close()
    return {
        "success": True,
        "message": f"{row['full_name'] or row['email']} adlı öğrenci kaydı silindi."
    }


def create_support_ticket(
    message: str,
    category: str = "general",
    full_name: str = "",
    email: str = "",
    phone: str = "",
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    conn = get_db()
    with conn:
        cur = conn.execute("""
            INSERT INTO support_tickets (user_id, full_name, email, phone, category, message, status)
            VALUES (?, ?, ?, ?, ?, ?, 'open')
        """, (
            user_id,
            (full_name or "").strip(),
            (email or "").strip(),
            (phone or "").strip(),
            (category or "general").strip(),
            (message or "").strip(),
        ))
        tid = cur.lastrowid
    conn.close()
    return {
        "success": True,
        "ticket_id": tid,
        "message": "Destek talebiniz başarıyla kaydedildi. En kısa sürede size dönüş yapılacaktır."
    }


def list_support_tickets(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db()
    rows = conn.execute("""
        SELECT id, user_id, full_name, email, phone, category, message, status, created_at
        FROM support_tickets
        ORDER BY id DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]




