class ReminderApplicationError(Exception):
    """Base exception for reminder application errors."""


class ReminderNotFoundError(ReminderApplicationError):
    """Raised when a reminder does not exist."""
