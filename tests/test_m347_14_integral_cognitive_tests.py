from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.cognitive_intent import CognitiveIntent, InteractionIntent
from core.cognitive_memory import MemoryWriteDisposition
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_recall import (
    MemoryRelevanceReason,
    SessionContinuityReason,
)
from core.cognitive_memory_store import (
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.conversation_strategy import CognitiveAction, ConversationContext
from core.memory_prompt_context import MemoryPromptContextBuilder
from core.personal_identity_and_session_profiles.models import (
    RuntimeSessionProfile,
)


def _integration(tmp_path: Path) -> CognitiveMemoryIntegration:
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )
    return CognitiveMemoryIntegration(store)


def _session(session_id: str, profile_id: str = "carlos") -> RuntimeSessionProfile:
    now = datetime.now(UTC)
    return RuntimeSessionProfile(
        session_id=session_id,
        profile_id=profile_id,
        created_at=now - timedelta(minutes=5),
        last_active_at=now,
    )


def test_integral_turn_classifies_plans_traces_and_persists(tmp_path):
    integration = _integration(tmp_path)
    session = _session("session-a")

    result = integration.process_turn(
        "En ROBY usamos Ruff y pytest antes de cerrar cada milestone",
        session_profile=session,
    )

    assert result.intent_result.intent is CognitiveIntent.PROJECT_WORK
    assert result.intent_result.interaction_intent is InteractionIntent.UNKNOWN
    assert result.strategy.selected_action is CognitiveAction.ANSWER
    assert result.strategy.decision_trace is not None
    assert result.strategy.decision_trace.selected_action is CognitiveAction.ANSWER
    assert result.learning_result.write_decision is not None
    assert (
        result.learning_result.write_decision.disposition
        is MemoryWriteDisposition.WRITE
    )
    assert result.stored_memory_ids
    assert integration.store.count() == 1
    assert result.session_profile is session


def test_integral_memory_continues_across_sessions_and_builds_prompt(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn(
        "En ROBY usamos Ruff y pytest antes de cerrar cada milestone",
        session_profile=_session("session-a"),
    )

    result = integration.process_turn(
        "Recordemos Ruff y pytest para cerrar este milestone",
        session_profile=_session("session-b"),
        enable_learning=False,
    )
    prompt_context = MemoryPromptContextBuilder().build(
        result.recall_result,
        strategy=result.strategy,
    )

    assert result.recall_result.should_use_memory is True
    assert result.recall_result.relevance_decision is not None
    assert (
        result.recall_result.relevance_decision.reason
        is MemoryRelevanceReason.RELEVANT_MEMORY_FOUND
    )
    assert result.recall_result.continuity_decision is not None
    assert (
        result.recall_result.continuity_decision.reason
        is SessionContinuityReason.CROSS_SESSION_MEMORY
    )
    assert prompt_context.should_include is True
    assert "ruff y pytest" in prompt_context.context
    assert "Estrategia:" in prompt_context.context


def test_integral_context_is_shared_by_planning_learning_and_recall(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn(
        "En ROBY la memoria conversacional mantiene continuidad relevante"
    )
    context = ConversationContext(
        active_topic="memoria conversacional",
        active_entities=("ROBY",),
        previous_action=CognitiveAction.ANSWER,
        turn_index=3,
    )

    result = integration.process_turn(
        "Continuemos con eso",
        context=context,
        enable_learning=False,
    )

    assert result.strategy.conversation_context is context
    assert result.strategy.decision_trace is not None
    assert result.strategy.decision_trace.conversation_context is context
    assert result.recall_result.relevance_decision is not None
    assert result.recall_result.relevance_decision.context_considered is True
    assert "memoria" in result.recall_result.relevance_decision.context_signals
    assert result.recall_result.should_use_memory is True


def test_integral_correction_does_not_append_a_second_truth(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("Prefiero respuestas breves para los commits")
    context = ConversationContext(
        active_topic="preferencias de respuesta",
        previous_action=CognitiveAction.ANSWER,
        correction_target="longitud de respuesta",
        turn_index=4,
    )

    result = integration.process_turn(
        "No, prefiero respuestas detalladas para los commits",
        context=context,
    )

    assert result.intent_result.interaction_intent is InteractionIntent.CORRECTION
    assert result.strategy.selected_action is CognitiveAction.REVISE_CONTEXT
    assert result.learning_result.write_decision is not None
    assert (
        result.learning_result.write_decision.disposition
        is MemoryWriteDisposition.REVIEW
    )
    assert result.stored_memory_ids == ()
    assert integration.store.count() == 1


def test_integral_profile_isolation_prevents_prompt_projection(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn(
        "En ROBY usamos Ruff y pytest antes de cerrar cada milestone",
        session_profile=_session("session-a", profile_id="otro"),
    )

    result = integration.process_turn(
        "Recordemos Ruff y pytest para cerrar este milestone",
        session_profile=_session("session-b", profile_id="carlos"),
        enable_learning=False,
    )
    prompt_context = MemoryPromptContextBuilder().build(result.recall_result)

    assert result.recall_result.should_use_memory is False
    assert result.recall_result.continuity_decision is not None
    assert result.recall_result.continuity_decision.filtered_profile_count == 1
    assert prompt_context.should_include is False
    assert prompt_context.context == ""


def test_integral_decisions_serialize_without_memory_content(tmp_path):
    integration = _integration(tmp_path)
    secret = "En ROBY usamos Ruff y pytest antes de cerrar cada milestone"
    integration.process_turn(
        secret,
        session_profile=_session("session-a"),
    )
    result = integration.process_turn(
        "Recordemos Ruff y pytest para cerrar este milestone",
        session_profile=_session("session-b"),
        enable_learning=False,
    )

    assert result.strategy.decision_trace is not None
    assert result.learning_result.write_decision is not None
    assert result.recall_result.relevance_decision is not None
    assert result.recall_result.continuity_decision is not None
    serialized = {
        "trace": result.strategy.decision_trace.as_dict(),
        "write": result.learning_result.write_decision.as_dict(),
        "relevance": result.recall_result.relevance_decision.as_dict(),
        "continuity": result.recall_result.continuity_decision.as_dict(),
    }

    assert secret not in repr(serialized)
    assert "prompt" not in repr(serialized).lower()
    assert "memory" not in serialized["continuity"]


def test_integral_feature_switches_do_not_bypass_cognitive_analysis(tmp_path):
    integration = _integration(tmp_path)

    result = integration.process_turn(
        "En ROBY usamos Ruff y pytest antes de cerrar cada milestone",
        enable_learning=False,
        enable_recall=False,
    )

    assert result.intent_result.intent is CognitiveIntent.PROJECT_WORK
    assert result.strategy.decision_trace is not None
    assert result.recall_result.should_use_memory is False
    assert result.recall_result.reason == "recall_disabled"
    assert result.stored_memory_ids == ()
    assert integration.store.count() == 0
