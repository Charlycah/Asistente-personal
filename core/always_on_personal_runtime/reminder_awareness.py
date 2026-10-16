from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import UUID

from domain.reminders import Reminder


class DueReminderSource(Protocol):
    def list_due(self, *, now: datetime) -> list[Reminder]: ...

    def was_notified(self, reminder_id: UUID, *, due_at: datetime) -> bool: ...

    def mark_notified(
        self,
        reminder_id: UUID,
        *,
        due_at: datetime,
        notified_at: datetime,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ReminderAdvanceStage:
    key: str
    offset: timedelta


@dataclass(frozen=True, slots=True)
class IntelligentReminderPolicy:
    """Defines deterministic, persistent advance notices for personal reminders."""

    stages: tuple[ReminderAdvanceStage, ...] = (
        ReminderAdvanceStage("three_days", timedelta(days=3)),
        ReminderAdvanceStage("one_day", timedelta(days=1)),
        ReminderAdvanceStage("same_day", timedelta(hours=8)),
        ReminderAdvanceStage("one_hour", timedelta(hours=1)),
    )
    delivery_tolerance: timedelta = timedelta(minutes=10)

    def __post_init__(self) -> None:
        if not self.stages:
            raise ValueError("intelligent reminder policy requires stages")
        if self.delivery_tolerance.total_seconds() < 0:
            raise ValueError("reminder delivery tolerance must not be negative")
        keys = [stage.key for stage in self.stages]
        if len(set(keys)) != len(keys):
            raise ValueError("reminder advance stage keys must be unique")
        if any(stage.offset.total_seconds() <= 0 for stage in self.stages):
            raise ValueError("reminder advance offsets must be positive")


class ReminderAwarenessService:
    """Delivers staged advance notices and due reminders exactly once."""

    def __init__(
        self,
        source: DueReminderSource,
        *,
        notify: Callable[[str], None],
        owner: str = "Carlos",
        poll_interval: timedelta = timedelta(seconds=30),
        clock: Callable[[], datetime] | None = None,
        wait: Callable[[float], bool] | None = None,
        intelligent_policy: IntelligentReminderPolicy | None = None,
        enhance_notice: Callable[[Reminder, str], str] | None = None,
    ) -> None:
        if poll_interval.total_seconds() <= 0:
            raise ValueError("reminder poll interval must be positive")
        self.source = source
        self.notify = notify
        self.owner = owner.strip() or "Carlos"
        self.poll_interval = poll_interval
        self.intelligent_policy = intelligent_policy
        self.enhance_notice = enhance_notice
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._stop = threading.Event()
        self._wait = wait or self._stop.wait
        self._thread: threading.Thread | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def start(self) -> None:
        if self.is_running:
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="roby-reminder-awareness",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=2.0)
        self._thread = None

    def check_once(self, *, now: datetime | None = None) -> tuple[str, ...]:
        timestamp = now or self._clock()
        if timestamp.tzinfo is None:
            raise ValueError("reminder awareness time must be timezone-aware")

        messages = list(self._check_advance_notices(timestamp))
        try:
            due = self.source.list_due(now=timestamp)
        except Exception:
            return tuple(messages)

        for reminder in due:
            try:
                if self.source.was_notified(reminder.id, due_at=reminder.due_at):
                    continue
                message = self._enhance(reminder, self._render_due(reminder))
                self.notify(message)
                self.source.mark_notified(
                    reminder.id,
                    due_at=reminder.due_at,
                    notified_at=timestamp,
                )
                messages.append(message)
            except Exception:
                continue
        return tuple(messages)

    def _check_advance_notices(self, now: datetime) -> tuple[str, ...]:
        if self.intelligent_policy is None:
            return ()
        list_upcoming = getattr(self.source, "list_upcoming", None)
        was_advance_notified = getattr(self.source, "was_advance_notified", None)
        mark_advance_notified = getattr(self.source, "mark_advance_notified", None)
        if not all((list_upcoming, was_advance_notified, mark_advance_notified)):
            return ()

        longest = max(stage.offset for stage in self.intelligent_policy.stages)
        try:
            upcoming = list_upcoming(now=now, until=now + longest)
        except Exception:
            return ()

        messages: list[str] = []
        for reminder in upcoming:
            stage = self._eligible_stage(reminder, now)
            if stage is None:
                continue
            try:
                if was_advance_notified(
                    reminder.id,
                    due_at=reminder.due_at,
                    stage=stage.key,
                ):
                    continue
                message = self._enhance(
                    reminder,
                    self._render_advance(reminder, stage, now),
                )
                self.notify(message)
                mark_advance_notified(
                    reminder.id,
                    due_at=reminder.due_at,
                    stage=stage.key,
                    notified_at=now,
                )
                messages.append(message)
            except Exception:
                continue
        return tuple(messages)

    def _eligible_stage(
        self,
        reminder: Reminder,
        now: datetime,
    ) -> ReminderAdvanceStage | None:
        remaining = reminder.due_at - now
        if remaining.total_seconds() <= 0:
            return None
        tolerance = self.intelligent_policy.delivery_tolerance
        eligible = [
            stage
            for stage in self.intelligent_policy.stages
            if remaining <= stage.offset + tolerance
        ]
        if not eligible:
            return None
        # Choose the nearest not-yet-passed milestone. Persistence prevents repeats.
        return min(eligible, key=lambda stage: stage.offset)

    def _enhance(self, reminder: Reminder, message: str) -> str:
        if self.enhance_notice is None:
            return message
        try:
            enhanced = self.enhance_notice(reminder, message)
        except Exception:
            return message
        return enhanced.strip() or message

    def _render_due(self, reminder: Reminder) -> str:
        description = (reminder.description or "").strip()
        detail = f" {description}" if description else ""
        return f"No te olvides: {reminder.title}.{detail}".strip()

    def _render_advance(
        self,
        reminder: Reminder,
        stage: ReminderAdvanceStage,
        now: datetime,
    ) -> str:
        due = reminder.due_at.astimezone(now.tzinfo)
        hour = due.strftime("%H:%M")
        if stage.key == "three_days":
            day = self._weekday_name(due)
            prefix = f"no te olvides de que el {day}"
        elif stage.key == "one_day":
            prefix = "mañana"
        elif stage.key == "same_day":
            prefix = "hoy"
        elif stage.key == "one_hour":
            prefix = "en una hora"
        else:
            prefix = f"el {due.strftime('%d/%m/%Y')}"
        return f"{prefix.capitalize()} a las {hour} tenés {reminder.title}."

    @staticmethod
    def _weekday_name(value: datetime) -> str:
        names = (
            "lunes",
            "martes",
            "miércoles",
            "jueves",
            "viernes",
            "sábado",
            "domingo",
        )
        return names[value.weekday()]

    def _run(self) -> None:
        self.check_once()
        interval = self.poll_interval.total_seconds()
        while not self._wait(interval):
            self.check_once()
