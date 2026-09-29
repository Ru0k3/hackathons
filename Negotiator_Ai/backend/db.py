from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).resolve().parent.parent / "negotiator.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_profiles (
              username TEXT PRIMARY KEY,
              timezone TEXT NOT NULL,
              busy_text TEXT NOT NULL,
              preferences_text TEXT NOT NULL,
              updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def upsert_user_profile(
    *,
    username: str,
    timezone_name: str,
    busy_text: str,
    preferences_text: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_profiles(username, timezone, busy_text, preferences_text, updated_at)
            VALUES(?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
              timezone=excluded.timezone,
              busy_text=excluded.busy_text,
              preferences_text=excluded.preferences_text,
              updated_at=excluded.updated_at
            """,
            (username, timezone_name, busy_text, preferences_text, now),
        )
        conn.commit()
    return get_user_profile(username)


def get_user_profile(username: str) -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT username, timezone, busy_text, preferences_text, updated_at FROM user_profiles WHERE username=?",
            (username,),
        ).fetchone()
        if not row:
            raise KeyError(f"Unknown user: {username}")
        return dict(row)


def list_users() -> list[str]:
    with _connect() as conn:
        rows = conn.execute("SELECT username FROM user_profiles ORDER BY username").fetchall()
        return [r["username"] for r in rows]

