from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from core.household_goals import HouseholdGoal


class SQLiteHouseholdGoalRepository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def save(self, goal: HouseholdGoal) -> HouseholdGoal:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO household_goals (
                    goal_id, name, description, status, progress_percent,
                    target_date, linked_project, linked_routine, next_step,
                    notes_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(goal_id) DO UPDATE SET
                    name=excluded.name,
                    description=excluded.description,
                    status=excluded.status,
                    progress_percent=excluded.progress_percent,
                    target_date=excluded.target_date,
                    linked_project=excluded.linked_project,
                    linked_routine=excluded.linked_routine,
                    next_step=excluded.next_step,
                    notes_json=excluded.notes_json,
                    created_at=excluded.created_at,
                    updated_at=excluded.updated_at
                """,
                (
                    goal.goal_id,
                    goal.name,
                    goal.description,
                    goal.normalized_status.value,
                    goal.progress_percent,
                    goal.target_date.isoformat() if goal.target_date else None,
                    goal.linked_project,
                    goal.linked_routine,
                    goal.next_step,
                    json.dumps(goal.notes, ensure_ascii=False),
                    goal.created_at.isoformat(),
                    goal.updated_at.isoformat(),
                ),
            )
        return goal

    def get(self, goal_id: str) -> HouseholdGoal | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM household_goals WHERE goal_id = ?", (goal_id,)
            ).fetchone()
        return self._decode(row) if row else None

    def list_all(self) -> tuple[HouseholdGoal, ...]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM household_goals ORDER BY created_at, goal_id"
            ).fetchall()
        return tuple(self._decode(row) for row in rows)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS household_goals (
                    goal_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress_percent INTEGER NOT NULL,
                    target_date TEXT,
                    linked_project TEXT NOT NULL,
                    linked_routine TEXT NOT NULL,
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
    def _decode(row: sqlite3.Row) -> HouseholdGoal:
        return HouseholdGoal(
            goal_id=row["goal_id"],
            name=row["name"],
            description=row["description"],
            status=row["status"],
            progress_percent=int(row["progress_percent"]),
            target_date=(
                date.fromisoformat(row["target_date"]) if row["target_date"] else None
            ),
            linked_project=row["linked_project"],
            linked_routine=row["linked_routine"],
            next_step=row["next_step"],
            notes=tuple(json.loads(row["notes_json"])),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
