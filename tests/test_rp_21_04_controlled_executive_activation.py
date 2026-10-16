from datetime import datetime, timezone

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import CapabilityKind
from core.cognitive_planning import ExecutiveActivationDecision
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def request(text: str, session_id: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


class FixedResponse:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls = 0

    def intercept(self, incoming, *, now):
        del incoming, now
        self.calls += 1
        return GovernedOperationalInterception(
            response_text=self.response_text,
            rationale="fixed_completed",
        )


def register_kind(registry, *, name, interceptor, kind):
    registry.register(
        name=name,
        description=name,
        interceptor=interceptor,
        semantic_triggers=("estado",),
    )
    registration = registry.registration_for(name)
    assert registration is not None
    object.__setattr__(registration.descriptor, "kind", kind)


def test_controlled_activation_skips_incompatible_semantic_candidate():
    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(executive_activation_enabled=True)
    registry.set_cognitive_planner_shadow(shadow)
    calendar = FixedResponse("calendario")
    weather = FixedResponse("clima")
    register_kind(
        registry,
        name="calendar.provider",
        interceptor=calendar,
        kind=CapabilityKind.CALENDAR,
    )
    register_kind(
        registry,
        name="weather.provider",
        interceptor=weather,
        kind=CapabilityKind.WEATHER,
    )

    result = registry.intercept(
        request("¿Cuál es el estado del clima hoy?", "controlled"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "clima"
    assert calendar.calls == 0
    assert weather.calls == 1
    assert shadow.snapshot.executive_skips == 1
    assert shadow.snapshot.executive_activations == 1
    assert shadow.snapshot.last_executive_activation is not None
    assert (
        shadow.snapshot.last_executive_activation.decision
        is ExecutiveActivationDecision.EXECUTE
    )


def test_activation_disabled_preserves_legacy_first_match():
    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(executive_activation_enabled=False)
    registry.set_cognitive_planner_shadow(shadow)
    calendar = FixedResponse("calendario")
    weather = FixedResponse("clima")
    register_kind(
        registry,
        name="calendar.provider",
        interceptor=calendar,
        kind=CapabilityKind.CALENDAR,
    )
    register_kind(
        registry,
        name="weather.provider",
        interceptor=weather,
        kind=CapabilityKind.WEATHER,
    )

    result = registry.intercept(
        request("¿Cuál es el estado del clima hoy?", "legacy"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "calendario"
    assert calendar.calls == 1
    assert weather.calls == 0
    assert shadow.snapshot.executive_activation_evaluations == 0


def test_unconfident_plan_falls_back_to_legacy_execution():
    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(executive_activation_enabled=True)
    registry.set_cognitive_planner_shadow(shadow)
    capability = FixedResponse("respuesta histórica")
    register_kind(
        registry,
        name="calendar.provider",
        interceptor=capability,
        kind=CapabilityKind.CALENDAR,
    )

    result = registry.intercept(
        request("Hola, estado general", "fallback"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta histórica"
    assert capability.calls == 1
    assert shadow.snapshot.executive_fallbacks == 1
    assert shadow.snapshot.last_executive_activation is not None
    assert (
        shadow.snapshot.last_executive_activation.decision
        is ExecutiveActivationDecision.FALLBACK
    )


def test_activation_policy_failure_is_fail_open():
    class BrokenPolicy:
        def assess_semantic_candidate(self, plan, descriptor):
            del plan, descriptor
            raise RuntimeError("unavailable")

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(
        executive_activation_enabled=True,
        executive_activation_policy=BrokenPolicy(),
    )
    registry.set_cognitive_planner_shadow(shadow)
    capability = FixedResponse("respuesta intacta")
    register_kind(
        registry,
        name="weather.provider",
        interceptor=capability,
        kind=CapabilityKind.WEATHER,
    )

    result = registry.intercept(
        request("¿Cuál es el estado del clima hoy?", "failure"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta intacta"
    assert capability.calls == 1
    assert shadow.snapshot.executive_activation_failures == 1
