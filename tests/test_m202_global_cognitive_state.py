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
from core.global_cognitive_state import (
    GlobalCognitiveReadiness,
    GlobalCognitiveStateEngine,
    GlobalCognitiveStateRuntimeContributor,
)
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
)
from tests.test_m173_governed_provider_execution_adapter import RecordingProvider
from tests.test_m178_runtime_composition_root import (
    InferencePort,
    NeedPort,
    ObservationsPort,
    ReadinessPort,
    WorkloadPort,
)

NOW = datetime(2026, 7, 14, 0, 0, tzinfo=timezone.utc)


def conversation_stack():
    adaptive = AdaptiveConversationIntelligence()
    repair = ConversationalRepairIntelligence(adaptive)
    grounding = ConversationalGroundingIntelligence(repair)
    commitment = ConversationalCommitmentIntelligence(grounding)
    consolidation = AdaptiveConversationOperationalConsolidation(
        adaptive, repair, grounding, commitment
    )
    return adaptive, repair, grounding, commitment, consolidation


def publish(
    blackboard: UnifiedCognitiveBlackboard,
    *,
    key: str = "adaptive_conversation_operational_state",
    value: str = "ready",
    domain: CognitiveBlackboardDomain = CognitiveBlackboardDomain.CONVERSATION,
    kind: CognitiveBlackboardEntryKind = CognitiveBlackboardEntryKind.SIGNAL,
    confidence: float = 0.9,
):
    return blackboard.publish(
        CognitiveBlackboardEntry(
            owner="Carlos",
            session_id="main",
            domain=domain,
            kind=kind,
            key=key,
            value=value,
            confidence=confidence,
            created_at=NOW,
        )
    )


def dependencies(**overrides):
    values = {
        "readiness_port": ReadinessPort(),
        "observations_port": ObservationsPort(),
        "workload_port": WorkloadPort(),
        "knowledge_need_port": NeedPort(),
        "inference_request_port": InferencePort(),
        "local_providers": (RecordingProvider(),),
    }
    values.update(overrides)
    return RuntimeCompositionDependencies(**values)


def test_state_projects_ready_blackboard_as_stable():
    blackboard = UnifiedCognitiveBlackboard()
    source = publish(blackboard)
    state = GlobalCognitiveStateEngine(blackboard).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.readiness is GlobalCognitiveReadiness.STABLE
    assert state.signal_count == 1
    assert state.dimension("conversation_readiness").value == "ready"
    assert source.entry_id in state.source_reference_ids


def test_state_projects_repair_as_blocked():
    blackboard = UnifiedCognitiveBlackboard()
    publish(blackboard, value="repair_required")
    state = GlobalCognitiveStateEngine(blackboard).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.readiness is GlobalCognitiveReadiness.BLOCKED
    assert "conversation_repair_required" in state.constraints


def test_state_projects_grounding_as_limited():
    blackboard = UnifiedCognitiveBlackboard()
    publish(blackboard, value="grounding_required")
    state = GlobalCognitiveStateEngine(blackboard).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.readiness is GlobalCognitiveReadiness.LIMITED


def test_empty_blackboard_is_degraded():
    state = GlobalCognitiveStateEngine(UnifiedCognitiveBlackboard()).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.readiness is GlobalCognitiveReadiness.DEGRADED
    assert state.signal_count == 0


def test_active_domains_and_average_confidence_are_aggregated():
    blackboard = UnifiedCognitiveBlackboard()
    publish(blackboard, confidence=0.8)
    publish(
        blackboard,
        key="reasoning_confidence",
        value="high",
        domain=CognitiveBlackboardDomain.REASONING,
        confidence=0.6,
    )
    state = GlobalCognitiveStateEngine(blackboard).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.active_domains == (
        CognitiveBlackboardDomain.CONVERSATION,
        CognitiveBlackboardDomain.REASONING,
    )
    assert state.average_confidence == pytest.approx(0.7)


def test_constraints_limit_otherwise_ready_state():
    blackboard = UnifiedCognitiveBlackboard()
    publish(blackboard)
    publish(
        blackboard,
        key="scope_constraint",
        value="human_review_required",
        domain=CognitiveBlackboardDomain.SYSTEM,
        kind=CognitiveBlackboardEntryKind.CONSTRAINT,
    )
    state = GlobalCognitiveStateEngine(blackboard).assess(
        owner="Carlos", session_id="main", now=NOW
    )
    assert state.readiness is GlobalCognitiveReadiness.LIMITED
    assert state.constraints == ("human_review_required",)


def test_runtime_contributor_publishes_state_to_blackboard():
    blackboard = UnifiedCognitiveBlackboard()
    publish(blackboard)
    engine = GlobalCognitiveStateEngine()
    contribution = GlobalCognitiveStateRuntimeContributor(
        engine, blackboard
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="Continúa",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    snapshot = blackboard.snapshot(owner="Carlos", session_id="main", now=NOW)
    assert snapshot.latest("global_cognitive_state").value == "stable"
    assert contribution.reference_ids


def test_official_composition_orders_m202_after_m201():
    adaptive, repair, grounding, commitment, consolidation = conversation_stack()
    blackboard = UnifiedCognitiveBlackboard()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                adaptive_conversation_intelligence=adaptive,
                conversational_repair_intelligence=repair,
                conversational_grounding_intelligence=grounding,
                conversational_commitment_intelligence=commitment,
                adaptive_conversation_operational_consolidation=consolidation,
                unified_cognitive_blackboard=blackboard,
                global_cognitive_state=GlobalCognitiveStateEngine(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M202",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "unified_cognitive_blackboard",
        "global_cognitive_state",
    )


def test_m202_preserves_provider_request_settings():
    blackboard = UnifiedCognitiveBlackboard()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=blackboard,
                global_cognitive_state=GlobalCognitiveStateEngine(),
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    request = LLMRequest(
        prompt="base",
        system_prompt="system",
        model="local",
        max_tokens=222,
        temperature=0.1,
        metadata={"origin": "m202"},
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa M202",
        request=request,
        now=NOW,
    )
    assert result.request.system_prompt is not None
    assert result.request.system_prompt.startswith("system\n\n")
    assert "[Contexto cognitivo gobernado]" in result.request.system_prompt
    assert result.request.model == "local"
    assert result.request.max_tokens == 222
    assert result.request.temperature == 0.1
    assert result.request.metadata["origin"] == "m202"


def test_composition_rejects_global_state_without_blackboard():
    with pytest.raises(ValueError, match="requires the unified cognitive blackboard"):
        RuntimeCompositionRoot(
            dependencies(global_cognitive_state=GlobalCognitiveStateEngine())
        ).compose()
