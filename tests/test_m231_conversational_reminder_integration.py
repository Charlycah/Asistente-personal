from __future__ import annotations

from datetime import datetime, timedelta, timezone

from application.reminders import ReminderConversationService
from infrastructure.persistence.sqlite import (
    SQLiteReminderRepository,
    create_connection,
    init_reminders_schema,
)

NOW = datetime(2026, 7, 14, 20, 0, tzinfo=timezone.utc)


def pending(db_path):
    connection = create_connection(db_path)
    init_reminders_schema(connection)
    try:
        return SQLiteReminderRepository(connection).list_pending()
    finally:
        connection.close()


def test_create_reminder_from_conversation(tmp_path):
    db_path = tmp_path / "reminders.db"
    result = ReminderConversationService(db_path).handle(
        owner="Carlos",
        text="ROBY, recordame llamar al médico mañana a las 10",
        now=NOW,
    )

    assert result.handled is True
    assert "Listo" in result.response_text
    items = pending(db_path)
    assert len(items) == 1
    assert items[0].title == "llamar al médico"
    assert items[0].due_at == datetime(2026, 7, 15, 10, 0, tzinfo=timezone.utc)


def test_create_relative_reminder(tmp_path):
    db_path = tmp_path / "reminders.db"
    ReminderConversationService(db_path).handle(
        owner="Carlos",
        text="recordame en 30 minutos que saque la ropa",
        now=NOW,
    )

    assert pending(db_path)[0].due_at == NOW + timedelta(minutes=30)


def test_list_cancel_and_snooze_reminders(tmp_path):
    db_path = tmp_path / "reminders.db"
    service = ReminderConversationService(db_path)
    service.handle(
        owner="Carlos",
        text="recordame llamar al médico mañana a las 10",
        now=NOW,
    )
    listed = service.handle(owner="Carlos", text="qué recordatorios tengo", now=NOW)
    cancelled = service.handle(
        owner="Carlos",
        text="cancelá el recordatorio llamar al médico",
        now=NOW,
    )
    service.handle(
        owner="Carlos",
        text="recordame comprar pan mañana a las 11",
        now=NOW,
    )
    snoozed = service.handle(
        owner="Carlos",
        text="postergá el recordatorio comprar pan por media hora",
        now=NOW,
    )

    assert "llamar al médico" in listed.response_text
    assert "Cancelé" in cancelled.response_text
    assert "Postergué" in snoozed.response_text
    assert pending(db_path) == []


def test_non_reminder_conversation_is_not_intercepted(tmp_path):
    result = ReminderConversationService(tmp_path / "reminders.db").handle(
        owner="Carlos",
        text="contame cómo funciona la fotosíntesis",
        now=NOW,
    )

    assert result.handled is False
    assert result.response_text == ""


def test_unparseable_create_request_is_handled_safely(tmp_path):
    result = ReminderConversationService(tmp_path / "reminders.db").handle(
        owner="Carlos",
        text="recordame comprar leche",
        now=NOW,
    )

    assert result.handled is True
    assert "No pude identificar" in result.response_text
    assert pending(tmp_path / "reminders.db") == []


def test_parser_separates_weekday_and_first_person_from_title(tmp_path):
    service = ReminderConversationService(tmp_path / "reminders.db")

    result = service.handle(
        owner="Carlos",
        text="recordame que el viernes tengo turno con el dentista a las 12",
        now=NOW,
    )

    assert result.handled is True
    with create_connection(tmp_path / "reminders.db") as connection:
        init_reminders_schema(connection)
        reminders = SQLiteReminderRepository(connection).list_pending()
    assert len(reminders) == 1
    assert reminders[0].title == "turno con el dentista"
    assert reminders[0].due_at.weekday() == 4
    assert reminders[0].due_at.hour == 12
