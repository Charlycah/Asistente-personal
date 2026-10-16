from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

from domain.reminders import (
    RecurrenceFrequency,
    RecurrenceRule,
    Reminder,
)
from infrastructure.persistence.sqlite import (
    SQLiteReminderRepository,
    create_connection,
    init_reminders_schema,
)

from .commands import (
    CancelReminderCommand,
    CreateReminderCommand,
    SnoozeReminderCommand,
)
from .use_cases import (
    CancelReminderUseCase,
    CreateReminderUseCase,
    SnoozeReminderUseCase,
)

WEEKDAYS = {
    "lunes": 0,
    "martes": 1,
    "miércoles": 2,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sábado": 5,
    "sabado": 5,
    "domingo": 6,
}


MONTHS = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

NUMBER_WORDS = {
    "una": 1,
    "uno": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
    "once": 11,
    "doce": 12,
}


@dataclass(frozen=True)
class ReminderConversationResult:
    handled: bool
    response_text: str = ""


class ReminderConversationService:
    """Deterministic conversational adapter over the existing reminder use cases."""

    def __init__(
        self,
        database_path: Path | str,
        *,
        routines_enabled: bool = True,
    ) -> None:
        self.database_path = Path(database_path)
        self.routines_enabled = routines_enabled

    def handle(
        self,
        *,
        owner: str,
        text: str,
        now: datetime,
    ) -> ReminderConversationResult:
        owner_scope = HOUSEHOLD_SCOPE
        if now.tzinfo is None:
            raise ValueError("reminder conversation time must be timezone-aware")
        normalized = _normalize(text)
        if _is_list_request(normalized):
            return ReminderConversationResult(True, self._list_pending(owner_scope))
        if _is_cancel_request(normalized):
            return ReminderConversationResult(
                True, self._cancel(normalized, now, owner_scope)
            )
        if _is_snooze_request(normalized):
            return ReminderConversationResult(
                True, self._snooze(normalized, now, owner_scope)
            )
        if _is_create_request(normalized):
            return ReminderConversationResult(
                True, self._create(text, now, owner_scope)
            )
        return ReminderConversationResult(False)

    def list_pending(self) -> tuple[Reminder, ...]:
        """Return visible pending reminders without mutating reminder state."""
        connection, repository = self._repository()
        try:
            return tuple(
                _visible_pending(
                    connection,
                    repository.list_pending(),
                    HOUSEHOLD_SCOPE,
                )
            )
        finally:
            connection.close()

    def _repository(self):
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        connection = create_connection(self.database_path)
        init_reminders_schema(connection)
        return connection, SQLiteReminderRepository(connection)

    def _create(self, text: str, now: datetime, owner_scope: str) -> str:
        try:
            command = parse_create_reminder(
                text, now, routines_enabled=self.routines_enabled
            )
        except ValueError:
            return (
                "No pude identificar cuándo querés el recordatorio. "
                "Probá, por ejemplo: 'recordame llamar al médico mañana a las 10'."
            )
        connection, repository = self._repository()
        try:
            reminder = CreateReminderUseCase(repository).execute(command, now=now)
            _set_owner_scope(connection, reminder.id, owner_scope)
        finally:
            connection.close()
        if reminder.recurrence is not None:
            cadence = _format_recurrence(reminder.recurrence)
            return (
                f"Listo. Creé la rutina {reminder.title}, {cadence}, "
                f"desde el {_format_due(reminder.due_at)}."
            )
        return (
            f"Listo. Te recordaré {reminder.title} el {_format_due(reminder.due_at)}."
        )

    def _list_pending(self, owner_scope: str) -> str:
        connection, repository = self._repository()
        try:
            reminders = _visible_pending(
                connection,
                repository.list_pending(),
                owner_scope,
            )
        finally:
            connection.close()
        if not reminders:
            return "No tenés recordatorios pendientes."
        lines = ["Tus recordatorios pendientes son:"]
        for index, reminder in enumerate(reminders, start=1):
            cadence = (
                f" — {_format_recurrence(reminder.recurrence)}"
                if reminder.recurrence is not None
                else ""
            )
            lines.append(
                f"{index}. {reminder.title} — {_format_due(reminder.due_at)}{cadence}"
            )
        return "\n".join(lines)

    def _cancel(self, normalized: str, now: datetime, owner_scope: str) -> str:
        target = _extract_target(
            normalized, ("cancelá", "cancela", "cancelar", "eliminá", "elimina")
        )
        connection, repository = self._repository()
        try:
            reminder = _find_pending(
                _visible_pending(connection, repository.list_pending(), owner_scope),
                target,
            )
            if reminder is None:
                return "No encontré un recordatorio pendiente que coincida."
            CancelReminderUseCase(repository).execute(
                CancelReminderCommand(reminder_id=reminder.id, cancelled_at=now)
            )
        finally:
            connection.close()
        return f"Cancelé el recordatorio: {reminder.title}."

    def _snooze(self, normalized: str, now: datetime, owner_scope: str) -> str:
        duration = _extract_duration(normalized)
        if duration is None:
            return (
                "Indicame cuánto querés postergarlo, por ejemplo: "
                "'media hora' o '30 minutos'."
            )
        target = _extract_target(
            normalized,
            ("postergá", "posterga", "posponé", "pospone", "reprogramá", "reprograma"),
        )
        target = re.sub(r"\b(?:por|durante)\b.*$", "", target).strip()
        connection, repository = self._repository()
        try:
            reminder = _find_pending(
                _visible_pending(connection, repository.list_pending(), owner_scope),
                target,
            )
            if reminder is None:
                return "No encontré un recordatorio pendiente que coincida."
            new_due_at = max(reminder.due_at, now) + duration
            SnoozeReminderUseCase(repository).execute(
                SnoozeReminderCommand(
                    reminder_id=reminder.id,
                    new_due_at=new_due_at,
                    snoozed_at=now,
                )
            )
        finally:
            connection.close()
        return f"Postergué {reminder.title} hasta el {_format_due(new_due_at)}."


