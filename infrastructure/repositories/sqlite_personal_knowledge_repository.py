from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core.personal_knowledge_base import (
    KnowledgeItem,
    KnowledgeRelation,
)


class SQLitePersonalKnowledgeRepository:
    """Persistent adapter for the existing M74 repository contract."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self._memory_connection: sqlite3.Connection | None = None
        if str(db_path) != ":memory:":
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_item(self, item: KnowledgeItem) -> KnowledgeItem:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO personal_knowledge (
                    item_id, title, content, kind, source, owner, summary,
                    tags_json, confidence, status, source_reference,
                    superseded_by, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    title=excluded.title,
                    content=excluded.content,
                    kind=excluded.kind,
                    source=excluded.source,
                    owner=excluded.owner,
                    summary=excluded.summary,
                    tags_json=excluded.tags_json,
                    confidence=excluded.confidence,
                    status=excluded.status,
                    source_reference=excluded.source_reference,
                    superseded_by=excluded.superseded_by,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                self._item_values(item),
            )
        return item

    def get_item(self, item_id: str) -> KnowledgeItem | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM personal_knowledge WHERE item_id = ?",
                (item_id,),
            ).fetchone()
        return self._decode_item(row) if row else None

    def get_by_fingerprint(self, fingerprint: str) -> KnowledgeItem | None:
        for item in self.list_items():
            if item.fingerprint == fingerprint:
                return item
        return None

    def list_items(self) -> tuple[KnowledgeItem, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM personal_knowledge
                ORDER BY created_at, item_id
                """
            ).fetchall()
        return tuple(self._decode_item(row) for row in rows)

    def save_relation(self, relation: KnowledgeRelation) -> KnowledgeRelation:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO personal_knowledge_relations (
                    relation_id, source_item_id, target_item_id,
                    relation_type, rationale, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(relation_id) DO UPDATE SET
                    source_item_id=excluded.source_item_id,
                    target_item_id=excluded.target_item_id,
                    relation_type=excluded.relation_type,
                    rationale=excluded.rationale,
                    created_at=excluded.created_at
                """,
                (
                    relation.relation_id,
                    relation.source_item_id,
                    relation.target_item_id,
                    relation.normalized_type.value,
                    relation.rationale,
                    relation.created_at.isoformat(),
                ),
            )
        return relation

    def list_relations(self) -> tuple[KnowledgeRelation, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM personal_knowledge_relations
                ORDER BY created_at, relation_id
                """
            ).fetchall()
        return tuple(
            KnowledgeRelation(
                source_item_id=row["source_item_id"],
                target_item_id=row["target_item_id"],
                relation_type=row["relation_type"],
                rationale=row["rationale"],
                created_at=datetime.fromisoformat(row["created_at"]),
                relation_id=row["relation_id"],
            )
            for row in rows
        )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS personal_knowledge (
                    item_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    source_reference TEXT,
                    superseded_by TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS personal_knowledge_relations (
                    relation_id TEXT PRIMARY KEY,
                    source_item_id TEXT NOT NULL,
                    target_item_id TEXT NOT NULL,
                    relation_type TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
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
    def _item_values(item: KnowledgeItem) -> tuple[object, ...]:
        return (
            item.item_id,
            item.title,
            item.content,
            item.normalized_kind.value,
            item.normalized_source.value,
            item.normalized_owner.value,
            item.summary,
            json.dumps(item.normalized_tags, ensure_ascii=False),
            item.confidence,
            item.normalized_status.value,
            item.source_reference,
            item.superseded_by,
            item.created_at.isoformat(),
            item.updated_at.isoformat(),
        )

    @staticmethod
    def _decode_item(row: sqlite3.Row) -> KnowledgeItem:
        return KnowledgeItem(
            item_id=row["item_id"],
            title=row["title"],
            content=row["content"],
            kind=row["kind"],
            source=row["source"],
            owner=row["owner"],
            summary=row["summary"],
            tags=tuple(json.loads(row["tags_json"])),
            confidence=float(row["confidence"]),
            status=row["status"],
            source_reference=row["source_reference"],
            superseded_by=row["superseded_by"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
