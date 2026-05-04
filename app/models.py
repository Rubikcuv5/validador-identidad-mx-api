import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.environ.get("DB_PATH", "audit.db")


def _conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with _conn() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT NOT NULL,
                doc_value TEXT NOT NULL,
                is_valid INTEGER NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
            )"""
        )


def save_audit(doc_type: str, doc_value: str, is_valid: bool, reason: str):
    with _conn() as con:
        con.execute(
            "INSERT INTO audit_log (doc_type, doc_value, is_valid, reason, created_at) VALUES (?,?,?,?,?)",
            (doc_type, doc_value, int(is_valid), reason, datetime.now(timezone.utc).isoformat()),
        )


def get_audit_log(limit: int = 50) -> list[dict]:
    with _conn() as con:
        rows = con.execute(
            "SELECT id, doc_type, doc_value, is_valid, reason, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "id": r[0],
            "doc_type": r[1],
            "doc_value": r[2],
            "is_valid": bool(r[3]),
            "reason": r[4],
            "created_at": r[5],
        }
        for r in rows
    ]


init_db()
