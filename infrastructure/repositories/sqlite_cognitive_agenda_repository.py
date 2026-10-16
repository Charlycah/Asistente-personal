from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from domain.cognitive_agenda import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaStatus,
    CognitiveCommitmentStatus,
    CognitiveMetacognitiveStatus,
)


class SQLiteCognitiveAgendaRepository:
    """Persist the canonical cognitive agenda without owning runtime lifecycle."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def load_open(self) -> tuple[CognitiveAgendaItem, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM cognitive_agenda_items
                WHERE status IN ('active', 'watching', 'blocked')
                ORDER BY score DESC, item_key
                """
            ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def save(self, items: tuple[CognitiveAgendaItem, ...]) -> None:
        if not items:
            return
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO cognitive_agenda_items (
                    item_key, kind, title, sources_json, score, priority,
                    urgency, relevance, status, first_seen_at, last_seen_at,
                    expires_at, rationale, resume_conditions_json,
                    last_activated_at, activation_count, resolution_conditions_json,
                    last_transition, expected_benefit, cognitive_cost,
                    dependencies_json, context_tags_json, commitment_status,
                    commitment_started_at, progress, last_progress_at,
                    execution_note, stall_count, metacognitive_status,
                    progress_quality, formulation_clarity, review_count,
                    last_reviewed_at, review_note, adaptive_priority_adjustment,
                    adaptive_cost_adjustment, learning_event_count, last_learned_at,
                    learning_rationale
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                ON CONFLICT(item_key) DO UPDATE SET
                    kind=excluded.kind,
                    title=excluded.title,
                    sources_json=excluded.sources_json,
                    score=excluded.score,
                    priority=excluded.priority,
                    urgency=excluded.urgency,
                    relevance=excluded.relevance,
                    status=excluded.status,
                    first_seen_at=excluded.first_seen_at,
                    last_seen_at=excluded.last_seen_at,
                    expires_at=excluded.expires_at,
                    rationale=excluded.rationale,
                    resume_conditions_json=excluded.resume_conditions_json,
                    last_activated_at=excluded.last_activated_at,
                    activation_count=excluded.activation_count,
                    resolution_conditions_json=excluded.resolution_conditions_json,
                    last_transition=excluded.last_transition,
                    expected_benefit=excluded.expected_benefit,
                    cognitive_cost=excluded.cognitive_cost,
                    dependencies_json=excluded.dependencies_json,
                    context_tags_json=excluded.context_tags_json,
                    commitment_status=excluded.commitment_status,
                    commitment_started_at=excluded.commitment_started_at,
                    progress=excluded.progress,
                    last_progress_at=excluded.last_progress_at,
                    execution_note=excluded.execution_note,
                    stall_count=excluded.stall_count,
                    metacognitive_status=excluded.metacognitive_status,
                    progress_quality=excluded.progress_quality,
                    formulation_clarity=excluded.formulation_clarity,
                    review_count=excluded.review_count,
                    last_reviewed_at=excluded.last_reviewed_at,
                    review_note=excluded.review_note,
                    adaptive_priority_adjustment=excluded.adaptive_priority_adjustment,
                    adaptive_cost_adjustment=excluded.adaptive_cost_adjustment,
                    learning_event_count=excluded.learning_event_count,
                    last_learned_at=excluded.last_learned_at,
                    learning_rationale=excluded.learning_rationale
                """,
                [self._encode(item) for item in items],
            )

    def set_status(self, key: str, status: CognitiveAgendaStatus) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "UPDATE cognitive_agenda_items SET status = ? WHERE item_key = ?",
                (status.value, key),
            )
        return cursor.rowcount > 0

    def status_for(self, key: str) -> CognitiveAgendaStatus | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT status FROM cognitive_agenda_items WHERE item_key = ?",
                (key,),
            ).fetchone()
        return CognitiveAgendaStatus(row["status"]) if row is not None else None

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS cognitive_agenda_items (
                    item_key TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    title TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    score REAL NOT NULL,
                    priority REAL NOT NULL,
                    urgency REAL NOT NULL,
                    relevance REAL NOT NULL,
                    status TEXT NOT NULL,
                    first_seen_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    expires_at TEXT,
                    rationale TEXT NOT NULL,
                    resume_conditions_json TEXT NOT NULL DEFAULT '[]',
                    last_activated_at TEXT,
                    activation_count INTEGER NOT NULL DEFAULT 0,
                    resolution_conditions_json TEXT NOT NULL DEFAULT '[]',
                    last_transition TEXT NOT NULL DEFAULT '',
                    expected_benefit REAL NOT NULL DEFAULT 0.5,
                    cognitive_cost REAL NOT NULL DEFAULT 0.5,
                    dependencies_json TEXT NOT NULL DEFAULT '[]',
                    context_tags_json TEXT NOT NULL DEFAULT '[]',
                    commitment_status TEXT NOT NULL DEFAULT 'pending',
                    commitment_started_at TEXT,
                    progress REAL NOT NULL DEFAULT 0.0,
                    last_progress_at TEXT,
                    execution_note TEXT NOT NULL DEFAULT '',
                    stall_count INTEGER NOT NULL DEFAULT 0,
                    metacognitive_status TEXT NOT NULL DEFAULT 'unreviewed',
                    progress_quality REAL NOT NULL DEFAULT 1.0,
                    formulation_clarity REAL NOT NULL DEFAULT 1.0,
                    review_count INTEGER NOT NULL DEFAULT 0,
                    last_reviewed_at TEXT,
                    review_note TEXT NOT NULL DEFAULT '',
                    adaptive_priority_adjustment REAL NOT NULL DEFAULT 0.0,
                    adaptive_cost_adjustment REAL NOT NULL DEFAULT 0.0,
                    learning_event_count INTEGER NOT NULL DEFAULT 0,
                    last_learned_at TEXT,
                    learning_rationale TEXT NOT NULL DEFAULT ''
                )
                """
            )
            columns = {
                row["name"]
                for row in connection.execute(
                    "PRAGMA table_info(cognitive_agenda_items)"
                ).fetchall()
            }
            if "last_activated_at" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN last_activated_at TEXT"
                )
            if "activation_count" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN activation_count INTEGER NOT NULL DEFAULT 0"
                )
            if "resolution_conditions_json" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN resolution_conditions_json TEXT NOT NULL DEFAULT '[]'"
                )
            if "last_transition" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN last_transition TEXT NOT NULL DEFAULT ''"
                )
            if "expected_benefit" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN expected_benefit REAL NOT NULL DEFAULT 0.5"
                )
            if "cognitive_cost" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN cognitive_cost REAL NOT NULL DEFAULT 0.5"
                )
            if "dependencies_json" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN dependencies_json TEXT NOT NULL DEFAULT '[]'"
                )
            if "context_tags_json" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN context_tags_json TEXT NOT NULL DEFAULT '[]'"
                )
            if "commitment_status" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN commitment_status TEXT NOT NULL DEFAULT 'pending'"
                )
            if "commitment_started_at" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN commitment_started_at TEXT"
                )
            if "progress" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN progress REAL NOT NULL DEFAULT 0.0"
                )
            if "last_progress_at" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN last_progress_at TEXT"
                )
            if "execution_note" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN execution_note TEXT NOT NULL DEFAULT ''"
                )
            if "stall_count" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN stall_count INTEGER NOT NULL DEFAULT 0"
                )
            if "metacognitive_status" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN metacognitive_status TEXT NOT NULL "
                    "DEFAULT 'unreviewed'"
                )
            if "progress_quality" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN progress_quality REAL NOT NULL DEFAULT 1.0"
                )
            if "formulation_clarity" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN formulation_clarity REAL NOT NULL DEFAULT 1.0"
                )
            if "review_count" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN review_count INTEGER NOT NULL DEFAULT 0"
                )
            if "last_reviewed_at" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN last_reviewed_at TEXT"
                )
            if "review_note" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN review_note TEXT NOT NULL DEFAULT ''"
                )
            if "adaptive_priority_adjustment" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN adaptive_priority_adjustment REAL NOT NULL DEFAULT 0.0"
                )
            if "adaptive_cost_adjustment" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN adaptive_cost_adjustment REAL NOT NULL DEFAULT 0.0"
                )
            if "learning_event_count" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN learning_event_count INTEGER NOT NULL DEFAULT 0"
                )
            if "last_learned_at" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items ADD COLUMN last_learned_at TEXT"
                )
            if "learning_rationale" not in columns:
                connection.execute(
                    "ALTER TABLE cognitive_agenda_items "
                    "ADD COLUMN learning_rationale TEXT NOT NULL DEFAULT ''"
                )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _encode(item: CognitiveAgendaItem) -> tuple[object, ...]:
        return (
            item.key,
            item.kind.value,
            item.title,
            json.dumps(item.sources, ensure_ascii=False),
            item.score,
            item.priority,
            item.urgency,
            item.relevance,
            item.status.value,
            item.first_seen_at.isoformat(),
            item.last_seen_at.isoformat(),
            item.expires_at.isoformat() if item.expires_at else None,
            item.rationale,
            json.dumps(item.resume_conditions, ensure_ascii=False),
            (
                item.last_activated_at.isoformat()
                if item.last_activated_at is not None
                else None
            ),
            item.activation_count,
            json.dumps(item.resolution_conditions, ensure_ascii=False),
            item.last_transition,
            item.expected_benefit,
            item.cognitive_cost,
            json.dumps(item.dependencies, ensure_ascii=False),
            json.dumps(item.context_tags, ensure_ascii=False),
            item.commitment_status.value,
            (
                item.commitment_started_at.isoformat()
                if item.commitment_started_at is not None
                else None
            ),
            item.progress,
            item.last_progress_at.isoformat() if item.last_progress_at else None,
            item.execution_note,
            item.stall_count,
            item.metacognitive_status.value,
            item.progress_quality,
            item.formulation_clarity,
            item.review_count,
            item.last_reviewed_at.isoformat() if item.last_reviewed_at else None,
            item.review_note,
            item.adaptive_priority_adjustment,
            item.adaptive_cost_adjustment,
            item.learning_event_count,
            item.last_learned_at.isoformat() if item.last_learned_at else None,
            item.learning_rationale,
        )

    @staticmethod
    def _decode(row: sqlite3.Row) -> CognitiveAgendaItem:
        return CognitiveAgendaItem(
            key=row["item_key"],
            kind=CognitiveAgendaKind(row["kind"]),
            title=row["title"],
            sources=tuple(json.loads(row["sources_json"])),
            score=float(row["score"]),
            priority=float(row["priority"]),
            urgency=float(row["urgency"]),
            relevance=float(row["relevance"]),
            status=CognitiveAgendaStatus(row["status"]),
            first_seen_at=datetime.fromisoformat(row["first_seen_at"]),
            last_seen_at=datetime.fromisoformat(row["last_seen_at"]),
            expires_at=(
                datetime.fromisoformat(row["expires_at"]) if row["expires_at"] else None
            ),
            rationale=row["rationale"],
            resume_conditions=tuple(json.loads(row["resume_conditions_json"])),
            last_activated_at=(
                datetime.fromisoformat(row["last_activated_at"])
                if row["last_activated_at"]
                else None
            ),
            activation_count=int(row["activation_count"]),
            resolution_conditions=tuple(
                json.loads(row["resolution_conditions_json"] or "[]")
            ),
            last_transition=row["last_transition"] or "",
            expected_benefit=float(row["expected_benefit"]),
            cognitive_cost=float(row["cognitive_cost"]),
            dependencies=tuple(json.loads(row["dependencies_json"] or "[]")),
            context_tags=tuple(json.loads(row["context_tags_json"] or "[]")),
            commitment_status=CognitiveCommitmentStatus(row["commitment_status"]),
            commitment_started_at=(
                datetime.fromisoformat(row["commitment_started_at"])
                if row["commitment_started_at"]
                else None
            ),
            progress=float(row["progress"]),
            last_progress_at=(
                datetime.fromisoformat(row["last_progress_at"])
                if row["last_progress_at"]
                else None
            ),
            execution_note=row["execution_note"] or "",
            stall_count=int(row["stall_count"]),
            metacognitive_status=CognitiveMetacognitiveStatus(
                row["metacognitive_status"]
            ),
            progress_quality=float(row["progress_quality"]),
            formulation_clarity=float(row["formulation_clarity"]),
            review_count=int(row["review_count"]),
            last_reviewed_at=(
                datetime.fromisoformat(row["last_reviewed_at"])
                if row["last_reviewed_at"]
                else None
            ),
            review_note=row["review_note"] or "",
            adaptive_priority_adjustment=float(row["adaptive_priority_adjustment"]),
            adaptive_cost_adjustment=float(row["adaptive_cost_adjustment"]),
            learning_event_count=int(row["learning_event_count"]),
            last_learned_at=(
                datetime.fromisoformat(row["last_learned_at"])
                if row["last_learned_at"]
                else None
            ),
            learning_rationale=row["learning_rationale"] or "",
        )
