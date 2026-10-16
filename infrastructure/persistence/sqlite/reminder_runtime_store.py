from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import UUID

from domain.reminders import Reminder

from .connection import create_connection
from .reminder_repository import SQLiteReminderRepository
from .schema import init_reminders_schema


class SQLiteReminderRuntimeStore:
    """Thread-safe runtime facade using one short-lived SQLite connection per call."""

    def __init__(self, db_path: str | Path, *, owner: str | None = None) -> None:
        self.db_path = Path(db_path)
        self.owner_scope = owner.strip().casefold() if owner else None
        with create_connection(self.db_path) as connection:
            init_reminders_schema(connection)

    def list_due(self, *, now: datetime) -> list[Reminder]:
        with create_connection(self.db_path) as connection:
            repository = SQLiteReminderRepository(connection)
            pending = [item for item in repository.list_pending() if item.due_at <= now]
            # M236: Carlos and Cristina are one household identity. Owner metadata
            # is retained only for backward-compatible data migration.
            return pending

    def list_upcoming(self, *, now: datetime, until: datetime) -> list[Reminder]:
        with create_connection(self.db_path) as connection:
            repository = SQLiteReminderRepository(connection)
            return [
                item
                for item in repository.list_pending()
                if now < item.due_at <= until
            ]

    def was_advance_notified(
        self,
        reminder_id: UUID,
        *,
        due_at: datetime,
        stage: str,
    ) -> bool:
        with create_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT 1 FROM reminder_advance_notifications
                WHERE reminder_id = ? AND due_at = ? AND stage = ?
                """,
                (str(reminder_id), due_at.isoformat(), stage),
            ).fetchone()
            return row is not None

    def mark_advance_notified(
        self,
        reminder_id: UUID,
        *,
        due_at: datetime,
        stage: str,
        notified_at: datetime,
    ) -> None:
        with create_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO reminder_advance_notifications (
                    reminder_id, due_at, stage, notified_at
                ) VALUES (?, ?, ?, ?)
                """,
                (
                    str(reminder_id),
                    due_at.isoformat(),
                    stage,
                    notified_at.isoformat(),
                ),
            )
            connection.commit()

    def was_notified(self, reminder_id: UUID, *, due_at: datetime) -> bool:
        with create_connection(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT 1 FROM reminder_notifications
                WHERE reminder_id = ? AND due_at = ?
                """,
                (str(reminder_id), due_at.isoformat()),
            ).fetchone()
            return row is not None

    def mark_notified(
        self,
        reminder_id: UUID,
        *,
        due_at: datetime,
        notified_at: datetime,
    ) -> None:
        with create_connection(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO reminder_notifications (
                    reminder_id, due_at, notified_at
                ) VALUES (?, ?, ?)
                """,
                (str(reminder_id), due_at.isoformat(), notified_at.isoformat()),
            )
            repository = SQLiteReminderRepository(connection)
            reminder = repository.get_by_id(reminder_id)
            if (
                reminder is not None
                and reminder.recurrence is not None
                and reminder.due_at == due_at
            ):
                reminder.due_at = reminder.recurrence.next_due_after(
                    due_at, notified_at
                )
                reminder.updated_at = notified_at
                repository.save(reminder)
            else:
                connection.commit()
