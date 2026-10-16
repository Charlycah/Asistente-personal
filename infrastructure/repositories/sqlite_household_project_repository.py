from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from core.household_projects import HouseholdProject


class SQLiteHouseholdProjectRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, project: HouseholdProject) -> HouseholdProject:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO household_projects (
                    project_id, name, description, status, next_step,
                    notes_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    status=excluded.status,
                    next_step=excluded.next_step,
                    notes_json=excluded.notes_json,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    project.project_id,
                    project.name,
                    project.description,
                    project.normalized_status.value,
                    project.next_step,
                    json.dumps(project.notes, ensure_ascii=False),
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                ),
            )
        return project

    def get(self, project_id: str) -> HouseholdProject | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM household_projects WHERE project_id = ?", (project_id,)
            ).fetchone()
        return self._decode(row) if row else None

    def list_all(self) -> tuple[HouseholdProject, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM household_projects ORDER BY created_at, project_id"
            ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS household_projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    next_step TEXT NOT NULL,
                    notes_json TEXT NOT NULL,
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
    def _decode(row: sqlite3.Row) -> HouseholdProject:
        return HouseholdProject(
            project_id=row["project_id"],
            name=row["name"],
            description=row["description"],
            status=row["status"],
            next_step=row["next_step"],
            notes=tuple(json.loads(row["notes_json"])),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
