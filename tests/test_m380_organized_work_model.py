import pytest

from core.organized_work import (
    OrganizedWorkAuthority,
    OrganizedWorkKind,
    OrganizedWorkReference,
    OrganizedWorkSnapshot,
)
from core.personal_organization import PersonalOrganizationAuthority


def _references() -> tuple[OrganizedWorkReference, ...]:
    return (
        OrganizedWorkReference("goal", "goal-1", "Publicar ROBY XI.2"),
        OrganizedWorkReference(
            "project", "project-1", "Fase IV", parent_goal_id="goal-1"
        ),
        OrganizedWorkReference(
            "task",
            "task-1",
            "Validar M380",
            parent_goal_id="goal-1",
            parent_project_id="project-1",
        ),
    )


def test_organized_work_links_goals_projects_and_tasks() -> None:
    snapshot = OrganizedWorkAuthority().snapshot(_references())
    assert snapshot.items("goal")[0].item_id == "goal-1"
    assert snapshot.items("project")[0].parent_goal_id == "goal-1"
    assert snapshot.items("task")[0].parent_project_id == "project-1"


def test_personal_organization_remains_the_canonical_authority() -> None:
    snapshot = PersonalOrganizationAuthority().organized_work_snapshot()
    assert snapshot.canonical_authority == "PersonalOrganizationAuthority"
    assert snapshot.unified_core is True


def test_snapshot_rejects_missing_parent_references() -> None:
    with pytest.raises(ValueError):
        OrganizedWorkSnapshot(
            (OrganizedWorkReference("project", "p1", "Project", "missing"),)
        )


def test_snapshot_rejects_duplicate_domain_identities() -> None:
    item = OrganizedWorkReference("goal", "g1", "Goal")
    with pytest.raises(ValueError):
        OrganizedWorkSnapshot((item, item))


def test_goal_and_project_parent_invariants_are_governed() -> None:
    with pytest.raises(ValueError):
        OrganizedWorkReference("goal", "g1", "Goal", parent_goal_id="g0")
    with pytest.raises(ValueError):
        OrganizedWorkReference("project", "p1", "Project", parent_project_id="p0")


def test_m380_does_not_create_planner_execution_or_model_writes() -> None:
    references = _references()
    with pytest.raises(ValueError):
        OrganizedWorkSnapshot(references, creates_parallel_planner=True)
    with pytest.raises(ValueError):
        OrganizedWorkSnapshot(references, writes_existing_models=True)
    with pytest.raises(ValueError):
        OrganizedWorkSnapshot(references, execution_authorized=True)


def test_reference_requires_traceable_identity_and_title() -> None:
    with pytest.raises(ValueError):
        OrganizedWorkReference(OrganizedWorkKind.TASK, "", "Task")
    with pytest.raises(ValueError):
        OrganizedWorkReference(OrganizedWorkKind.TASK, "t1", "")


def test_authorities_expose_no_crud_planner_memory_or_agent_api() -> None:
    authority = OrganizedWorkAuthority()
    for name in (
        "create_goal",
        "create_project",
        "create_task",
        "execute_task",
        "write_memory",
        "spawn_agent",
        "call_llm",
    ):
        assert not hasattr(authority, name)
