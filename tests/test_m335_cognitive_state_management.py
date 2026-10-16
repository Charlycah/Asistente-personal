from datetime import datetime, timezone

import pytest

from core.cognitive_state_contract import (
    CognitiveState,
    CognitiveStateManager,
    CognitiveStateStore,
    CognitiveStateUpdate,
    CognitiveStateUpdater,
)

INITIAL_TIME = datetime(2026, 7, 28, 10, 0, tzinfo=timezone.utc)
UPDATED_TIME = datetime(2026, 7, 28, 10, 5, tzinfo=timezone.utc)


class MemoryStore:
    def __init__(self, state: CognitiveState | None = None) -> None:
        self.state = state
        self.saved: list[CognitiveState] = []

    def load(self) -> CognitiveState | None:
        return self.state

    def save(self, state: CognitiveState):
        self.state = state
        self.saved.append(state)
        return None

    def delete(self) -> bool:
        existed = self.state is not None
        self.state = None
        return existed


def make_state() -> CognitiveState:
    return CognitiveState(
        active_objective="Help the user",
        current_focus="Review M334",
        confidence=0.6,
        last_decision="Add controlled updates next",
        updated_at=INITIAL_TIME,
    )


def test_snapshot_returns_stored_state_without_writing():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    assert manager.snapshot() == make_state()
    assert store.saved == []


def test_snapshot_returns_empty_state_when_storage_is_absent():
    store = MemoryStore()
    manager = CognitiveStateManager(store, clock=lambda: INITIAL_TIME)

    assert manager.snapshot() == CognitiveState.empty(updated_at=INITIAL_TIME)
    assert store.saved == []


def test_update_changes_only_explicit_fields_and_persists():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    result = manager.update(
        CognitiveStateUpdate(
            current_focus="Implement M335",
            confidence=0.8,
        )
    )

    assert result == CognitiveState(
        active_objective="Help the user",
        current_focus="Implement M335",
        confidence=0.8,
        last_decision="Add controlled updates next",
        updated_at=UPDATED_TIME,
    )
    assert store.saved == [result]


def test_update_can_clear_optional_fields_explicitly():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    result = manager.update(
        CognitiveStateUpdate(
            active_objective=None,
            current_focus=None,
            last_decision=None,
        )
    )

    assert result.active_objective is None
    assert result.current_focus is None
    assert result.last_decision is None
    assert result.confidence == 0.6


def test_empty_update_is_a_no_op_without_persistence():
    state = make_state()
    store = MemoryStore(state)
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    result = manager.update(CognitiveStateUpdate())

    assert result is state
    assert store.saved == []


def test_update_from_absent_storage_uses_empty_baseline():
    store = MemoryStore()
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    result = manager.update(CognitiveStateUpdate(active_objective="Assist"))

    assert result == CognitiveState(
        active_objective="Assist",
        current_focus=None,
        confidence=0.0,
        last_decision=None,
        updated_at=UPDATED_TIME,
    )
    assert store.saved == [result]


def test_reset_persists_an_empty_state():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    result = manager.reset()

    assert result == CognitiveState.empty(updated_at=UPDATED_TIME)
    assert store.saved == [result]


def test_contract_validation_rejects_invalid_updates_without_writing():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    with pytest.raises(ValueError, match="confidence"):
        manager.update(CognitiveStateUpdate(confidence=1.5))

    assert store.saved == []


def test_update_rejects_values_outside_the_update_contract():
    store = MemoryStore(make_state())
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    with pytest.raises(TypeError, match="CognitiveStateUpdate"):
        manager.update(object())


def test_clock_must_return_a_datetime():
    manager = CognitiveStateManager(MemoryStore(), clock=lambda: "now")

    with pytest.raises(TypeError, match="datetime"):
        manager.snapshot()


def test_clock_must_return_timezone_aware_values():
    naive = datetime(2026, 7, 28, 10, 0)
    manager = CognitiveStateManager(MemoryStore(), clock=lambda: naive)

    with pytest.raises(ValueError, match="timezone-aware"):
        manager.snapshot()


def test_update_and_store_protocols_are_runtime_checkable():
    store = MemoryStore()
    manager = CognitiveStateManager(store, clock=lambda: UPDATED_TIME)

    assert isinstance(store, CognitiveStateStore)
    assert isinstance(manager, CognitiveStateUpdater)
