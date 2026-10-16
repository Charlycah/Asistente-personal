from datetime import datetime, timezone
from uuid import uuid4

from domain.reminders import Reminder, ReminderRepository, ReminderStatus

from .commands import (
    CancelReminderCommand,
    CompleteReminderCommand,
    CreateReminderCommand,
    SnoozeReminderCommand,
)
from .exceptions import ReminderNotFoundError


class CreateReminderUseCase:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def execute(
        self, command: CreateReminderCommand, *, now: datetime | None = None
    ) -> Reminder:
        now = now or datetime.now(timezone.utc)

        reminder = Reminder(
            id=uuid4(),
            title=command.title,
            description=command.description,
            due_at=command.due_at,
            status=ReminderStatus.PENDING,
            recurrence=command.recurrence,
            created_at=now,
            updated_at=now,
        )

        self.repository.save(reminder)
        return reminder


class CompleteReminderUseCase:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def execute(self, command: CompleteReminderCommand) -> Reminder:
        reminder = self.repository.get_by_id(command.reminder_id)

        if reminder is None:
            raise ReminderNotFoundError("Reminder not found.")

        reminder.complete(command.completed_at)
        self.repository.save(reminder)

        return reminder


class CancelReminderUseCase:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def execute(self, command: CancelReminderCommand) -> Reminder:
        reminder = self.repository.get_by_id(command.reminder_id)

        if reminder is None:
            raise ReminderNotFoundError("Reminder not found.")

        reminder.cancel(command.cancelled_at)
        self.repository.save(reminder)

        return reminder


class SnoozeReminderUseCase:
    def __init__(self, repository: ReminderRepository) -> None:
        self.repository = repository

    def execute(self, command: SnoozeReminderCommand) -> Reminder:
        reminder = self.repository.get_by_id(command.reminder_id)

        if reminder is None:
            raise ReminderNotFoundError("Reminder not found.")

        reminder.snooze(
            new_due_at=command.new_due_at,
            snoozed_at=command.snoozed_at,
        )
        self.repository.save(reminder)

        return reminder
