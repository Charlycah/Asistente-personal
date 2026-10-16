from enum import StrEnum


class ReminderStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    SNOOZED = "snoozed"
