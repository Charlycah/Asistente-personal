from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    DeterministicGoalPlanner,
    GoalPlanStepStatus,
    JsonGoalPlanStore,
    JsonPersistentGoalStore,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 22, 0, tzinfo=timezone.utc)


def _goal(tmp_path):
    store = JsonPersistentGoalStore(tmp_path / "goals.json")
    return store.create(
        title="Keep audio stable",
        description="Detect and diagnose local audio failures safely.",
        priority=0.9,
        created_at=NOW,
    )


def test_deterministic_goal_planner_builds_auditable_dependency_chain(tmp_path):
    goal = _goal(tmp_path)

    plan = DeterministicGoalPlanner().plan(goal, planned_at=NOW)

    assert plan.goal_id == goal.goal_id
    assert len(plan.steps) == 4
    assert [step.sequence for step in plan.steps] == [1, 2, 3, 4]
    assert plan.steps[0].dependencies == ()
    assert plan.steps[1].dependencies == (plan.steps[0].step_id,)
    assert plan.steps[2].dependencies == (plan.steps[1].step_id,)
    assert plan.steps[3].dependencies == (plan.steps[2].step_id,)
    assert all(step.status is GoalPlanStepStatus.PENDING for step in plan.steps)


def test_goal_plan_store_survives_restart(tmp_path):
    path = tmp_path / "goal_plans.json"
    plan = DeterministicGoalPlanner().plan(_goal(tmp_path), planned_at=NOW)
    JsonGoalPlanStore(path).append(plan)

    restored = JsonGoalPlanStore(path).snapshot()

    assert restored.plans == (plan,)
    assert restored.active_count == 1


def test_runtime_creates_and_exposes_persistent_goal_plan(tmp_path):
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    goal = runtime.create_persistent_goal(
        title="Keep audio stable",
        description="Detect and diagnose local audio failures safely.",
        priority=0.9,
        created_at=NOW,
    )

    plan = runtime.create_goal_plan(goal.goal_id, planned_at=NOW)

    assert runtime.goal_plans().plans == (plan,)
    assert runtime.snapshot.persistent_goal_plan_count == 1
    assert runtime.snapshot.active_goal_plan_count == 1
    assert goal.progress_summary == "Goal created"


def test_runtime_rejects_unknown_goal_for_planning(tmp_path):
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
    )

    with pytest.raises(KeyError, match="unknown persistent goal"):
        runtime.create_goal_plan("missing", planned_at=NOW)


def test_corrupted_goal_plan_file_is_rejected(tmp_path):
    path = tmp_path / "goal_plans.json"
    path.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid goal plan file"):
        JsonGoalPlanStore(path)
