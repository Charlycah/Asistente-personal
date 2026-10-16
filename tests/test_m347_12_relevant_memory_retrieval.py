from pathlib import Path

from core.cognitive_intent import CognitiveIntentAnalyzer
from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
    MemoryRelevanceReason,
)
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.conversation_strategy import ConversationContext, ConversationStrategyPlanner


def _store(tmp_path: Path) -> CognitiveMemoryStore:
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )


def _integration(tmp_path: Path) -> CognitiveMemoryIntegration:
    return CognitiveMemoryIntegration(_store(tmp_path))


def _candidate(content: str, *, confidence: float = 0.8) -> LearningCandidate:
    return LearningCandidate(
        content=content,
        category=LearningCategory.PROJECT_CONVENTION,
        action=LearningAction.STORE,
        confidence=confidence,
        reason="project_convention_is_reusable",
        tags=("project_convention", "project_work", "project_focused"),
        metadata={"source": "test"},
    )


def _request(
    text: str,
    *,
    context: ConversationContext | None = None,
    minimum_score: float = 0.35,
) -> CognitiveMemoryRecallRequest:
    intent = CognitiveIntentAnalyzer().analyze(text)
    strategy = ConversationStrategyPlanner().plan(intent, context=context)
    return CognitiveMemoryRecallRequest(
        text=text,
        intent_result=intent,
        strategy=strategy,
        minimum_score=minimum_score,
    )


def test_relevance_decision_reports_selected_and_rejected_counts(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(_candidate("ROBY usa Ruff y pytest por milestone"))
    store.store_candidate(_candidate("Cristina prefiere recetas breves"))

    result = CognitiveMemoryRecall(store).recall(
        _request("sigamos con Ruff pytest y milestones")
    )

    assert result.should_use_memory is True
    assert result.relevance_decision is not None
    assert result.relevance_decision.reason is (
        MemoryRelevanceReason.RELEVANT_MEMORY_FOUND
    )
    assert result.relevance_decision.selected_count == len(result.items)
    assert result.relevance_decision.considered_count >= len(result.items)


def test_recall_rejects_candidates_below_explicit_threshold(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(_candidate("ROBY usa metodología incremental"))

    result = CognitiveMemoryRecall(store).recall(
        _request("sigamos con ROBY", minimum_score=0.95)
    )

    assert result.should_use_memory is False
    assert result.items == ()
    assert result.relevance_decision is not None
    assert result.relevance_decision.reason is (
        MemoryRelevanceReason.BELOW_RELEVANCE_THRESHOLD
    )
    assert result.relevance_decision.minimum_score == 0.95


def test_active_topic_contributes_to_relevant_memory_selection(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(
        _candidate("La memoria conversacional usa recuperación relevante")
    )
    context = ConversationContext(
        active_topic="memoria conversacional",
        turn_index=3,
    )

    result = CognitiveMemoryRecall(store).recall(
        _request("continuemos", context=context)
    )

    assert result.should_use_memory is True
    assert result.relevance_decision is not None
    assert result.relevance_decision.context_considered is True
    assert "memoria" in result.relevance_decision.context_signals
    assert "memoria" in result.items[0].matched_signals


def test_active_entities_are_used_without_parallel_context(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(_candidate("ROBY XI.2 mantiene un núcleo cognitivo"))
    context = ConversationContext(active_entities=("ROBY XI.2",), turn_index=2)
    request = _request("seguimos con eso", context=context)

    result = CognitiveMemoryRecall(store).recall(request)

    assert request.strategy is not None
    assert request.strategy.conversation_context is context
    assert result.should_use_memory is True
    assert result.relevance_decision is not None
    assert "roby" in result.relevance_decision.context_signals


def test_archived_memory_is_never_selected(tmp_path):
    store = _store(tmp_path)
    memory_id = store.store_candidate(
        _candidate("ROBY usa Ruff y pytest por milestone")
    )
    assert store.archive(memory_id) is True

    result = CognitiveMemoryRecall(store).recall(
        _request("ROBY Ruff pytest milestone")
    )

    assert result.should_use_memory is False
    assert result.items == ()
    assert result.relevance_decision is not None
    assert result.relevance_decision.reason is MemoryRelevanceReason.ARCHIVED_MEMORY


def test_empty_query_has_structured_safe_relevance_decision(tmp_path):
    result = CognitiveMemoryRecall(_store(tmp_path)).recall(_request(""))

    assert result.relevance_decision is not None
    assert result.relevance_decision.reason is MemoryRelevanceReason.EMPTY_QUERY
    assert result.relevance_decision.considered_count == 0
    assert result.relevance_decision.selected_count == 0


def test_relevance_serialization_excludes_memory_content(tmp_path):
    store = _store(tmp_path)
    secret_content = "ROBY usa Ruff y pytest por milestone"
    store.store_candidate(_candidate(secret_content))

    result = CognitiveMemoryRecall(store).recall(
        _request("ROBY Ruff pytest milestone")
    )

    assert result.relevance_decision is not None
    serialized = result.relevance_decision.as_dict()
    assert serialized["should_use_memory"] is True
    assert "content" not in serialized
    assert "prompt" not in serialized
    assert secret_content not in repr(serialized)


def test_relevance_threshold_is_clamped_to_safe_range(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(_candidate("ROBY usa Ruff y pytest"))

    result = CognitiveMemoryRecall(store).recall(
        _request("ROBY Ruff pytest", minimum_score=2.0)
    )

    assert result.relevance_decision is not None
    assert result.relevance_decision.minimum_score == 1.0


def test_two_strong_lexical_signals_preserve_historical_recall(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos Ruff y pytest antes del commit")

    result = integration.process_turn("Recordemos Ruff y pytest para M39")

    assert result.recall_result.should_use_memory is True
    assert len(result.recall_result.items) == 1
    assert result.recall_result.items[0].score >= 0.35


def test_single_lexical_signal_remains_below_default_threshold(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos Ruff antes del commit")

    result = integration.process_turn("Recordemos Ruff")

    assert result.recall_result.should_use_memory is False
    assert result.recall_result.relevance_decision is not None
    assert (
        result.recall_result.relevance_decision.reason
        is MemoryRelevanceReason.BELOW_RELEVANCE_THRESHOLD
    )
