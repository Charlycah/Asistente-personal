from datetime import datetime, timezone

import pytest

from core.adaptive_cognition import (
    ExecutiveMilestone,
    ExecutiveObjective,
    ExecutivePlan,
    ExecutivePlanHorizon,
    ExecutivePlanningEngine,
    ExecutivePlanningManager,
    ExecutivePlanningPolicy,
    ExecutivePlanStatus,
    ExecutivePriority,
    InMemoryExecutivePlanRepository,
)

NOW = datetime(2026, 7, 10, 18, 0, tzinfo=timezone.utc)


def objective(
    title: str = "Stabilize adaptive cognition",
    priority: ExecutivePriority = ExecutivePriority.HIGH,
) -> ExecutiveObjective:
    return ExecutiveObjective(
        title=title,
        success_criteria=("All milestones are governed",),
        priority=priority,
    )


def plan_parts() -> tuple[
    tuple[ExecutiveObjective, ...], tuple[ExecutiveMilestone, ...]
]:
    first = objective()
    second = objective("Complete integration", ExecutivePriority.MEDIUM)
    milestone_one = ExecutiveMilestone(
        title="Establish planning baseline",
        objective_ids=(first.objective_id,),
        sequence=1,
    )
    milestone_two = ExecutiveMilestone(
        title="Integrate planning",
        objective_ids=(second.objective_id,),
        sequence=2,
        dependencies=(milestone_one.milestone_id,),
    )
    return (first, second), (milestone_one, milestone_two)


def make_plan(
    *,
    horizon: ExecutivePlanHorizon = ExecutivePlanHorizon.MID,
    status: ExecutivePlanStatus = ExecutivePlanStatus.DRAFT,
    revision: int = 1,
) -> ExecutivePlan:
    objectives, milestones = plan_parts()
    return ExecutivePlan(
        owner="carlos",
        title="ROBY Phase IX",
        purpose="Complete adaptive cognition safely",
        horizon=horizon,
        objectives=objectives,
        milestones=milestones,
        status=status,
        revision=revision,
        domains=("roby",),
        constraints=("No direct execution",),
        created_at=NOW,
    )


def test_objective_has_stable_hash_identity() -> None:
    assert objective().objective_id == objective().objective_id


def test_objective_requires_success_criteria() -> None:
    with pytest.raises(ValueError):
        ExecutiveObjective(title="Goal", success_criteria=())


def test_objective_rejects_duplicate_criteria() -> None:
    with pytest.raises(ValueError):
        ExecutiveObjective(title="Goal", success_criteria=("a", "a"))


def test_milestone_requires_positive_sequence() -> None:
    item = objective()
    with pytest.raises(ValueError):
        ExecutiveMilestone("Milestone", (item.objective_id,), 0)


def test_plan_requires_owner_title_and_purpose() -> None:
    objectives, milestones = plan_parts()
    with pytest.raises(ValueError):
        ExecutivePlan("", "Title", "Purpose", "mid", objectives, milestones)


def test_plan_rejects_naive_timestamp() -> None:
    objectives, milestones = plan_parts()
    with pytest.raises(ValueError):
        ExecutivePlan(
            "owner",
            "Title",
            "Purpose",
            "mid",
            objectives,
            milestones,
            created_at=datetime(2026, 1, 1),
        )


def test_plan_rejects_non_contiguous_milestones() -> None:
    item = objective()
    milestone = ExecutiveMilestone("Later", (item.objective_id,), 2)
    with pytest.raises(ValueError):
        ExecutivePlan("owner", "Title", "Purpose", "mid", (item,), (milestone,))


def test_plan_rejects_unknown_objective_reference() -> None:
    item = objective()
    milestone = ExecutiveMilestone("Bad", ("unknown",), 1)
    with pytest.raises(ValueError):
        ExecutivePlan("owner", "Title", "Purpose", "mid", (item,), (milestone,))


