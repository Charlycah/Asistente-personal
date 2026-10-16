from datetime import datetime, timezone

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


class _Capability:
    def __init__(self) -> None:
        self.calls = 0

    def intercept(self, request, *, now):
        self.calls += 1
        return GovernedOperationalInterception(
            response_text=request.text,
            rationale="test_capability_completed",
        )


def _request(text="hola"):
    return GovernedConversationPipelineRequest(
        owner="Carlos", session_id="test", text=text
    )


def test_registry_execution_crosses_official_gateway_once():
    capability = _Capability()
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="test.capability",
        description="test",
        interceptor=capability,
    )
    registration = registry.registration_for("test.capability")

    result = registry.execute_registration(
        registration,
        _request(),
        now=datetime.now(timezone.utc),
        origin="test",
    )

    assert result.response_text == "hola"
    assert capability.calls == 1
    assert registry.gateway.snapshot.executions == 1
    assert registry.gateway.snapshot.last_capability == "test.capability"
    assert registry.gateway.snapshot.last_origin == "test"


def test_registry_normal_interception_uses_same_gateway():
    capability = _Capability()
    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(
        name="test.capability",
        description="test",
        interceptor=capability,
    )

    result = registry.intercept(_request(), now=datetime.now(timezone.utc))

    assert result.response_text == "hola"
    assert registry.gateway.snapshot.executions == 1
    assert registry.gateway.snapshot.last_origin == "registry"


def test_gateway_records_empty_capability_result():
    class _Empty:
        def intercept(self, request, *, now):
            return None

    registry = OfficialRuntimeCapabilityRegistry()
    registry.register(name="empty", description="empty", interceptor=_Empty())
    registration = registry.registration_for("empty")

    assert (
        registry.execute_registration(
            registration,
            _request(),
            now=datetime.now(timezone.utc),
            origin="test",
        )
        is None
    )
    assert registry.gateway.snapshot.last_rationale is None
