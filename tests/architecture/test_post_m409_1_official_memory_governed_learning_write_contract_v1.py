from __future__ import annotations

from pathlib import Path

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.memory_consolidation import OfficialMemoryGateway
from core.cognitive_memory import LearningCategory
from core.memory import MemoryItem
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

from .test_post_m409_1_governed_memory_write_adapter_foundation_v1 import (
    _proposal,
)


def _runtime(tmp_path: Path) -> MemoryRuntimeIntegration:
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=tmp_path / "memory")
    )


def test_v1_governed_learning_write_preserves_preference_semantics(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    request = GovernedMemoryWriteAdapterFoundation().adapt(_proposal())

    result = gateway.remember_governed_learning(request)

    assert result.stored_count == 1
    records = runtime.private_store("Carlos").search(
        __import__("core.cognitive_memory_store", fromlist=[
            "CognitiveMemorySearch"
        ]).CognitiveMemorySearch(limit=10)
    )
    assert len(records) == 1
    record = records[0]
    assert record.category is LearningCategory.USER_PREFERENCE
    assert record.confidence == 0.82
    assert record.reason == "governed_human_approved_learning"
    assert record.tags == (
        "governed_learning",
        "human_approved",
        "preference",
    )
    assert record.metadata["approval_scope"] == "project"
    assert record.metadata["learning_candidate_id"] == "learning-candidate-1"
    assert record.metadata["write_request_id"] == request.request_id


def test_v1_same_request_is_idempotent_and_returns_existing_memory(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    request = GovernedMemoryWriteAdapterFoundation().adapt(_proposal())

    first = gateway.remember_governed_learning(request)
    second = gateway.remember_governed_learning(request)

    assert first.stored_count == 1
    assert second.stored_count == 0
    assert first.stored_memory_ids == second.stored_memory_ids
    assert runtime.count(owner="Carlos") == 1
    assert second.rationale == ("governed_learning_already_stored",)


def test_v1_different_idempotency_keys_create_distinct_memories(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    foundation = GovernedMemoryWriteAdapterFoundation()
    first = foundation.adapt(_proposal())
    second = foundation.adapt(
        _proposal(
            proposal_id="approved-learning-memory-proposal-fedcba0987654321",
            source_fingerprint="d" * 64,
        )
    )

    gateway.remember_governed_learning(first)
    gateway.remember_governed_learning(second)

    assert runtime.count(owner="Carlos") == 2


def test_v1_legacy_remember_contract_is_unchanged(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")

    gateway.remember(MemoryItem("Recordar este dato legacy"))

    records = runtime.search(owner="Carlos", query="dato legacy", limit=5)
    assert len(records) == 1
    record = records[0]
    assert record.category is LearningCategory.STABLE_KNOWLEDGE
    assert record.confidence == 1.0
    assert record.reason == "explicit_user_memory_request"
    assert record.tags == ("explicit", "personal")


def test_v1_idempotency_table_does_not_change_legacy_schema_version(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    store = runtime.private_store("Carlos")
    assert store.schema_version() == 1


def test_v1_writer_rejects_obsolete_or_uncertified_request_contract(tmp_path) -> None:
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    request = GovernedMemoryWriteAdapterFoundation().adapt(_proposal())
    object.__setattr__(request, "semantic_mapping_supported", False)

    try:
        gateway.remember_governed_learning(request)
    except ValueError as exc:
        assert "semantic mapping" in str(exc)
    else:
        raise AssertionError("uncertified request must fail closed")
