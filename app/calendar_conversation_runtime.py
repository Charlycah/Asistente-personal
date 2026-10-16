from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from threading import RLock

from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
    CalendarEventDraft,
    CalendarTimeRange,
)
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
)


@dataclass(frozen=True)
class CalendarConversationQuery:
    """Normalized read-only Calendar request resolved from conversation."""

    operation: str
    time_range: CalendarTimeRange
    label: str


class CalendarConversationInterceptionPort:
    """Expose Calendar reads and confirmation-gated event creation."""

    _READ_TERMS = (
        "agenda",
        "calendario",
        "evento",
        "compromiso",
        "disponibilidad",
        "disponible",
        "libre",
        "ocupado",
        "ocupada",
    )
    _WRITE_TERMS = (
        "crear evento",
        "agendar",
        "añadir evento",
        "anadir evento",
        "agrega evento",
        "programar una reunion",
        "programar reunión",
    )
    _CONFIRM_TERMS = ("si crear", "confirmo crear", "crear ahora")
    _CANCEL_TERMS = ("cancelar", "no crear", "descartar")

    def __init__(self, runtime: CalendarRuntimeComposition) -> None:
        self.runtime = runtime
        self._pending: dict[tuple[str, str], CalendarEventDraft] = {}
        self._lock = RLock()

    def intercept(self, request: GovernedConversationPipelineRequest, *, now: datetime):
        normalized = _normalize(request.text)
        command = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
        key = (request.owner.casefold(), request.session_id)
        if any(term in command for term in self._CANCEL_TERMS):
            with self._lock:
                pending = self._pending.pop(key, None)
            if pending is None:
                return None
            return GovernedOperationalInterception(
                response_text="Descarté el borrador del evento. No modifiqué Calendar.",
                rationale="calendar_event_draft_cancelled",
            )
        if any(term in command for term in self._CONFIRM_TERMS):
            return self._confirm_pending(key, now=now)

        all_terms = (*self._READ_TERMS, *self._WRITE_TERMS)
        if not any(term in normalized for term in all_terms):
            return None
        snapshot = self.runtime.snapshot()
        if snapshot.state.value != "ready":
            return GovernedOperationalInterception(
                response_text=(
                    "Calendar está integrado, pero todavía no está listo para operar."
                ),
                rationale=(
                    f"calendar_unavailable_{snapshot.reason or snapshot.state.value}"
                ),
            )
        if any(term in normalized for term in self._WRITE_TERMS):
            return self._prepare_draft(request, normalized, now=now, key=key)

        query = _parse_query(normalized, now=now)
        provider = self.runtime.require_provider()
        if query.operation == "availability":
            availability = provider.check_availability(query.time_range)
            text = _format_availability(availability, query.label)
            rationale = "calendar_availability_read_completed"
        else:
            events = provider.list_events(query.time_range)
            text = _format_events(events, query.label)
            rationale = "calendar_events_read_completed"
        return GovernedOperationalInterception(response_text=text, rationale=rationale)

    def _prepare_draft(self, request, normalized: str, *, now: datetime, key):
        query = _parse_query(normalized, now=now)
        title = _event_title(request.text)
        if title is None:
            return GovernedOperationalInterception(
                response_text=(
                    "Necesito el título del evento antes de preparar el borrador. "
                    "Por ejemplo: agendar Médico mañana a las 15."
                ),
                rationale="calendar_event_draft_missing_title",
            )
        draft = CalendarEventDraft(title=title, time_range=query.time_range)
        availability = self.runtime.require_provider().check_availability(
            draft.time_range, calendar_id=draft.calendar_id
        )
        if not availability.is_free:
            return GovernedOperationalInterception(
                response_text=(
                    f"No preparé el evento {title!r} porque ese horario está ocupado. "
                    "Consultá otro horario y lo revisamos."
                ),
                rationale="calendar_event_draft_conflict",
            )
        with self._lock:
            self._pending[key] = draft
        interval = draft.time_range
        return GovernedOperationalInterception(
            response_text=(
                "Preparé este borrador, pero todavía no modifiqué Calendar:\n"
                f"- {draft.title}\n"
                f"- {interval.starts_at:%d/%m/%Y %H:%M}–{interval.ends_at:%H:%M}\n"
                "Para crearlo respondé exactamente: sí, crear. "
                "Para descartarlo respondé: cancelar."
            ),
            rationale="calendar_event_draft_awaiting_confirmation",
        )

    def _confirm_pending(self, key, *, now: datetime):
        del now
        with self._lock:
            draft = self._pending.pop(key, None)
        if draft is None:
            return GovernedOperationalInterception(
                response_text=(
                    "No hay ningún borrador de Calendar pendiente para confirmar."
                ),
                rationale="calendar_event_confirmation_without_draft",
            )
        snapshot = self.runtime.snapshot()
        if snapshot.state.value != "ready":
            return GovernedOperationalInterception(
                response_text=(
                    "No pude crear el evento porque Calendar ya no está listo."
                ),
                rationale="calendar_event_creation_runtime_unavailable",
            )
        availability = self.runtime.require_provider().check_availability(
            draft.time_range, calendar_id=draft.calendar_id
        )
        if not availability.is_free:
            return GovernedOperationalInterception(
                response_text=(
                    "El horario dejó de estar disponible. No creé el evento y descarté "
                    "el borrador para evitar una colisión."
                ),
                rationale="calendar_event_creation_conflict_revalidated",
            )
        event = self.runtime.require_provider().create_event(draft)
        return GovernedOperationalInterception(
            response_text=(
                f"Creé {event.title!r} el {event.time_range.starts_at:%d/%m/%Y} "
                f"de {event.time_range.starts_at:%H:%M} a "
                f"{event.time_range.ends_at:%H:%M}."
            ),
            rationale="calendar_event_created_after_explicit_confirmation",
        )


