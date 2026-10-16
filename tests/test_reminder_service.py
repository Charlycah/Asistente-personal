from datetime import datetime, timedelta, timezone
from uuid import uuid4

from domain.reminders import Reminder, ReminderService, ReminderStatus


def make_reminder(
    *,
    title: str,
    due_at: datetime,
    status: ReminderStatus = ReminderStatus.PENDING,
) -> Reminder:
    created = due_at - timedelta(hours=1)

    return Reminder(
        id=uuid4(),
        title=title,
        description=None,
        due_at=due_at,
        status=status,
        recurrence=None,
        created_at=created,
        updated_at=created,
    )


def test_list_due_returns_only_pending_due_reminders() -> None:
    service = ReminderService()
    now = datetime(2026, 7, 3, 15, 0, tzinfo=timezone.utc)

    reminders = [
        make_reminder(title="Vencido", due_at=now - timedelta(minutes=10)),
        make_reminder(title="Futuro", due_at=now + timedelta(hours=1)),
        make_reminder(
            title="Completado",
            due_at=now - timedelta(minutes=5),
            status=ReminderStatus.COMPLETED,
        ),
    ]

    result = service.list_due(reminders, now)

    assert [r.title for r in result] == ["Vencido"]


def test_list_for_day_returns_only_today_pending() -> None:
    service = ReminderService()

    today = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)
    tomorrow = today + timedelta(days=1)

    reminders = [
        make_reminder(title="Hoy", due_at=today),
        make_reminder(title="Mañana", due_at=tomorrow),
    ]

    result = service.list_for_day(reminders, today.date())

    assert [r.title for r in result] == ["Hoy"]


def test_list_next_returns_sorted_upcoming() -> None:
    service = ReminderService()
    now = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)

    reminders = [
        make_reminder(title="3", due_at=now + timedelta(hours=3)),
        make_reminder(title="1", due_at=now + timedelta(hours=1)),
        make_reminder(title="2", due_at=now + timedelta(hours=2)),
    ]

    result = service.list_next(reminders, now)

    assert [r.title for r in result] == ["1", "2", "3"]


def test_list_next_respects_limit() -> None:
    service = ReminderService()
    now = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)

    reminders = [
        make_reminder(title=str(i), due_at=now + timedelta(hours=i))
        for i in range(1, 10)
    ]

    result = service.list_next(reminders, now, limit=3)

    assert len(result) == 3
    assert [r.title for r in result] == ["1", "2", "3"]
