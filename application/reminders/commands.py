from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.reminders import RecurrenceRule


@dataclass(frozen=True)
class CreateReminderCommand:
    title: str
    description: str | None
    due_at: datetime
    recurrence: RecurrenceRule | None = None


@dataclass(frozen=True)
class CompleteReminderCommand:
    reminder_id: UUID
    completed_at: datetime


@dataclass(frozen=True)
class CancelReminderCommand:
    reminder_id: UUID
    cancelled_at: datetime


@dataclass(frozen=True)
class SnoozeReminderCommand:
    reminder_id: UUID
    new_due_at: datetime
    snoozed_at: datetime
