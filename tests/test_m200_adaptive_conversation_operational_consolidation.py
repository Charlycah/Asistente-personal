from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalAction,
    AdaptiveConversationOperationalAssessment,
    AdaptiveConversationOperationalConsolidation,
    AdaptiveConversationOperationalRuntimeContributor,
    AdaptiveConversationOperationalState,
)
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
from core.conversational_commitment_intelligence import (
    ConversationalCommitmentIntelligence,
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

NOW = datetime(2026, 7, 13, 22, 0, tzinfo=timezone.utc)


def stack():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    consolidation = AdaptiveConversationOperationalConsolidation(
        adaptive, repair, grounding, commitment
    )
    return adaptive, repair, grounding, commitment, consolidation


def test_aligned_stack_is_ready():
    *_, consolidation = stack()
    result = consolidation.assess(
        owner="Carlos", session_id="main", text="Implementa M200 con pruebas", now=NOW
    )
    assert result.state is AdaptiveConversationOperationalState.READY
    assert result.action is AdaptiveConversationOperationalAction.PROCEED
    assert len(result.source_reference_ids) == 4


def test_ambiguous_reference_prioritizes_repair():
    *_, consolidation = stack()
    result = consolidation.assess(
        owner="Carlos", session_id="main", text="Hazlo", now=NOW
    )
    assert result.state is AdaptiveConversationOperationalState.REPAIR_REQUIRED
    assert result.action is AdaptiveConversationOperationalAction.APPLY_REPAIR


def test_absolute_guarantee_requires_expectation_calibration():
    *_, consolidation = stack()
    result = consolidation.assess(
        owner="Carlos",
        session_id="main",
        text="Garantiza que funcionará siempre y sin errores",
        now=NOW,
    )
    assert (
        result.state
        is AdaptiveConversationOperationalState.EXPECTATION_CALIBRATION_REQUIRED
    )
    assert result.action is AdaptiveConversationOperationalAction.CALIBRATE_EXPECTATION


def test_assessment_identifier_is_deterministic():
    *_, consolidation = stack()
    first = consolidation.assess(
        owner="Carlos", session_id="main", text="Implementa M200", now=NOW
    )
    second = consolidation.assess(
        owner="Carlos", session_id="main", text="Implementa M200", now=NOW
    )
    assert first.assessment_id == second.assessment_id


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="confidence"):
        AdaptiveConversationOperationalAssessment(
            owner="Carlos",
            session_id="main",
            state=AdaptiveConversationOperationalState.READY,
            action=AdaptiveConversationOperationalAction.PROCEED,
            confidence=2.0,
            source_reference_ids=(),
            rationale=(),
            prompt_lines=(),
            created_at=NOW,
        )


def test_runtime_contributor_is_advisory_and_traceable():
    *_, consolidation = stack()
    contribution = AdaptiveConversationOperationalRuntimeContributor(
        consolidation
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Implementa M200",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert len(contribution.reference_ids) == 5
    assert any(
        "Consolidación conversacional" in line for line in contribution.prompt_lines
    )


def test_official_composition_orders_m200_after_m199():
    adaptive, repair, grounding, commitment, consolidation = stack()
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
        adaptive_conversation_operational_consolidation=consolidation,
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M200",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages == (
        "adaptive_conversation_intelligence",
        "conversational_repair_intelligence",
        "conversational_grounding_intelligence",
        "conversational_commitment_intelligence",
        "adaptive_conversation_operational_consolidation",
    )


def test_composition_binds_all_m196_m199_sources():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence()
    grounding = ConversationalGroundingIntelligence()
    commitment = ConversationalCommitmentIntelligence()
    consolidation = AdaptiveConversationOperationalConsolidation()
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
        adaptive_conversation_operational_consolidation=consolidation,
    )
    RuntimeCompositionRoot(dependencies).compose()
    assert consolidation.adaptive_intelligence is adaptive
    assert consolidation.repair_intelligence is repair
    assert consolidation.grounding_intelligence is grounding
    assert consolidation.commitment_intelligence is commitment


def test_m200_preserves_provider_request_settings():
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
        adaptive_conversation_operational_consolidation=AdaptiveConversationOperationalConsolidation(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M200",
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


def test_consolidation_does_not_mutate_request_or_execute_actions():
    request = LLMRequest(prompt="original", metadata={"origin": "test"})
    AdaptiveConversationOperationalConsolidation().assess(
        owner="Carlos", session_id="main", text="Implementa M200", now=NOW
    )
    assert request.prompt == "original"
    assert request.metadata == {"origin": "test"}
