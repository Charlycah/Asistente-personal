from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import (
    GoalPlanStepStatus,
    JsonGoalSelectionStore,
    update_goal_plan_step,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 23, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl",
    )


def _goal(runtime, title, priority, review_at=None):
    return runtime.create_persistent_goal(
        title=title,
        description=f"Maintain {title.lower()}.",
        priority=priority,
        created_at=NOW - timedelta(days=1),
        review_at=review_at,
    )


def test_due_review_can_out_rank_higher_priority_goal(tmp_path):
    runtime = _runtime(tmp_path)
    due = _goal(runtime, "Review audio", 0.65, NOW - timedelta(minutes=1))
    _goal(runtime, "Inspect news", 0.8, NOW + timedelta(days=1))

    report = runtime.select_next_goal(observed_at=NOW)

    assert report.selected_goal_id == due.goal_id
    assert report.scores[0].goal_id == due.goal_id
    assert "review_due" in report.scores[0].reasons


def test_latest_blockage_penalizes_but_does_not_make_goal_ineligible(tmp_path):
    runtime = _runtime(tmp_path)
    blocked_goal = _goal(runtime, "Repair audio", 0.9)
    other_goal = _goal(runtime, "Review runtime", 0.75)
    plan = runtime.create_goal_plan(blocked_goal.goal_id, planned_at=NOW)
    blocked_plan = update_goal_plan_step(
        plan,
        "assess-current-state",
        status=GoalPlanStepStatus.BLOCKED,
        updated_at=NOW,
        evidence=("state unavailable",),
        blocked_reason="State unavailable.",
    )
    runtime.goal_plan_store.replace(blocked_plan)
    runtime.detect_goal_blockage(plan.plan_id, observed_at=NOW)

    report = runtime.select_next_goal(observed_at=NOW)
    blocked_score = next(
        item for item in report.scores if item.goal_id == blocked_goal.goal_id
    )

    assert blocked_score.eligible
    assert blocked_score.blockage_adjustment < 0
    assert report.selected_goal_id == other_goal.goal_id


def test_completed_goal_is_never_selected(tmp_path):
    runtime = _runtime(tmp_path)
    completed = _goal(runtime, "Completed objective", 1.0)
    active = _goal(runtime, "Active objective", 0.2)
    runtime.update_persistent_goal(
        completed.goal_id,
        updated_at=NOW,
        status="completed",
    )

    report = runtime.select_next_goal(observed_at=NOW)

    assert report.selected_goal_id == active.goal_id
    score = next(item for item in report.scores if item.goal_id == completed.goal_id)
    assert not score.eligible
    assert score.score == 0.0


def test_selection_survives_restart_and_updates_snapshot(tmp_path):
    runtime = _runtime(tmp_path)
    goal = _goal(runtime, "Persist selection", 0.8)

    report = runtime.select_next_goal(observed_at=NOW)
    restored = JsonGoalSelectionStore(tmp_path / "goal_selections.json").snapshot()

    assert report.selected_goal_id == goal.goal_id
    assert restored.reports == (report,)
    assert runtime.snapshot.goal_selection_report_count == 1
    assert runtime.snapshot.successful_goal_selection_count == 1


def test_selection_does_not_modify_goals_plans_or_authorize_actions(tmp_path):
    runtime = _runtime(tmp_path)
    goal = _goal(runtime, "Keep audio stable", 0.8)
    runtime.create_goal_plan(goal.goal_id, planned_at=NOW)
    goals_before = runtime.persistent_goals().goals
    plans_before = runtime.goal_plans().plans

    report = runtime.select_next_goal(observed_at=NOW)

    assert report.selected_goal_id == goal.goal_id
    assert runtime.persistent_goals().goals == goals_before
    assert runtime.goal_plans().plans == plans_before
    assert runtime.snapshot.autonomous_cycle_count == 0


def test_corrupt_goal_selection_file_is_rejected(tmp_path):
    path = tmp_path / "goal_selections.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid goal selection file"):
        JsonGoalSelectionStore(path)
