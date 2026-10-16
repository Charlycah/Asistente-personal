from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .enums import ReminderStatus
from .exceptions import (
    InvalidReminderDueDateError,
    InvalidReminderStateTransitionError,
    InvalidReminderTitleError,
)
from .value_objects import RecurrenceRule


@dataclass
class Reminder:
    id: UUID
    title: str
    description: str | None
    due_at: datetime
    status: ReminderStatus
    recurrence: RecurrenceRule | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.title or not self.title.strip():
            raise InvalidReminderTitleError("Reminder title cannot be empty.")

        if self.due_at < self.created_at:
            raise InvalidReminderDueDateError(
                "Reminder due date cannot be before creation date."
            )

    def complete(self, completed_at: datetime) -> None:
        if self.status != ReminderStatus.PENDING:
            raise InvalidReminderStateTransitionError(
                "Only pending reminders can be completed."
            )

        self.status = ReminderStatus.COMPLETED
        self.updated_at = completed_at

    def cancel(self, cancelled_at: datetime) -> None:
        if self.status == ReminderStatus.COMPLETED:
            raise InvalidReminderStateTransitionError(
                "Completed reminders cannot be cancelled."
            )

        self.status = ReminderStatus.CANCELLED
        self.updated_at = cancelled_at

    def snooze(self, new_due_at: datetime, snoozed_at: datetime) -> None:
        if self.status != ReminderStatus.PENDING:
            raise InvalidReminderStateTransitionError(
                "Only pending reminders can be snoozed."
            )

        if new_due_at <= snoozed_at:
            raise InvalidReminderDueDateError("Snoozed due date must be in the future.")

        self.due_at = new_due_at
        self.status = ReminderStatus.SNOOZED
        self.updated_at = snoozed_at
