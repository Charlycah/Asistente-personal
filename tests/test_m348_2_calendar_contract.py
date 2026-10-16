from datetime import datetime, timedelta, timezone

import pytest

from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
    CalendarEventDraft,
    CalendarProvider,
    CalendarTimeRange,
)


def _range(*, hour: int = 10, duration_hours: int = 1) -> CalendarTimeRange:
    starts_at = datetime(2026, 8, 3, hour, tzinfo=timezone.utc)
    return CalendarTimeRange(
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=duration_hours),
    )


def test_calendar_time_range_requires_timezone_aware_values() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        CalendarTimeRange(
            starts_at=datetime(2026, 8, 3, 10),
            ends_at=datetime(2026, 8, 3, 11),
        )


def test_calendar_time_range_requires_ordered_bounds() -> None:
    starts_at = datetime(2026, 8, 3, 10, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="end must be after start"):
        CalendarTimeRange(starts_at=starts_at, ends_at=starts_at)


def test_calendar_event_normalizes_provider_independent_data() -> None:
    event = CalendarEvent(
        event_id="event-1",
        title="Control médico",
        time_range=_range(),
        attendee_emails=("cristina@example.invalid",),
        provider_metadata={"etag": "opaque-provider-value"},
    )

    assert event.calendar_id == "primary"
    assert event.title == "Control médico"
    assert event.provider_metadata["etag"] == "opaque-provider-value"


def test_calendar_event_draft_rejects_blank_title() -> None:
    with pytest.raises(ValueError, match="title"):
        CalendarEventDraft(title=" ", time_range=_range())


def test_calendar_availability_reports_free_interval() -> None:
    availability = CalendarAvailability(requested_range=_range())

    assert availability.is_free is True


def test_calendar_availability_rejects_unrelated_busy_ranges() -> None:
    requested = _range(hour=10)
    unrelated = _range(hour=15)

    with pytest.raises(ValueError, match="must overlap"):
        CalendarAvailability(
            requested_range=requested,
            busy_ranges=(unrelated,),
        )


def test_calendar_provider_protocol_accepts_structural_implementation() -> None:
    class StubCalendarProvider:
        def list_events(
            self,
            time_range: CalendarTimeRange,
            *,
            calendar_id: str = "primary",
        ) -> tuple[CalendarEvent, ...]:
            return ()

        def check_availability(
            self,
            time_range: CalendarTimeRange,
            *,
            calendar_id: str = "primary",
        ) -> CalendarAvailability:
            return CalendarAvailability(requested_range=time_range)

        def create_event(self, draft: CalendarEventDraft) -> CalendarEvent:
            return CalendarEvent(
                event_id="created-1",
                title=draft.title,
                time_range=draft.time_range,
                calendar_id=draft.calendar_id,
            )

    provider: CalendarProvider = StubCalendarProvider()
    assert provider.list_events(_range()) == ()
    assert provider.check_availability(_range()).is_free is True
    assert provider.create_event(
        CalendarEventDraft(title="Reunión", time_range=_range())
    ).event_id == "created-1"
