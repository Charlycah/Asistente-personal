from datetime import datetime, timezone

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.cognitive_planning import (
    CognitiveIntent,
    CognitivePlanner,
    ContextRequirement,
    EvidenceLevel,
    FreshnessRequirement,
    PlannedResponseDecision,
    ToolRequirement,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def request(text: str, session_id: str = "rp-21-shadow"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def test_planner_requires_current_corroborated_evidence_for_current_affairs():
    plan = CognitivePlanner().plan("¿Cuáles son las últimas noticias de OpenAI?")

    assert plan.intent is CognitiveIntent.CURRENT_INFORMATION
    assert plan.needs_current_information is True
    assert plan.freshness is FreshnessRequirement.CURRENT
    assert plan.minimum_evidence is EvidenceLevel.CORROBORATED
    assert plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED
    assert ToolRequirement.CURRENT_AFFAIRS in plan.required_tools


def test_planner_detects_contextual_memory_dependency():
    plan = CognitivePlanner().plan("Y eso que habíamos hablado antes, ¿cómo sigue?")

    assert ContextRequirement.CONVERSATION in plan.required_context
    assert ContextRequirement.PERSONAL_MEMORY in plan.required_context
    assert ToolRequirement.MEMORY in plan.required_tools


def test_weather_uses_provider_evidence_without_current_affairs_router():
    plan = CognitivePlanner().plan("¿Cómo está el clima hoy?")

    assert plan.intent is CognitiveIntent.CURRENT_INFORMATION
    assert plan.required_tools == (ToolRequirement.WEATHER,)
    assert plan.minimum_evidence is EvidenceLevel.SINGLE_SOURCE
    assert plan.response_decision is PlannedResponseDecision.ABSTAIN_IF_UNVERIFIED


def test_shadow_records_plan_by_session_without_returning_an_interception():
    shadow = CognitivePlannerShadowRuntime()
    turn = request("¿Qué pasó hoy con la NASA?", session_id="nasa-session")

    result = shadow.observe(turn, now=datetime.now(timezone.utc))

    assert result is shadow.plan_for_session("nasa-session")
    assert shadow.snapshot.evaluations == 1
    assert shadow.snapshot.failures == 0
    assert shadow.snapshot.last_session_id == "nasa-session"


def test_registry_response_is_unchanged_when_shadow_planner_is_enabled():
    class FixedResponse:
        def intercept(self, incoming, *, now):
            del incoming, now
            return GovernedOperationalInterception(
                response_text="respuesta existente",
                rationale="existing_response_completed",
            )

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime()
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="test.existing",
        description="Respuesta de compatibilidad",
        interceptor=FixedResponse(),
    )

    result = registry.intercept(
        request("Hola Roby"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta existente"
    assert result.rationale == "existing_response_completed"
    assert shadow.snapshot.last_plan is not None
    assert shadow.snapshot.last_plan.intent is CognitiveIntent.CONVERSATION


def test_shadow_failure_does_not_block_existing_runtime_response():
    class BrokenPlanner:
        def plan(self, text):
            del text
            raise RuntimeError("planner unavailable")

    class FixedResponse:
        def intercept(self, incoming, *, now):
            del incoming, now
            return GovernedOperationalInterception(
                response_text="fallback intacto",
                rationale="fallback_completed",
            )

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(BrokenPlanner())
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="test.fallback",
        description="Compatibilidad ante fallo sombra",
        interceptor=FixedResponse(),
    )

    result = registry.intercept(
        request("consulta cualquiera"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "fallback intacto"
    assert shadow.snapshot.failures == 1