def parse_create_reminder(
    text: str,
    now: datetime,
    *,
    routines_enabled: bool = True,
) -> CreateReminderCommand:
    normalized = _normalize(text)
    normalized = re.sub(r"^roby[,:]?\s*", "", normalized)
    normalized = re.sub(
        r"^(?:creá|crea|crear)\s+(?:una\s+)?rutina(?:\s+para)?\s+",
        "",
        normalized,
    )
    normalized = re.sub(
        r"^(?:haceme acordar(?: que)?|recordame(?: que)?|recuérdame(?: que)?)\s+",
        "",
        normalized,
    )
    recurrence, normalized = _extract_recurrence(normalized)
    if recurrence is not None and not routines_enabled:
        raise ValueError("Household routines are disabled.")
    normalized = re.sub(
        r"\s+para\s+(?:carlos|cristina|todos|ambos|el hogar)\s*$",
        "",
        normalized,
    )
    normalized = re.sub(r"\s+compartido(?:\s+del hogar)?\s*$", "", normalized)

    relative = re.search(
        r"(?:dentro de|en)\s+(\d+|\w+)\s+(minutos?|horas?)\s+(?:que\s+)?(.+)",
        normalized,
    )
    if relative:
        amount = _parse_number(relative.group(1))
        unit = relative.group(2)
        delta = (
            timedelta(minutes=amount)
            if unit.startswith("minuto")
            else timedelta(hours=amount)
        )
        return CreateReminderCommand(
            relative.group(3).strip(), None, now + delta, recurrence
        )

    normalized = re.sub(r"(?<=\d)[.](?=\d{2}\b)", ":", normalized)
    day_offset = 0
    absolute_date, normalized = _extract_absolute_date(normalized, now=now)
    weekday_index: int | None = None
    weekday_match = re.search(
        r"\b(?:el\s+)?(lunes|martes|miércoles|miercoles|jueves|viernes|"
        r"sábado|sabado|domingo)\b",
        normalized,
    )
    if weekday_match is not None:
        weekday_index = WEEKDAYS[weekday_match.group(1)]
        before = normalized[: weekday_match.start()]
        after = normalized[weekday_match.end() :]
        normalized = f"{before} {after}".strip()

    # Remove every temporal marker from the stored title. The structured
    # due_at field is the only authoritative date and time. This also avoids
    # contradictory legacy-style titles such as "hoy ... el viernes ...".
    if "mañana" in normalized:
        if weekday_index is None:
            day_offset = 1
        normalized = re.sub(r"\bmañana\b", " ", normalized)
    if "hoy" in normalized:
        normalized = re.sub(r"\bhoy\b", " ", normalized)

    match = re.search(r"(.+?)\s+a las\s+(\d{1,2}|\w+)(?::(\d{2}))?\b", normalized)
    if not match:
        match = re.search(r"a las\s+(\d{1,2}|\w+)(?::(\d{2}))?\s+(.+)", normalized)
        if not match:
            raise ValueError("Could not parse reminder time.")
        raw_hour, raw_minute, title = match.group(1), match.group(2), match.group(3)
    else:
        title, raw_hour, raw_minute = match.group(1), match.group(2), match.group(3)

    hour = _normalize_ambiguous_hour(_parse_hour(raw_hour))
    minute = int(raw_minute or 0)
    if weekday_index is not None:
        day_offset = (weekday_index - now.weekday()) % 7
    if absolute_date is not None:
        due_at = absolute_date.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        )
        if due_at <= now:
            if absolute_date.year == now.year and not _absolute_date_has_year(text):
                due_at = due_at.replace(year=due_at.year + 1)
            else:
                raise ValueError("Reminder date must be in the future.")
    else:
        due_at = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0,
        ) + timedelta(days=day_offset)
        if weekday_index is not None and due_at <= now:
            due_at += timedelta(days=7)
        elif weekday_index is None and day_offset == 0 and due_at <= now:
            due_at += timedelta(days=1)
    clean_title = _clean_reminder_title(title)
    if not clean_title:
        raise ValueError("Could not parse reminder title.")
    return CreateReminderCommand(clean_title, None, due_at, recurrence)



