import sqlite3

_REMINDERS_SCHEMA_VERSION = 2
_REMINDER_TABLES = (
    "reminder_advance_notifications",
    "reminder_notifications",
    "reminder_ownership",
    "reminders",
)


def init_reminders_schema(connection: sqlite3.Connection) -> None:
    """Create an empty reminder store and purge pre-v2 legacy reminder data once."""
    current_version = int(connection.execute("PRAGMA user_version").fetchone()[0])
    if current_version < _REMINDERS_SCHEMA_VERSION:
        _drop_legacy_reminder_tables(connection)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reminders (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            due_at TEXT NOT NULL,
            status TEXT NOT NULL,
            recurrence_frequency TEXT,
            recurrence_interval INTEGER,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reminder_ownership (
            reminder_id TEXT PRIMARY KEY,
            owner_scope TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reminder_notifications (
            reminder_id TEXT NOT NULL,
            due_at TEXT NOT NULL,
            notified_at TEXT NOT NULL,
            PRIMARY KEY (reminder_id, due_at)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reminder_advance_notifications (
            reminder_id TEXT NOT NULL,
            due_at TEXT NOT NULL,
            stage TEXT NOT NULL,
            notified_at TEXT NOT NULL,
            PRIMARY KEY (reminder_id, due_at, stage)
        )
        """
    )
    connection.execute(f"PRAGMA user_version = {_REMINDERS_SCHEMA_VERSION}")
    connection.commit()


def _drop_legacy_reminder_tables(connection: sqlite3.Connection) -> None:
    for table in _REMINDER_TABLES:
        connection.execute(f"DROP TABLE IF EXISTS {table}")
    connection.commit()
