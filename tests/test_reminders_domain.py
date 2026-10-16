from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from domain.reminders import Reminder, ReminderStatus
from domain.reminders.exceptions import (
    InvalidReminderDueDateError,
    InvalidReminderStateTransitionError,
    InvalidReminderTitleError,
)


def make_reminder(
    *,
    title: str = "Tomar agua",
    status: ReminderStatus = ReminderStatus.PENDING,
) -> Reminder:
    now = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)

    return Reminder(
        id=uuid4(),
        title=title,
        description=None,
        due_at=now + timedelta(hours=1),
        status=status,
        recurrence=None,
        created_at=now,
        updated_at=now,
    )


def test_create_valid_reminder() -> None:
    reminder = make_reminder()

    assert reminder.title == "Tomar agua"
    assert reminder.status == ReminderStatus.PENDING


def test_reject_empty_title() -> None:
    with pytest.raises(InvalidReminderTitleError):
        make_reminder(title="   ")


def test_reject_due_date_before_created_at() -> None:
    now = datetime(2026, 7, 3, 10, 0, tzinfo=timezone.utc)

    with pytest.raises(InvalidReminderDueDateError):
        Reminder(
            id=uuid4(),
            title="Recordatorio inválido",
            description=None,
            due_at=now - timedelta(minutes=1),
            status=ReminderStatus.PENDING,
            recurrence=None,
            created_at=now,
            updated_at=now,
        )


def test_complete_pending_reminder() -> None:
    reminder = make_reminder()
    completed_at = reminder.created_at + timedelta(minutes=10)

    reminder.complete(completed_at)

    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.updated_at == completed_at


def test_reject_complete_cancelled_reminder() -> None:
    reminder = make_reminder(status=ReminderStatus.CANCELLED)

    with pytest.raises(InvalidReminderStateTransitionError):
        reminder.complete(datetime.now(timezone.utc))


def test_cancel_pending_reminder() -> None:
    reminder = make_reminder()
    cancelled_at = reminder.created_at + timedelta(minutes=5)

    reminder.cancel(cancelled_at)

    assert reminder.status == ReminderStatus.CANCELLED
    assert reminder.updated_at == cancelled_at


def test_reject_cancel_completed_reminder() -> None:
    reminder = make_reminder(status=ReminderStatus.COMPLETED)

    with pytest.raises(InvalidReminderStateTransitionError):
        reminder.cancel(datetime.now(timezone.utc))


def test_snooze_pending_reminder() -> None:
    reminder = make_reminder()
    snoozed_at = reminder.created_at + timedelta(minutes=5)
    new_due_at = snoozed_at + timedelta(hours=2)

    reminder.snooze(new_due_at=new_due_at, snoozed_at=snoozed_at)

    assert reminder.status == ReminderStatus.SNOOZED
    assert reminder.due_at == new_due_at
    assert reminder.updated_at == snoozed_at


def test_reject_snooze_completed_reminder() -> None:
    reminder = make_reminder(status=ReminderStatus.COMPLETED)
    now = datetime.now(timezone.utc)

    with pytest.raises(InvalidReminderStateTransitionError):
        reminder.snooze(
            new_due_at=now + timedelta(hours=1),
            snoozed_at=now,
        )


def test_reject_snooze_to_past_date() -> None:
    reminder = make_reminder()
    now = datetime.now(timezone.utc)

    with pytest.raises(InvalidReminderDueDateError):
        reminder.snooze(
            new_due_at=now - timedelta(minutes=1),
            snoozed_at=now,
        )
