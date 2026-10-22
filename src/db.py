import json
import sqlite3
from datetime import datetime, timezone

from config import DATA_DIR, SQLITE_PATH


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS advisories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                language TEXT,
                generated_answer TEXT,
                final_answer TEXT,
                trust_score REAL,
                verdict TEXT,
                sources_json TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_advisory(record: dict) -> int:
    init_db()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO advisories (
                question, language, generated_answer, final_answer,
                trust_score, verdict, sources_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["question"],
                record.get("language", "en"),
                record.get("generated_answer", ""),
                record["final_answer"],
                record["trust_score"],
                record["verdict"],
                json.dumps(record.get("sources", []), ensure_ascii=False),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)


def list_advisories(limit: int = 20) -> list[dict]:
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, question, language, final_answer, trust_score, verdict,
                   sources_json, created_at
            FROM advisories
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    history = []
    for row in rows:
        item = dict(row)
        item["sources"] = json.loads(item.pop("sources_json") or "[]")
        history.append(item)
    return history
