from datetime import datetime, timezone

import pytest

from core.adaptive_cognition import (
    CoordinationStatus,
    DirectiveStatus,
    ExecutiveCoordination,
    ExecutiveCoordinationEngine,
    ExecutiveCoordinationManager,
    ExecutiveCoordinationPolicy,
    ExecutiveDirective,
    ExecutiveMilestone,
    ExecutiveObjective,
    ExecutivePlan,
    ExecutivePlanStatus,
    ExecutivePriority,
    ExecutiveSubsystem,
    InMemoryExecutiveCoordinationRepository,
)

NOW = datetime(2026, 7, 10, 20, 0, tzinfo=timezone.utc)


def make_plan(
    status: ExecutivePlanStatus = ExecutivePlanStatus.APPROVED,
) -> ExecutivePlan:
    objective = ExecutiveObjective("Coordinate ROBY", ("Coordination governed",))
    milestone = ExecutiveMilestone(
        "Coordinate subsystems", (objective.objective_id,), 1
    )
    return ExecutivePlan(
        owner="carlos",
        title="ROBY Phase IX",
        purpose="Coordinate adaptive cognition",
        horizon="mid",
        objectives=(objective,),
        milestones=(milestone,),
        status=status,
        created_at=NOW,
    )


def directive(
    plan: ExecutivePlan,
    *,
    subsystem: ExecutiveSubsystem = ExecutiveSubsystem.REASONING,
    priority: ExecutivePriority = ExecutivePriority.HIGH,
    sequence: int = 1,
    dependencies: tuple[str, ...] = (),
) -> ExecutiveDirective:
    return ExecutiveDirective(
        title="Assess next governed step",
        subsystem=subsystem,
        milestone_id=plan.milestones[0].milestone_id,
        sequence=sequence,
        priority=priority,
        dependencies=dependencies,
    )


def test_directive_has_stable_hash_identity() -> None:
    plan = make_plan()
    assert directive(plan).directive_id == directive(plan).directive_id


def test_directive_requires_title_and_milestone() -> None:
    with pytest.raises(ValueError):
        ExecutiveDirective("", "reasoning", "milestone", 1)


def test_directive_rejects_non_positive_sequence() -> None:
    plan = make_plan()
    with pytest.raises(ValueError):
        ExecutiveDirective("Title", "reasoning", plan.milestones[0].milestone_id, 0)


def test_directive_rejects_duplicate_dependencies() -> None:
    plan = make_plan()
    with pytest.raises(ValueError):
        ExecutiveDirective(
            "Title",
            "reasoning",
            plan.milestones[0].milestone_id,
            1,
            dependencies=("a", "a"),
        )


def test_coordination_requires_directives() -> None:
    with pytest.raises(ValueError):
        ExecutiveCoordination("owner", "plan", ())


def test_coordination_rejects_naive_timestamp() -> None:
    plan = make_plan()
    with pytest.raises(ValueError):
        ExecutiveCoordination(
            "owner",
            plan.plan_id,
            (directive(plan),),
            created_at=datetime(2026, 1, 1),
        )


def test_coordination_requires_contiguous_sequence() -> None:
    plan = make_plan()
    with pytest.raises(ValueError):
        ExecutiveCoordination(
            "owner",
            plan.plan_id,
            (directive(plan, sequence=2),),
            created_at=NOW,
        )


def test_coordination_rejects_unknown_dependency() -> None:
    plan = make_plan()
    with pytest.raises(ValueError):
        ExecutiveCoordination(
            "owner",
            plan.plan_id,
            (directive(plan, dependencies=("unknown",)),),
            created_at=NOW,
        )


def test_policy_forbids_direct_execution() -> None:
    with pytest.raises(ValueError):
        ExecutiveCoordinationPolicy(allow_direct_execution=True)


def test_engine_requires_approved_or_active_plan() -> None:
    plan = make_plan(ExecutivePlanStatus.DRAFT)
    with pytest.raises(ValueError):
        ExecutiveCoordinationEngine().create(
            plan=plan,
            directives=(directive(plan),),
            now=NOW,
        )


def test_engine_rejects_unknown_plan_milestone() -> None:
    plan = make_plan()
    bad = ExecutiveDirective("Bad", "reasoning", "unknown", 1)
    with pytest.raises(ValueError):
        ExecutiveCoordinationEngine().create(plan=plan, directives=(bad,), now=NOW)


def test_critical_directive_requires_review() -> None:
    plan = make_plan()
    item = ExecutiveCoordinationEngine().create(
        plan=plan,
        directives=(directive(plan, priority=ExecutivePriority.CRITICAL),),
        now=NOW,
    )
    assert item.normalized_status is CoordinationStatus.REVIEW_REQUIRED


def test_autonomy_directive_requires_review() -> None:
    plan = make_plan()
    item = ExecutiveCoordinationEngine().create(
        plan=plan,
        directives=(directive(plan, subsystem=ExecutiveSubsystem.AUTONOMY),),
        now=NOW,
    )
    assert item.requires_review is True


def test_repository_requires_first_revision_one() -> None:
    plan = make_plan()
    repository = InMemoryExecutiveCoordinationRepository()
    item = ExecutiveCoordination(
        "owner", plan.plan_id, (directive(plan),), revision=2, created_at=NOW
    )
    with pytest.raises(ValueError):
        repository.add(item)


def test_repository_rejects_duplicate() -> None:
    plan = make_plan()
    repository = InMemoryExecutiveCoordinationRepository()
    item = ExecutiveCoordination(
        "owner", plan.plan_id, (directive(plan),), created_at=NOW
    )
    repository.add(item)
    with pytest.raises(ValueError):
        repository.add(item)


def test_allowed_transition_creates_revision() -> None:
    plan = make_plan()
    item = ExecutiveCoordinationEngine().create(
        plan=plan, directives=(directive(plan),), now=NOW
    )
    approved = ExecutiveCoordinationEngine().transition(item, "approved", now=NOW)
    assert approved.revision == 2
    assert approved.normalized_status is CoordinationStatus.APPROVED


def test_invalid_transition_is_blocked() -> None:
    plan = make_plan()
    item = ExecutiveCoordinationEngine().create(
        plan=plan, directives=(directive(plan),), now=NOW
    )
    with pytest.raises(ValueError):
        ExecutiveCoordinationEngine().transition(item, "completed", now=NOW)


def test_directive_update_is_immutable() -> None:
    plan = make_plan()
    manager = ExecutiveCoordinationManager()
    first = manager.create(plan=plan, directives=(directive(plan),), now=NOW)
    second = manager.update_directive(
        first,
        first.directives[0].directive_id,
        DirectiveStatus.ACKNOWLEDGED,
        now=NOW,
    )
    assert first.directives[0].normalized_status is DirectiveStatus.PROPOSED
    assert second.directives[0].normalized_status is DirectiveStatus.ACKNOWLEDGED
    assert second.revision == 2


def test_unknown_directive_update_is_blocked() -> None:
    plan = make_plan()
    item = ExecutiveCoordinationEngine().create(
        plan=plan, directives=(directive(plan),), now=NOW
    )
    with pytest.raises(ValueError):
        ExecutiveCoordinationEngine().update_directive(item, "unknown", "ready")


def test_system_prompt_preserves_execution_boundary() -> None:
    text = " ".join(ExecutiveCoordinationManager().system_prompt_lines())
    assert "no mediante ejecución" in text
    assert "No invoques herramientas" in text
