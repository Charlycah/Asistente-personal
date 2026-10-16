from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import AdaptiveConversationIntelligence
from core.adaptive_conversation_operational_consolidation import (
    AdaptiveConversationOperationalConsolidation,
)
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
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
    UnifiedCognitiveBlackboardRuntimeContributor,
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 13, 23, 0, tzinfo=timezone.utc)


def stack():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    consolidation = AdaptiveConversationOperationalConsolidation(
        adaptive, repair, grounding, commitment
    )
    return adaptive, repair, grounding, commitment, consolidation


def entry(**overrides):
    values = {
        "owner": "Carlos",
        "session_id": "main",
        "domain": CognitiveBlackboardDomain.REASONING,
        "kind": CognitiveBlackboardEntryKind.SIGNAL,
        "key": "confidence",
        "value": "high",
        "confidence": 0.9,
        "created_at": NOW,
    }
    values.update(overrides)
    return CognitiveBlackboardEntry(**values)


def test_publish_and_snapshot_preserve_immutable_entry():
    blackboard = UnifiedCognitiveBlackboard()
    published = blackboard.publish(entry())
    snapshot = blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
    assert snapshot.entries == (published,)
    assert snapshot.latest("confidence") is published


def test_blackboard_isolates_owner_and_session():
    blackboard = UnifiedCognitiveBlackboard()
    blackboard.publish(entry())
    assert not blackboard.snapshot(owner="Other", session_id="main", now=NOW).entries
    assert not blackboard.snapshot(owner="Carlos", session_id="other", now=NOW).entries


def test_duplicate_entry_is_idempotent():
    blackboard = UnifiedCognitiveBlackboard()
    item = entry()
    blackboard.publish(item)
    blackboard.publish(item)
    snapshot = blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
    assert len(snapshot.entries) == 1


def test_retention_is_bounded_per_session():
    blackboard = UnifiedCognitiveBlackboard(maximum_entries_per_session=2)
    for index in range(3):
        blackboard.publish(entry(key=f"signal_{index}", value=str(index)))
    snapshot = blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
    assert tuple(item.key for item in snapshot.entries) == ("signal_1", "signal_2")


def test_domain_filter_returns_only_requested_entries():
    blackboard = UnifiedCognitiveBlackboard()
    blackboard.publish(entry(domain=CognitiveBlackboardDomain.REASONING))
    blackboard.publish(entry(domain=CognitiveBlackboardDomain.PLANNING, key="plan"))
    snapshot = blackboard.snapshot(
        owner="Carlos",
        session_id="main",
        domains=(CognitiveBlackboardDomain.PLANNING,),
        now=NOW,
    )
    assert tuple(item.domain for item in snapshot.entries) == (
        CognitiveBlackboardDomain.PLANNING,
    )


def test_invalid_confidence_is_rejected():
    with pytest.raises(ValueError, match="confidence"):
        entry(confidence=2.0)


def test_runtime_contributor_publishes_m200_state():
    *_, consolidation = stack()
    blackboard = UnifiedCognitiveBlackboard()
    contribution = UnifiedCognitiveBlackboardRuntimeContributor(
        blackboard, consolidation
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Implementa M201 con pruebas",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    snapshot = blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
    assert snapshot.latest("adaptive_conversation_operational_state").value == "ready"
    assert contribution.reference_ids


def test_official_composition_orders_m201_after_m200():
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
        unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M201",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "adaptive_conversation_operational_consolidation",
        "unified_cognitive_blackboard",
    )


def test_m201_preserves_provider_request_settings():
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
        unified_cognitive_blackboard=UnifiedCognitiveBlackboard(),
    )
    runtime = (
        RuntimeCompositionRoot(dependencies)
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M201",
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


def test_clear_session_removes_only_target_identity():
    blackboard = UnifiedCognitiveBlackboard()
    blackboard.publish(entry())
    blackboard.publish(entry(session_id="other"))
    assert blackboard.clear_session(owner="Carlos", session_id="main") == 1
    assert blackboard.snapshot(owner="Carlos", session_id="other", now=NOW).entries
