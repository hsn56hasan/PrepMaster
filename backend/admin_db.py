"""
Yönetici paneli veritabanı işlemleri: genel bakış, sipariş/destek/izin yönetimi, öğrenci ayrıntısı,
site duyurusu, soru düzeltmeleri (gizle/düzelt) ve yönetici işlem kaydı.
Bu modül yalnızca admin uçlarından çağrılır; öğrenciye açık hiçbir uç bu fonksiyonları kullanmaz.
"""
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

try:
    from database import get_db, _istanbul_today
except ImportError:  # paket olarak içe aktarıldığında
    from backend.database import get_db, _istanbul_today

TICKET_STATUSES = ("open", "in_progress", "answered", "closed")
ORDER_STATUSES = ("pending", "success", "failed", "amount_mismatch")
QUESTION_PATCH_FIELDS = ("question", "options", "correct_answer", "explanation_tr", "explanation_en")

# Hesap silinince kaldırılan kişisel ilerleme tabloları. Ödeme/sipariş ve onay kayıtları
# (vergi mevzuatı ve KVKK ispat yükü nedeniyle) saklanır; Aydınlatma Metni'ndeki saklama sürelerine bakın.
USER_DATA_TABLES = (
    "student_verifications", "exam_attempts", "vocab_progress", "question_bookmarks", "mistake_vault",
    "question_progress", "daily_activity", "lesson_progress",
)


