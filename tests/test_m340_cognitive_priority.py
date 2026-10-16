from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from core.cognitive_confidence import ConfidenceLevel
from core.cognitive_focus import Focus, FocusType
from core.cognitive_goals import (
    CognitiveGoal,
    GoalCollection,
    GoalPriority,
    GoalStatus,
)
from core.cognitive_priority import (
    DeterministicPriorityPolicy,
    PriorityDecision,
    PriorityManager,
    PriorityPolicy,
    PriorityReason,
    PriorityResolver,
)

BASE = datetime(2026, 7, 27, 12, 0, tzinfo=timezone.utc)


def goal(
    identifier: str,
    *,
    title: str | None = None,
    priority: GoalPriority = GoalPriority.MEDIUM,
    status: GoalStatus = GoalStatus.ACTIVE,
    offset: int = 0,
) -> CognitiveGoal:
    timestamp = BASE + timedelta(minutes=offset)
    return CognitiveGoal(
        identifier=identifier,
        title=title or identifier.title(),
        description=None,
        priority=priority,
        status=status,
        created_at=timestamp,
        updated_at=timestamp,
    )


def focus(identifier: str, *, title: str | None = None) -> Focus:
    return Focus(
        identifier=identifier,
        type=FocusType.TASK,
        title=title or identifier.title(),
        description=None,
        priority=10,
        created_at=BASE,
        updated_at=BASE,
    )


def manager() -> PriorityManager:
    return PriorityManager(DeterministicPriorityPolicy())


def test_public_protocols_are_runtime_checkable() -> None:
    policy = DeterministicPriorityPolicy()
    resolver = manager()
    assert isinstance(policy, PriorityPolicy)
    assert isinstance(resolver, PriorityResolver)


def test_empty_collection_produces_empty_decision() -> None:
    decision = manager().resolve(GoalCollection())
    assert decision.goal is None
    assert decision.reason is None
    assert decision.considered_goal_ids == ()
    assert decision.selected_goal_id is None


def test_only_active_goals_are_considered() -> None:
    goals = GoalCollection(
        (
            goal("paused", priority=GoalPriority.CRITICAL, status=GoalStatus.PAUSED),
            goal("active", priority=GoalPriority.LOW),
        )
    )
    decision = manager().resolve(goals)
    assert decision.selected_goal_id == "active"
    assert decision.considered_goal_ids == ("active",)


def test_higher_goal_priority_wins() -> None:
    goals = GoalCollection(
        (
            goal("low", priority=GoalPriority.LOW),
            goal("high", priority=GoalPriority.HIGH, offset=10),
        )
    )
    decision = manager().resolve(goals)
    assert decision.selected_goal_id == "high"
    assert decision.reason is PriorityReason.GOAL_PRIORITY


def test_focus_breaks_equal_priority_tie_by_identifier() -> None:
    goals = GoalCollection((goal("one"), goal("two", offset=5)))
    decision = manager().resolve(goals, focus=focus("two"))
    assert decision.selected_goal_id == "two"
    assert decision.reason is PriorityReason.FOCUS_ALIGNMENT
    assert decision.focus_aligned is True


def test_focus_breaks_equal_priority_tie_by_title() -> None:
    goals = GoalCollection((goal("one", title="First"), goal("two", title="Second")))
    decision = manager().resolve(goals, focus=focus("other", title="Second"))
    assert decision.selected_goal_id == "two"
    assert decision.reason is PriorityReason.FOCUS_ALIGNMENT


def test_focus_never_overrides_higher_priority() -> None:
    goals = GoalCollection(
        (
            goal("critical", priority=GoalPriority.CRITICAL),
            goal("focused", priority=GoalPriority.HIGH),
        )
    )
    decision = manager().resolve(goals, focus=focus("focused"))
    assert decision.selected_goal_id == "critical"
    assert decision.reason is PriorityReason.GOAL_PRIORITY


