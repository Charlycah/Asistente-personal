from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from core.tool_gateway import ToolCapability, ToolGatewayManager
from infrastructure.calendar.calendar_contract import (
    CalendarEventDraft,
    CalendarTimeRange,
)
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
)


class CalendarToolGatewayRegistration:
    """Register Calendar behind M61 without granting conversational writes."""

    LIST = "calendar.events.list"
    AVAILABILITY = "calendar.availability.check"
    CREATE = "calendar.event.create"

    def __init__(self, runtime: CalendarRuntimeComposition) -> None:
        self.runtime = runtime

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        ready = self.runtime.snapshot().state.value == "ready"
        common = {"kind": "calendar", "provider": "google", "runtime": "official"}
        gateway.register_capability(
            ToolCapability(
                self.LIST,
                "Lista eventos del calendario en un intervalo explícito.",
                enabled=ready,
                metadata={**common, "permission_scope": "read"},
            ),
            self._list_events if ready else None,
        )
        gateway.register_capability(
            ToolCapability(
                self.AVAILABILITY,
                "Consulta disponibilidad del calendario en un intervalo explícito.",
                enabled=ready,
                metadata={**common, "permission_scope": "read"},
            ),
            self._check_availability if ready else None,
        )
        gateway.register_capability(
            ToolCapability(
                self.CREATE,
                "Crea un evento sólo tras confirmación explícita y payload validado.",
                risk_level="high",
                enabled=ready,
                requires_confirmation=True,
                metadata={
                    **common,
                    "permission_scope": "write",
                    "activation": "explicit_confirmation",
                },
            ),
            self._create_event if ready else None,
        )

    def _create_event(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if payload.get("confirmed") is not True:
            raise PermissionError(
                "calendar event creation requires explicit confirmation"
            )
        title = str(payload.get("title", "")).strip()
        if not title:
            raise ValueError("calendar payload requires a non-empty title")
        draft = CalendarEventDraft(
            title=title,
            time_range=_time_range(payload),
            calendar_id=str(payload.get("calendar_id", "primary")),
            description=_optional_text(payload.get("description")),
            location=_optional_text(payload.get("location")),
            attendee_emails=tuple(
                str(item).strip()
                for item in payload.get("attendee_emails", ())
            ),
        )
        availability = self.runtime.require_provider().check_availability(
            draft.time_range, calendar_id=draft.calendar_id
        )
        if not availability.is_free:
            raise RuntimeError("calendar event interval is no longer available")
        event = self.runtime.require_provider().create_event(draft)
        return {
            "event": {
                "id": event.event_id,
                "title": event.title,
                "starts_at": event.time_range.starts_at.isoformat(),
                "ends_at": event.time_range.ends_at.isoformat(),
                "calendar_id": event.calendar_id,
            }
        }

    def _list_events(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        interval = _time_range(payload)
        events = self.runtime.require_provider().list_events(
            interval,
            calendar_id=str(payload.get("calendar_id", "primary")),
        )
        return {
            "events": [
                {
                    "id": event.event_id,
                    "title": event.title,
                    "starts_at": event.time_range.starts_at.isoformat(),
                    "ends_at": event.time_range.ends_at.isoformat(),
                    "calendar_id": event.calendar_id,
                }
                for event in events
            ]
        }

    def _check_availability(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        availability = self.runtime.require_provider().check_availability(
            _time_range(payload),
            calendar_id=str(payload.get("calendar_id", "primary")),
        )
        return {
            "is_free": availability.is_free,
            "busy_ranges": [
                {
                    "starts_at": item.starts_at.isoformat(),
                    "ends_at": item.ends_at.isoformat(),
                }
                for item in availability.busy_ranges
            ],
        }


def _time_range(payload: Mapping[str, Any]) -> CalendarTimeRange:
    try:
        starts_at = datetime.fromisoformat(str(payload["starts_at"]))
        ends_at = datetime.fromisoformat(str(payload["ends_at"]))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("calendar payload requires ISO starts_at and ends_at") from exc
    return CalendarTimeRange(starts_at=starts_at, ends_at=ends_at)


def _optional_text(value: Any) -> str | None:
    text = str(value).strip() if value is not None else ""
    return text or None
