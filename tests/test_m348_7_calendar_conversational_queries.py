from datetime import datetime, timedelta, timezone

from app.calendar_conversation_runtime import CalendarConversationInterceptionPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
    CalendarTimeRange,
)
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
    CalendarRuntimeConfig,
)


class RecordingProvider:
    def __init__(self, *, events=(), busy_ranges=()):
        self.events = tuple(events)
        self.busy_ranges = tuple(busy_ranges)
        self.last_range = None

    def list_events(self, time_range, *, calendar_id="primary"):
        del calendar_id
        self.last_range = time_range
        return self.events

    def check_availability(self, time_range, *, calendar_id="primary"):
        del calendar_id
        self.last_range = time_range
        return CalendarAvailability(time_range, self.busy_ranges)


class OAuth:
    class Config:
        allow_interactive_authorization = False

    config = Config()

    def load(self, account):
        del account

        class Credentials:
            valid = True
            expired = False

        class Material:
            scopes = (
                "https://www.googleapis.com/auth/calendar.events",
                "https://www.googleapis.com/auth/calendar.events.freebusy",
            )
            revoked = False
            expires_at = None
            deployment_credentials = Credentials()

        return Material()


def _port(provider):
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True), oauth=OAuth(), provider=provider
    )
    return CalendarConversationInterceptionPort(runtime)


def _request(text):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="s", text=text
    )


def test_tomorrow_agenda_uses_complete_local_day():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = _port(provider).intercept(
        _request("qué tengo mañana en la agenda"), now=now
    )
    assert provider.last_range.starts_at == datetime(2026, 7, 31, tzinfo=timezone.utc)
    assert provider.last_range.ends_at == datetime(2026, 8, 1, tzinfo=timezone.utc)
    assert result.response_text == "No tenés eventos mañana."


def test_this_week_starts_now_and_ends_next_monday():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    _port(provider).intercept(_request("mostrame la agenda de esta semana"), now=now)
    assert provider.last_range.starts_at == now
    assert provider.last_range.ends_at == datetime(2026, 8, 3, tzinfo=timezone.utc)


def test_next_week_uses_monday_to_monday():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    _port(provider).intercept(_request("eventos de la próxima semana"), now=now)
    assert provider.last_range.starts_at == datetime(2026, 8, 3, tzinfo=timezone.utc)
    assert provider.last_range.ends_at == datetime(2026, 8, 10, tzinfo=timezone.utc)


def test_weekday_resolves_next_occurrence():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    _port(provider).intercept(_request("qué eventos tengo el lunes"), now=now)
    assert provider.last_range.starts_at == datetime(2026, 8, 3, tzinfo=timezone.utc)


def test_daypart_limits_availability_interval():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = _port(provider).intercept(
        _request("estoy libre mañana por la tarde"), now=now
    )
    assert provider.last_range.starts_at == datetime(
        2026, 7, 31, 12, tzinfo=timezone.utc
    )
    assert provider.last_range.ends_at == datetime(2026, 7, 31, 19, tzinfo=timezone.utc)
    assert result.response_text == "Estás libre mañana, por la tarde."


def test_explicit_hour_range_is_supported():
    provider = RecordingProvider()
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    _port(provider).intercept(
        _request("tengo disponibilidad mañana de 15 a 17"), now=now
    )
    assert provider.last_range.starts_at == datetime(
        2026, 7, 31, 15, tzinfo=timezone.utc
    )
    assert provider.last_range.ends_at == datetime(2026, 7, 31, 17, tzinfo=timezone.utc)


def test_busy_availability_lists_concrete_ranges():
    busy = CalendarTimeRange(
        datetime(2026, 7, 31, 15, tzinfo=timezone.utc),
        datetime(2026, 7, 31, 16, 30, tzinfo=timezone.utc),
    )
    provider = RecordingProvider(busy_ranges=(busy,))
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = _port(provider).intercept(
        _request("estoy ocupado mañana de 15 a 17"), now=now
    )
    assert "15:00–16:30" in result.response_text
    assert result.rationale == "calendar_availability_read_completed"


def test_event_response_is_sorted_and_includes_location():
    interval = CalendarTimeRange(
        datetime(2026, 7, 31, tzinfo=timezone.utc),
        datetime(2026, 8, 1, tzinfo=timezone.utc),
    )
    events = (
        CalendarEvent("2", "Banco", CalendarTimeRange(
            interval.starts_at + timedelta(hours=14),
            interval.starts_at + timedelta(hours=15),
        )),
        CalendarEvent("1", "Médico", CalendarTimeRange(
            interval.starts_at + timedelta(hours=9),
            interval.starts_at + timedelta(hours=10),
        ), location="Consultorio"),
    )
    provider = RecordingProvider(events=events)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = _port(provider).intercept(_request("agenda de mañana"), now=now)
    assert result.response_text.index("Médico") < result.response_text.index("Banco")
    assert "09:00–10:00: Médico — Consultorio" in result.response_text


def test_explicit_date_without_year_rolls_forward():
    provider = RecordingProvider()
    now = datetime(2026, 12, 30, 12, tzinfo=timezone.utc)
    _port(provider).intercept(_request("agenda del 02/01"), now=now)
    assert provider.last_range.starts_at == datetime(2027, 1, 2, tzinfo=timezone.utc)


def test_write_prepares_draft_without_creating_event():
    provider = RecordingProvider()
    provider.created = []
    provider.create_event = provider.created.append
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = _port(provider).intercept(
        _request("agendar una reunión mañana a las 15"), now=now
    )
    assert provider.last_range is not None
    assert provider.created == []
    assert result.rationale == "calendar_event_draft_awaiting_confirmation"
