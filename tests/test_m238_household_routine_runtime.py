from __future__ import annotations

from datetime import datetime, timezone

from application.reminders.natural_language import (
    ReminderConversationService,
    parse_create_reminder,
)
from core.always_on_personal_runtime import ReminderAwarenessService
from domain.reminders import RecurrenceFrequency, RecurrenceRule
from infrastructure.persistence.sqlite import SQLiteReminderRuntimeStore

UTC = timezone.utc


def test_parse_daily_household_routine() -> None:
    now = datetime(2026, 7, 15, 18, 0, tzinfo=UTC)

    command = parse_create_reminder(
        "Recordame tomar el remedio todos los días a las 8",
        now,
    )

    assert command.title == "tomar el remedio"
    assert command.due_at == datetime(2026, 7, 16, 8, 0, tzinfo=UTC)
    assert command.recurrence == RecurrenceRule(RecurrenceFrequency.DAILY)


def test_parse_interval_household_routine() -> None:
    now = datetime(2026, 7, 15, 10, 0, tzinfo=UTC)

    command = parse_create_reminder(
        "Creá una rutina para regar las plantas cada 2 días a las 9",
        now,
    )

    assert command.title == "regar las plantas"
    assert command.recurrence == RecurrenceRule(
        RecurrenceFrequency.DAILY,
        interval=2,
    )


def test_conversation_creates_and_lists_routine(tmp_path) -> None:
    service = ReminderConversationService(tmp_path / "reminders.db")
    now = datetime(2026, 7, 15, 10, 0, tzinfo=UTC)

    created = service.handle(
        owner="Familia",
        text="Recordame sacar la basura todas las semanas a las 20",
        now=now,
    )
    listed = service.handle(
        owner="Familia",
        text="¿Qué rutinas tengo?",
        now=now,
    )

    assert created.handled is True
    assert "Creé la rutina sacar la basura" in created.response_text
    assert "cada semana" in created.response_text
    assert "sacar la basura" in listed.response_text
    assert "cada semana" in listed.response_text


def test_routine_delivery_advances_next_due_persistently(tmp_path) -> None:
    db_path = tmp_path / "reminders.db"
    service = ReminderConversationService(db_path)
    created_at = datetime(2026, 7, 15, 7, 0, tzinfo=UTC)
    service.handle(
        owner="Familia",
        text="Recordame tomar agua todos los días a las 8",
        now=created_at,
    )
    store = SQLiteReminderRuntimeStore(db_path, owner="Familia")
    messages: list[str] = []
    runtime = ReminderAwarenessService(
        store,
        notify=messages.append,
        owner="Familia",
    )

    first_due = datetime(2026, 7, 15, 8, 0, tzinfo=UTC)
    assert runtime.check_once(now=first_due) == ("No te olvides: tomar agua.",)
    assert runtime.check_once(now=first_due) == ()
    assert store.list_due(now=first_due) == []

    next_due = datetime(2026, 7, 16, 8, 0, tzinfo=UTC)
    assert runtime.check_once(now=next_due) == ("No te olvides: tomar agua.",)
    assert len(messages) == 2


def test_routine_catches_up_to_first_future_occurrence(tmp_path) -> None:
    db_path = tmp_path / "reminders.db"
    service = ReminderConversationService(db_path)
    service.handle(
        owner="Familia",
        text="Recordame revisar el filtro todos los días a las 8",
        now=datetime(2026, 7, 15, 7, 0, tzinfo=UTC),
    )
    store = SQLiteReminderRuntimeStore(db_path, owner="Familia")
    runtime = ReminderAwarenessService(
        store,
        notify=lambda _message: None,
        owner="Familia",
    )

    resumed_at = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)
    runtime.check_once(now=resumed_at)

    assert store.list_due(now=resumed_at) == []
    pending = service.handle(
        owner="Familia",
        text="¿Qué rutinas tengo?",
        now=resumed_at,
    )
    assert "21/07/2026 a las 08:00" in pending.response_text


def test_monthly_recurrence_clamps_end_of_month() -> None:
    rule = RecurrenceRule(RecurrenceFrequency.MONTHLY)
    current = datetime(2026, 1, 31, 9, 0, tzinfo=UTC)

    assert rule.next_due(current) == datetime(2026, 2, 28, 9, 0, tzinfo=UTC)
