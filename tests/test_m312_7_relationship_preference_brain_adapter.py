from __future__ import annotations

from datetime import datetime, timezone

from application.brain import BrainQuery, RelationshipPreferenceBrainAdapter
from core.relationship_memory import (
    RelationshipMemoryEngine,
    RelationshipMemoryKind,
    RelationshipMemoryManager,
    RelationshipMemoryRecord,
)
from domain.brain import BrainMemoryType


def _manager_with(*turns: str) -> RelationshipMemoryManager:
    manager = RelationshipMemoryManager(RelationshipMemoryEngine())
    now = datetime(2026, 7, 23, tzinfo=timezone.utc)
    for turn in turns:
        manager.observe_turn(turn, now=now)
    return manager


def test_adapter_maps_preferences_and_boundaries_as_preferences() -> None:
    adapter = RelationshipPreferenceBrainAdapter(
        relationship_memory=_manager_with(
            "Prefiero que mantengamos cambios pequeños y reversibles.",
            "No quiero que reemplaces algo que ya funciona.",
        ),
        owner="Carlos",
    )

    memories = adapter.recall(BrainQuery())

    assert len(memories) == 2
    assert all(
        memory.normalized_type is BrainMemoryType.PREFERENCE
        for memory in memories
    )
    assert all(memory.metadata["read_only"] is True for memory in memories)
    assert all(memory.memory_id.startswith("relationship:") for memory in memories)


def test_adapter_maps_trust_signal_as_profile_context() -> None:
    now = datetime(2026, 7, 23, tzinfo=timezone.utc)

    class RelationshipSource:
        records = (
            RelationshipMemoryRecord(
                content="la continuidad del proyecto genera confianza",
                kind=RelationshipMemoryKind.TRUST_SIGNAL,
                confidence=0.8,
                reason="historical_trust_signal",
                created_at=now,
            ),
        )

    adapter = RelationshipPreferenceBrainAdapter(
        relationship_memory=RelationshipSource(),
        owner="Carlos",
    )

    memory = adapter.recall(BrainQuery())[0]

    assert memory.normalized_type is BrainMemoryType.PROFILE
    assert memory.source == "relationship_memory"
    assert memory.metadata["relationship_kind"] == "trust_signal"


def test_adapter_does_not_mutate_relationship_history() -> None:
    manager = _manager_with("Prefiero validar siempre con ruff y pytest.")
    before = manager.history
    adapter = RelationshipPreferenceBrainAdapter(
        relationship_memory=manager,
        owner="Carlos",
    )

    adapter.recall(BrainQuery(text="pytest"))

    assert manager.history == before


def test_adapter_rejects_blank_owner() -> None:
    try:
        RelationshipPreferenceBrainAdapter(
            relationship_memory=RelationshipMemoryManager(),
            owner=" ",
        )
    except ValueError as error:
        assert "owner" in str(error)
    else:
        raise AssertionError("blank owner should be rejected")
