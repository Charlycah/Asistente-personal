from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from app.context_continuity_runtime import OfficialContextContinuityRuntimeGateway
from core.cognitive_planning import ShadowAssessmentStatus
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest


def request(text: str, *, session_id: str, context=()):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id=session_id,
        text=text,
        recent_context=tuple(context),
    )


def test_follow_up_context_requirement_matches_injected_history():
    shadow = CognitivePlannerShadowRuntime()
    gateway = OfficialContextContinuityRuntimeGateway()
    gateway.set_cognitive_planner_shadow(shadow)
    incoming = request(
        "¿Y por qué?",
        session_id="follow-up",
        context=(ConversationalContextTurn("Tema", "Explicación previa"),),
    )
    shadow.observe(incoming, now=None)

    enriched = gateway.enrich(
        conversation=incoming,
        inference_request=LLMRequest(prompt=incoming.text),
    )

    assessment = shadow.context_assessment_for_session("follow-up")
    assert enriched.prompt != incoming.text
    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.SATISFIED
    assert assessment.conversation_context_required is True
    assert assessment.conversation_context_satisfied is True
    assert assessment.selected_conversation_turns == 1


def test_missing_required_conversation_context_is_observed_only():
    shadow = CognitivePlannerShadowRuntime()
    gateway = OfficialContextContinuityRuntimeGateway()
    gateway.set_cognitive_planner_shadow(shadow)
    incoming = request("¿Y por qué?", session_id="missing")
    shadow.observe(incoming, now=None)

    enriched = gateway.enrich(
        conversation=incoming,
        inference_request=LLMRequest(prompt=incoming.text),
    )

    assessment = shadow.context_assessment_for_session("missing")
    assert enriched.prompt == incoming.text
    assert assessment is not None
    assert assessment.status is ShadowAssessmentStatus.UNSATISFIED
    assert "planned_conversation_context_missing" in assessment.rationale_codes


def test_unplanned_context_injection_is_reported_without_trimming_prompt():
    shadow = CognitivePlannerShadowRuntime()
    gateway = OfficialContextContinuityRuntimeGateway()
    gateway.set_cognitive_planner_shadow(shadow)
    incoming = request(
        "Explicá la fotosíntesis",
        session_id="over-injection",
        context=(ConversationalContextTurn("Otro tema", "Respuesta anterior"),),
    )
    shadow.observe(incoming, now=None)

    enriched = gateway.enrich(
        conversation=incoming,
        inference_request=LLMRequest(prompt=incoming.text),
    )

    assessment = shadow.context_assessment_for_session("over-injection")
    assert enriched.prompt != incoming.text
    assert assessment is not None
    assert assessment.over_injection_observed is True
    assert assessment.status is ShadowAssessmentStatus.PARTIAL


def test_context_assessor_failure_is_fail_open():
    class BrokenAssessor:
        def assess(self, plan, **kwargs):
            del plan, kwargs
            raise RuntimeError("unavailable")

    shadow = CognitivePlannerShadowRuntime(context_assessor=BrokenAssessor())
    gateway = OfficialContextContinuityRuntimeGateway()
    gateway.set_cognitive_planner_shadow(shadow)
    incoming = request(
        "¿Y eso?",
        session_id="failure",
        context=(ConversationalContextTurn("Tema", "Respuesta"),),
    )
    shadow.observe(incoming, now=None)

    enriched = gateway.enrich(
        conversation=incoming,
        inference_request=LLMRequest(prompt=incoming.text),
    )

    assert enriched.prompt != incoming.text
    assert shadow.snapshot.context_failures == 1