def test_plan_rejects_unknown_dependency() -> None:
    item = objective()
    milestone = ExecutiveMilestone(
        "Bad", (item.objective_id,), 1, dependencies=("unknown",)
    )
    with pytest.raises(ValueError):
        ExecutivePlan("owner", "Title", "Purpose", "mid", (item,), (milestone,))


def test_long_horizon_requires_review() -> None:
    objectives, milestones = plan_parts()
    plan = ExecutivePlanningEngine().create_plan(
        owner="owner",
        title="Long plan",
        purpose="Plan long term",
        horizon="long",
        objectives=objectives,
        milestones=milestones,
        now=NOW,
    )
    assert plan.status is ExecutivePlanStatus.REVIEW_REQUIRED
    assert plan.requires_review is True


def test_critical_objective_requires_review() -> None:
    item = objective(priority=ExecutivePriority.CRITICAL)
    milestone = ExecutiveMilestone("Critical", (item.objective_id,), 1)
    plan = ExecutivePlanningEngine().create_plan(
        owner="owner",
        title="Critical plan",
        purpose="Protect system",
        horizon="near",
        objectives=(item,),
        milestones=(milestone,),
        now=NOW,
    )
    assert plan.normalized_status is ExecutivePlanStatus.REVIEW_REQUIRED


def test_policy_forbids_direct_execution() -> None:
    with pytest.raises(ValueError):
        ExecutivePlanningPolicy(allow_direct_execution=True)


def test_engine_enforces_objective_limit() -> None:
    policy = ExecutivePlanningPolicy(max_objectives=1)
    objectives, milestones = plan_parts()
    with pytest.raises(ValueError):
        ExecutivePlanningEngine(policy).create_plan(
            owner="owner",
            title="Too large",
            purpose="Test limit",
            horizon="mid",
            objectives=objectives,
            milestones=milestones,
            now=NOW,
        )


def test_repository_requires_first_revision_one() -> None:
    repository = InMemoryExecutivePlanRepository()
    with pytest.raises(ValueError):
        repository.add(make_plan(revision=2))


def test_repository_rejects_duplicate_plan() -> None:
    repository = InMemoryExecutivePlanRepository()
    plan = make_plan()
    repository.add(plan)
    with pytest.raises(ValueError):
        repository.add(plan)


def test_revision_is_immutable_and_contiguous() -> None:
    manager = ExecutivePlanningManager()
    objectives, milestones = plan_parts()
    first = manager.create(
        owner="carlos",
        title="ROBY Phase IX",
        purpose="Complete phase",
        horizon="mid",
        objectives=objectives,
        milestones=milestones,
        now=NOW,
    )
    second = manager.revise(first, purpose="Complete phase safely", now=NOW)
    assert first.revision == 1
    assert second.revision == 2
    assert second.plan_id != first.plan_id
    assert manager.repository.history("carlos", "ROBY Phase IX") == (first, second)


def test_allowed_status_transition_creates_revision() -> None:
    engine = ExecutivePlanningEngine()
    plan = make_plan()
    approved = engine.transition(plan, ExecutivePlanStatus.APPROVED, now=NOW)
    assert approved.revision == 2
    assert approved.normalized_status is ExecutivePlanStatus.APPROVED


def test_invalid_status_transition_is_blocked() -> None:
    engine = ExecutivePlanningEngine()
    with pytest.raises(ValueError):
        engine.transition(make_plan(), ExecutivePlanStatus.COMPLETED, now=NOW)


def test_activation_does_not_execute_milestones() -> None:
    engine = ExecutivePlanningEngine()
    approved = engine.transition(make_plan(), "approved", now=NOW)
    active = engine.transition(approved, "active", now=NOW)
    assert active.normalized_status is ExecutivePlanStatus.ACTIVE
    assert active.milestones == approved.milestones


def test_system_prompt_preserves_governance_boundary() -> None:
    lines = ExecutivePlanningManager().system_prompt_lines()
    text = " ".join(lines)
    assert "no acciones" in text
    assert "No calendarices, ejecutes ni autorices" in text
