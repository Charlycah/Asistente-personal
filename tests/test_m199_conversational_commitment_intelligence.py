from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
    ConversationalCommitmentRuntimeContributor,
    ConversationCommitmentAction,
    ConversationCommitmentAssessment,
    ConversationCommitmentState,
)
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
)
from core.conversational_repair_intelligence import ConversationalRepairIntelligence
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

NOW = datetime(2026, 7, 13, 21, 0, tzinfo=timezone.utc)


def test_normal_request_keeps_expectations_aligned():
    result = ConversationalCommitmentIntelligence().assess(
        owner="Carlos", session_id="main", text="Implementa M199 con pruebas", now=NOW
    )
    assert result.state is ConversationCommitmentState.EXPECTATION_ALIGNED
    assert result.action is ConversationCommitmentAction.PROCEED


def test_explicit_commitment_is_bounded_to_current_turn():
    result = ConversationalCommitmentIntelligence().assess(
        owner="Carlos",
        session_id="main",
        text="Confirma que vas a completar el módulo",
        now=NOW,
    )
    assert result.state is ConversationCommitmentState.COMMITMENT_REQUESTED
    assert result.action is ConversationCommitmentAction.STATE_BOUNDED_COMMITMENT


def test_absolute_guarantee_is_calibrated():
    result = ConversationalCommitmentIntelligence().assess(
        owner="Carlos",
        session_id="main",
        text="Garantiza que funcionará siempre y sin errores",
        now=NOW,
    )
    assert result.state is ConversationCommitmentState.ABSOLUTE_GUARANTEE_REQUESTED
    assert result.action is ConversationCommitmentAction.CALIBRATE_EXPECTATION


def test_pending_grounding_defers_commitment():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    repair.assess(owner="Carlos", session_id="main", text="Hazlo", now=NOW)
    grounding.assess(owner="Carlos", session_id="main", text="Hazlo", now=NOW)
    result = commitment.assess(
        owner="Carlos", session_id="main", text="Promete terminarlo", now=NOW
    )
    assert result.state is ConversationCommitmentState.GROUNDING_BLOCKED
    assert result.action is ConversationCommitmentAction.DEFER_COMMITMENT


def test_assessment_identifier_is_deterministic():
    intelligence = ConversationalCommitmentIntelligence()
    first = intelligence.assess(
        owner="Carlos", session_id="main", text="Implementa M199", now=NOW
    )
    second = intelligence.assess(
        owner="Carlos", session_id="main", text="Implementa M199", now=NOW
    )
    assert first.assessment_id == second.assessment_id


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="confidence"):
        ConversationCommitmentAssessment(
            owner="Carlos",
            session_id="main",
            state=ConversationCommitmentState.EXPECTATION_ALIGNED,
            action=ConversationCommitmentAction.PROCEED,
            confidence=2.0,
            expectation_markers=(),
            rationale=(),
            prompt_lines=(),
            created_at=NOW,
        )


def test_runtime_contributor_is_advisory_and_traceable():
    contribution = ConversationalCommitmentRuntimeContributor(
        ConversationalCommitmentIntelligence()
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Garantiza que no falle",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert contribution.reference_ids
    assert any(
        "Compromiso conversacional" in line for line in contribution.prompt_lines
    )


def test_official_composition_orders_m199_after_m198():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence()
    grounding = ConversationalGroundingIntelligence()
    commitment = ConversationalCommitmentIntelligence()
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        adaptive_conversation_intelligence=adaptive,
        conversational_repair_intelligence=repair,
        conversational_grounding_intelligence=grounding,
        conversational_commitment_intelligence=commitment,
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Correcto, garantiza el resultado",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
        "conversational_commitment_intelligence",
    )
    assert commitment.grounding_intelligence is grounding


def test_m199_preserves_provider_request_settings():
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
        conversational_commitment_intelligence=ConversationalCommitmentIntelligence(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M199",
        request=request,
        now=NOW,
    )
    assert result.request.system_prompt is not None
    assert result.request.system_prompt.startswith("system\n\n")
    assert "[Contexto cognitivo gobernado]" in result.request.system_prompt
    assert result.request.model == "local"
    assert result.request.max_tokens == 321
    assert result.request.temperature == 0.2
    assert result.request.metadata["origin"] == "test"


def test_commitment_does_not_mutate_request_or_execute_actions():
    request = LLMRequest(prompt="original", metadata={"origin": "test"})
    ConversationalCommitmentIntelligence().assess(
        owner="Carlos", session_id="main", text="Promete hacerlo", now=NOW
    )
    assert request.prompt == "original"
    assert request.metadata == {"origin": "test"}
