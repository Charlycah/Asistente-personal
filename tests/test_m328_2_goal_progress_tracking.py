from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import (
    DeterministicGoalPlanner,
    GoalPlanStatus,
    GoalPlanStepStatus,
    JsonGoalPlanStore,
    JsonPersistentGoalStore,
    goal_progress,
    update_goal_plan_step,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 23, 0, tzinfo=timezone.utc)


def _plan(tmp_path):
    goals = JsonPersistentGoalStore(tmp_path / "goals.json")
    goal = goals.create(
        title="Keep audio stable",
        description="Track safe progress without executing actions.",
        priority=0.9,
        created_at=NOW,
    )
    return DeterministicGoalPlanner().plan(goal, planned_at=NOW)


def test_progress_uses_completed_steps_and_dependency_availability(tmp_path):
    plan = _plan(tmp_path)

    initial = goal_progress(plan)
    updated = update_goal_plan_step(
        plan,
        "assess-current-state",
        status=GoalPlanStepStatus.COMPLETED,
        updated_at=NOW + timedelta(minutes=1),
        evidence=("runtime baseline captured",),
    )
    progress = goal_progress(updated)

    assert initial.summary == "0 of 4 steps completed"
    assert initial.available_step_ids == ("assess-current-state",)
    assert progress.summary == "1 of 4 steps completed"
    assert progress.available_step_ids == ("collect-evidence",)
    assert updated.steps[0].evidence == ("runtime baseline captured",)


def test_step_cannot_advance_before_dependencies_complete(tmp_path):
    plan = _plan(tmp_path)

    with pytest.raises(ValueError, match="dependencies are not completed"):
        update_goal_plan_step(
            plan,
            "collect-evidence",
            status=GoalPlanStepStatus.COMPLETED,
            updated_at=NOW + timedelta(minutes=1),
        )


def test_blocked_step_requires_reason_and_is_reported(tmp_path):
    plan = _plan(tmp_path)
    updated = update_goal_plan_step(
        plan,
        "assess-current-state",
        status=GoalPlanStepStatus.BLOCKED,
        updated_at=NOW + timedelta(minutes=1),
        evidence=("audio reader unavailable",),
        blocked_reason="Required runtime evidence is unavailable.",
    )

    progress = goal_progress(updated)

    assert progress.blocked_steps == 1
    assert progress.completed_steps == 0
    assert updated.steps[0].blocked_reason == (
        "Required runtime evidence is unavailable."
    )


def test_runtime_persists_progress_and_updates_snapshot(tmp_path):
    path = tmp_path / "journal.jsonl"
    runtime = RuntimeExecutiveIntegration(decision_journal_path=path)
    goal = runtime.create_persistent_goal(
        title="Keep audio stable",
        description="Track safe progress without executing actions.",
        priority=0.9,
        created_at=NOW,
    )
    plan = runtime.create_goal_plan(goal.goal_id, planned_at=NOW)

    runtime.update_goal_plan_step(
        plan.plan_id,
        "assess-current-state",
        status=GoalPlanStepStatus.BLOCKED,
        updated_at=NOW + timedelta(minutes=1),
        blocked_reason="Evidence source unavailable.",
    )
    restarted = RuntimeExecutiveIntegration(decision_journal_path=path)

    assert restarted.goal_progress(plan.plan_id).blocked_steps == 1
    assert restarted.snapshot.blocked_goal_plan_step_count == 1
    assert restarted.snapshot.persistent_goal_plan_count == 1


def test_completing_all_steps_completes_plan_without_execution(tmp_path):
    plan = _plan(tmp_path)
    for index, step in enumerate(plan.steps, start=1):
        plan = update_goal_plan_step(
            plan,
            step.step_id,
            status=GoalPlanStepStatus.COMPLETED,
            updated_at=NOW + timedelta(minutes=index),
            evidence=(f"evidence-{index}",),
        )

    store = JsonGoalPlanStore(tmp_path / "plans.json")
    store.append(plan)
    restored = JsonGoalPlanStore(tmp_path / "plans.json").snapshot()

    assert plan.status is GoalPlanStatus.COMPLETED
    assert goal_progress(plan).completed_steps == 4
    assert restored.completed_count == 1
    assert restored.active_count == 0
