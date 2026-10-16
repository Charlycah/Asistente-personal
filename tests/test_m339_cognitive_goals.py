from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_goals import (
    CognitiveGoal,
    GoalCollection,
    GoalManager,
    GoalPriority,
    GoalStatus,
    PriorityGoalResolver,
)
from core.cognitive_state_contract import CognitiveState, CognitiveStateUpdate

BASE_TIME = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)


class RecordingUpdater:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.updates: list[CognitiveStateUpdate] = []
        self.state = CognitiveState.empty(updated_at=BASE_TIME)

    def snapshot(self) -> CognitiveState:
        return self.state

    def update(self, changes: CognitiveStateUpdate) -> CognitiveState:
        if self.fail:
            raise RuntimeError("write failed")
        self.updates.append(changes)
        active = self.state.active_objective
        if changes.active_objective is not None:
            active = changes.active_objective
        else:
            active = None
        self.state = CognitiveState(
            active_objective=active,
            current_focus=self.state.current_focus,
            confidence=self.state.confidence,
            last_decision=self.state.last_decision,
            updated_at=BASE_TIME,
        )
        return self.state

    def reset(self) -> CognitiveState:
        self.state = CognitiveState.empty(updated_at=BASE_TIME)
        return self.state


def goal(
    identifier: str = "goal-1",
    *,
    title: str = "Resolver tarea",
    priority: GoalPriority = GoalPriority.MEDIUM,
    status: GoalStatus = GoalStatus.ACTIVE,
    created_at: datetime = BASE_TIME,
) -> CognitiveGoal:
    return CognitiveGoal(
        identifier=identifier,
        title=title,
        description="Objetivo explícito",
        priority=priority,
        status=status,
        created_at=created_at,
        updated_at=created_at,
    )


def manager(updater: RecordingUpdater | None = None) -> GoalManager:
    return GoalManager(
        updater or RecordingUpdater(),
        PriorityGoalResolver(),
        clock=lambda: BASE_TIME + timedelta(minutes=1),
    )


def test_goal_normalizes_text_and_is_frozen() -> None:
    value = CognitiveGoal(
        identifier=" goal-1 ",
        title=" Resolver ",
        description=" Detalle ",
        priority=GoalPriority.HIGH,
        status=GoalStatus.ACTIVE,
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
    )
    assert value.identifier == "goal-1"
    assert value.title == "Resolver"
    assert value.description == "Detalle"
    with pytest.raises(FrozenInstanceError):
        value.title = "Otro"  # type: ignore[misc]


@pytest.mark.parametrize("field", ["identifier", "title"])
def test_goal_rejects_blank_required_text(field: str) -> None:
    values = {
        "identifier": "goal-1",
        "title": "Resolver",
    }
    values[field] = "  "
    with pytest.raises(ValueError):
        goal(values["identifier"], title=values["title"])


def test_goal_rejects_blank_description() -> None:
    with pytest.raises(ValueError):
        CognitiveGoal(
            identifier="goal-1",
            title="Resolver",
            description=" ",
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.ACTIVE,
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )


def test_goal_rejects_invalid_priority_and_status() -> None:
    with pytest.raises(TypeError):
        CognitiveGoal(
            identifier="goal-1",
            title="Resolver",
            description=None,
            priority=20,  # type: ignore[arg-type]
            status=GoalStatus.ACTIVE,
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )
    with pytest.raises(TypeError):
        CognitiveGoal(
            identifier="goal-1",
            title="Resolver",
            description=None,
            priority=GoalPriority.MEDIUM,
            status="active",  # type: ignore[arg-type]
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )


def test_goal_rejects_naive_or_reversed_timestamps() -> None:
    with pytest.raises(ValueError):
        goal(created_at=datetime(2026, 7, 27, 12, 0))
    with pytest.raises(ValueError):
        CognitiveGoal(
            identifier="goal-1",
            title="Resolver",
            description=None,
            priority=GoalPriority.MEDIUM,
            status=GoalStatus.ACTIVE,
            created_at=BASE_TIME,
            updated_at=BASE_TIME - timedelta(seconds=1),
        )


def test_goal_with_status_returns_new_value() -> None:
    original = goal()
    updated = original.with_status(
        GoalStatus.PAUSED,
        updated_at=BASE_TIME + timedelta(minutes=1),
    )
    assert original.status is GoalStatus.ACTIVE
    assert updated.status is GoalStatus.PAUSED
    assert updated.identifier == original.identifier


def test_collection_rejects_duplicate_identifiers() -> None:
    with pytest.raises(ValueError):
        GoalCollection((goal(), goal()))


def test_collection_add_get_remove_and_replace() -> None:
    original = goal()
    collection = GoalCollection().add(original)
    assert collection.get(" goal-1 ") == original
    paused = original.with_status(
        GoalStatus.PAUSED,
        updated_at=BASE_TIME + timedelta(minutes=1),
    )
    collection = collection.replace(paused)
    assert collection.get("goal-1") == paused
    assert collection.remove("goal-1").all_goals() == ()


