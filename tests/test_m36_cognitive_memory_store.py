import sqlite3

import pytest

from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_store import (
    CognitiveMemorySearch,
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)


def make_candidate(
    content: str = "Prefiero metodología incremental con tests",
    category: LearningCategory = LearningCategory.USER_PREFERENCE,
    action: LearningAction = LearningAction.STORE,
) -> LearningCandidate:
    return LearningCandidate(
        content=content,
        category=category,
        action=action,
        confidence=0.82,
        reason="user_preference_is_reusable",
        tags=(category.value, "project_work"),
        metadata={"intent": "project_work", "strategy": "milestone"},
    )


def make_store(tmp_path):
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "roby_brain.sqlite3")
    )


def test_memory_store_initializes_sqlite_schema(tmp_path):
    store = make_store(tmp_path)

    assert store.schema_version() == 1
    assert store.count() == 0


def test_memory_store_persists_store_candidates(tmp_path):
    store = make_store(tmp_path)

    memory_id = store.store_candidate(make_candidate())
    memory = store.get(memory_id)

    assert memory is not None
    assert memory.content == "prefiero metodología incremental con tests"
    assert memory.category == LearningCategory.USER_PREFERENCE
    assert memory.confidence == 0.82
    assert memory.metadata["strategy"] == "milestone"


def test_memory_store_rejects_non_store_candidates(tmp_path):
    store = make_store(tmp_path)
    candidate = make_candidate(action=LearningAction.REVIEW)

    with pytest.raises(ValueError, match="only_store_candidates"):
        store.store_candidate(candidate)

    assert store.count() == 0


def test_memory_store_searches_by_query(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(make_candidate("Prefiero commits cortos para milestones"))
    store.store_candidate(make_candidate("Me gusta documentar arquitectura"))

    results = store.search(CognitiveMemorySearch(query="commits"))

    assert len(results) == 1
    assert results[0].content == "prefiero commits cortos para milestones"


def test_memory_store_filters_by_category(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(make_candidate(category=LearningCategory.USER_PREFERENCE))
    store.store_candidate(
        make_candidate(
            content="architecture 1.0 usa cierres por milestone",
            category=LearningCategory.PROJECT_CONVENTION,
        )
    )

    results = store.search(
        CognitiveMemorySearch(category=LearningCategory.PROJECT_CONVENTION)
    )

    assert len(results) == 1
    assert results[0].category == LearningCategory.PROJECT_CONVENTION


def test_memory_store_filters_by_tag(tmp_path):
    store = make_store(tmp_path)
    store.store_candidate(make_candidate(category=LearningCategory.USER_PREFERENCE))
    store.store_candidate(
        LearningCandidate(
            content="provider router desacopla modelos",
            category=LearningCategory.STABLE_KNOWLEDGE,
            action=LearningAction.STORE,
            confidence=0.7,
            reason="stable_knowledge_is_reusable",
            tags=("stable_knowledge", "technical_question"),
            metadata={"intent": "technical_question"},
        )
    )

    results = store.search(CognitiveMemorySearch(tag="technical_question"))

    assert len(results) == 1
    assert results[0].content == "provider router desacopla modelos"


def test_memory_store_limits_search_results(tmp_path):
    store = make_store(tmp_path)
    for index in range(5):
        store.store_candidate(make_candidate(f"Prefiero aprendizaje número {index}"))

    results = store.search(CognitiveMemorySearch(limit=2))

    assert len(results) == 2
    assert results[0].id > results[1].id


def test_memory_store_tracks_access_count(tmp_path):
    store = make_store(tmp_path)
    memory_id = store.store_candidate(make_candidate())

    first_read = store.get(memory_id)
    second_read = store.get(memory_id)

    assert first_read is not None
    assert second_read is not None
    assert first_read.access_count == 1
    assert second_read.access_count == 2
    assert second_read.last_accessed_at is not None


def test_memory_store_truncates_oversized_content(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(
            db_path=tmp_path / "roby_brain.sqlite3",
            max_content_length=12,
        )
    )

    memory_id = store.store_candidate(make_candidate("Prefiero respuestas extensas"))
    memory = store.get(memory_id)

    assert memory is not None
    assert memory.content == "prefiero res"


def test_memory_store_persists_across_instances(tmp_path):
    db_path = tmp_path / "roby_brain.sqlite3"
    first_store = CognitiveMemoryStore(CognitiveMemoryStoreConfig(db_path=db_path))
    memory_id = first_store.store_candidate(make_candidate())

    second_store = CognitiveMemoryStore(CognitiveMemoryStoreConfig(db_path=db_path))
    memory = second_store.get(memory_id)

    assert memory is not None
    assert second_store.count() == 1


def test_memory_store_uses_regular_sqlite_file(tmp_path):
    db_path = tmp_path / "roby_brain.sqlite3"
    store = CognitiveMemoryStore(CognitiveMemoryStoreConfig(db_path=db_path))
    store.store_candidate(make_candidate())

    with sqlite3.connect(db_path) as connection:
        total = connection.execute(
            "SELECT COUNT(*) FROM cognitive_memories"
        ).fetchone()[0]

    assert total == 1
