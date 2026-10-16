from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from core.always_on_personal_runtime.reminder_awareness import (
    IntelligentReminderPolicy,
    ReminderAdvanceStage,
    ReminderAwarenessService,
)
from domain.reminders import Reminder, ReminderStatus
from infrastructure.persistence.sqlite import (
    SQLiteReminderRepository,
    SQLiteReminderRuntimeStore,
    create_connection,
    init_reminders_schema,
)

NOW = datetime(2026, 7, 20, 12, 0, tzinfo=timezone.utc)


def _save(db_path, *, due_at: datetime, title: str = "reunión con Laura"):
    item = Reminder(
        id=uuid4(),
        title=title,
        description=None,
        due_at=due_at,
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=NOW - timedelta(days=1),
        updated_at=NOW - timedelta(days=1),
    )
    with create_connection(db_path) as connection:
        init_reminders_schema(connection)
        SQLiteReminderRepository(connection).save(item)
    return item


def _service(db_path, messages, *, stages):
    return ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
        owner="Carlos",
        intelligent_policy=IntelligentReminderPolicy(stages=stages),
    )


def test_three_day_notice_preserves_exact_time_and_weekday(tmp_path):
    db_path = tmp_path / "reminders.db"
    due = NOW + timedelta(days=3)
    _save(db_path, due_at=due)
    messages = []
    service = _service(
        db_path,
        messages,
        stages=(ReminderAdvanceStage("three_days", timedelta(days=3)),),
    )

    result = service.check_once(now=NOW)

    assert result == (
        "No te olvides de que el jueves a las 12:00 "
        "tenés reunión con Laura.",
    )
    assert messages == list(result)


def test_advance_notice_is_persistent_and_not_repeated_after_restart(tmp_path):
    db_path = tmp_path / "reminders.db"
    _save(db_path, due_at=NOW + timedelta(days=1))
    messages = []
    stages = (ReminderAdvanceStage("one_day", timedelta(days=1)),)

    first = _service(db_path, messages, stages=stages).check_once(now=NOW)
    second = _service(db_path, messages, stages=stages).check_once(
        now=NOW + timedelta(minutes=2)
    )

    assert first == ("Mañana a las 12:00 tenés reunión con Laura.",)
    assert second == ()


def test_same_day_and_one_hour_are_independent_stages(tmp_path):
    db_path = tmp_path / "reminders.db"
    _save(db_path, due_at=NOW + timedelta(hours=8))
    messages = []
    stages = (
        ReminderAdvanceStage("same_day", timedelta(hours=8)),
        ReminderAdvanceStage("one_hour", timedelta(hours=1)),
    )
    service = _service(db_path, messages, stages=stages)

    morning = service.check_once(now=NOW)
    near = service.check_once(now=NOW + timedelta(hours=7))

    assert morning == ("Hoy a las 20:00 tenés reunión con Laura.",)
    assert near == ("En una hora a las 20:00 tenés reunión con Laura.",)


def test_due_notification_omits_owner_prefix(tmp_path):
    db_path = tmp_path / "reminders.db"
    _save(db_path, due_at=NOW)
    messages = []

    result = ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
        owner="Carlos",
    ).check_once(now=NOW)

    assert result == ("No te olvides: reunión con Laura.",)


def test_future_reminder_outside_policy_window_is_silent(tmp_path):
    db_path = tmp_path / "reminders.db"
    _save(db_path, due_at=NOW + timedelta(days=5))
    messages = []

    result = ReminderAwarenessService(
        SQLiteReminderRuntimeStore(db_path),
        notify=messages.append,
    ).check_once(now=NOW)

    assert result == ()
    assert messages == []


def test_changed_due_date_allows_new_advance_sequence(tmp_path):
    db_path = tmp_path / "reminders.db"
    item = _save(db_path, due_at=NOW + timedelta(days=1))
    messages = []
    stages = (ReminderAdvanceStage("one_day", timedelta(days=1)),)
    service = _service(db_path, messages, stages=stages)
    assert service.check_once(now=NOW)

    item.due_at = NOW + timedelta(days=2)
    item.updated_at = NOW
    with create_connection(db_path) as connection:
        SQLiteReminderRepository(connection).save(item)

    assert service.check_once(now=NOW + timedelta(days=1))
