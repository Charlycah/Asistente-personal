from datetime import datetime, timezone

import pytest

from core.adaptive_conversation_intelligence import (
    AdaptiveConversationIntelligence,
    AdaptiveConversationRuntimeContributor,
    AdaptiveConversationState,
    AdaptiveConversationStateStore,
    ConversationDepth,
    ConversationIntentEvolution,
    ConversationResponseStrategy,
)
from core.cognitive_runtime_orchestration import CognitiveRuntimeStageStatus
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

NOW = datetime(2026, 7, 13, 18, 0, tzinfo=timezone.utc)


def test_initial_turn_creates_deterministic_adaptive_state():
    intelligence = AdaptiveConversationIntelligence()
    result = intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="Implementa la arquitectura técnica de M196",
        now=NOW,
    )
    assert result.state.turn_count == 1
    assert result.state.intent_evolution is ConversationIntentEvolution.INITIAL
    assert result.state.strategy is ConversationResponseStrategy.TECHNICAL
    assert result.state.depth is ConversationDepth.DEEP
    assert result.state.state_id


def test_continuation_is_detected_from_topic_overlap():
    intelligence = AdaptiveConversationIntelligence()
    intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="Revisemos la arquitectura del runtime conversacional",
        now=NOW,
    )
    result = intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="La arquitectura del runtime necesita más pruebas",
        now=NOW,
    )
    assert result.state.intent_evolution is ConversationIntentEvolution.CONTINUATION
    assert result.state.continuity_score >= 0.35


def test_correction_and_refinement_are_explicitly_distinguished():
    intelligence = AdaptiveConversationIntelligence()
    intelligence.assess(
        owner="Carlos", session_id="a", text="Diseña el módulo", now=NOW
    )
    correction = intelligence.assess(
        owner="Carlos",
        session_id="a",
        text="No, corrección: diseña solamente la interfaz",
        now=NOW,
    )
    assert correction.state.intent_evolution is ConversationIntentEvolution.CORRECTION

    intelligence.assess(
        owner="Carlos", session_id="b", text="Diseña el módulo", now=NOW
    )
    refinement = intelligence.assess(
        owner="Carlos",
        session_id="b",
        text="Además, profundiza en sus pruebas",
        now=NOW,
    )
    assert refinement.state.intent_evolution is ConversationIntentEvolution.REFINEMENT


def test_topic_shift_reduces_continuity_without_failure():
    intelligence = AdaptiveConversationIntelligence()
    intelligence.assess(
        owner="Carlos", session_id="main", text="Arquitectura Python", now=NOW
    )
    result = intelligence.assess(
        owner="Carlos", session_id="main", text="Planifica una cena familiar", now=NOW
    )
    assert result.state.intent_evolution is ConversationIntentEvolution.TOPIC_SHIFT
    assert result.state.coherence_score == 0.7


def test_strategy_selects_concise_collaborative_and_explanatory_modes():
    intelligence = AdaptiveConversationIntelligence()
    concise = intelligence.assess(
        owner="Carlos", session_id="1", text="Dame un resumen breve", now=NOW
    )
    collaborative = intelligence.assess(
        owner="Carlos", session_id="2", text="Ayúdame a resolver esta decisión", now=NOW
    )
    explanatory = intelligence.assess(
        owner="Carlos",
        session_id="3",
        text="Explica cómo funciona esta decisión",
        now=NOW,
    )
    assert concise.state.strategy is ConversationResponseStrategy.CONCISE
    assert collaborative.state.strategy is ConversationResponseStrategy.COLLABORATIVE
    assert explanatory.state.strategy is ConversationResponseStrategy.EXPLANATORY


def test_sessions_and_owners_are_isolated():
    store = AdaptiveConversationStateStore()
    intelligence = AdaptiveConversationIntelligence(store)
    intelligence.assess(owner="Carlos", session_id="one", text="Tema uno", now=NOW)
    intelligence.assess(owner="Carlos", session_id="two", text="Tema dos", now=NOW)
    assert store.get("Carlos", "one").turn_count == 1
    assert store.get("Carlos", "two").turn_count == 1
    assert store.get("Other", "one") is None


def test_state_store_is_bounded():
    store = AdaptiveConversationStateStore(maximum_sessions=2)
    intelligence = AdaptiveConversationIntelligence(store)
    for index in range(3):
        intelligence.assess(
            owner="Carlos",
            session_id=str(index),
            text=f"Tema {index}",
            now=NOW.replace(second=index),
        )
    assert store.get("Carlos", "0") is None
    assert store.get("Carlos", "2") is not None


def test_invalid_state_invariants_are_rejected():
    with pytest.raises(ValueError, match="turn count"):
        AdaptiveConversationState(
            owner="Carlos",
            session_id="main",
            turn_count=0,
            dominant_topic="topic",
            active_goal="goal",
            intent_evolution=ConversationIntentEvolution.INITIAL,
            strategy=ConversationResponseStrategy.DIRECT,
            depth=ConversationDepth.LIGHT,
            continuity_score=1.0,
            coherence_score=1.0,
            updated_at=NOW,
        )


def test_runtime_contributor_is_advisory_and_emits_reference():
    contributor = AdaptiveConversationRuntimeContributor(
        AdaptiveConversationIntelligence()
    )
    contribution = contributor.contribute(
        owner="Carlos",
        session_id="main",
        text="Implementa pruebas técnicas",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.status is CognitiveRuntimeStageStatus.APPLIED
    assert contribution.reference_ids
    assert any(
        "Adaptación conversacional" in line for line in contribution.prompt_lines
    )


def test_official_composition_inserts_m196_before_existing_cognitive_stages():
    dependencies = RuntimeCompositionDependencies(
        readiness_port=ReadinessPort(),
        observations_port=ObservationsPort(),
        workload_port=WorkloadPort(),
        knowledge_need_port=NeedPort(),
        inference_request_port=InferencePort(),
        local_providers=(RecordingProvider(),),
        adaptive_conversation_intelligence=AdaptiveConversationIntelligence(),
    )
    composition = RuntimeCompositionRoot(dependencies).compose()
    result = composition.preparation.dependencies.cognitive_runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Implementa la arquitectura técnica",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages == ("adaptive_conversation_intelligence",)
    assert "Adaptación conversacional" in result.request.prompt
    assert "cognitive_context" in result.request.metadata


def test_assessment_does_not_mutate_provider_request_or_execute_any_action():
    request = LLMRequest(prompt="original", metadata={"origin": "test"})
    intelligence = AdaptiveConversationIntelligence()
    intelligence.assess(owner="Carlos", session_id="main", text="Hola", now=NOW)
    assert request.prompt == "original"
    assert request.metadata == {"origin": "test"}
