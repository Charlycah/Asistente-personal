from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    DeterministicGoalBlockageDetector,
    ExperienceMemorySnapshot,
    ExperiencePattern,
    GoalBlockerKind,
    GoalPlanStepStatus,
    JsonGoalBlockageStore,
    update_goal_plan_step,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 27, 22, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl",
    )


def _plan(runtime):
    goal = runtime.create_persistent_goal(
        title="Stabilize audio recognition",
        description="Keep local speech recognition reliable.",
        priority=0.8,
        created_at=NOW,
    )
    return runtime.create_goal_plan(goal.goal_id, planned_at=NOW)


def test_detects_explicit_and_dependent_blockers(tmp_path):
    runtime = _runtime(tmp_path)
    plan = _plan(runtime)
    blocked = update_goal_plan_step(
        plan,
        "assess-current-state",
        status=GoalPlanStepStatus.BLOCKED,
        updated_at=NOW,
        evidence=("runtime evidence unavailable",),
        blocked_reason="Runtime evidence is unavailable.",
    )
    runtime.goal_plan_store.replace(blocked)

    report = runtime.detect_goal_blockage(blocked.plan_id, observed_at=NOW)

    kinds = {blocker.kind for blocker in report.blockers}
    assert report.is_blocked
    assert GoalBlockerKind.EXPLICIT_STEP_BLOCK in kinds
    assert GoalBlockerKind.BLOCKED_DEPENDENCY in kinds


def test_detects_missing_capability_and_authorization(tmp_path):
    runtime = _runtime(tmp_path)
    plan = _plan(runtime)
    target = plan.steps[2]
    modified = replace(
        plan,
        steps=plan.steps[:2]
        + (
            replace(
                target,
                required_capability="repair_audio_runtime",
                risk="medium",
            ),
        )
        + plan.steps[3:],
    )
    report = DeterministicGoalBlockageDetector().detect(
        modified,
        experience=ExperienceMemorySnapshot(patterns=()),
        observed_at=NOW,
    )

    kinds = {blocker.kind for blocker in report.blockers}
    assert GoalBlockerKind.MISSING_CAPABILITY in kinds
    assert GoalBlockerKind.AUTHORIZATION_REQUIRED in kinds


def test_repeated_failures_are_detected(tmp_path):
    runtime = _runtime(tmp_path)
    plan = _plan(runtime)
    target = plan.steps[2]
    modified = replace(
        plan,
        steps=plan.steps[:2]
        + (replace(target, required_capability="diagnose_audio_runtime"),)
        + plan.steps[3:],
    )
    experience = ExperienceMemorySnapshot(
        patterns=(
            ExperiencePattern(
                situation_kind="audio_runtime_error",
                action="diagnose_audio_runtime",
                occurrences=4,
                succeeded=1,
                degraded=0,
                failed=3,
                unknown=0,
                last_observed_at=NOW,
                last_summary="Audio diagnosis failed.",
            ),
        )
    )

    report = DeterministicGoalBlockageDetector().detect(
        modified,
        experience=experience,
        observed_at=NOW,
        available_capabilities=frozenset({"diagnose_audio_runtime"}),
    )

    assert any(
        blocker.kind is GoalBlockerKind.REPEATED_FAILURE
        for blocker in report.blockers
    )


def test_goal_blockage_reports_survive_restart(tmp_path):
    runtime = _runtime(tmp_path)
    plan = _plan(runtime)
    report = runtime.detect_goal_blockage(plan.plan_id, observed_at=NOW)

    restored = JsonGoalBlockageStore(tmp_path / "goal_blockages.json").snapshot()

    assert restored.reports == (report,)
    assert runtime.snapshot.goal_blockage_report_count == 1
    assert runtime.snapshot.blocked_goal_report_count == 0


def test_detection_does_not_modify_goal_or_plan(tmp_path):
    runtime = _runtime(tmp_path)
    plan = _plan(runtime)
    goals_before = runtime.persistent_goals().goals
    plans_before = runtime.goal_plans().plans

    report = runtime.detect_goal_blockage(plan.plan_id, observed_at=NOW)

    assert not report.is_blocked
    assert runtime.persistent_goals().goals == goals_before
    assert runtime.goal_plans().plans == plans_before


def test_corrupt_goal_blockage_file_is_rejected(tmp_path):
    path = tmp_path / "goal_blockages.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid goal blockage report file"):
        JsonGoalBlockageStore(path)