def _parse_query(text: str, *, now: datetime) -> CalendarConversationQuery:
    operation = (
        "availability"
        if any(
            term in text
            for term in ("disponibilidad", "disponible", "libre", "ocupado", "ocupada")
        )
        else "events"
    )
    day_start, day_end, label = _date_interval(text, now)
    starts_at, ends_at, time_label = _apply_time_window(
        text,
        day_start=day_start,
        day_end=day_end,
    )
    if time_label:
        label = f"{label}, {time_label}"
    return CalendarConversationQuery(
        operation=operation,
        time_range=CalendarTimeRange(starts_at=starts_at, ends_at=ends_at),
        label=label,
    )


def _date_interval(text: str, now: datetime) -> tuple[datetime, datetime, str]:
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    if "pasado manana" in text:
        start = today + timedelta(days=2)
        return start, start + timedelta(days=1), "pasado mañana"
    if "manana" in text:
        start = today + timedelta(days=1)
        return start, start + timedelta(days=1), "mañana"
    if "proxima semana" in text or "semana que viene" in text:
        start = today + timedelta(days=7 - today.weekday())
        return start, start + timedelta(days=7), "la próxima semana"
    if "esta semana" in text:
        start = now
        end = today + timedelta(days=7 - today.weekday())
        return start, end, "lo que queda de esta semana"

    weekday = _requested_weekday(text)
    if weekday is not None:
        delta = (weekday - today.weekday()) % 7
        if delta == 0 and now >= today + timedelta(days=1):
            delta = 7
        start = today + timedelta(days=delta)
        return start, start + timedelta(days=1), _weekday_label(start)

    explicit = re.search(r"\b(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?\b", text)
    if explicit:
        day, month = int(explicit.group(1)), int(explicit.group(2))
        year_text = explicit.group(3)
        year = int(year_text) if year_text else now.year
        if year < 100:
            year += 2000
        try:
            start = today.replace(year=year, month=month, day=day)
        except ValueError:
            return now, now + timedelta(days=1), "las próximas 24 horas"
        if not year_text and start.date() < today.date():
            start = start.replace(year=year + 1)
        return start, start + timedelta(days=1), start.strftime("el %d/%m/%Y")

    if "hoy" in text:
        return now, today + timedelta(days=1), "hoy"
    return now, now + timedelta(days=1), "las próximas 24 horas"


