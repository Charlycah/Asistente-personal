from __future__ import annotations

import os
import random
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

from infrastructure.persistence.sqlite.connection import create_connection
from infrastructure.persistence.sqlite.reminder_repository import (
    SQLiteReminderRepository,
)
from infrastructure.persistence.sqlite.schema import init_reminders_schema

_TRUE = {"1", "true", "yes", "on"}


class BatterySnapshotPort(Protocol):
    def read(self): ...


class GmailBriefingPort(Protocol):
    def announce(self): ...


class GoalProjectReviewPort(Protocol):
    def briefing_lines(self, *, now: datetime) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class DailyHouseholdBriefingConfig:
    enabled: bool = True
    horizon_hours: int = 24
    max_items: int = 8
    include_gmail: bool = True
    include_battery: bool = True
    battery_warning_percent: float = 10.0


class DailyHouseholdBriefingService:
    """Composes a deterministic household briefing from official local runtimes."""

    def __init__(
        self,
        *,
        reminder_db_path: str | Path,
        config: DailyHouseholdBriefingConfig | None = None,
        battery_sensor: BatterySnapshotPort | None = None,
        gmail_announcer: GmailBriefingPort | None = None,
        goal_project_review: GoalProjectReviewPort | None = None,
    ) -> None:
        self.reminder_db_path = Path(reminder_db_path)
        self.config = config or DailyHouseholdBriefingConfig()
        self.battery_sensor = battery_sensor
        self.gmail_announcer = gmail_announcer
        self.goal_project_review = goal_project_review

    def generate(self, *, now: datetime | None = None) -> str:
        timestamp = now or datetime.now().astimezone()
        if not self.config.enabled:
            return ""
        lines = [self._greeting(timestamp)]
        items = self._reminder_lines(timestamp)
        battery = self._battery_line()
        if battery:
            items.append(battery)
        gmail = self._gmail_line()
        if gmail:
            items.append(gmail)
        items.extend(self._review_lines(timestamp))
        if not items:
            return "\n".join(lines)
        visible_items = items[: self.config.max_items]
        if len(visible_items) == 1 and visible_items[0].startswith("Recordatorio: "):
            lines.append("No te olvides:")
            visible_items[0] = visible_items[0].removeprefix("Recordatorio: ")
        elif len(visible_items) == 1:
            lines.append("Tengo algo importante para contarte:")
        else:
            lines.append("Tengo algunas cosas importantes para contarte:")
        lines.extend(f"- {item}" for item in visible_items)
        return "\n".join(lines)

    def _reminder_lines(self, now: datetime) -> list[str]:
        try:
            with create_connection(self.reminder_db_path) as connection:
                init_reminders_schema(connection)
                pending = SQLiteReminderRepository(connection).list_pending()
        except (OSError, ValueError):
            return []
        horizon = now + timedelta(hours=self.config.horizon_hours)
        due = sorted(
            (item for item in pending if item.due_at <= horizon),
            key=lambda item: item.due_at,
        )
        lines = []
        for reminder in due:
            label = "Rutina" if reminder.recurrence is not None else "Recordatorio"
            local_due = reminder.due_at.astimezone(now.tzinfo)
            when = self._format_when(local_due, now).capitalize()
            title = self._spoken_reminder_title(reminder.title)
            if re.match(r"(?i)^tenés\b", title):
                rendered = f"{when} {title}."
            elif re.match(r"(?i)^(?:turno|reunión|reunion|cita)\b", title):
                rendered = f"{when} tenés {title}."
            else:
                rendered = f"{when}: {title}."
            lines.append(f"{label}: {rendered}")
        return lines


    @staticmethod
    def _spoken_reminder_title(title: str) -> str:
        spoken = " ".join(title.strip().split())
        # The reminder stores the owner's original first-person wording.
        # During a briefing ROBY speaks to the owner, so use voseo.
        spoken = re.sub(r"(?i)^tengo\b", "tenés", spoken)
        spoken = re.sub(r"(?i)^yo\s+tengo\b", "tenés", spoken)
        # Structured due_at is authoritative. Remove stale temporal tails that
        # may remain in reminders created by older parser versions.
        spoken = re.sub(
            r"(?i),?\s*(?:hoy|mañana|el\s+(?:lunes|martes|miércoles|miercoles|"
            r"jueves|viernes|sábado|sabado|domingo))\s+a\s+las\s+"
            r"\d{1,2}(?::|[.])\d{2}\s*$",
            "",
            spoken,
        )
        return spoken.strip(" ,.")

    def _battery_line(self) -> str:
        if not self.config.include_battery or self.battery_sensor is None:
            return ""
        try:
            snapshot = self.battery_sensor.read()
            percent = getattr(snapshot, "percent", None)
            plugged = getattr(snapshot, "plugged", None)
        except Exception:
            return ""
        if percent is None or bool(plugged):
            return ""
        level = float(percent)
        if level > self.config.battery_warning_percent:
            return ""
        rounded = round(level)
        if rounded <= 5:
            return (
                f"La batería está en {rounded}%. "
                "Es importante conectar el equipo ahora."
            )
        return f"La batería está en {rounded}%. Conviene conectar el equipo pronto."

    def _review_lines(self, now: datetime) -> list[str]:
        if self.goal_project_review is None:
            return []
        try:
            return list(self.goal_project_review.briefing_lines(now=now))
        except Exception:
            return []

    def _gmail_line(self) -> str:
        if not self.config.include_gmail or self.gmail_announcer is None:
            return ""
        try:
            result = self.gmail_announcer.announce()
        except Exception:
            return ""
        return str(getattr(result, "text", "")).strip()

    @staticmethod
    def _greeting(now: datetime) -> str:
        if now.hour < 12:
            greetings = (
                "Buen día. ¿Cómo estás?",
                "Buen día. ¿Todo bien?",
                "Buen día. ¿Cómo va todo?",
            )
        elif now.hour < 20:
            greetings = (
                "Buenas tardes. ¿Cómo estás?",
                "Buenas tardes. ¿Todo bien?",
                "Buenas tardes. ¿Cómo va todo?",
            )
        else:
            greetings = (
                "Buenas noches. ¿Cómo estás?",
                "Buenas noches. ¿Todo bien?",
                "Buenas noches. ¿Cómo va todo?",
            )
        return random.choice(greetings)

    @staticmethod
    def _format_when(due_at: datetime, now: datetime) -> str:
        if due_at.date() == now.date():
            return f"hoy a las {due_at:%H:%M}"
        days_ahead = (due_at.date() - now.date()).days
        if 0 < days_ahead <= 7:
            weekdays = (
                "lunes",
                "martes",
                "miércoles",
                "jueves",
                "viernes",
                "sábado",
                "domingo",
            )
            return f"el {weekdays[due_at.weekday()]} a las {due_at:%H:%M}"
        return f"el {due_at:%d/%m} a las {due_at:%H:%M}"


