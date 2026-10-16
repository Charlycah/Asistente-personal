from datetime import datetime, timedelta, timezone

from app.calendar_conversation_runtime import CalendarConversationInterceptionPort
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import CapabilityKind, CapabilityRisk, PermissionScope
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from infrastructure.calendar.calendar_contract import (
    CalendarAvailability,
    CalendarEvent,
)
from infrastructure.calendar.calendar_runtime_composition import (
    CalendarRuntimeComposition,
    CalendarRuntimeConfig,
)
from infrastructure.calendar.calendar_tool_gateway import (
    CalendarToolGatewayRegistration,
)


class Provider:
    def list_events(self, time_range, *, calendar_id="primary"):
        return (CalendarEvent("1", "Médico", time_range, calendar_id=calendar_id),)

    def check_availability(self, time_range, *, calendar_id="primary"):
        return CalendarAvailability(time_range)


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


def ready_runtime():
    return CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True), oauth=OAuth(), provider=Provider()
    )


def test_gateway_registers_reads_and_blocks_write():
    gateway = ToolGatewayManager()
    CalendarToolGatewayRegistration(ready_runtime()).register_with_gateway(gateway)
    assert gateway.capabilities[CalendarToolGatewayRegistration.LIST].enabled
    assert gateway.capabilities[CalendarToolGatewayRegistration.AVAILABILITY].enabled
    create = gateway.capabilities[CalendarToolGatewayRegistration.CREATE]
    assert create.enabled
    assert create.requires_confirmation


def test_gateway_routes_event_listing():
    gateway = ToolGatewayManager()
    CalendarToolGatewayRegistration(ready_runtime()).register_with_gateway(gateway)
    start = datetime(2026, 7, 31, 9, tzinfo=timezone.utc)
    result = gateway.execute(
        ToolRequest(
            CalendarToolGatewayRegistration.LIST,
            {
                "starts_at": start.isoformat(),
                "ends_at": (start + timedelta(hours=2)).isoformat(),
            },
        )
    )
    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["events"][0]["title"] == "Médico"


def test_gateway_blocks_creation_even_when_runtime_is_ready():
    gateway = ToolGatewayManager()
    CalendarToolGatewayRegistration(ready_runtime()).register_with_gateway(gateway)
    result = gateway.execute(ToolRequest(CalendarToolGatewayRegistration.CREATE, {}))
    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "handler_error:PermissionError"


def test_disabled_runtime_registers_read_capabilities_as_disabled():
    gateway = ToolGatewayManager()
    registration = CalendarToolGatewayRegistration(CalendarRuntimeComposition())
    registration.register_with_gateway(gateway)
    assert not gateway.capabilities[CalendarToolGatewayRegistration.LIST].enabled


def test_planner_registry_exposes_calendar_as_calendar_kind():
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="calendar.read", description="Consulta agenda", interceptor=object(),
        kind=CapabilityKind.CALENDAR, risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.READ,
    )
    descriptor = registry.manager.get("calendar.read")
    assert descriptor is not None
    assert descriptor.normalized_kind is CapabilityKind.CALENDAR
    assert descriptor.normalized_permission_scope is PermissionScope.READ


def test_conversation_port_lists_events_and_prepares_creation_draft():
    port = CalendarConversationInterceptionPort(ready_runtime())
    now = datetime(2026, 7, 31, 9, tzinfo=timezone.utc)
    read = port.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos", session_id="s", text="qué tengo en la agenda"
        ),
        now=now,
    )
    assert read is not None and "Médico" in read.response_text
    write = port.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos", session_id="s", text="agendar una reunión"
        ),
        now=now,
    )
    assert write is not None
    assert write.rationale == "calendar_event_draft_awaiting_confirmation"


def test_calendar_read_is_safe_for_implicit_planner_use():
    registry = OfficialRuntimeCapabilityRegistry()
    port = CalendarConversationInterceptionPort(ready_runtime())
    registry.register(
        name="calendar.read", description="Consulta agenda", interceptor=port,
        kind=CapabilityKind.CALENDAR, risk=CapabilityRisk.LOW,
        permission_scope=PermissionScope.READ, requires_confirmation=False,
        semantic_triggers=("agenda",),
    )
    descriptor = registry.registration_for("calendar.read").descriptor
    assert descriptor.enabled
    assert not descriptor.requires_confirmation
    assert descriptor.normalized_risk is CapabilityRisk.LOW