def _apply_time_window(
    text: str,
    *,
    day_start: datetime,
    day_end: datetime,
) -> tuple[datetime, datetime, str | None]:
    tzinfo = day_start.tzinfo
    base = day_start.replace(hour=0, minute=0, second=0, microsecond=0)
    ranges = (
        ("por la manana", time(6), time(12), "por la mañana"),
        ("a la manana", time(6), time(12), "por la mañana"),
        ("por la tarde", time(12), time(19), "por la tarde"),
        ("a la tarde", time(12), time(19), "por la tarde"),
        ("por la noche", time(19), time(23, 59, 59), "por la noche"),
        ("a la noche", time(19), time(23, 59, 59), "por la noche"),
    )
    for term, starts, ends, label in ranges:
        if term in text:
            start = datetime.combine(base.date(), starts, tzinfo=tzinfo)
            end = datetime.combine(base.date(), ends, tzinfo=tzinfo)
            return max(day_start, start), min(day_end, end), label

    match = re.search(
        r"(?:de|entre)\s+(?:las\s+)?(\d{1,2})(?::(\d{2}))?\s+"
        r"(?:a|y)\s+(?:las\s+)?(\d{1,2})(?::(\d{2}))?",
        text,
    )
    if match:
        start_hour, start_minute = int(match.group(1)), int(match.group(2) or 0)
        end_hour, end_minute = int(match.group(3)), int(match.group(4) or 0)
        if start_hour < 24 and end_hour < 24:
            start = base.replace(hour=start_hour, minute=start_minute)
            end = base.replace(hour=end_hour, minute=end_minute)
            if end > start:
                return start, end, f"de {start:%H:%M} a {end:%H:%M}"

    match = re.search(r"(?:a\s+las|desde\s+las)\s+(\d{1,2})(?::(\d{2}))?", text)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2) or 0)
        if hour < 24:
            start = base.replace(hour=hour, minute=minute)
            return (
                start,
                min(start + timedelta(hours=1), day_end),
                f"a las {start:%H:%M}",
            )
    return day_start, day_end, None


def _requested_weekday(text: str) -> int | None:
    names = {
        "lunes": 0,
        "martes": 1,
        "miercoles": 2,
        "jueves": 3,
        "viernes": 4,
        "sabado": 5,
        "domingo": 6,
    }
    for name, value in names.items():
        if re.search(rf"\b{name}\b", text):
            return value
    return None


def _format_events(events: tuple[CalendarEvent, ...], label: str) -> str:
    ordered = sorted(events, key=lambda event: event.time_range.starts_at)
    if not ordered:
        return f"No tenés eventos {label}."
    lines = [f"Tu agenda para {label}:"]
    for event in ordered:
        starts_at = event.time_range.starts_at
        ends_at = event.time_range.ends_at
        when = f"{starts_at:%H:%M}–{ends_at:%H:%M}"
        detail = f" — {event.location}" if event.location else ""
        lines.append(f"- {when}: {event.title}{detail}")
    return "\n".join(lines)


def _format_availability(availability: CalendarAvailability, label: str) -> str:
    if availability.is_free:
        return f"Estás libre {label}."
    busy = sorted(availability.busy_ranges, key=lambda item: item.starts_at)
    lines = [f"Tenés ocupación {label} en estos horarios:"]
    lines.extend(f"- {item.starts_at:%H:%M}–{item.ends_at:%H:%M}" for item in busy)
    return "\n".join(lines)


def _weekday_label(value: datetime) -> str:
    names = (
        "el lunes",
        "el martes",
        "el miércoles",
        "el jueves",
        "el viernes",
        "el sábado",
        "el domingo",
    )
    return names[value.weekday()]


def _event_title(original: str) -> str | None:
    text = original.strip()
    match = re.match(
        r"(?:agendar|programar|crear|añadir|anadir|agrega)\s+(.+)",
        text,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    remainder = match.group(1).strip()
    temporal = re.search(
        r"\s+(?=hoy\b|mañana\b|manana\b|pasado\s+mañana\b|"
        r"pasado\s+manana\b|el\s+(?:lunes|martes|miércoles|miercoles|"
        r"jueves|viernes|sábado|sabado|domingo)\b|\d{1,2}[/-]\d{1,2}|"
        r"a\s+las\b|de\s+\d|entre\s+\d)",
        remainder,
        flags=re.IGNORECASE,
    )
    if temporal:
        remainder = remainder[: temporal.start()].strip()
    normalized = _normalize(remainder)
    if normalized in {"evento", "un evento", "una evento"}:
        return None
    for prefix in ("un evento ", "una reunion ", "un reunion ", "reunion "):
        if normalized.startswith(prefix):
            remainder = remainder[len(prefix) :].strip()
            normalized = _normalize(remainder)
            break
    if normalized in {"una reunion", "un reunion", "reunion"}:
        return "Reunión"
    if not remainder:
        return None
    return remainder[0].upper() + remainder[1:]


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.strip().casefold())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