def build_daily_household_briefing_from_environment(
    *, battery_sensor=None, gmail_announcer=None, goal_project_review=None
) -> DailyHouseholdBriefingService | None:
    enabled = (
        os.getenv("ROBY_DAILY_BRIEFING_ENABLED", "true").strip().casefold() in _TRUE
    )
    if not enabled:
        return None
    return DailyHouseholdBriefingService(
        reminder_db_path=os.getenv("ROBY_REMINDER_DB_PATH", ".roby/reminders.db"),
        config=DailyHouseholdBriefingConfig(
            enabled=True,
            horizon_hours=int(os.getenv("ROBY_DAILY_BRIEFING_HORIZON_HOURS", "24")),
            max_items=int(os.getenv("ROBY_DAILY_BRIEFING_MAX_ITEMS", "8")),
            include_gmail=(
                os.getenv("ROBY_DAILY_BRIEFING_INCLUDE_GMAIL", "true")
                .strip()
                .casefold()
                in _TRUE
            ),
            include_battery=(
                os.getenv("ROBY_DAILY_BRIEFING_INCLUDE_BATTERY", "true")
                .strip()
                .casefold()
                in _TRUE
            ),
            battery_warning_percent=float(
                os.getenv("ROBY_DAILY_BRIEFING_BATTERY_WARNING_PERCENT", "10")
            ),
        ),
        battery_sensor=battery_sensor,
        gmail_announcer=gmail_announcer,
        goal_project_review=goal_project_review,
    )
