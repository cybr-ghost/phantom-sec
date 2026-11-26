"""Local SQLite history and preferences. Data stays on the user's machine."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def default_database() -> Path:
    base = Path.home() / ".local" / "share" / "phantom-sec"
    base.mkdir(parents=True, exist_ok=True)
    return base / "phantom-sec.sqlite3"


class Store:
    def __init__(self, database: Path | None = None):
        self.database = database or default_database()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                result_json TEXT NOT NULL
            )""")
            connection.execute("""CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )""")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database)

    def record_run(self, module_id: str, result: dict[str, Any]) -> None:
        payload = json.dumps(result, sort_keys=True, default=str)
        with self._connect() as connection:
            connection.execute("INSERT INTO runs(module_id, created_at, result_json) VALUES (?, ?, ?)",
                               (module_id, datetime.now(timezone.utc).isoformat(), payload))

    def history(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT id, module_id, created_at, result_json FROM runs ORDER BY id DESC LIMIT ?",
                (max(1, min(limit, 500)),)
            ).fetchall()
        return [{"id": row[0], "module_id": row[1], "created_at": row[2],
                 "result": json.loads(row[3])} for row in rows]

    def set_setting(self, key: str, value: str) -> None:
        with self._connect() as connection:
            connection.execute("INSERT INTO settings(key, value) VALUES (?, ?) "
                               "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with self._connect() as connection:
            row = connection.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return row[0] if row else default
