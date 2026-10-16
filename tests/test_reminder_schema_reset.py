import sqlite3

from infrastructure.persistence.sqlite.schema import init_reminders_schema


def test_legacy_reminder_tables_are_dropped_and_recreated_empty(tmp_path):
    db = tmp_path / "reminders.db"
    connection = sqlite3.connect(db)
    connection.execute("CREATE TABLE reminders (id TEXT PRIMARY KEY, title TEXT)")
    connection.execute(
        "INSERT INTO reminders (id, title) VALUES ('old', 'turno heredado')"
    )
    connection.commit()

    init_reminders_schema(connection)

    assert connection.execute("SELECT COUNT(*) FROM reminders").fetchone()[0] == 0
    assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
    connection.close()
