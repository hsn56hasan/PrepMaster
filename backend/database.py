import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "prepmaster.db"

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

        CREATE TABLE IF NOT EXISTS exam_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            status TEXT DEFAULT 'learning',
            review_count INTEGER DEFAULT 1,
            last_reviewed TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS question_bookmarks (
            question_id TEXT PRIMARY KEY,
            note TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS mistake_vault (
            question_id TEXT PRIMARY KEY,
            university_id TEXT,
            level TEXT,
            category TEXT,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_answer TEXT,
            last_wrong_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_resolved INTEGER DEFAULT 0,
            resolved_at TEXT
        );
    """)
    conn.close()

# Auto-initialize on import
init_db()

def get_profile() -> Dict[str, Any]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT university_id, current_level, target_score, streak_days, last_active FROM user_profile WHERE id = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "university_id": "itu",
        "current_level": "B2",
        "target_score": 65,
        "streak_days": 1,
        "last_active": datetime.now().isoformat()
    }

def update_profile(university_id: str, current_level: str, target_score: int) -> Dict[str, Any]:
    conn = get_db()
    with conn:
        conn.execute("""
            UPDATE user_profile 
            SET university_id = ?, current_level = ?, target_score = ?, last_active = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (university_id, current_level, target_score))
    conn.close()
    return get_profile()

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

