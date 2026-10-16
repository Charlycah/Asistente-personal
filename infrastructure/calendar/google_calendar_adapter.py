from __future__ import annotations

import importlib
from collections.abc import Callable, Mapping
from datetime import date, datetime, time, timezone
from typing import Any, Protocol

from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
    CalendarEventDraft,
    CalendarProvider,
    CalendarTimeRange,
)


class CalendarProviderAuthenticationError(RuntimeError):
    """Google Calendar rejected or could not obtain deployment credentials."""


class CalendarProviderRateLimitError(RuntimeError):
    """Google Calendar refused the request because of provider throttling."""


class CalendarProviderRejectedError(RuntimeError):
    """Google Calendar rejected a validly transported request."""


class CalendarApiRequest(Protocol):
    def execute(self) -> Mapping[str, Any]: ...


class CalendarApiServiceFactory(Protocol):
    def __call__(self) -> Any: ...


class GoogleCalendarApiServiceFactory:
    """Lazily build the Google Calendar SDK client from governed credentials."""

    def __init__(self, credentials_loader: Callable[[], object]) -> None:
        self._credentials_loader = credentials_loader

    def __call__(self) -> Any:
        credentials = self._credentials_loader()
        if credentials is None:
            raise CalendarProviderAuthenticationError("credentials unavailable")
        build = _import_symbol("googleapiclient.discovery", "build")
        return build(
            "calendar",
            "v3",
            credentials=credentials,
            cache_discovery=False,
        )


