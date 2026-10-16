from datetime import datetime, timezone

from app.calendar_conversation_runtime import CalendarConversationInterceptionPort
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
)
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
    CalendarRuntimeConfig,
)


class Provider:
    def __init__(self, *, busy=False):
        self.busy = busy
        self.created = []
        self.checked = 0

    def list_events(self, time_range, *, calendar_id="primary"):
        del time_range, calendar_id
        return ()

    def check_availability(self, time_range, *, calendar_id="primary"):
        del calendar_id
        self.checked += 1
        busy_ranges = (time_range,) if self.busy else ()
        return CalendarAvailability(time_range, busy_ranges)

    def create_event(self, draft):
        self.created.append(draft)
        return CalendarEvent("evt-1", draft.title, draft.time_range)


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


def _request(text, *, session="s"):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id=session, text=text
    )


def test_creation_prepares_draft_without_mutation():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = port.intercept(_request("agendar Médico mañana a las 15"), now=now)
    assert result.rationale == "calendar_event_draft_awaiting_confirmation"
    assert "todavía no modifiqué Calendar" in result.response_text
    assert provider.created == []
    assert provider.checked == 1


def test_explicit_confirmation_creates_once():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    port.intercept(_request("agendar Médico mañana a las 15"), now=now)
    result = port.intercept(_request("sí, crear"), now=now)
    assert result.rationale == "calendar_event_created_after_explicit_confirmation"
    assert len(provider.created) == 1
    assert provider.created[0].title == "Médico"
    again = port.intercept(_request("sí, crear"), now=now)
    assert again.rationale == "calendar_event_confirmation_without_draft"
    assert len(provider.created) == 1


def test_confirmation_is_scoped_by_session():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    port.intercept(_request("agendar Médico mañana a las 15", session="a"), now=now)
    result = port.intercept(_request("sí, crear", session="b"), now=now)
    assert result.rationale == "calendar_event_confirmation_without_draft"
    assert provider.created == []


def test_cancellation_discards_pending_draft():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    port.intercept(_request("agendar Médico mañana a las 15"), now=now)
    cancelled = port.intercept(_request("cancelar"), now=now)
    assert cancelled.rationale == "calendar_event_draft_cancelled"
    confirmation = port.intercept(_request("sí, crear"), now=now)
    assert confirmation.rationale == "calendar_event_confirmation_without_draft"
    assert provider.created == []


def test_conflict_blocks_draft_before_confirmation():
    provider = Provider(busy=True)
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = port.intercept(_request("agendar Médico mañana a las 15"), now=now)
    assert result.rationale == "calendar_event_draft_conflict"
    assert provider.created == []


def test_conflict_is_revalidated_at_confirmation():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    port.intercept(_request("agendar Médico mañana a las 15"), now=now)
    provider.busy = True
    result = port.intercept(_request("sí, crear"), now=now)
    assert result.rationale == "calendar_event_creation_conflict_revalidated"
    assert provider.created == []


def test_missing_title_does_not_create_pending_draft():
    provider = Provider()
    port = _port(provider)
    now = datetime(2026, 7, 30, 17, 30, tzinfo=timezone.utc)
    result = port.intercept(_request("crear evento mañana a las 15"), now=now)
    assert result.rationale == "calendar_event_draft_missing_title"
    assert provider.checked == 0
    assert provider.created == []
