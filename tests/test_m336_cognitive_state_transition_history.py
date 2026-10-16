import json
from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_state_contract import (
    CognitiveState,
    CognitiveStateManager,
    CognitiveStateTransition,
    CognitiveStateTransitionStore,
    CognitiveStateUpdate,
    JsonCognitiveStateTransitionStore,
)

BASE_TIME = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


class MemoryStateStore:
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


class MemoryTransitionStore:
    def __init__(self) -> None:
        self.items: list[CognitiveStateTransition] = []

    def append(self, transition: CognitiveStateTransition) -> None:
        self.items.append(transition)

    def recent(self, limit: int | None = None):
        if limit is None:
            return tuple(self.items)
        return tuple(self.items[-limit:]) if limit else ()

    def clear(self) -> bool:
        existed = bool(self.items)
        self.items.clear()
        return existed


class FailingStateStore(MemoryStateStore):
    def save(self, state: CognitiveState):
        raise OSError("write failed")


def make_state(index: int = 0) -> CognitiveState:
    return CognitiveState(
        active_objective=f"Objective {index}",
        current_focus=f"Focus {index}",
        confidence=min(index / 10, 1.0),
        last_decision=f"Decision {index}",
        updated_at=BASE_TIME + timedelta(minutes=index),
    )


def make_transition(index: int = 1) -> CognitiveStateTransition:
    return CognitiveStateTransition(
        before=make_state(index - 1),
        after=make_state(index),
        recorded_at=BASE_TIME + timedelta(minutes=index),
        reason="update",
    )


def test_transition_normalizes_reason():
    transition = CognitiveStateTransition(
        before=make_state(0),
        after=make_state(1),
        recorded_at=BASE_TIME,
        reason="  update  ",
    )

    assert transition.reason == "update"


def test_transition_rejects_blank_reason():
    with pytest.raises(ValueError, match="reason"):
        CognitiveStateTransition(
            before=make_state(0),
            after=make_state(1),
            recorded_at=BASE_TIME,
            reason="   ",
        )


def test_transition_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        CognitiveStateTransition(
            before=make_state(0),
            after=make_state(1),
            recorded_at=datetime(2026, 7, 28, 12, 0),
            reason="update",
        )


def test_json_history_starts_empty_without_creating_file(tmp_path):
    path = tmp_path / "history.json"
    store = JsonCognitiveStateTransitionStore(path)

    assert store.recent() == ()
    assert not path.exists()


def test_json_history_round_trip(tmp_path):
    store = JsonCognitiveStateTransitionStore(tmp_path / "history.json")
    transition = make_transition()

    store.append(transition)

    assert store.recent() == (transition,)


def test_json_history_keeps_only_capacity_most_recent_entries(tmp_path):
    store = JsonCognitiveStateTransitionStore(
        tmp_path / "history.json",
        capacity=2,
    )

    store.append(make_transition(1))
    store.append(make_transition(2))
    store.append(make_transition(3))

    assert store.recent() == (make_transition(2), make_transition(3))


def test_recent_limit_returns_latest_entries_in_chronological_order(tmp_path):
    store = JsonCognitiveStateTransitionStore(
        tmp_path / "history.json",
        capacity=5,
    )
    for index in range(1, 4):
        store.append(make_transition(index))

    assert store.recent(limit=2) == (make_transition(2), make_transition(3))
    assert store.recent(limit=0) == ()


def test_history_clear_removes_existing_file(tmp_path):
    store = JsonCognitiveStateTransitionStore(tmp_path / "history.json")
    store.append(make_transition())

    assert store.clear() is True
    assert store.recent() == ()
    assert store.clear() is False


def test_history_uses_atomic_document_shape(tmp_path):
    path = tmp_path / "history.json"
    store = JsonCognitiveStateTransitionStore(path)
    store.append(make_transition())

    document = json.loads(path.read_text(encoding="utf-8"))

    assert document["schema_version"] == 1
    assert len(document["transitions"]) == 1
    assert document["transitions"][0]["reason"] == "update"
    assert list(tmp_path.glob("*.tmp")) == []


def test_history_rejects_invalid_documents(tmp_path):
    path = tmp_path / "history.json"
    path.write_text("{}", encoding="utf-8")
    store = JsonCognitiveStateTransitionStore(path)

    with pytest.raises(ValueError, match="invalid cognitive state history"):
        store.recent()


def test_history_validates_capacity_and_limit(tmp_path):
    with pytest.raises(ValueError, match="at least one"):
        JsonCognitiveStateTransitionStore(tmp_path / "history.json", capacity=0)
    with pytest.raises(TypeError, match="integer"):
        JsonCognitiveStateTransitionStore(tmp_path / "history.json", capacity=True)

    store = JsonCognitiveStateTransitionStore(tmp_path / "history.json")
    with pytest.raises(ValueError, match="negative"):
        store.recent(limit=-1)
    with pytest.raises(TypeError, match="integer or None"):
        store.recent(limit=True)


def test_history_rejects_non_transition_values(tmp_path):
    store = JsonCognitiveStateTransitionStore(tmp_path / "history.json")

    with pytest.raises(TypeError, match="CognitiveStateTransition"):
        store.append(object())


def test_manager_records_successful_update_transition():
    state_store = MemoryStateStore(make_state(0))
    history = MemoryTransitionStore()
    manager = CognitiveStateManager(
        state_store,
        clock=lambda: BASE_TIME + timedelta(minutes=1),
        transition_store=history,
    )

    result = manager.update(CognitiveStateUpdate(current_focus="M336"))

    assert history.items == [
        CognitiveStateTransition(
            before=make_state(0),
            after=result,
            recorded_at=result.updated_at,
            reason="update",
        )
    ]


def test_manager_records_reset_transition():
    initial = make_state(0)
    state_store = MemoryStateStore(initial)
    history = MemoryTransitionStore()
    manager = CognitiveStateManager(
        state_store,
        clock=lambda: BASE_TIME + timedelta(minutes=2),
        transition_store=history,
    )

    result = manager.reset()

    assert history.items[0].before == initial
    assert history.items[0].after == result
    assert history.items[0].reason == "reset"


def test_manager_does_not_record_empty_update():
    state_store = MemoryStateStore(make_state(0))
    history = MemoryTransitionStore()
    manager = CognitiveStateManager(
        state_store,
        clock=lambda: BASE_TIME,
        transition_store=history,
    )

    manager.update(CognitiveStateUpdate())

    assert history.items == []


def test_manager_does_not_record_when_state_save_fails():
    history = MemoryTransitionStore()
    manager = CognitiveStateManager(
        FailingStateStore(make_state(0)),
        clock=lambda: BASE_TIME + timedelta(minutes=1),
        transition_store=history,
    )

    with pytest.raises(OSError, match="write failed"):
        manager.update(CognitiveStateUpdate(current_focus="M336"))

    assert history.items == []


def test_history_store_protocol_is_runtime_checkable(tmp_path):
    store = JsonCognitiveStateTransitionStore(tmp_path / "history.json")

    assert isinstance(store, CognitiveStateTransitionStore)


def test_default_history_path_is_separate_from_snapshot(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    assert JsonCognitiveStateTransitionStore.default_path() == (
        tmp_path / ".roby" / "cognitive_state_history.json"
    )
