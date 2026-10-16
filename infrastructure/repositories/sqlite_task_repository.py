from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core.task_intelligence import (
    Task,
    TaskDependency,
)


class SQLiteTaskRepository:
    """Persistent infrastructure adapter for the existing TaskRepository contract."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save_task(self, task: Task) -> Task:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO tasks (
                    task_id, title, description, owner, origin, importance, urgency,
                    deadline, estimated_minutes, tags_json, source_reference,
                    confidence, status, created_at, updated_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    title=excluded.title,
                    description=excluded.description,
                    owner=excluded.owner,
                    origin=excluded.origin,
                    importance=excluded.importance,
                    urgency=excluded.urgency,
                    deadline=excluded.deadline,
                    estimated_minutes=excluded.estimated_minutes,
                    tags_json=excluded.tags_json,
                    source_reference=excluded.source_reference,
                    confidence=excluded.confidence,
                    status=excluded.status,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at,
                    completed_at=excluded.completed_at
                """,
                self._task_values(task),
            )
        return task

    def get_task(self, task_id: str) -> Task | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE task_id = ?", (task_id,)
            ).fetchone()
        return self._decode_task(row) if row else None

    def get_by_fingerprint(self, fingerprint: str) -> Task | None:
        for task in self.list_tasks():
            if task.fingerprint == fingerprint:
                return task
        return None

    def list_tasks(self) -> tuple[Task, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY created_at, task_id"
            ).fetchall()
        return tuple(self._decode_task(row) for row in rows)

    def save_dependency(self, dependency: TaskDependency) -> TaskDependency:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO task_dependencies (
                    dependency_id, task_id, depends_on_task_id, created_at
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(dependency_id) DO UPDATE SET
                    task_id=excluded.task_id,
                    depends_on_task_id=excluded.depends_on_task_id,
                    created_at=excluded.created_at
                """,
                (
                    dependency.dependency_id,
                    dependency.task_id,
                    dependency.depends_on_task_id,
                    dependency.created_at.isoformat(),
                ),
            )
        return dependency

    def list_dependencies(self) -> tuple[TaskDependency, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM task_dependencies
                ORDER BY created_at, dependency_id
                """
            ).fetchall()
        return tuple(
            TaskDependency(
                task_id=row["task_id"],
                depends_on_task_id=row["depends_on_task_id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                dependency_id=row["dependency_id"],
            )
            for row in rows
        )

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    origin TEXT NOT NULL,
                    importance INTEGER NOT NULL,
                    urgency INTEGER NOT NULL,
                    deadline TEXT,
                    estimated_minutes INTEGER,
                    tags_json TEXT NOT NULL,
                    source_reference TEXT,
                    confidence REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    dependency_id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL,
                    depends_on_task_id TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _task_values(task: Task) -> tuple[object, ...]:
        return (
            task.task_id,
            task.title,
            task.description,
            task.normalized_owner.value,
            task.normalized_origin.value,
            task.importance,
            task.urgency,
            task.deadline.isoformat() if task.deadline else None,
            task.estimated_minutes,
            json.dumps(task.normalized_tags, ensure_ascii=False),
            task.source_reference,
            task.confidence,
            task.normalized_status.value,
            task.created_at.isoformat(),
            task.updated_at.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None,
        )

    @staticmethod
    def _decode_task(row: sqlite3.Row) -> Task:
        return Task(
            task_id=row["task_id"],
            title=row["title"],
            description=row["description"],
            owner=row["owner"],
            origin=row["origin"],
            importance=int(row["importance"]),
            urgency=int(row["urgency"]),
            deadline=(
                datetime.fromisoformat(row["deadline"]) if row["deadline"] else None
            ),
            estimated_minutes=row["estimated_minutes"],
            tags=tuple(json.loads(row["tags_json"])),
            source_reference=row["source_reference"],
            confidence=float(row["confidence"]),
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"])
                if row["completed_at"]
                else None
            ),
        )
