from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from application.reminders import (
    CancelReminderCommand,
    CancelReminderUseCase,
    CompleteReminderCommand,
    CompleteReminderUseCase,
    CreateReminderCommand,
    CreateReminderUseCase,
    ReminderNotFoundError,
    SnoozeReminderCommand,
    SnoozeReminderUseCase,
)
from domain.reminders import Reminder, ReminderRepository, ReminderStatus


class InMemoryReminderRepository(ReminderRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Reminder] = {}

    def save(self, reminder: Reminder) -> None:
        self.items[reminder.id] = reminder

    def get_by_id(self, reminder_id: UUID) -> Reminder | None:
        return self.items.get(reminder_id)

    def list_pending(self) -> list[Reminder]:
        return [
            reminder
            for reminder in self.items.values()
            if reminder.status == ReminderStatus.PENDING
        ]

    def delete(self, reminder_id: UUID) -> None:
        self.items.pop(reminder_id, None)


def test_create_reminder_use_case_saves_pending_reminder() -> None:
    repository = InMemoryReminderRepository()
    use_case = CreateReminderUseCase(repository)
    due_at = datetime.now(timezone.utc) + timedelta(hours=1)

    reminder = use_case.execute(
        CreateReminderCommand(
            title="Comprar pan",
            description="Pasar por la panadería",
            due_at=due_at,
        )
    )

    saved = repository.get_by_id(reminder.id)

    assert saved is reminder
    assert reminder.title == "Comprar pan"
    assert reminder.description == "Pasar por la panadería"
    assert reminder.status == ReminderStatus.PENDING
    assert reminder.due_at == due_at


def test_complete_reminder_use_case_updates_status() -> None:
    repository = InMemoryReminderRepository()
    created = CreateReminderUseCase(repository).execute(
        CreateReminderCommand(
            title="Llamar a Juan",
            description=None,
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )

    completed_at = datetime.now(timezone.utc)

    reminder = CompleteReminderUseCase(repository).execute(
        CompleteReminderCommand(
            reminder_id=created.id,
            completed_at=completed_at,
        )
    )

    assert reminder.status == ReminderStatus.COMPLETED
    assert reminder.updated_at == completed_at


def test_complete_missing_reminder_raises_not_found() -> None:
    repository = InMemoryReminderRepository()

    with pytest.raises(ReminderNotFoundError):
        CompleteReminderUseCase(repository).execute(
            CompleteReminderCommand(
                reminder_id=UUID("00000000-0000-0000-0000-000000000000"),
                completed_at=datetime.now(timezone.utc),
            )
        )


def test_cancel_reminder_use_case_updates_status() -> None:
    repository = InMemoryReminderRepository()
    created = CreateReminderUseCase(repository).execute(
        CreateReminderCommand(
            title="Cancelar suscripción",
            description=None,
            due_at=datetime.now(timezone.utc) + timedelta(days=1),
        )
    )

    cancelled_at = datetime.now(timezone.utc)

    reminder = CancelReminderUseCase(repository).execute(
        CancelReminderCommand(
            reminder_id=created.id,
            cancelled_at=cancelled_at,
        )
    )

    assert reminder.status == ReminderStatus.CANCELLED
    assert reminder.updated_at == cancelled_at


def test_snooze_reminder_use_case_updates_due_date() -> None:
    repository = InMemoryReminderRepository()
    created = CreateReminderUseCase(repository).execute(
        CreateReminderCommand(
            title="Tomar medicación",
            description=None,
            due_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    )

    snoozed_at = datetime.now(timezone.utc)
    new_due_at = snoozed_at + timedelta(hours=2)

    reminder = SnoozeReminderUseCase(repository).execute(
        SnoozeReminderCommand(
            reminder_id=created.id,
            new_due_at=new_due_at,
            snoozed_at=snoozed_at,
        )
    )

    assert reminder.status == ReminderStatus.SNOOZED
    assert reminder.due_at == new_due_at
    assert reminder.updated_at == snoozed_at


def test_list_pending_reminders_use_case_returns_only_pending() -> None:
    repository = InMemoryReminderRepository()

    pending = CreateReminderUseCase(repository).execute(
        CreateReminderCommand(
            title="Pendiente",
            description=None,
            due_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
    )

    completed = CreateReminderUseCase(repository).execute(
        CreateReminderCommand(
            title="Completado",
            description=None,
            due_at=datetime.now(timezone.utc) + timedelta(hours=2),
        )
    )

    CompleteReminderUseCase(repository).execute(
        CompleteReminderCommand(
            reminder_id=completed.id,
            completed_at=datetime.now(timezone.utc),
        )
    )

    result = repository.list_pending()

    assert result == [pending]
