from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory


@dataclass(frozen=True)
class CognitiveMemoryRecord:
    """Registro persistente de un aprendizaje cognitivo de ROBY."""

    id: int
    content: str
    category: LearningCategory
    confidence: float
    reason: str
    tags: tuple[str, ...]
    metadata: dict[str, str]
    created_at: str
    last_accessed_at: str | None = None
    access_count: int = 0


@dataclass(frozen=True)
class CognitiveMemoryStoreConfig:
    """Configuración mínima del store cognitivo local."""

    db_path: str | Path
    schema_version: int = 1
    max_content_length: int = 4000
    enable_wal: bool = True


@dataclass(frozen=True)
class CognitiveMemorySearch:
    query: str | None = None
    category: LearningCategory | None = None
    tag: str | None = None
    created_at_from: str | None = None
    created_at_before: str | None = None
    limit: int = 20


class CognitiveMemoryStore:
    """
    DB cerebral local para aprendizajes aprobados por la política cognitiva.

    M36 persiste recuerdos estructurados en SQLite, sin embeddings, sin
    recuperación semántica y sin comportamiento proactivo. Es una base local,
    portable y testeable para que milestones posteriores agreguen recall,
    compactación y políticas de retención.
    """

    def __init__(self, config: CognitiveMemoryStoreConfig) -> None:
        self.config = config
        self.db_path = Path(config.db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def store_candidate_idempotent(
        self,
        candidate: LearningCandidate,
        *,
        idempotency_key: str,
    ) -> tuple[int, bool]:
        if candidate.action is not LearningAction.STORE:
            raise ValueError("only_store_candidates_can_be_persisted")
        normalized_key = idempotency_key.strip()
        if not normalized_key:
            raise ValueError("idempotency_key_cannot_be_empty")

        content = self._normalize_content(candidate.content)
        created_at = self._now()

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                """
                SELECT memory_id
                FROM cognitive_memory_idempotency
                WHERE idempotency_key = ?
                """,
                (normalized_key,),
            ).fetchone()
            if existing is not None:
                return int(existing["memory_id"]), False

            cursor = connection.execute(
                """
                INSERT INTO cognitive_memories (
                    content,
                    category,
                    confidence,
                    reason,
                    tags_json,
                    metadata_json,
                    created_at,
                    access_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    content,
                    candidate.category.value,
                    candidate.confidence,
                    candidate.reason,
                    self._dump_json(tuple(candidate.tags)),
                    self._dump_json(candidate.metadata),
                    created_at,
                ),
            )
            memory_id = int(cursor.lastrowid)
            connection.execute(
                """
                INSERT INTO cognitive_memory_idempotency (
                    idempotency_key,
                    memory_id,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (normalized_key, memory_id, created_at),
            )
            return memory_id, True



    def apply_governed_revision_atomic(
        self,
        *,
        target_memory_id: str,
        target_category: str,
        expected_current_content: str,
        expected_target_fingerprint: str,
        replacement_content: str,
        replacement_idempotency_key: str,
        revision_request_id: str,
        revision_proposal_id: str,
        revision_approval_id: str,
        application_proposal_id: str,
        corrective_evidence_ids: tuple[str, ...],
        revision_proposal_fingerprint: str,
        human_approval_fingerprint: str,
        application_proposal_fingerprint: str,
        target_owner: str,
    ) -> tuple[int, bool]:
        """Atomically replace an exact active memory and supersede its prior version."""
        try:
            memory_id = int(target_memory_id)
        except ValueError as exc:
            raise ValueError("governed revision target id must be numeric") from exc
        normalized_replacement = self._normalize_content(replacement_content)
        normalized_key = replacement_idempotency_key.strip()
        if not normalized_key:
            raise ValueError("governed revision requires replacement idempotency key")

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM cognitive_memories WHERE id = ?",
                (memory_id,),
            ).fetchone()
            if row is None:
                raise ValueError("governed revision target not found")

            current = self._record_from_row(row)
            target_fingerprint = sha256(
                repr(
                    (
                        target_owner,
                        target_memory_id,
                        current.category.value,
                        current.content,
                    )
                ).encode("utf-8")
            ).hexdigest()
            if current.category.value != target_category:
                raise ValueError("governed revision target category changed")
            if current.content != self._normalize_content(expected_current_content):
                raise ValueError("governed revision target content changed")
            if target_fingerprint != expected_target_fingerprint:
                raise ValueError("governed revision target fingerprint changed")

            existing = connection.execute(
                """
                SELECT memory_id
                FROM cognitive_memory_idempotency
                WHERE idempotency_key = ?
                """,
                (normalized_key,),
            ).fetchone()
            if existing is not None:
                replacement_id = int(existing["memory_id"])
                replacement = connection.execute(
                    "SELECT metadata_json FROM cognitive_memories WHERE id = ?",
                    (replacement_id,),
                ).fetchone()
                if replacement is None:
                    raise RuntimeError("revision idempotency points to missing memory")
                replacement_metadata = dict(
                    json.loads(str(replacement["metadata_json"]))
                )
                if (
                    replacement_metadata.get("revision_request_id")
                    != revision_request_id
                    or current.metadata.get("superseded_by")
                    != str(replacement_id)
                ):
                    raise ValueError("revision idempotency lineage conflict")
                return replacement_id, False

            if current.metadata.get("status", "active") != "active":
                raise ValueError("governed revision target is not active")

            created_at = self._now()
            replacement_metadata = dict(current.metadata)
            replacement_metadata.update(
                {
                    "status": "active",
                    "supersedes": str(memory_id),
                    "revision_request_id": revision_request_id,
                    "revision_proposal_id": revision_proposal_id,
                    "revision_approval_id": revision_approval_id,
                    "application_proposal_id": application_proposal_id,
                    "corrective_evidence_ids": json.dumps(
                        corrective_evidence_ids,
                        ensure_ascii=False,
                    ),
                    "revision_proposal_fingerprint": revision_proposal_fingerprint,
                    "human_approval_fingerprint": human_approval_fingerprint,
                    "application_proposal_fingerprint": (
                        application_proposal_fingerprint
                    ),
                    "replacement_idempotency_key": normalized_key,
                }
            )
            replacement_metadata.pop("superseded_by", None)
            cursor = connection.execute(
                """
                INSERT INTO cognitive_memories (
                    content,
                    category,
                    confidence,
                    reason,
                    tags_json,
                    metadata_json,
                    created_at,
                    access_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    normalized_replacement,
                    current.category.value,
                    current.confidence,
                    current.reason,
                    self._dump_json(current.tags),
                    self._dump_json(replacement_metadata),
                    created_at,
                ),
            )
            replacement_id = int(cursor.lastrowid)

            prior_metadata = dict(current.metadata)
            prior_metadata.update(
                {
                    "status": "superseded",
                    "superseded_by": str(replacement_id),
                    "revision_request_id": revision_request_id,
                    "revision_proposal_id": revision_proposal_id,
                    "revision_approval_id": revision_approval_id,
                    "application_proposal_id": application_proposal_id,
                }
            )
            connection.execute(
                """
                UPDATE cognitive_memories
                SET metadata_json = ?
                WHERE id = ?
                """,
                (self._dump_json(prior_metadata), memory_id),
            )
            connection.execute(
                """
                INSERT INTO cognitive_memory_idempotency (
                    idempotency_key,
                    memory_id,
                    created_at
                )
                VALUES (?, ?, ?)
                """,
                (normalized_key, replacement_id, created_at),
            )
            return replacement_id, True

    def store_candidate(self, candidate: LearningCandidate) -> int:
        if candidate.action is not LearningAction.STORE:
            msg = "only_store_candidates_can_be_persisted"
            raise ValueError(msg)

        content = self._normalize_content(candidate.content)
        created_at = self._now()

        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO cognitive_memories (
                    content,
                    category,
                    confidence,
                    reason,
                    tags_json,
                    metadata_json,
                    created_at,
                    access_count
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    content,
                    candidate.category.value,
                    candidate.confidence,
                    candidate.reason,
                    self._dump_json(tuple(candidate.tags)),
                    self._dump_json(candidate.metadata),
                    created_at,
                ),
            )
            return int(cursor.lastrowid)

    def get(self, memory_id: int) -> CognitiveMemoryRecord | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM cognitive_memories
                WHERE id = ?
                """,
                (memory_id,),
            ).fetchone()

            if row is None:
                return None

            accessed_at = self._now()
            connection.execute(
                """
                UPDATE cognitive_memories
                SET last_accessed_at = ?, access_count = access_count + 1
                WHERE id = ?
                """,
                (accessed_at, memory_id),
            )

        updated = dict(row)
        updated["last_accessed_at"] = accessed_at
        updated["access_count"] = int(updated["access_count"]) + 1
        return self._record_from_row(updated)

    def search(
        self,
        criteria: CognitiveMemorySearch,
    ) -> tuple[CognitiveMemoryRecord, ...]:
        limit = max(1, min(criteria.limit, 100))
        clauses: list[str] = []
        values: list[Any] = []

        if criteria.query:
            clauses.append("content LIKE ?")
            values.append(f"%{criteria.query.strip().lower()}%")
        if criteria.category:
            clauses.append("category = ?")
            values.append(criteria.category.value)
        if criteria.tag:
            clauses.append("tags_json LIKE ?")
            values.append(f'%"{criteria.tag}"%')
        if criteria.created_at_from:
            clauses.append("created_at >= ?")
            values.append(criteria.created_at_from)
        if criteria.created_at_before:
            clauses.append("created_at < ?")
            values.append(criteria.created_at_before)

        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)

        with self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM cognitive_memories
                {where_sql}
                ORDER BY id DESC
                LIMIT ?
                """,
                values,
            ).fetchall()

        return tuple(self._record_from_row(row) for row in rows)

    def update_content(
        self,
        memory_id: int,
        content: str,
        *,
        metadata: dict[str, str] | None = None,
    ) -> bool:
        normalized = self._normalize_content(content)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_json FROM cognitive_memories WHERE id = ?",
                (memory_id,),
            ).fetchone()
            if row is None:
                return False
            merged = dict(json.loads(str(row["metadata_json"])))
            merged.update(metadata or {})
            cursor = connection.execute(
                """
                UPDATE cognitive_memories
                SET content = ?, metadata_json = ?
                WHERE id = ?
                """,
                (normalized, self._dump_json(merged), memory_id),
            )
        return cursor.rowcount == 1

    def archive(self, memory_id: int, *, archived_at: str | None = None) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT metadata_json FROM cognitive_memories WHERE id = ?",
                (memory_id,),
            ).fetchone()
            if row is None:
                return False
            metadata = dict(json.loads(str(row["metadata_json"])))
            metadata["status"] = "archived"
            metadata["archived_at"] = archived_at or self._now()
            cursor = connection.execute(
                "UPDATE cognitive_memories SET metadata_json = ? WHERE id = ?",
                (self._dump_json(metadata), memory_id),
            )
        return cursor.rowcount == 1

    def count(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM cognitive_memories"
            ).fetchone()
        return int(row["total"])

    def schema_version(self) -> int:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT version
                FROM cognitive_memory_schema
                ORDER BY applied_at DESC
                LIMIT 1
                """,
            ).fetchone()
        return int(row["version"])

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            if self.config.enable_wal:
                connection.execute("PRAGMA journal_mode=WAL")

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_memory_schema (
                    version INTEGER NOT NULL,
                    applied_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reason TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT,
                    access_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_memory_idempotency (
                    idempotency_key TEXT PRIMARY KEY,
                    memory_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(memory_id) REFERENCES cognitive_memories(id)
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cognitive_memories_category
                ON cognitive_memories(category)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_cognitive_memories_created_at
                ON cognitive_memories(created_at)
                """
            )
            connection.execute(
                """
                INSERT INTO cognitive_memory_schema(version, applied_at)
                SELECT ?, ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM cognitive_memory_schema WHERE version = ?
                )
                """,
                (self.config.schema_version, self._now(), self.config.schema_version),
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _normalize_content(self, content: str) -> str:
        normalized = " ".join(content.strip().lower().split())
        if not normalized:
            msg = "memory_content_cannot_be_empty"
            raise ValueError(msg)
        return normalized[: self.config.max_content_length]

    @staticmethod
    def _record_from_row(row: sqlite3.Row | dict[str, Any]) -> CognitiveMemoryRecord:
        return CognitiveMemoryRecord(
            id=int(row["id"]),
            content=str(row["content"]),
            category=LearningCategory(str(row["category"])),
            confidence=float(row["confidence"]),
            reason=str(row["reason"]),
            tags=tuple(json.loads(str(row["tags_json"]))),
            metadata=dict(json.loads(str(row["metadata_json"]))),
            created_at=str(row["created_at"]),
            last_accessed_at=row["last_accessed_at"],
            access_count=int(row["access_count"]),
        )

    @staticmethod
    def _dump_json(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()
