from dataclasses import fields

from app import memory_consolidation
from app.memory_consolidation import OfficialMemoryGateway
from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_store import (
    CognitiveMemorySearch,
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.memory_runtime_integration import MemoryRuntimeIntegration


def _governed_candidate(content: str) -> LearningCandidate:
    return LearningCandidate(
        content=content,
        category=LearningCategory.STABLE_KNOWLEDGE,
        action=LearningAction.STORE,
        confidence=0.91,
        reason="governed_human_approved_learning",
        tags=("governed_learning", "human_approved", "stable_knowledge"),
        metadata={"source": "intel_g2_contract_red"},
    )


def test_intel_g2_search_contract_exposes_explicit_created_at_interval() -> None:
    field_names = {field.name for field in fields(CognitiveMemorySearch)}

    assert "created_at_from" in field_names
    assert "created_at_before" in field_names


def test_intel_g2_store_filters_governed_learning_by_half_open_interval(
    tmp_path,
) -> None:
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "memory.sqlite3")
    )
    store.store_candidate(_governed_candidate("conocimiento durable gobernado"))

    results = store.search(
        CognitiveMemorySearch(
            tag="governed_learning",
            created_at_from="2000-01-01T00:00:00+00:00",
            created_at_before="2100-01-01T00:00:00+00:00",
            limit=10,
        )
    )

    assert len(results) == 1
    assert results[0].content == "conocimiento durable gobernado"


def test_intel_g2_runtime_exposes_owner_scoped_temporal_learning_introspection() -> (
    None
):
    assert hasattr(
        MemoryRuntimeIntegration,
        "governed_learning_temporal_introspection",
    )


def test_intel_g2_official_gateway_exposes_temporal_learning_introspection() -> None:
    assert hasattr(
        OfficialMemoryGateway,
        "governed_learning_temporal_introspection",
    )


def test_intel_g2_official_projection_is_frozen_read_only_view() -> None:
    view = getattr(
        memory_consolidation,
        "GovernedLearningTemporalIntrospectionView",
        None,
    )

    assert view is not None
    assert getattr(view, "__dataclass_params__").frozen is True
