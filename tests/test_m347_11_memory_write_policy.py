from pathlib import Path

from core.cognitive_intent import CognitiveIntentAnalyzer
from core.cognitive_memory import (
    CognitiveLearningPolicy,
    MemoryWriteDisposition,
    MemoryWriteReason,
)
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import (
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.conversation_strategy import (
    CognitiveAction,
    ConversationContext,
    ConversationStrategyPlanner,
)


def _evaluate(text: str, context: ConversationContext | None = None):
    intent = CognitiveIntentAnalyzer().analyze(text)
    strategy = ConversationStrategyPlanner().plan(intent, context=context)
    return CognitiveLearningPolicy().evaluate(text, intent, strategy)


def _store(tmp_path: Path) -> CognitiveMemoryStore:
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )


def test_durable_preference_authorizes_memory_write():
    result = _evaluate("Prefiero respuestas breves para los commits")

    assert result.should_store is True
    assert result.write_decision is not None
    assert result.write_decision.disposition is MemoryWriteDisposition.WRITE
    assert result.write_decision.reason is MemoryWriteReason.DURABLE_CANDIDATE
    assert result.write_decision.persistence_allowed is True


def test_temporary_context_requires_review_without_write():
    result = _evaluate("Hoy seguimos con la memoria conversacional")

    assert result.should_store is False
    assert result.write_decision is not None
    assert result.write_decision.disposition is MemoryWriteDisposition.REVIEW
    assert result.write_decision.reason is MemoryWriteReason.TEMPORARY_CONTEXT
    assert result.write_decision.requires_confirmation is True


def test_correction_requires_reconciliation_instead_of_append():
    context = ConversationContext(
        active_topic="preferencias de respuesta",
        previous_action=CognitiveAction.ANSWER,
        correction_target="longitud de respuesta",
        turn_index=4,
    )

    result = _evaluate(
        "No, prefiero respuestas detalladas para los commits",
        context=context,
    )

    assert result.should_store is False
    assert result.write_decision is not None
    assert result.write_decision.disposition is MemoryWriteDisposition.REVIEW
    assert result.write_decision.reason is (
        MemoryWriteReason.CORRECTION_REQUIRES_RECONCILIATION
    )
    assert result.write_decision.context_considered is True


def test_noise_is_explicitly_skipped():
    result = _evaluate("ok")

    assert result.write_decision is not None
    assert result.write_decision.disposition is MemoryWriteDisposition.SKIP
    assert result.write_decision.reason is MemoryWriteReason.NOISE_OR_TRANSIENT
    assert result.write_decision.persistence_allowed is False


def test_empty_content_has_safe_write_decision():
    result = _evaluate("   ")

    assert result.write_decision is not None
    assert result.write_decision.disposition is MemoryWriteDisposition.SKIP
    assert result.write_decision.reason is MemoryWriteReason.EMPTY_CONTENT
    assert result.write_decision.candidate_category is None


def test_write_decision_serialization_excludes_memory_content():
    result = _evaluate("Prefiero respuestas breves para los commits")

    assert result.write_decision is not None
    serialized = result.write_decision.as_dict()

    assert serialized["disposition"] == "write"
    assert serialized["candidate_category"] == "user_preference"
    assert "content" not in serialized
    assert "prompt" not in serialized


def test_memory_integration_uses_same_context_and_write_policy(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)
    context = ConversationContext(
        active_topic="preferencias de respuesta",
        correction_target="longitud de respuesta",
        turn_index=5,
    )

    result = integration.process_turn(
        "No, prefiero respuestas detalladas para los commits",
        context=context,
    )

    assert result.strategy.conversation_context is context
    assert result.learning_result.write_decision is not None
    assert result.learning_result.write_decision.context_considered is True
    assert result.stored_memory_ids == ()
    assert store.count() == 0


def test_memory_integration_persists_only_authorized_write(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)

    result = integration.process_turn(
        "En ROBY usamos Ruff y pytest antes de cerrar milestones"
    )

    assert result.learning_result.write_decision is not None
    assert result.learning_result.write_decision.persistence_allowed is True
    assert result.stored_memory_ids
    assert store.count() == 1
