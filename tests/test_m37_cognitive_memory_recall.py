from core.cognitive_intent import CognitiveIntent, CognitiveIntentResult
from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
)
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.conversation_strategy import ConversationStrategyPlanner


def make_store(tmp_path):
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "roby_brain.sqlite3")
    )


def make_candidate(
    content: str,
    category: LearningCategory,
    tags: tuple[str, ...],
    confidence: float = 0.8,
) -> LearningCandidate:
    return LearningCandidate(
        content=content,
        category=category,
        action=LearningAction.STORE,
        confidence=confidence,
        reason=f"{category.value}_is_reusable",
        tags=tags,
        metadata={"source": "test"},
    )


def intent_result(
    intent: CognitiveIntent = CognitiveIntent.PROJECT_WORK,
    text: str = "ROBY usa milestones con tests y ruff",
) -> CognitiveIntentResult:
    return CognitiveIntentResult(
        intent=intent,
        confidence=0.8,
        normalized_text=text.lower(),
        signals=(intent.value,),
    )


def request_for(
    text: str,
    intent: CognitiveIntent = CognitiveIntent.PROJECT_WORK,
) -> CognitiveMemoryRecallRequest:
    result = intent_result(intent=intent, text=text)
    strategy = ConversationStrategyPlanner().plan(result)
    return CognitiveMemoryRecallRequest(
        text=text,
        intent_result=result,
        strategy=strategy,
    )


def test_recall_returns_no_memory_for_empty_text(tmp_path):
    recall = CognitiveMemoryRecall(make_store(tmp_path))

    result = recall.recall(request_for(""))

    assert result.should_use_memory is False
    assert result.items == ()
    assert result.reason == "empty_text_has_no_recall_signal"


def test_recall_finds_memory_by_shared_text_signal(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "Architecture 1.0 usa milestones cerrados con Ruff y pytest",
            LearningCategory.PROJECT_CONVENTION,
            ("project_convention", "project_work"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(request_for("sigamos con milestones y pytest en ROBY"))

    assert result.should_use_memory is True
    assert result.items[0].memory.category == LearningCategory.PROJECT_CONVENTION
    assert "milestones" in result.items[0].matched_signals


def test_recall_finds_memory_by_intent_tag_even_without_shared_text(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "Provider router desacopla modelos concretos",
            LearningCategory.STABLE_KNOWLEDGE,
            ("stable_knowledge", "technical_question"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(
        request_for(
            "explicame una decisión de arquitectura",
            CognitiveIntent.TECHNICAL_QUESTION,
        )
    )

    assert result.should_use_memory is True
    assert (
        result.items[0].memory.content == "provider router desacopla modelos concretos"
    )
    assert "technical_question" in result.items[0].matched_signals


def test_recall_prioritizes_higher_scored_memory(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "ROBY usa metodología incremental",
            LearningCategory.PROJECT_CONVENTION,
            ("project_convention", "project_work"),
            confidence=0.7,
        )
    )
    store.store_candidate(
        make_candidate(
            "ROBY usa metodología incremental con Ruff pytest y commits por milestone",
            LearningCategory.PROJECT_CONVENTION,
            ("project_convention", "project_work", "project_focused"),
            confidence=0.9,
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(request_for("ROBY Ruff pytest milestone"))

    assert result.items[0].memory.content.endswith("commits por milestone")
    assert result.items[0].score > result.items[1].score


def test_recall_respects_limit(tmp_path):
    store = make_store(tmp_path)
    for index in range(5):
        store.store_candidate(
            make_candidate(
                f"ROBY aprendizaje reusable número {index}",
                LearningCategory.PROJECT_CONVENTION,
                ("project_convention", "project_work"),
            )
        )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(
        CognitiveMemoryRecallRequest(
            text="ROBY aprendizaje reusable",
            intent_result=intent_result(),
            limit=2,
        )
    )

    assert len(result.items) == 2


def test_recall_tracks_memory_access_through_store(tmp_path):
    store = make_store(tmp_path)
    memory_id = store.store_candidate(
        make_candidate(
            "ROBY recuerda preferencias de respuesta",
            LearningCategory.USER_PREFERENCE,
            ("user_preference", "project_work"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(request_for("ROBY preferencias de respuesta"))
    memory = store.get(memory_id)

    assert result.should_use_memory is True
    assert memory is not None
    assert memory.access_count == 2
    assert memory.last_accessed_at is not None


def test_recall_returns_safe_result_when_nothing_matches(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "Provider router desacopla modelos",
            LearningCategory.STABLE_KNOWLEDGE,
            ("stable_knowledge", "technical_question"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(request_for("hola buen día", CognitiveIntent.CASUAL_CHAT))

    assert result.should_use_memory is False
    assert result.items == ()
    assert result.reason == "no_relevant_memory_found"


def test_recall_uses_strategy_tone_as_signal(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "En ROBY los milestones se cierran solo con criterios verificables",
            LearningCategory.PROJECT_CONVENTION,
            ("project_convention", "project_work", "project_focused"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(request_for("sigamos con ROBY"))

    assert result.should_use_memory is True
    assert "project_focused" in result.items[0].matched_signals


def test_recall_items_are_the_canonical_memory_projection(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(
        make_candidate(
            "roby conserva conocimiento estable",
            LearningCategory.STABLE_KNOWLEDGE,
            ("stable_knowledge", "technical_question"),
        )
    )
    recall = CognitiveMemoryRecall(store)

    result = recall.recall(
        request_for("conocimiento técnico estable", CognitiveIntent.TECHNICAL_QUESTION)
    )

    assert tuple(item.memory.content for item in result.items) == (
        "roby conserva conocimiento estable",
    )
