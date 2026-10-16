from datetime import datetime, timezone

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import CapabilityKind
from core.cognitive_planning import ToolRequirement
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def request(text: str, session_id: str = "rp-21-02"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


class FixedResponse:
    def intercept(self, incoming, *, now):
        del incoming, now
        return GovernedOperationalInterception(
            response_text="respuesta intacta",
            rationale="fixed_completed",
        )


def test_weather_selection_matches_planned_abstract_tool():
    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime()
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="weather.provider",
        description="Obtiene clima actual",
        interceptor=FixedResponse(),
        tags=("clima",),
        semantic_triggers=("clima",),
    )
    registration = registry.registration_for("weather.provider")
    assert registration is not None
    object.__setattr__(registration.descriptor, "kind", CapabilityKind.WEATHER)

    result = registry.intercept(
        request("¿Cómo está el clima hoy?", "weather-session"),
        now=datetime.now(timezone.utc),
    )

    assessment = shadow.capability_assessment_for_session("weather-session")
    assert result is not None
    assert result.response_text == "respuesta intacta"
    assert assessment is not None
    assert assessment.compatible is True
    assert assessment.matched_requirement is ToolRequirement.WEATHER
    assert assessment.governed is True
    assert assessment.provider_agnostic is True


def test_unplanned_capability_is_observed_but_not_blocked():
    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime()
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="calendar.provider",
        description="Consulta calendario",
        interceptor=FixedResponse(),
        semantic_triggers=("hola",),
    )
    registration = registry.registration_for("calendar.provider")
    assert registration is not None
    object.__setattr__(registration.descriptor, "kind", CapabilityKind.CALENDAR)

    result = registry.intercept(
        request("Hola Roby", "mismatch-session"),
        now=datetime.now(timezone.utc),
    )

    assessment = shadow.capability_assessment_for_session("mismatch-session")
    assert result is not None
    assert result.response_text == "respuesta intacta"
    assert assessment is not None
    assert assessment.compatible is False
    assert "planned_tool_requirement_not_matched" in assessment.rationale_codes


def test_capability_assessor_failure_is_fail_open():
    class BrokenAssessor:
        def assess(self, plan, descriptor, *, origin):
            del plan, descriptor, origin
            raise RuntimeError("unavailable")

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(capability_assessor=BrokenAssessor())
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="test.capability",
        description="Capacidad de prueba",
        interceptor=FixedResponse(),
        semantic_triggers=("prueba",),
    )

    result = registry.intercept(
        request("prueba", "failure-session"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta intacta"
    assert shadow.snapshot.capability_failures == 1
