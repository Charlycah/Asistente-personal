from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from infrastructure.calendar.calendar_contract import (
    CalendarEventDraft,
    CalendarTimeRange,
)
from infrastructure.calendar.google_calendar_adapter import (
    CalendarProviderAuthenticationError,
    CalendarProviderRateLimitError,
    CalendarProviderRejectedError,
    GoogleCalendarAdapter,
    GoogleCalendarApiServiceFactory,
)


class Request:
    def __init__(self, response=None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error

    def execute(self):
        if self.error is not None:
            raise self.error
        return self.response


class EventsResource:
    def __init__(self, list_response=(), insert_response=None) -> None:
        self.list_response = list_response
        self.insert_response = insert_response
        self.list_kwargs = None
        self.insert_kwargs = None

    def list(self, **kwargs):
        self.list_kwargs = kwargs
        return Request({"items": self.list_response})

    def insert(self, **kwargs):
        self.insert_kwargs = kwargs
        return Request(self.insert_response)


class FreeBusyResource:
    def __init__(self, response) -> None:
        self.response = response
        self.body = None

    def query(self, *, body):
        self.body = body
        return Request(self.response)


class Service:
    def __init__(self, events, freebusy) -> None:
        self._events = events
        self._freebusy = freebusy

    def events(self):
        return self._events

    def freebusy(self):
        return self._freebusy


def _range() -> CalendarTimeRange:
    starts_at = datetime(2026, 8, 3, 10, tzinfo=timezone.utc)
    return CalendarTimeRange(starts_at, starts_at + timedelta(hours=1))


def _event_payload(event_id: str = "event-1") -> dict[str, object]:
    return {
        "id": event_id,
        "summary": "Control médico",
        "start": {"dateTime": "2026-08-03T10:00:00+00:00"},
        "end": {"dateTime": "2026-08-03T11:00:00+00:00"},
        "attendees": [{"email": "cristina@example.invalid"}],
        "etag": "opaque",
    }


def test_list_events_translates_google_payload_to_neutral_event() -> None:
    events = EventsResource(list_response=[_event_payload()])
    adapter = GoogleCalendarAdapter(
        lambda: Service(events, FreeBusyResource({"calendars": {}}))
    )

    result = adapter.list_events(_range())

    assert result[0].event_id == "event-1"
    assert result[0].title == "Control médico"
    assert result[0].attendee_emails == ("cristina@example.invalid",)
    assert result[0].provider_metadata == {"etag": "opaque"}
    assert events.list_kwargs["calendarId"] == "primary"
    assert events.list_kwargs["singleEvents"] is True


def test_list_events_skips_cancelled_entries() -> None:
    cancelled = _event_payload("cancelled-1")
    cancelled["status"] = "cancelled"
    adapter = GoogleCalendarAdapter(
        lambda: Service(
            EventsResource(list_response=[cancelled]),
            FreeBusyResource({"calendars": {}}),
        )
    )

    assert adapter.list_events(_range()) == ()


def test_check_availability_translates_busy_ranges() -> None:
    freebusy = FreeBusyResource(
        {
            "calendars": {
                "primary": {
                    "busy": [
                        {
                            "start": "2026-08-03T10:15:00Z",
                            "end": "2026-08-03T10:45:00Z",
                        }
                    ]
                }
            }
        }
    )
    adapter = GoogleCalendarAdapter(
        lambda: Service(EventsResource(), freebusy)
    )

    availability = adapter.check_availability(_range())

    assert availability.is_free is False
    assert len(availability.busy_ranges) == 1
    assert freebusy.body["items"] == [{"id": "primary"}]


def test_create_event_builds_google_body_and_normalizes_response() -> None:
    events = EventsResource(insert_response=_event_payload("created-1"))
    adapter = GoogleCalendarAdapter(
        lambda: Service(events, FreeBusyResource({"calendars": {}}))
    )
    draft = CalendarEventDraft(
        title="Control médico",
        time_range=_range(),
        description="Consulta anual",
        location="Consultorio",
        attendee_emails=("cristina@example.invalid",),
    )

    created = adapter.create_event(draft)

    assert created.event_id == "created-1"
    assert events.insert_kwargs["calendarId"] == "primary"
    assert events.insert_kwargs["body"]["summary"] == "Control médico"
    assert events.insert_kwargs["body"]["attendees"] == [
        {"email": "cristina@example.invalid"}
    ]


def test_all_day_google_event_is_normalized_to_utc_bounds() -> None:
    payload = {
        "id": "all-day-1",
        "summary": "Aniversario",
        "start": {"date": "2026-08-03"},
        "end": {"date": "2026-08-04"},
    }
    adapter = GoogleCalendarAdapter(
        lambda: Service(
            EventsResource(list_response=[payload]),
            FreeBusyResource({"calendars": {}}),
        )
    )

    event = adapter.list_events(_range())[0]

    assert event.time_range.starts_at.tzinfo is timezone.utc
    assert event.time_range.ends_at - event.time_range.starts_at == timedelta(days=1)


def test_missing_event_id_is_rejected() -> None:
    payload = _event_payload()
    payload.pop("id")
    adapter = GoogleCalendarAdapter(
        lambda: Service(
            EventsResource(list_response=[payload]),
            FreeBusyResource({"calendars": {}}),
        )
    )

    with pytest.raises(CalendarProviderRejectedError, match="id is missing"):
        adapter.list_events(_range())


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, CalendarProviderAuthenticationError),
        (429, CalendarProviderRateLimitError),
        (403, CalendarProviderRejectedError),
        (503, ConnectionError),
    ],
)
def test_provider_errors_are_normalized(status, error_type) -> None:
    error = RuntimeError("provider failure")
    error.resp = SimpleNamespace(status=status)

    class FailingEvents:
        def list(self, **kwargs):
            return Request(error=error)

    adapter = GoogleCalendarAdapter(
        lambda: Service(FailingEvents(), FreeBusyResource({"calendars": {}}))
    )

    with pytest.raises(error_type):
        adapter.list_events(_range())


def test_service_factory_rejects_missing_credentials() -> None:
    factory = GoogleCalendarApiServiceFactory(lambda: None)

    with pytest.raises(CalendarProviderAuthenticationError):
        factory()
