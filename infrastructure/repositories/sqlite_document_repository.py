from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core.document_inbox import DocumentMetadata, DocumentRecord


class SQLiteDocumentRepository:
    """Durable adapter for the canonical ``DocumentRepository`` contract."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._memory_connection: sqlite3.Connection | None = None
        if str(db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, record: DocumentRecord) -> DocumentRecord:
        metadata = record.metadata
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id, title, source_name, media_type, author,
                    issued_at, expires_at, tags_json, content, category, status,
                    content_hash, linked_household_entry_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(document_id) DO UPDATE SET
                    title=excluded.title,
                    source_name=excluded.source_name,
                    media_type=excluded.media_type,
                    author=excluded.author,
                    issued_at=excluded.issued_at,
                    expires_at=excluded.expires_at,
                    tags_json=excluded.tags_json,
                    content=excluded.content,
                    category=excluded.category,
                    status=excluded.status,
                    content_hash=excluded.content_hash,
                    linked_household_entry_id=excluded.linked_household_entry_id,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    record.document_id,
                    metadata.title,
                    metadata.source_name,
                    metadata.media_type,
                    metadata.author,
                    metadata.issued_at.isoformat() if metadata.issued_at else None,
                    metadata.expires_at.isoformat() if metadata.expires_at else None,
                    json.dumps(metadata.tags, ensure_ascii=False),
                    record.content,
                    record.normalized_category.value,
                    record.normalized_status.value,
                    record.effective_hash,
                    record.linked_household_entry_id,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ),
            )
        return record

    def get(self, document_id: str) -> DocumentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return self._decode(row) if row else None

    def get_by_hash(self, content_hash: str) -> DocumentRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE content_hash = ?",
                (content_hash,),
            ).fetchone()
        return self._decode(row) if row else None

    def list_all(self) -> tuple[DocumentRecord, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM documents ORDER BY created_at, document_id"
            ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    author TEXT,
                    issued_at TEXT,
                    expires_at TEXT,
                    tags_json TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content_hash TEXT NOT NULL UNIQUE,
                    linked_household_entry_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        if str(self.db_path) == ":memory:":
            if self._memory_connection is None:
                self._memory_connection = sqlite3.connect(":memory:")
                self._memory_connection.row_factory = sqlite3.Row
            return self._memory_connection
        connection = sqlite3.connect(str(self.db_path))
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _decode(row: sqlite3.Row) -> DocumentRecord:
        metadata = DocumentMetadata(
            title=row["title"],
            source_name=row["source_name"],
            media_type=row["media_type"],
            author=row["author"],
            issued_at=(
                datetime.fromisoformat(row["issued_at"]) if row["issued_at"] else None
            ),
            expires_at=(
                datetime.fromisoformat(row["expires_at"])
                if row["expires_at"]
                else None
            ),
            tags=tuple(json.loads(row["tags_json"])),
        )
        return DocumentRecord(
            metadata=metadata,
            content=row["content"],
            category=row["category"],
            status=row["status"],
            content_hash=row["content_hash"],
            linked_household_entry_id=row["linked_household_entry_id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            document_id=row["document_id"],
        )