def test_oldest_goal_breaks_equal_priority_without_focus() -> None:
    goals = GoalCollection((goal("new", offset=10), goal("old", offset=0)))
    decision = manager().resolve(goals)
    assert decision.selected_goal_id == "old"
    assert decision.reason is PriorityReason.OLDEST_GOAL


def test_identifier_is_final_stable_tiebreaker() -> None:
    goals = GoalCollection((goal("zeta"), goal("alpha")))
    decision = manager().resolve(goals)
    assert decision.selected_goal_id == "alpha"
    assert decision.reason is PriorityReason.STABLE_IDENTIFIER


def test_decision_preserves_supplied_confidence_level() -> None:
    decision = manager().resolve(
        GoalCollection((goal("one"),)),
        confidence_level=ConfidenceLevel.HIGH,
    )
    assert decision.confidence_level is ConfidenceLevel.HIGH


def test_confidence_does_not_change_selection() -> None:
    goals = GoalCollection((goal("one"), goal("two", offset=1)))
    low = manager().resolve(goals, confidence_level=ConfidenceLevel.VERY_LOW)
    high = manager().resolve(goals, confidence_level=ConfidenceLevel.VERY_HIGH)
    assert low.selected_goal_id == high.selected_goal_id == "one"


def test_single_goal_reports_focus_alignment_without_using_it_as_reason() -> None:
    goals = GoalCollection((goal("one"),))
    decision = manager().resolve(goals, focus=focus("one"))
    assert decision.reason is PriorityReason.GOAL_PRIORITY
    assert decision.focus_aligned is True


def test_resolution_has_no_side_effects() -> None:
    goals = GoalCollection((goal("one"), goal("two")))
    before = goals.all_goals()
    manager().resolve(goals, focus=focus("two"))
    assert goals.all_goals() == before


def test_same_inputs_produce_equal_decisions() -> None:
    goals = GoalCollection((goal("one"), goal("two")))
    first = manager().resolve(goals, focus=focus("two"))
    second = manager().resolve(goals, focus=focus("two"))
    assert first == second


def test_policy_rejects_invalid_goal_collection() -> None:
    with pytest.raises(TypeError, match="GoalCollection"):
        DeterministicPriorityPolicy().decide(  # type: ignore[arg-type]
            (),
            focus=None,
            confidence_level=ConfidenceLevel.MEDIUM,
        )


def test_policy_rejects_invalid_focus() -> None:
    with pytest.raises(TypeError, match="Focus or None"):
        manager().resolve(GoalCollection(), focus="task")  # type: ignore[arg-type]


def test_policy_rejects_invalid_confidence_level() -> None:
    with pytest.raises(TypeError, match="ConfidenceLevel"):
        manager().resolve(  # type: ignore[arg-type]
            GoalCollection(),
            confidence_level="high",
        )


def test_manager_rejects_non_policy() -> None:
    with pytest.raises(TypeError, match="PriorityPolicy"):
        PriorityManager(object())  # type: ignore[arg-type]


def test_decision_rejects_goal_without_reason() -> None:
    with pytest.raises(ValueError, match="require a reason"):
        PriorityDecision(
            goal("one"),
            None,
            ConfidenceLevel.MEDIUM,
            ("one",),
        )


def test_empty_decision_rejects_reason() -> None:
    with pytest.raises(ValueError, match="empty decisions"):
        PriorityDecision(
            None,
            PriorityReason.GOAL_PRIORITY,
            ConfidenceLevel.MEDIUM,
            (),
        )


def test_decision_requires_tuple_of_identifiers() -> None:
    with pytest.raises(TypeError, match="must be a tuple"):
        PriorityDecision(  # type: ignore[arg-type]
            None,
            None,
            ConfidenceLevel.MEDIUM,
            ["one"],
        )


def test_considered_order_matches_active_collection_order() -> None:
    goals = GoalCollection(
        (
            goal("third", priority=GoalPriority.LOW),
            goal("first", priority=GoalPriority.HIGH),
            goal("second", priority=GoalPriority.MEDIUM),
        )
    )
    decision = manager().resolve(goals)
    assert decision.considered_goal_ids == ("third", "first", "second")