def _extract_absolute_date(text: str, *, now: datetime) -> tuple[datetime | None, str]:
    numeric = re.search(
        r"\b(?:el\s+)?(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b",
        text,
    )
    if numeric is not None:
        day = int(numeric.group(1))
        month = int(numeric.group(2))
        year_text = numeric.group(3)
        year = _normalize_year(year_text, now.year)
        value = now.replace(
            year=year,
            month=month,
            day=day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return value, _remove_span(text, numeric.span())

    named = re.search(
        r"\b(?:el\s+)?(\d{1,2})\s+de\s+"
        r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
        r"octubre|noviembre|diciembre)"
        r"(?:\s+de\s+(\d{2,4}))?\b",
        text,
    )
    if named is None:
        return None, text
    day = int(named.group(1))
    month = MONTHS[named.group(2)]
    year = _normalize_year(named.group(3), now.year)
    value = now.replace(
        year=year,
        month=month,
        day=day,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    return value, _remove_span(text, named.span())


def _normalize_year(raw: str | None, fallback: int) -> int:
    if raw is None:
        return fallback
    year = int(raw)
    return year + 2000 if year < 100 else year


def _absolute_date_has_year(text: str) -> bool:
    if re.search(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", text):
        return True
    return bool(
        re.search(
            r"\b\d{1,2}\s+de\s+(?:enero|febrero|marzo|abril|mayo|"
            r"junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
            r"\s+de\s+\d{2,4}\b",
            text,
        )
    )


def _remove_span(text: str, span: tuple[int, int]) -> str:
    start, end = span
    return " ".join((text[:start] + " " + text[end:]).split())

def _clean_reminder_title(title: str) -> str:
    """Store semantic content only; date/time and speaker person stay separate."""
    clean = " ".join(title.strip(" ,.").split())
    clean = re.sub(
        r"(?i)\b(?:hoy|mañana|el\s+(?:lunes|martes|miércoles|miercoles|"
        r"jueves|viernes|sábado|sabado|domingo))\b",
        " ",
        clean,
    )
    clean = re.sub(r"(?i)^yo\s+tengo\s+", "", clean)
    clean = re.sub(r"(?i)^tengo\s+", "", clean)
    return " ".join(clean.strip(" ,.").split())


def _extract_recurrence(text: str) -> tuple[RecurrenceRule | None, str]:
    patterns = (
        (
            r"\b(?:todos los días|todos los dias|cada día|cada dia)\b",
            RecurrenceFrequency.DAILY,
            1,
        ),
        (r"\b(?:todas las semanas|cada semana)\b", RecurrenceFrequency.WEEKLY, 1),
        (r"\b(?:todos los meses|cada mes)\b", RecurrenceFrequency.MONTHLY, 1),
        (
            r"\b(?:todos los años|todos los anos|cada año|cada ano)\b",
            RecurrenceFrequency.YEARLY,
            1,
        ),
    )
    for pattern, frequency, interval in patterns:
        if re.search(pattern, text):
            return (
                RecurrenceRule(frequency=frequency, interval=interval),
                re.sub(pattern, " ", text).strip(),
            )

    interval_match = re.search(
        r"\bcada\s+(\d+|\w+)\s+"
        r"(días|dias|semanas|meses|años|anos)\b",
        text,
    )
    if interval_match is None:
        return None, text
    interval = _parse_number(interval_match.group(1))
    unit = interval_match.group(2)
    frequency = {
        "días": RecurrenceFrequency.DAILY,
        "dias": RecurrenceFrequency.DAILY,
        "semanas": RecurrenceFrequency.WEEKLY,
        "meses": RecurrenceFrequency.MONTHLY,
        "años": RecurrenceFrequency.YEARLY,
        "anos": RecurrenceFrequency.YEARLY,
    }[unit]
    return (
        RecurrenceRule(frequency=frequency, interval=interval),
        (text[: interval_match.start()] + " " + text[interval_match.end() :]).strip(),
    )


def _format_recurrence(rule: RecurrenceRule) -> str:
    singular = {
        RecurrenceFrequency.DAILY: "día",
        RecurrenceFrequency.WEEKLY: "semana",
        RecurrenceFrequency.MONTHLY: "mes",
        RecurrenceFrequency.YEARLY: "año",
    }[rule.frequency]
    plural = {
        RecurrenceFrequency.DAILY: "días",
        RecurrenceFrequency.WEEKLY: "semanas",
        RecurrenceFrequency.MONTHLY: "meses",
        RecurrenceFrequency.YEARLY: "años",
    }[rule.frequency]
    if rule.interval == 1:
        return f"cada {singular}"
    return f"cada {rule.interval} {plural}"


def _normalize(text: str) -> str:
    return " ".join(text.casefold().strip().split())


def _is_create_request(text: str) -> bool:
    return bool(
        re.search(
            r"\b(recordame|recuérdame|haceme acordar|"
            r"creá una rutina|crea una rutina)\b",
            text,
        )
    )


def _is_list_request(text: str) -> bool:
    return bool(
        re.search(r"\b(recordatorio|recordatorios|rutina|rutinas)\b", text)
    ) and bool(
        re.search(r"\b(qué|que|cuáles|cuales|lista|mostrá|mostra|tengo)\b", text)
    )


def _is_cancel_request(text: str) -> bool:
    return bool(
        re.search(r"\b(recordatorio|recordatorios|rutina|rutinas)\b", text)
    ) and bool(re.search(r"\b(cancelá|cancela|cancelar|eliminá|elimina)\b", text))


def _is_snooze_request(text: str) -> bool:
    return bool(
        re.search(r"\b(recordatorio|recordatorios|rutina|rutinas)\b", text)
    ) and bool(
        re.search(
            r"\b(postergá|posterga|posponé|pospone|reprogramá|reprograma)\b", text
        )
    )


def _extract_target(text: str, verbs: tuple[str, ...]) -> str:
    pattern = "|".join(re.escape(item) for item in verbs)
    target = re.sub(rf"^.*?\b(?:{pattern})\b", "", text).strip()
    target = re.sub(
        r"^(?:(?:el|la|un|una)\s+)?(?:recordatorio|rutina)(?:\s+de)?\s+", "", target
    ).strip()
    return target


def _find_pending(reminders: list[Reminder], target: str) -> Reminder | None:
    if not reminders:
        return None
    if not target:
        return reminders[0] if len(reminders) == 1 else None
    if target.isdigit():
        index = int(target) - 1
        return reminders[index] if 0 <= index < len(reminders) else None
    try:
        reminder_id = UUID(target)
    except ValueError:
        reminder_id = None
    for reminder in reminders:
        if reminder_id == reminder.id or str(reminder.id).startswith(target):
            return reminder
        if target in reminder.title.casefold():
            return reminder
    return None


def _extract_duration(text: str) -> timedelta | None:
    if "media hora" in text:
        return timedelta(minutes=30)
    match = re.search(r"(\d+|\w+)\s+(minutos?|horas?)", text)
    if not match:
        return None
    amount = _parse_number(match.group(1))
    return (
        timedelta(minutes=amount)
        if match.group(2).startswith("minuto")
        else timedelta(hours=amount)
    )


def _parse_number(raw: str) -> int:
    if raw.isdigit():
        return int(raw)
    if raw in NUMBER_WORDS:
        return NUMBER_WORDS[raw]
    raise ValueError(f"Unsupported number: {raw}")


def _parse_hour(raw_hour: str) -> int:
    hour = _parse_number(raw_hour)
    if not 0 <= hour <= 23:
        raise ValueError(f"Unsupported hour: {raw_hour}")
    return hour


def _normalize_ambiguous_hour(hour: int) -> int:
    if 1 <= hour <= 7:
        return hour + 12
    return hour


def _format_due(due_at: datetime) -> str:
    return due_at.strftime("%d/%m/%Y a las %H:%M")


HOUSEHOLD_SCOPE = "__household__"


def _set_owner_scope(connection, reminder_id: UUID, owner_scope: str) -> None:
    connection.execute(
        """
        INSERT INTO reminder_ownership (reminder_id, owner_scope) VALUES (?, ?)
        ON CONFLICT(reminder_id) DO UPDATE SET owner_scope = excluded.owner_scope
        """,
        (str(reminder_id), owner_scope),
    )
    connection.commit()


def _visible_pending(
    connection, reminders: list[Reminder], owner_scope: str
) -> list[Reminder]:
    visible: list[Reminder] = []
    for reminder in reminders:
        row = connection.execute(
            "SELECT owner_scope FROM reminder_ownership WHERE reminder_id = ?",
            (str(reminder.id),),
        ).fetchone()
        # Carlos and Cristina share one household identity. Historical owner rows
        # remain readable for backward compatibility and never restrict access.
        if row is None or row["owner_scope"]:
            visible.append(reminder)
    return visible
