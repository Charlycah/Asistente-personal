from pathlib import Path

from core.cognitive_intent import CognitiveIntent
from core.cognitive_memory import LearningCategory
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import (
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.conversation_strategy import ConversationTone


def _store(tmp_path: Path) -> CognitiveMemoryStore:
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )


def test_cognitive_memory_integration_processes_intent_and_strategy(tmp_path):
    integration = CognitiveMemoryIntegration(_store(tmp_path))

    result = integration.process_turn("Seguimos con M38 en ROBY")

    assert result.intent_result.intent == CognitiveIntent.PROJECT_WORK
    assert result.strategy.tone == ConversationTone.PROJECT_FOCUSED
    assert result.learning_result.should_store is True
    assert result.learned_something is True


def test_cognitive_memory_integration_stores_approved_learning(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)

    result = integration.process_turn(
        "En este proyecto usamos Ruff y pytest antes de cerrar milestones"
    )

    assert result.stored_memory_ids
    assert store.count() == 1
    memory = store.get(result.stored_memory_ids[0])
    assert memory is not None
    assert memory.category == LearningCategory.PROJECT_CONVENTION


def test_cognitive_memory_integration_skips_noise_without_storing(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)

    result = integration.process_turn("ok")

    assert result.learning_result.should_store is False
    assert result.stored_memory_ids == ()
    assert result.learned_something is False
    assert store.count() == 0


def test_cognitive_memory_integration_recalls_existing_memory(tmp_path):
    integration = CognitiveMemoryIntegration(_store(tmp_path))
    integration.process_turn(
        "En ROBY mantenemos metodología incremental con Ruff y pytest"
    )

    result = integration.process_turn(
        "Recordemos la metodología incremental para este milestone"
    )

    assert result.recall_result.should_use_memory is True
    assert tuple(item.memory for item in result.recall_result.items)
    assert "metodología incremental" in result.recall_result.items[0].memory.content


def test_cognitive_memory_integration_recalls_before_storing_current_turn(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)

    result = integration.process_turn("Prefiero respuestas breves para commits")

    assert result.recall_result.should_use_memory is False
    assert result.learned_something is True
    assert store.count() == 1


def test_cognitive_memory_integration_can_disable_learning(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)

    result = integration.process_turn(
        "Prefiero respuestas breves para commits",
        enable_learning=False,
    )

    assert result.learning_result.should_store is True
    assert result.stored_memory_ids == ()
    assert store.count() == 0


def test_cognitive_memory_integration_can_disable_recall(tmp_path):
    integration = CognitiveMemoryIntegration(_store(tmp_path))
    integration.process_turn("En ROBY usamos milestones con pytest")

    result = integration.process_turn(
        "pytest en milestones",
        enable_recall=False,
    )

    assert result.recall_result.should_use_memory is False
    assert result.recall_result.reason == "recall_disabled"


def test_cognitive_memory_integration_limits_recall_results(tmp_path):
    integration = CognitiveMemoryIntegration(_store(tmp_path))
    integration.process_turn("En ROBY usamos Ruff para validar milestones")
    integration.process_turn("En ROBY usamos pytest para validar milestones")
    integration.process_turn("En ROBY usamos commits por milestone")

    result = integration.process_turn("validar milestones en ROBY", recall_limit=1)

    assert result.recall_result.should_use_memory is True
    assert len(result.recall_result.items) == 1


def test_cognitive_memory_integration_keeps_result_text(tmp_path):
    integration = CognitiveMemoryIntegration(_store(tmp_path))
    text = "Bowman estaba dibujando y ROBY mostró curiosidad cultural"

    result = integration.process_turn(text)

    assert result.text == text
    assert result.intent_result.intent == CognitiveIntent.CULTURAL_QUESTION
