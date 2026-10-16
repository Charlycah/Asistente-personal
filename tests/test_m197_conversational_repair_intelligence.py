from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.conversational_repair_intelligence import (
    ConversationalRepairIntelligence,
    ConversationalRepairRuntimeContributor,
    ConversationRepairAction,
    ConversationRepairAssessment,
    ConversationRepairIssue,
    ConversationRepairSeverity,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import (
    RuntimeCompositionDependencies,
    RuntimeCompositionRoot,
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 13, 19, 0, tzinfo=timezone.utc)


def test_grounded_request_proceeds_without_repair():
    result = ConversationalRepairIntelligence().assess(
        owner="Carlos",
        session_id="main",
        text="Implementa las pruebas unitarias del módulo M197",
        now=NOW,
    )
    assert result.issue is ConversationRepairIssue.NONE
    assert result.action is ConversationRepairAction.PROCEED
    assert result.severity is ConversationRepairSeverity.NONE


def test_missing_reference_requests_targeted_clarification():
    result = ConversationalRepairIntelligence().assess(
        owner="Carlos", session_id="main", text="Corrige eso", now=NOW
    )
    assert result.issue is ConversationRepairIssue.MISSING_REFERENCE
    assert result.action is ConversationRepairAction.ASK_TARGETED_CLARIFICATION


def test_generic_request_is_classified_as_underspecified():
    result = ConversationalRepairIntelligence().assess(
        owner="Carlos", session_id="main", text="Hazlo", now=NOW
    )
    assert result.issue is ConversationRepairIssue.UNDERSPECIFIED_REQUEST
    assert result.severity is ConversationRepairSeverity.MEDIUM


def test_uncertain_intent_recommends_confirmation():
    result = ConversationalRepairIntelligence().assess(
        owner="Carlos",
        session_id="main",
        text="Tal vez deberíamos cambiar la arquitectura",
        now=NOW,
    )
    assert result.issue is ConversationRepairIssue.UNCERTAIN_INTENT
    assert result.action is ConversationRepairAction.ASK_TARGETED_CLARIFICATION


def test_adaptive_correction_recommends_confirmation():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    adaptive.assess(owner="Carlos", session_id="main", text="Diseña el módulo", now=NOW)
    adaptive.assess(
        owner="Carlos",
        session_id="main",
        text="No, corrección: diseña solo la interfaz",
        now=NOW,
    )
    result = repair.assess(
        owner="Carlos",
        session_id="main",
        text="No, corrección: diseña solo la interfaz",
        now=NOW,
    )
    assert result.issue is ConversationRepairIssue.CORRECTION_TRANSITION
    assert result.action is ConversationRepairAction.CONFIRM_CORRECTION


def test_abrupt_short_topic_shift_is_acknowledged():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    adaptive.assess(
        owner="Carlos", session_id="main", text="Arquitectura Python", now=NOW
    )
    adaptive.assess(
        owner="Carlos", session_id="main", text="Cena familiar mañana", now=NOW
    )
    result = repair.assess(
        owner="Carlos", session_id="main", text="Cena familiar mañana", now=NOW
    )
    assert result.issue is ConversationRepairIssue.ABRUPT_TOPIC_SHIFT
    assert result.action is ConversationRepairAction.ACKNOWLEDGE_TOPIC_SHIFT


def test_assessment_identifier_is_deterministic():
    intelligence = ConversationalRepairIntelligence()
    first = intelligence.assess(
        owner="Carlos", session_id="main", text="Hazlo", now=NOW
    )
    second = intelligence.assess(
        owner="Carlos", session_id="main", text="Hazlo", now=NOW
    )
    assert first.assessment_id == second.assessment_id


def test_invalid_assessment_invariants_are_rejected():
    with pytest.raises(ValueError, match="confidence"):
        ConversationRepairAssessment(
            owner="Carlos",
            session_id="main",
            issue=ConversationRepairIssue.NONE,
            action=ConversationRepairAction.PROCEED,
            severity=ConversationRepairSeverity.NONE,
            confidence=1.1,
            rationale=(),
            prompt_lines=(),
            created_at=NOW,
        )


def test_runtime_contributor_is_advisory_and_traceable():
    contributor = ConversationalRepairRuntimeContributor(
        ConversationalRepairIntelligence()
    )
    contribution = contributor.contribute(
        owner="Carlos",
        session_id="main",
        text="Corrige eso",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert contribution.reference_ids
    assert any("aclaración" in line for line in contribution.prompt_lines)


def test_official_composition_orders_m197_immediately_after_m196():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence()
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        adaptive_conversation_intelligence=adaptive,
        conversational_repair_intelligence=repair,
    )
    composition = RuntimeCompositionRoot(dependencies).compose()
    result = composition.preparation.dependencies.cognitive_runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Corrige eso",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
    )
    assert repair.adaptive_intelligence is adaptive
    assert "Reparación conversacional" in result.request.prompt


def test_m197_preserves_provider_request_settings():
    request = LLMRequest(
        prompt="base",
        system_prompt="system",
        model="local",
        max_tokens=321,
        temperature=0.2,
        metadata={"origin": "test"},
    )
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        conversational_repair_intelligence=ConversationalRepairIntelligence(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos", session_id="main", text="Hazlo", request=request, now=NOW
    )
    assert result.request.system_prompt is not None
    assert result.request.system_prompt.startswith("system\n\n")
    assert "[Contexto cognitivo gobernado]" in result.request.system_prompt
    assert result.request.model == "local"
    assert result.request.max_tokens == 321
    assert result.request.temperature == 0.2
    assert result.request.metadata["origin"] == "test"


def test_repair_assessment_does_not_execute_or_mutate_actions():
    request = LLMRequest(prompt="original", metadata={"origin": "test"})
    ConversationalRepairIntelligence().assess(
        owner="Carlos", session_id="main", text="Hazlo", now=NOW
    )
    assert request.prompt == "original"
    assert request.metadata == {"origin": "test"}
