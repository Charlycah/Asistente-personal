import sqlite3
from datetime import datetime
from uuid import UUID

from domain.reminders import (
    RecurrenceFrequency,
    RecurrenceRule,
    Reminder,
    ReminderStatus,
)


class SQLiteReminderRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, reminder: Reminder) -> None:
        self.connection.execute(
            """
            INSERT INTO reminders (
                id,
                title,
                description,
                due_at,
                status,
                recurrence_frequency,
                recurrence_interval,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                description = excluded.description,
                due_at = excluded.due_at,
                status = excluded.status,
                recurrence_frequency = excluded.recurrence_frequency,
                recurrence_interval = excluded.recurrence_interval,
                updated_at = excluded.updated_at
            """,
            (
                str(reminder.id),
                reminder.title,
                reminder.description,
                reminder.due_at.isoformat(),
                reminder.status.value,
                reminder.recurrence.frequency.value if reminder.recurrence else None,
                reminder.recurrence.interval if reminder.recurrence else None,
                reminder.created_at.isoformat(),
                reminder.updated_at.isoformat(),
            ),
        )
        self.connection.commit()

    def get_by_id(self, reminder_id: UUID) -> Reminder | None:
        row = self.connection.execute(
            "SELECT * FROM reminders WHERE id = ?",
            (str(reminder_id),),
        ).fetchone()

        if row is None:
            return None

        return self._row_to_reminder(row)

    def list_pending(self) -> list[Reminder]:
        rows = self.connection.execute(
            """
            SELECT * FROM reminders
            WHERE status = ?
            ORDER BY due_at ASC
            """,
            (ReminderStatus.PENDING.value,),
        ).fetchall()

        return [self._row_to_reminder(row) for row in rows]

    def delete(self, reminder_id: UUID) -> None:
        self.connection.execute(
            "DELETE FROM reminders WHERE id = ?",
            (str(reminder_id),),
        )
        self.connection.commit()

    def _row_to_reminder(self, row: sqlite3.Row) -> Reminder:
        recurrence = None

        if row["recurrence_frequency"] is not None:
            recurrence = RecurrenceRule(
                frequency=RecurrenceFrequency(row["recurrence_frequency"]),
                interval=row["recurrence_interval"],
            )

        return Reminder(
            id=UUID(row["id"]),
            title=row["title"],
            description=row["description"],
            due_at=datetime.fromisoformat(row["due_at"]),
            status=ReminderStatus(row["status"]),
            recurrence=recurrence,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
