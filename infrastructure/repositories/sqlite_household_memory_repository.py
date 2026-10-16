from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core.household_memory import HouseholdMemoryEntry


class SQLiteHouseholdMemoryRepository:
    """Persistent repository for ROBY's existing household-memory domain."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, entry: HouseholdMemoryEntry) -> HouseholdMemoryEntry:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO household_knowledge (
                    entry_id, title, details, category, owner, status,
                    due_at, tags_json, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(entry_id) DO UPDATE SET
                    title=excluded.title,
                    details=excluded.details,
                    category=excluded.category,
                    owner=excluded.owner,
                    status=excluded.status,
                    due_at=excluded.due_at,
                    tags_json=excluded.tags_json,
                    source=excluded.source,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    entry.entry_id,
                    entry.title,
                    entry.details,
                    entry.normalized_category.value,
                    entry.normalized_owner.value,
                    entry.normalized_status.value,
                    entry.due_at.isoformat() if entry.due_at else None,
                    json.dumps(entry.normalized_tags, ensure_ascii=False),
                    entry.source,
                    entry.created_at.isoformat(),
                    entry.updated_at.isoformat(),
                ),
            )
        return entry

    def get(self, entry_id: str) -> HouseholdMemoryEntry | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM household_knowledge WHERE entry_id = ?", (entry_id,)
            ).fetchone()
        return self._decode(row) if row else None

    def list_all(self) -> tuple[HouseholdMemoryEntry, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM household_knowledge ORDER BY created_at, entry_id"
            ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS household_knowledge (
                    entry_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    details TEXT NOT NULL,
                    category TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    status TEXT NOT NULL,
                    due_at TEXT,
                    tags_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _decode(row: sqlite3.Row) -> HouseholdMemoryEntry:
        return HouseholdMemoryEntry(
            entry_id=row["entry_id"],
            title=row["title"],
            details=row["details"],
            category=row["category"],
            owner=row["owner"],
            status=row["status"],
            due_at=datetime.fromisoformat(row["due_at"]) if row["due_at"] else None,
            tags=tuple(json.loads(row["tags_json"])),
            source=row["source"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
