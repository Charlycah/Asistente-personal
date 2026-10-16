from datetime import date, datetime

from .entities import Reminder
from .enums import ReminderStatus


class ReminderService:
    def list_due(
        self,
        reminders: list[Reminder],
        now: datetime,
    ) -> list[Reminder]:
        return sorted(
            [
                reminder
                for reminder in reminders
                if reminder.status == ReminderStatus.PENDING and reminder.due_at <= now
            ],
            key=lambda reminder: reminder.due_at,
        )

    def list_for_day(
        self,
        reminders: list[Reminder],
        target_day: date,
    ) -> list[Reminder]:
        return sorted(
            [
                reminder
                for reminder in reminders
                if reminder.status == ReminderStatus.PENDING
                and reminder.due_at.date() == target_day
            ],
            key=lambda reminder: reminder.due_at,
        )

    def list_next(
        self,
        reminders: list[Reminder],
        now: datetime,
        limit: int = 5,
    ) -> list[Reminder]:
        upcoming = [
            reminder
            for reminder in reminders
            if reminder.status == ReminderStatus.PENDING and reminder.due_at > now
        ]

        return sorted(upcoming, key=lambda reminder: reminder.due_at)[:limit]
