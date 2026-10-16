from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class CalendarTimeRange:
    """Timezone-aware interval shared by all calendar providers."""

    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("calendar time range must be timezone-aware")
        if self.ends_at <= self.starts_at:
            raise ValueError("calendar time range end must be after start")


@dataclass(frozen=True)
class CalendarEvent:
    """Provider-neutral calendar event returned to ROBY."""

    event_id: str
    title: str
    time_range: CalendarTimeRange
    calendar_id: str = "primary"
    description: str | None = None
    location: str | None = None
    attendee_emails: tuple[str, ...] = ()
    provider_metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("calendar event id must not be blank")
        if not self.title.strip():
            raise ValueError("calendar event title must not be blank")
        if not self.calendar_id.strip():
            raise ValueError("calendar id must not be blank")
        if any(not email.strip() for email in self.attendee_emails):
            raise ValueError("calendar attendee emails must not be blank")
        if any(not key.strip() for key in self.provider_metadata):
            raise ValueError("calendar provider metadata keys must not be blank")


@dataclass(frozen=True)
class CalendarEventDraft:
    """Validated event proposal; creation remains provider-owned and governed."""

    title: str
    time_range: CalendarTimeRange
    calendar_id: str = "primary"
    description: str | None = None
    location: str | None = None
    attendee_emails: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("calendar event title must not be blank")
        if not self.calendar_id.strip():
            raise ValueError("calendar id must not be blank")
        if any(not email.strip() for email in self.attendee_emails):
            raise ValueError("calendar attendee emails must not be blank")


@dataclass(frozen=True)
class CalendarAvailability:
    """Normalized free/busy answer for one requested interval."""

    requested_range: CalendarTimeRange
    busy_ranges: tuple[CalendarTimeRange, ...] = ()

    @property
    def is_free(self) -> bool:
        return not self.busy_ranges

    def __post_init__(self) -> None:
        for busy_range in self.busy_ranges:
            if (
                busy_range.ends_at <= self.requested_range.starts_at
                or busy_range.starts_at >= self.requested_range.ends_at
            ):
                raise ValueError(
                    "calendar busy ranges must overlap the requested range"
                )


class CalendarProvider(Protocol):
    """Minimal provider-neutral boundary required by M348.2."""

    def list_events(
        self,
        time_range: CalendarTimeRange,
        *,
        calendar_id: str = "primary",
    ) -> tuple[CalendarEvent, ...]: ...

    def check_availability(
        self,
        time_range: CalendarTimeRange,
        *,
        calendar_id: str = "primary",
    ) -> CalendarAvailability: ...

    def create_event(self, draft: CalendarEventDraft) -> CalendarEvent: ...
