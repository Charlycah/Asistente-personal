from datetime import datetime, timezone

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.cognitive_planning import ShadowAssessmentStatus
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
    ResponseOriginMetadata,
)


def request(text: str, session_id: str = "rp-21-01"):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
    )


def test_current_plan_is_satisfied_by_recent_corroborated_evidence():
    shadow = CognitivePlannerShadowRuntime()
    turn = request("¿Cuáles son las últimas noticias de OpenAI?")
    shadow.observe(turn, now=datetime.now(timezone.utc))

    assessment = shadow.observe_result(
        turn,
        GovernedOperationalInterception(
            response_text="resultado web",
            rationale="current_affairs_completed",
            origin=ResponseOriginMetadata.web_recent(evidence_count=3),
        ),
        now=datetime.now(timezone.utc),
    )

    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.SATISFIED
    assert assessment.freshness_satisfied is True
    assert assessment.evidence_satisfied is True
    assert assessment.observed_evidence_count == 3


def test_current_plan_detects_answer_without_fresh_evidence():
    shadow = CognitivePlannerShadowRuntime()
    turn = request("¿Qué pasó hoy con la NASA?")
    shadow.observe(turn, now=datetime.now(timezone.utc))

    assessment = shadow.observe_result(
        turn,
        GovernedOperationalInterception(
            response_text="respuesta general",
            rationale="general_answer_completed",
            origin=ResponseOriginMetadata.general_knowledge(),
        ),
        now=datetime.now(timezone.utc),
    )

    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.UNSATISFIED
    assert assessment.freshness_satisfied is False
    assert assessment.evidence_satisfied is False
    assert assessment.abstention_consistent is False
    assert "planned_freshness_not_observed" in assessment.rationale_codes


def test_current_plan_accepts_abstention_when_evidence_is_unavailable():
    shadow = CognitivePlannerShadowRuntime()
    turn = request("¿Qué noticias hay hoy sobre OpenAI?")
    shadow.observe(turn, now=datetime.now(timezone.utc))

    assessment = shadow.observe_result(
        turn,
        GovernedOperationalInterception(
            response_text="No puedo verificarlo.",
            rationale="current_affairs_abstained",
            origin=ResponseOriginMetadata.abstained_web(),
        ),
        now=datetime.now(timezone.utc),
    )

    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.SATISFIED
    assert assessment.observed_abstention is True
    assert assessment.abstention_consistent is True


def test_conflicting_sources_are_recorded_without_changing_response():
    shadow = CognitivePlannerShadowRuntime()
    turn = request("¿Qué pasó hoy con la nueva ley?")
    shadow.observe(turn, now=datetime.now(timezone.utc))
    result = GovernedOperationalInterception(
        response_text="Encontré versiones contradictorias.",
        rationale="current_affairs_conflict",
        origin=ResponseOriginMetadata.web_recent_conflicted(evidence_count=2),
    )

    assessment = shadow.observe_result(
        turn,
        result,
        now=datetime.now(timezone.utc),
    )

    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.SATISFIED
    assert assessment.observed_conflicting_sources is True
    assert "conflicting_sources_observed" in assessment.rationale_codes
    assert result.response_text == "Encontré versiones contradictorias."


def test_registry_records_outcome_assessment_but_preserves_interception():
    class CurrentResult:
        def intercept(self, incoming, *, now):
            del incoming, now
            return GovernedOperationalInterception(
                response_text="respuesta web intacta",
                rationale="current_affairs_completed",
                origin=ResponseOriginMetadata.web_recent(evidence_count=2),
            )

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime()
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="test.current",
        description="Resultado actual de prueba",
        interceptor=CurrentResult(),
    )

    result = registry.intercept(
        request("¿Qué pasó hoy con OpenAI?", session_id="registry-current"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta web intacta"
    assessment = shadow.assessment_for_session("registry-current")
    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.SATISFIED


def test_outcome_assessor_failure_does_not_change_existing_response():
    class BrokenAssessor:
        def assess(self, plan, origin):
            del plan, origin
            raise RuntimeError("assessment unavailable")

    class CurrentResult:
        def intercept(self, incoming, *, now):
            del incoming, now
            return GovernedOperationalInterception(
                response_text="respuesta conservada",
                rationale="current_affairs_completed",
                origin=ResponseOriginMetadata.web_recent(evidence_count=2),
            )

    registry = OfficialRuntimeCapabilityRegistry()
    shadow = CognitivePlannerShadowRuntime(assessor=BrokenAssessor())
    registry.set_cognitive_planner_shadow(shadow)
    registry.register(
        name="test.current.failure",
        description="Fallo sombra contenido",
        interceptor=CurrentResult(),
    )

    result = registry.intercept(
        request("¿Qué pasó hoy con OpenAI?", session_id="failure-current"),
        now=datetime.now(timezone.utc),
    )

    assert result is not None
    assert result.response_text == "respuesta conservada"
    assert shadow.snapshot.outcome_failures == 1