class GoogleCalendarAdapter(CalendarProvider):
    """Translate Google Calendar API operations into ROBY's neutral contract."""

    def __init__(self, service_factory: CalendarApiServiceFactory) -> None:
        self._service_factory = service_factory

    def list_events(
        self,
        time_range: CalendarTimeRange,
        *,
        calendar_id: str = "primary",
    ) -> tuple[CalendarEvent, ...]:
        _require_calendar_id(calendar_id)
        try:
            response = (
                self._service_factory()
                .events()
                .list(
                    calendarId=calendar_id,
                    timeMin=_to_rfc3339(time_range.starts_at),
                    timeMax=_to_rfc3339(time_range.ends_at),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            items = response.get("items", ())
            if not isinstance(items, (list, tuple)):
                raise CalendarProviderRejectedError(
                    "google calendar events response must contain a list"
                )
            return tuple(
                _normalize_event(item, default_calendar_id=calendar_id)
                for item in items
                if isinstance(item, Mapping) and item.get("status") != "cancelled"
            )
        except (
            CalendarProviderAuthenticationError,
            CalendarProviderRateLimitError,
            CalendarProviderRejectedError,
            TimeoutError,
            ConnectionError,
            OSError,
        ):
            raise
        except Exception as exc:
            _raise_normalized(exc)

    def check_availability(
        self,
        time_range: CalendarTimeRange,
        *,
        calendar_id: str = "primary",
    ) -> CalendarAvailability:
        _require_calendar_id(calendar_id)
        body = {
            "timeMin": _to_rfc3339(time_range.starts_at),
            "timeMax": _to_rfc3339(time_range.ends_at),
            "items": [{"id": calendar_id}],
        }
        try:
            response = self._service_factory().freebusy().query(body=body).execute()
            calendars = response.get("calendars", {})
            if not isinstance(calendars, Mapping):
                raise CalendarProviderRejectedError(
                    "google calendar freebusy response must contain calendars"
                )
            calendar = calendars.get(calendar_id, {})
            if not isinstance(calendar, Mapping):
                raise CalendarProviderRejectedError(
                    "google calendar freebusy entry must be an object"
                )
            busy = calendar.get("busy", ())
            if not isinstance(busy, (list, tuple)):
                raise CalendarProviderRejectedError(
                    "google calendar busy response must contain a list"
                )
            busy_ranges = tuple(
                CalendarTimeRange(
                    starts_at=_parse_datetime(str(item["start"])),
                    ends_at=_parse_datetime(str(item["end"])),
                )
                for item in busy
                if isinstance(item, Mapping) and item.get("start") and item.get("end")
            )
            return CalendarAvailability(
                requested_range=time_range,
                busy_ranges=busy_ranges,
            )
        except (
            CalendarProviderAuthenticationError,
            CalendarProviderRateLimitError,
            CalendarProviderRejectedError,
            TimeoutError,
            ConnectionError,
            OSError,
        ):
            raise
        except Exception as exc:
            _raise_normalized(exc)

    def create_event(self, draft: CalendarEventDraft) -> CalendarEvent:
        body: dict[str, Any] = {
            "summary": draft.title,
            "start": {"dateTime": _to_rfc3339(draft.time_range.starts_at)},
            "end": {"dateTime": _to_rfc3339(draft.time_range.ends_at)},
        }
        if draft.description is not None:
            body["description"] = draft.description
        if draft.location is not None:
            body["location"] = draft.location
        if draft.attendee_emails:
            body["attendees"] = [
                {"email": email} for email in draft.attendee_emails
            ]
        try:
            response = (
                self._service_factory()
                .events()
                .insert(calendarId=draft.calendar_id, body=body)
                .execute()
            )
            return _normalize_event(
                response,
                default_calendar_id=draft.calendar_id,
            )
        except (
            CalendarProviderAuthenticationError,
            CalendarProviderRateLimitError,
            CalendarProviderRejectedError,
            TimeoutError,
            ConnectionError,
            OSError,
        ):
            raise
        except Exception as exc:
            _raise_normalized(exc)


def _normalize_event(
    payload: Mapping[str, Any],
    *,
    default_calendar_id: str,
) -> CalendarEvent:
    event_id = str(payload.get("id", "")).strip()
    title = str(payload.get("summary", "")).strip() or "Evento sin título"
    if not event_id:
        raise CalendarProviderRejectedError("google calendar event id is missing")
    start = payload.get("start", {})
    end = payload.get("end", {})
    if not isinstance(start, Mapping) or not isinstance(end, Mapping):
        raise CalendarProviderRejectedError("google calendar event time is invalid")
    time_range = CalendarTimeRange(
        starts_at=_parse_google_time(start),
        ends_at=_parse_google_time(end),
    )
    attendees = payload.get("attendees", ())
    attendee_emails = tuple(
        str(item["email"])
        for item in attendees
        if isinstance(item, Mapping) and item.get("email")
    ) if isinstance(attendees, (list, tuple)) else ()
    metadata = {
        key: str(payload[key])
        for key in ("etag", "htmlLink", "status")
        if payload.get(key) is not None
    }
    return CalendarEvent(
        event_id=event_id,
        title=title,
        time_range=time_range,
        calendar_id=default_calendar_id,
        description=_optional_text(payload.get("description")),
        location=_optional_text(payload.get("location")),
        attendee_emails=attendee_emails,
        provider_metadata=metadata,
    )


def _parse_google_time(value: Mapping[str, Any]) -> datetime:
    date_time = value.get("dateTime")
    if date_time:
        return _parse_datetime(str(date_time))
    date_value = value.get("date")
    if date_value:
        parsed_date = date.fromisoformat(str(date_value))
        return datetime.combine(parsed_date, time.min, tzinfo=timezone.utc)
    raise CalendarProviderRejectedError("google calendar event time is missing")


def _parse_datetime(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise CalendarProviderRejectedError(
            "google calendar datetime must be timezone-aware"
        )
    return parsed


def _to_rfc3339(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("google calendar datetime must be timezone-aware")
    return value.isoformat()


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text if text else None


def _require_calendar_id(calendar_id: str) -> None:
    if not calendar_id.strip():
        raise ValueError("calendar id must not be blank")


def _raise_normalized(exc: Exception) -> None:
    status = _http_status(exc)
    if status == 401:
        raise CalendarProviderAuthenticationError(
            "google calendar authentication failed"
        ) from exc
    if status == 429:
        raise CalendarProviderRateLimitError(
            "google calendar rate limited"
        ) from exc
    if status in {408, 504}:
        raise TimeoutError("google calendar request timed out") from exc
    if status is not None and status >= 500:
        raise ConnectionError("google calendar unavailable") from exc
    if status in {400, 403, 404, 409, 412}:
        raise CalendarProviderRejectedError(
            "google calendar request rejected"
        ) from exc
    raise ConnectionError("google calendar request failed") from exc


def _http_status(exc: Exception) -> int | None:
    response = getattr(exc, "resp", None)
    status = getattr(response, "status", None)
    return status if isinstance(status, int) else None


def _import_symbol(module_name: str, symbol_name: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            "google calendar deployment dependency unavailable"
        ) from exc
    try:
        return getattr(module, symbol_name)
    except AttributeError as exc:
        raise ImportError(
            "google calendar deployment dependency incomplete"
        ) from exc
