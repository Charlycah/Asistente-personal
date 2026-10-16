from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    GoalPlanStepStatus,
    JsonNextStepProposalStore,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 28, 0, 0, tzinfo=timezone.utc)


def _runtime(tmp_path):
    return RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )


def _planned_goal(runtime):
    goal = runtime.create_persistent_goal(
        title="Keep audio stable",
        description="Maintain audio runtime stability.",
        priority=0.8,
        created_at=NOW,
    )
    plan = runtime.create_goal_plan(goal.goal_id, planned_at=NOW)
    selection = runtime.select_next_goal(observed_at=NOW)
    return goal, plan, selection


def test_proposes_first_available_step_without_executing(tmp_path):
    runtime = _runtime(tmp_path)
    _, plan, selection = _planned_goal(runtime)

    proposal = runtime.propose_next_goal_step(selection.selection_id, proposed_at=NOW)

    assert proposal.plan_id == plan.plan_id
    assert proposal.step_id == "assess-current-state"
    assert not proposal.authorization_required
    assert runtime.snapshot.autonomous_cycle_count == 0


def test_proposes_next_dependency_resolved_step(tmp_path):
    runtime = _runtime(tmp_path)
    _, plan, selection = _planned_goal(runtime)
    runtime.update_goal_plan_step(
        plan.plan_id,
        "assess-current-state",
        status=GoalPlanStepStatus.COMPLETED,
        updated_at=NOW,
        evidence=("baseline captured",),
    )

    proposal = runtime.propose_next_goal_step(selection.selection_id, proposed_at=NOW)

    assert proposal.step_id == "collect-evidence"


def test_missing_plan_produces_non_actionable_proposal(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.create_persistent_goal(
        title="Unplanned goal",
        description="No plan yet.",
        priority=0.8,
        created_at=NOW,
    )
    selection = runtime.select_next_goal(observed_at=NOW)

    proposal = runtime.propose_next_goal_step(selection.selection_id, proposed_at=NOW)

    assert proposal.step_id is None
    assert "no active persistent plan" in proposal.summary.lower()


def test_proposal_survives_restart_and_updates_snapshot(tmp_path):
    runtime = _runtime(tmp_path)
    _, _, selection = _planned_goal(runtime)

    proposal = runtime.propose_next_goal_step(selection.selection_id, proposed_at=NOW)
    restored = JsonNextStepProposalStore(
        tmp_path / "next_step_proposals.json"
    ).snapshot()

    assert restored.proposals == (proposal,)
    assert runtime.snapshot.next_step_proposal_count == 1
    assert runtime.snapshot.actionable_next_step_proposal_count == 1


def test_unknown_selection_is_rejected(tmp_path):
    runtime = _runtime(tmp_path)

    with pytest.raises(KeyError, match="unknown goal selection"):
        runtime.propose_next_goal_step("missing", proposed_at=NOW)


def test_corrupt_proposal_file_is_rejected(tmp_path):
    path = tmp_path / "next_step_proposals.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid next step proposal file"):
        JsonNextStepProposalStore(path)