def _cols(conn, table: str) -> List[str]:
    return [r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def init_admin_tables() -> None:
    conn = get_db()
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS admin_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin TEXT,
                action TEXT NOT NULL,
                target TEXT,
                detail TEXT,
                ip TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS site_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS question_overrides (
                question_id TEXT PRIMARY KEY,
                hidden INTEGER DEFAULT 0,
                patch_json TEXT,
                note TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cols = _cols(conn, "support_tickets")
        if cols and "admin_note" not in cols:
            conn.execute("ALTER TABLE support_tickets ADD COLUMN admin_note TEXT")
        if cols and "updated_at" not in cols:
            conn.execute("ALTER TABLE support_tickets ADD COLUMN updated_at TEXT")
    conn.close()


# ---------------- Yönetici işlem kaydı ----------------

def log_admin_action(action: str, target: str = "", detail: str = "", admin: str = "", ip: str = "") -> None:
    conn = get_db()
    with conn:
        conn.execute(
            "INSERT INTO admin_audit_log (admin, action, target, detail, ip) VALUES (?, ?, ?, ?, ?)",
            (admin[:80], action[:80], str(target)[:120], (detail or "")[:500], (ip or "")[:64]),
        )
    conn.close()


def list_audit_log(limit: int = 200) -> List[Dict[str, Any]]:
    conn = get_db()
    rows = conn.execute(
        "SELECT id, admin, action, target, detail, ip, created_at FROM admin_audit_log ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------- Genel bakış ----------------

def admin_overview(days: int = 14) -> Dict[str, Any]:
    conn = get_db()
    one = lambda sql, args=(): (conn.execute(sql, args).fetchone() or [0])[0] or 0  # noqa: E731
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    d7 = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    d30 = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    # daily_activity günleri İstanbul takvimine göre tutulur
    today_ist = _istanbul_today()
    today = today_ist.isoformat()
    week_ago_ist = (today_ist - timedelta(days=7)).isoformat()

    users = {
        "total": one("SELECT COUNT(*) FROM users"),
        "new_7d": one("SELECT COUNT(*) FROM users WHERE created_at >= ?", (d7,)),
        "new_30d": one("SELECT COUNT(*) FROM users WHERE created_at >= ?", (d30,)),
        "verified": one("SELECT COUNT(*) FROM users WHERE is_verified_student = 1 OR verification_status = 'verified'"),
        "marketing_consent": one("SELECT COUNT(*) FROM users WHERE marketing_consent = 1"),
        "placement_done": one("SELECT COUNT(*) FROM users WHERE placement_level IS NOT NULL"),
    }
    users["active_today"] = one("SELECT COUNT(DISTINCT user_id) FROM daily_activity WHERE day = ?", (today,))
    users["active_7d"] = one(
        "SELECT COUNT(DISTINCT user_id) FROM daily_activity WHERE day >= ?", (week_ago_ist,)
    )

    orders = {s: one("SELECT COUNT(*) FROM paytr_orders WHERE status = ?", (s,)) for s in ORDER_STATUSES}
    revenue_paytr = one("SELECT COALESCE(SUM(COALESCE(total_amount_kurus, amount_kurus)), 0) FROM paytr_orders WHERE status = 'success'") / 100
    revenue_30d = one(
        "SELECT COALESCE(SUM(COALESCE(total_amount_kurus, amount_kurus)), 0) FROM paytr_orders WHERE status = 'success' AND created_at >= ?",
        (d30,),
    ) / 100
    paying_users = one("SELECT COUNT(DISTINCT user_id) FROM paytr_orders WHERE status = 'success'")

    tickets = {s: one("SELECT COUNT(*) FROM support_tickets WHERE COALESCE(status, 'open') = ?", (s,)) for s in TICKET_STATUSES}

    learning = {
        "exams": one("SELECT COUNT(*) FROM exam_attempts"),
        "lessons_completed": one("SELECT COUNT(*) FROM lesson_progress WHERE stars > 0"),
        "questions_answered_7d": one(
            "SELECT COALESCE(SUM(questions_answered), 0) FROM daily_activity WHERE day >= ?",
            (week_ago_ist,),
        ),
        "open_mistakes": one("SELECT COUNT(*) FROM mistake_vault WHERE is_resolved = 0"),
    }

    start = (now - timedelta(days=days - 1)).strftime("%Y-%m-%d")
    signups = {r[0]: r[1] for r in conn.execute(
        "SELECT substr(created_at, 1, 10) AS d, COUNT(*) FROM users WHERE substr(created_at, 1, 10) >= ? GROUP BY d", (start,)
    ).fetchall()}
    sales = {r[0]: r[1] for r in conn.execute(
        "SELECT substr(created_at, 1, 10) AS d, COUNT(*) FROM paytr_orders WHERE status = 'success' AND substr(created_at, 1, 10) >= ? GROUP BY d",
        (start,),
    ).fetchall()}
    series = []
    for i in range(days):
        d = (now - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        series.append({"day": d, "signups": signups.get(d, 0), "sales": sales.get(d, 0)})

    uni_rows = conn.execute(
        "SELECT university_id, COUNT(*) AS n FROM users GROUP BY university_id ORDER BY n DESC LIMIT 10"
    ).fetchall()
    conn.close()
    return {
        "users": users,
        "orders": orders,
        "revenue": {"total_try": round(revenue_paytr, 2), "last_30d_try": round(revenue_30d, 2), "paying_users": paying_users},
        "tickets": tickets,
        "learning": learning,
        "daily": series,
        "top_universities": [dict(r) for r in uni_rows],
    }


# ---------------- Siparişler ----------------

def admin_list_orders(status: str = "", search: str = "", limit: int = 300) -> Dict[str, Any]:
    conn = get_db()
    sql = """
        SELECT o.merchant_oid, o.user_id, o.university_id, o.amount_kurus, o.total_amount_kurus, o.status,
               o.failed_reason, o.created_at, o.updated_at, o.pre_info_accepted_at,
               u.full_name, u.email, u.username
        FROM paytr_orders o LEFT JOIN users u ON u.id = o.user_id
    """
    where, args = [], []
    if status and status in ORDER_STATUSES:
        where.append("o.status = ?")
        args.append(status)
    q = (search or "").strip().lower()
    if q:
        where.append("(lower(o.merchant_oid) LIKE ? OR lower(COALESCE(u.email,'')) LIKE ? OR lower(COALESCE(u.full_name,'')) LIKE ? OR lower(o.university_id) LIKE ?)")
        args += [f"%{q}%"] * 4
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY o.created_at DESC LIMIT ?"
    args.append(limit)
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    for r in rows:
        r["amount_try"] = round((r.get("total_amount_kurus") or r.get("amount_kurus") or 0) / 100, 2)
    return {"orders": rows, "count": len(rows)}


# ---------------- Destek talepleri ----------------

def admin_list_tickets(status: str = "", limit: int = 300) -> List[Dict[str, Any]]:
    conn = get_db()
    sql = """SELECT id, user_id, full_name, email, phone, category, message, COALESCE(status, 'open') AS status,
                    admin_note, created_at, updated_at FROM support_tickets"""
    args: List[Any] = []
    if status and status in TICKET_STATUSES:
        sql += " WHERE COALESCE(status, 'open') = ?"
        args.append(status)
    sql += " ORDER BY CASE COALESCE(status, 'open') WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END, id DESC LIMIT ?"
    args.append(limit)
    rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
    conn.close()
    return rows


def admin_update_ticket(ticket_id: int, status: Optional[str], admin_note: Optional[str]) -> Dict[str, Any]:
    if status is not None and status not in TICKET_STATUSES:
        return {"success": False, "detail": "Geçersiz durum."}
    conn = get_db()
    row = conn.execute("SELECT id FROM support_tickets WHERE id = ?", (ticket_id,)).fetchone()
    if not row:
        conn.close()
        return {"success": False, "detail": "Destek talebi bulunamadı."}
    with conn:
        if status is not None:
            conn.execute("UPDATE support_tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (status, ticket_id))
        if admin_note is not None:
            conn.execute("UPDATE support_tickets SET admin_note = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                         (admin_note.strip()[:2000], ticket_id))
    conn.close()
    return {"success": True}


# ---------------- Öğrenci ayrıntısı ve dışa aktarma ----------------

_PUBLIC_USER_COLS = (
    "id", "email", "username", "full_name", "university_id", "student_number", "is_verified_student",
    "verification_status", "verified_university", "unlocked_universities", "current_level", "target_score",
    "streak_days", "created_at", "last_active", "last_study_date", "placement_level", "placement_at",
    "terms_accepted_at", "privacy_notice_ack_at", "marketing_consent", "marketing_consent_at",
)


def admin_student_detail(user_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    cols = [c for c in _PUBLIC_USER_COLS if c in _cols(conn, "users")]
    row = conn.execute(f"SELECT {', '.join(cols)} FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return None
    user = dict(row)
    try:
        user["unlocked_universities"] = json.loads(user.get("unlocked_universities") or '["general"]')
    except Exception:
        user["unlocked_universities"] = ["general"]

    def rows(sql, args=(user_id,)):
        return [dict(r) for r in conn.execute(sql, args).fetchall()]

    detail = {
        "user": user,
        "orders": rows("""SELECT merchant_oid, university_id, amount_kurus, total_amount_kurus, status, failed_reason,
                                 created_at, updated_at FROM paytr_orders WHERE user_id = ? ORDER BY created_at DESC"""),
        "purchases": rows("""SELECT university_id, price_try, payment_reference, created_at
                             FROM university_purchases WHERE user_id = ? ORDER BY id DESC"""),
        "exams": rows("""SELECT university_id, level, score, total_questions, correct_count, duration_seconds, created_at
                         FROM exam_attempts WHERE user_id = ? ORDER BY id DESC LIMIT 20"""),
        "consents": rows("""SELECT doc_key, doc_version, action, channel, created_at
                            FROM consent_log WHERE user_id = ? ORDER BY id DESC LIMIT 50"""),
        "verifications": rows("""SELECT university_id, verification_type, verification_status, notes, verified_at
                                 FROM student_verifications WHERE user_id = ? ORDER BY id DESC LIMIT 10"""),
        "tickets": rows("""SELECT id, category, message, COALESCE(status,'open') AS status, created_at
                           FROM support_tickets WHERE user_id = ? ORDER BY id DESC LIMIT 20"""),
    }
    act = conn.execute(
        """SELECT COUNT(*) AS days, COALESCE(SUM(questions_answered),0) AS answered, COALESCE(SUM(questions_correct),0) AS correct,
                  COALESCE(SUM(vocab_reviews),0) AS vocab, MAX(day) AS last_day
           FROM daily_activity WHERE user_id = ?""", (user_id,)).fetchone()
    lp = conn.execute(
        "SELECT COUNT(*) AS lessons, COALESCE(SUM(xp_total),0) AS xp FROM lesson_progress WHERE user_id = ? AND stars > 0",
        (user_id,)).fetchone()
    mv = conn.execute(
        "SELECT COUNT(*) FROM mistake_vault WHERE user_id = ? AND is_resolved = 0", (user_id,)).fetchone()
    detail["activity"] = {**dict(act), "lessons_completed": lp["lessons"], "lesson_xp": lp["xp"], "open_mistakes": mv[0]}
    conn.close()
    return detail


def admin_students_export_rows() -> List[Dict[str, Any]]:
    conn = get_db()
    cols = [c for c in _PUBLIC_USER_COLS if c in _cols(conn, "users")]
    rows = [dict(r) for r in conn.execute(f"SELECT {', '.join(cols)} FROM users ORDER BY id").fetchall()]
    conn.close()
    return rows


def admin_marketing_consents() -> List[Dict[str, Any]]:
    """Ticari ileti onayı veren öğrenciler (İYS'ye yüklemek ve e-posta listesi için)."""
    conn = get_db()
    rows = [dict(r) for r in conn.execute(
        """SELECT id, full_name, email, marketing_consent_at FROM users
           WHERE marketing_consent = 1 AND email IS NOT NULL ORDER BY marketing_consent_at DESC"""
    ).fetchall()]
    conn.close()
    return rows


def admin_consent_summary() -> Dict[str, Any]:
    conn = get_db()
    rows = [dict(r) for r in conn.execute(
        """SELECT doc_key, action, COUNT(*) AS n, MAX(created_at) AS last_at
           FROM consent_log GROUP BY doc_key, action ORDER BY doc_key, action"""
    ).fetchall()]
    conn.close()
    return {"by_document": rows}


def admin_delete_user_everywhere(user_id: int) -> Dict[str, Any]:
    """Öğrenci hesabını ve kişisel ilerleme verilerini siler. Sipariş, satın alma ve onay kayıtları
    yasal saklama yükümlülüğü nedeniyle tutulur (kullanıcı satırı silindiği için kimlik bilgisi kalmaz)."""
    if user_id == 1:
        return {"success": False, "detail": "Varsayılan sistem öğrenci hesabı (ID: 1) silinemez."}
    conn = get_db()
    row = conn.execute("SELECT id, full_name, email FROM users WHERE id = ?", (user_id,)).fetchone()
    if not row:
        conn.close()
        return {"success": False, "detail": "Öğrenci bulunamadı."}
    with conn:
        for table in USER_DATA_TABLES:
            if "user_id" in _cols(conn, table):
                conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))
        if row["email"]:
            for table in ("student_otps", "password_resets"):
                if "email" in _cols(conn, table):
                    conn.execute(f"DELETE FROM {table} WHERE lower(email) = lower(?)", (row["email"],))
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.close()
    return {"success": True, "message": f"{row['full_name'] or row['email']} adlı öğrenci kaydı silindi."}


# ---------------- Site ayarları (duyuru) ----------------

def get_setting(key: str, default: Any = None) -> Any:
    conn = get_db()
    row = conn.execute("SELECT value FROM site_settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    if not row:
        return default
    try:
        return json.loads(row["value"])
    except Exception:
        return default


def set_setting(key: str, value: Any) -> None:
    conn = get_db()
    with conn:
        conn.execute(
            """INSERT INTO site_settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP""",
            (key, json.dumps(value, ensure_ascii=False)),
        )
    conn.close()


# ---------------- Soru düzeltmeleri ----------------

def list_question_overrides() -> Dict[str, Dict[str, Any]]:
    conn = get_db()
    rows = conn.execute("SELECT question_id, hidden, patch_json, note, updated_at FROM question_overrides").fetchall()
    conn.close()
    out = {}
    for r in rows:
        try:
            patch = json.loads(r["patch_json"] or "{}")
        except Exception:
            patch = {}
        out[r["question_id"]] = {"hidden": bool(r["hidden"]), "patch": patch, "note": r["note"], "updated_at": r["updated_at"]}
    return out


def save_question_override(question_id: str, hidden: bool, patch: Dict[str, Any], note: str = "") -> None:
    clean = {k: v for k, v in (patch or {}).items() if k in QUESTION_PATCH_FIELDS}
    conn = get_db()
    with conn:
        if not hidden and not clean:
            conn.execute("DELETE FROM question_overrides WHERE question_id = ?", (question_id,))
        else:
            conn.execute(
                """INSERT INTO question_overrides (question_id, hidden, patch_json, note, updated_at)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(question_id) DO UPDATE SET hidden = excluded.hidden, patch_json = excluded.patch_json,
                       note = excluded.note, updated_at = CURRENT_TIMESTAMP""",
                (question_id, 1 if hidden else 0, json.dumps(clean, ensure_ascii=False), (note or "")[:300]),
            )
    conn.close()


def apply_question_overrides(questions: Iterable[Dict[str, Any]], overrides: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Gizlenen soruları çıkarır, düzeltilen alanları uygular (orijinal listeyi değiştirmez)."""
    out = []
    for q in questions:
        ov = overrides.get(q.get("id"))
        if not ov:
            out.append(q)
            continue
        if ov.get("hidden"):
            continue
        out.append({**q, **ov.get("patch", {})})
    return out
