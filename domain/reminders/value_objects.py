from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum


class RecurrenceFrequency(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass(frozen=True)
class RecurrenceRule:
    frequency: RecurrenceFrequency
    interval: int = 1

    def __post_init__(self) -> None:
        if self.interval < 1:
            raise ValueError("Recurrence interval must be greater than zero.")

    def next_due(self, current_due: datetime) -> datetime:
        """Return the next calendar occurrence while preserving local wall time."""
        if self.frequency is RecurrenceFrequency.DAILY:
            return current_due + timedelta(days=self.interval)
        if self.frequency is RecurrenceFrequency.WEEKLY:
            return current_due + timedelta(weeks=self.interval)
        if self.frequency is RecurrenceFrequency.MONTHLY:
            return _add_months(current_due, self.interval)
        return _add_months(current_due, 12 * self.interval)

    def next_due_after(self, current_due: datetime, after: datetime) -> datetime:
        """Advance missed occurrences and return the first one after ``after``."""
        candidate = current_due
        while candidate <= after:
            candidate = self.next_due(candidate)
        return candidate


def _add_months(value: datetime, months: int) -> datetime:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)