def test_collection_rejects_duplicate_add_and_missing_changes() -> None:
    collection = GoalCollection().add(goal())
    with pytest.raises(ValueError):
        collection.add(goal())
    with pytest.raises(KeyError):
        collection.remove("missing")
    with pytest.raises(KeyError):
        collection.replace(goal("missing"))


def test_active_goals_excludes_non_active_statuses() -> None:
    collection = GoalCollection(
        (
            goal("active"),
            goal("paused", status=GoalStatus.PAUSED),
            goal("done", status=GoalStatus.COMPLETED),
            goal("cancelled", status=GoalStatus.CANCELLED),
        )
    )
    assert [item.identifier for item in collection.active_goals()] == ["active"]


def test_resolver_returns_none_without_active_goals() -> None:
    resolver = PriorityGoalResolver()
    assert resolver.resolve(GoalCollection()) is None
    assert resolver.resolve(
        GoalCollection((goal(status=GoalStatus.PAUSED),))
    ) is None


def test_resolver_selects_highest_priority() -> None:
    low = goal("low", priority=GoalPriority.LOW)
    critical = goal("critical", priority=GoalPriority.CRITICAL)
    selected = PriorityGoalResolver().resolve(GoalCollection((low, critical)))
    assert selected == critical


def test_resolver_uses_oldest_goal_for_priority_tie() -> None:
    older = goal("older", created_at=BASE_TIME)
    newer = goal("newer", created_at=BASE_TIME + timedelta(seconds=1))
    selected = PriorityGoalResolver().resolve(GoalCollection((newer, older)))
    assert selected == older


def test_manager_adds_first_goal_and_mirrors_title() -> None:
    updater = RecordingUpdater()
    value = goal()
    service = manager(updater)
    assert service.add(value) == value
    assert service.primary_goal() == value
    assert updater.updates[-1].active_objective == value.title


def test_manager_lower_priority_add_does_not_write_state() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    service.add(goal("high", title="Principal", priority=GoalPriority.HIGH))
    service.add(goal("low", title="Secundario", priority=GoalPriority.LOW))
    assert len(updater.updates) == 1
    assert service.primary_goal().identifier == "high"  # type: ignore[union-attr]


def test_manager_higher_priority_add_replaces_primary() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    service.add(goal("low", title="Bajo", priority=GoalPriority.LOW))
    service.add(goal("high", title="Alto", priority=GoalPriority.HIGH))
    assert [update.active_objective for update in updater.updates] == ["Bajo", "Alto"]


def test_manager_pause_selects_next_active_goal() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    service.add(goal("high", title="Alto", priority=GoalPriority.HIGH))
    service.add(goal("low", title="Bajo", priority=GoalPriority.LOW))
    paused = service.pause("high")
    assert paused.status is GoalStatus.PAUSED
    assert service.primary_goal().identifier == "low"  # type: ignore[union-attr]
    assert updater.updates[-1].active_objective == "Bajo"


def test_manager_resume_can_restore_primary_goal() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    service.add(goal("high", title="Alto", priority=GoalPriority.HIGH))
    service.pause("high")
    service.add(goal("low", title="Bajo", priority=GoalPriority.LOW))
    resumed = service.resume("high")
    assert resumed.status is GoalStatus.ACTIVE
    assert service.primary_goal().identifier == "high"  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("method", "expected"),
    [("complete", GoalStatus.COMPLETED), ("cancel", GoalStatus.CANCELLED)],
)
def test_manager_terminal_status_removes_goal_from_selection(
    method: str,
    expected: GoalStatus,
) -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    service.add(goal())
    updated = getattr(service, method)("goal-1")
    assert updated.status is expected
    assert service.primary_goal() is None
    assert updater.updates[-1].active_objective is None


def test_manager_remove_returns_removed_goal_and_clears_primary() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    value = goal()
    service.add(value)
    assert service.remove("goal-1") == value
    assert service.all_goals() == ()
    assert updater.updates[-1].active_objective is None


def test_manager_missing_identifier_raises_key_error() -> None:
    service = manager()
    with pytest.raises(KeyError):
        service.pause("missing")


def test_manager_same_status_is_a_no_op() -> None:
    updater = RecordingUpdater()
    service = manager(updater)
    value = goal()
    service.add(value)
    assert service.resume("goal-1") == value
    assert len(updater.updates) == 1


def test_manager_does_not_commit_collection_when_state_write_fails() -> None:
    updater = RecordingUpdater(fail=True)
    service = manager(updater)
    with pytest.raises(RuntimeError, match="write failed"):
        service.add(goal())
    assert service.all_goals() == ()


def test_manager_clock_must_return_aware_datetime() -> None:
    updater = RecordingUpdater()
    service = GoalManager(
        updater,
        PriorityGoalResolver(),
        clock=lambda: datetime(2026, 7, 27, 12, 0),
    )
    service.add(goal())
    with pytest.raises(ValueError):
        service.pause("goal-1")
