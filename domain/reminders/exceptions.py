from domain.exceptions import DomainError


class ReminderDomainError(DomainError):
    """Base exception for reminder domain errors."""


class InvalidReminderTitleError(ReminderDomainError):
    """Raised when a reminder title is invalid."""


class InvalidReminderDueDateError(ReminderDomainError):
    """Raised when a reminder due date is invalid."""


class InvalidReminderStateTransitionError(ReminderDomainError):
    """Raised when a reminder status transition is invalid."""
