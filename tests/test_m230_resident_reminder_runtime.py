from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.always_on_personal_runtime_wiring import (
    build_reminder_awareness_from_environment,
)
from core.always_on_personal_runtime import ReminderAwarenessService
from domain.reminders import Reminder, ReminderStatus
from infrastructure.persistence.sqlite import (
    SQLiteReminderRepository,
    SQLiteReminderRuntimeStore,
    create_connection,
    init_reminders_schema,
)

NOW = datetime(2026, 7, 14, 20, 0, tzinfo=timezone.utc)


def reminder(*, due_at: datetime = NOW, title: str = "Llamar al médico") -> Reminder:
    created = due_at - timedelta(hours=1)
    return Reminder(
        id=uuid4(),
        title=title,
        description="Pedir un turno.",
        due_at=due_at,
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=created,
        updated_at=created,
    )


def save(db_path, item: Reminder) -> None:
    connection = create_connection(db_path)
    init_reminders_schema(connection)
    SQLiteReminderRepository(connection).save(item)
    connection.close()


def test_due_reminder_is_delivered_once_and_persisted(tmp_path):
    db_path = tmp_path / "reminders.db"
    item = reminder()
    save(db_path, item)
    messages: list[str] = []
    service = ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
        owner="Carlos",
    )

    first = service.check_once(now=NOW)
    restarted = ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
        owner="Carlos",
    )
    second = restarted.check_once(now=NOW + timedelta(minutes=1))

    assert first == ("No te olvides: Llamar al médico. Pedir un turno.",)
    assert second == ()
    assert messages == list(first)


def test_future_and_non_pending_reminders_are_not_delivered(tmp_path):
    db_path = tmp_path / "reminders.db"
    save(db_path, reminder(due_at=NOW + timedelta(minutes=1)))
    completed = reminder(title="Ya hecho")
    completed.status = ReminderStatus.COMPLETED
    save(db_path, completed)
    messages: list[str] = []

    result = ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
    ).check_once(now=NOW)

    assert result == ()
    assert messages == []


def test_changed_due_date_can_be_delivered_again(tmp_path):
    db_path = tmp_path / "reminders.db"
    item = reminder()
    save(db_path, item)
    store = SQLiteReminderRuntimeStore(db_path)
    service = ReminderAwarenessService(store, notify=lambda message: None)
    service.check_once(now=NOW)

    item.due_at = NOW + timedelta(hours=1)
    item.updated_at = NOW
    save(db_path, item)

    assert service.check_once(now=NOW + timedelta(hours=1))


def test_storage_failure_degrades_silently():
    class BrokenStore:
        def list_due(self, *, now):
            raise OSError("database unavailable")

    assert (
        ReminderAwarenessService(BrokenStore(), notify=lambda message: None).check_once(
            now=NOW
        )
        == ()
    )


def test_naive_runtime_time_is_rejected():
    class EmptyStore:
        def list_due(self, *, now):
            return []

    service = ReminderAwarenessService(EmptyStore(), notify=lambda message: None)

    with pytest.raises(ValueError, match="timezone-aware"):
        service.check_once(now=datetime(2026, 7, 14, 20, 0))


def test_wiring_uses_governed_environment(monkeypatch, tmp_path):
    db_path = tmp_path / "reminders.db"
    monkeypatch.setenv("ROBY_REMINDER_DB_PATH", str(db_path))
    monkeypatch.setenv("ROBY_REMINDER_POLL_SECONDS", "7")

    service = build_reminder_awareness_from_environment(
        notify=lambda message: None,
        owner="Carlos",
    )

    assert service is not None
    assert service.poll_interval == timedelta(seconds=7)
    assert db_path.exists()


def test_wiring_can_disable_reminder_awareness(monkeypatch):
    monkeypatch.setenv("ROBY_REMINDER_AWARENESS_ENABLED", "false")

    assert (
        build_reminder_awareness_from_environment(
            notify=lambda message: None,
            owner="Carlos",
        )
        is None
    )
