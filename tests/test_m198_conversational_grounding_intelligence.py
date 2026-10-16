from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationalGroundingRuntimeContributor,
    ConversationGroundingAction,
    ConversationGroundingAssessment,
    ConversationGroundingState,
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

NOW = datetime(2026, 7, 13, 20, 0, tzinfo=timezone.utc)


def test_grounded_turn_proceeds_without_restatement():
    result = ConversationalGroundingIntelligence().assess(
        owner="Carlos", session_id="main", text="Implementa M198 con pruebas", now=NOW
    )
    assert result.state is ConversationGroundingState.ALIGNED
    assert result.action is ConversationGroundingAction.PROCEED


def test_explicit_confirmation_is_acknowledged():
    result = ConversationalGroundingIntelligence().assess(
        owner="Carlos",
        session_id="main",
        text="Correcto, seguimos con ese alcance",
        now=NOW,
    )
    assert result.state is ConversationGroundingState.EXPLICITLY_CONFIRMED
    assert result.action is ConversationGroundingAction.ACKNOWLEDGE_ALIGNMENT


def test_pending_repair_preserves_clarification_boundary():
    repair = ConversationalRepairIntelligence()
    grounding = ConversationalGroundingIntelligence(repair)
    repair.assess(owner="Carlos", session_id="main", text="Hazlo", now=NOW)
    result = grounding.assess(owner="Carlos", session_id="main", text="Hazlo", now=NOW)
    assert result.state is ConversationGroundingState.CLARIFICATION_PENDING
    assert result.action is ConversationGroundingAction.PRESERVE_CLARIFICATION_BOUNDARY


def test_correction_becomes_current_shared_scope():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    adaptive.assess(
        owner="Carlos",
        session_id="main",
        text="Diseña todo el módulo",
        now=NOW,
    )
    adaptive.assess(
        owner="Carlos",
        session_id="main",
        text="No, corrección: solo la interfaz",
        now=NOW,
    )
    repair.assess(
        owner="Carlos",
        session_id="main",
        text="No, corrección: solo la interfaz",
        now=NOW,
    )
    result = grounding.assess(
        owner="Carlos",
        session_id="main",
        text="No, corrección: solo la interfaz",
        now=NOW,
    )
    assert result.state is ConversationGroundingState.CORRECTED_SCOPE
    assert result.action is ConversationGroundingAction.RESTATE_CORRECTED_SCOPE
    assert "solo" in result.shared_scope


def test_assessment_identifier_is_deterministic():
    intelligence = ConversationalGroundingIntelligence()
    first = intelligence.assess(
        owner="Carlos", session_id="main", text="Implementa M198", now=NOW
    )
    second = intelligence.assess(
        owner="Carlos", session_id="main", text="Implementa M198", now=NOW
    )
    assert first.assessment_id == second.assessment_id


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="confidence"):
        ConversationGroundingAssessment(
            owner="Carlos",
            session_id="main",
            state=ConversationGroundingState.ALIGNED,
            action=ConversationGroundingAction.PROCEED,
            confidence=1.1,
            shared_scope=(),
            rationale=(),
            prompt_lines=(),
            created_at=NOW,
        )


def test_runtime_contributor_is_advisory_and_traceable():
    contributor = ConversationalGroundingRuntimeContributor(
        ConversationalGroundingIntelligence()
    )
    contribution = contributor.contribute(
        owner="Carlos",
        session_id="main",
        text="Correcto, seguimos",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert contribution.reference_ids
    assert any("Entendimiento compartido" in line for line in contribution.prompt_lines)


def test_official_composition_orders_m198_after_m197():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence()
    grounding = ConversationalGroundingIntelligence()
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
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Correcto, seguimos",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
    )
    assert grounding.repair_intelligence is repair
    assert "Entendimiento compartido" in result.request.prompt


def test_m198_preserves_provider_request_settings():
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
        conversational_grounding_intelligence=ConversationalGroundingIntelligence(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M198",
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


def test_grounding_does_not_mutate_request_or_execute_actions():
    request = LLMRequest(prompt="original", metadata={"origin": "test"})
    ConversationalGroundingIntelligence().assess(
        owner="Carlos", session_id="main", text="Correcto", now=NOW
    )
    assert request.prompt == "original"
    assert request.metadata == {"origin": "test"}
