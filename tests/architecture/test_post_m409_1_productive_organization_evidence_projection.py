from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from core.household_goals import GoalStatus, HouseholdGoal
from core.household_projects import HouseholdProject, ProjectStatus
from core.productive_organization_evidence_projection import (
    ProductiveOrganizationEvidenceProjection,
)
from core.task_intelligence import Task, TaskStatus
from domain.reminders.entities import Reminder
from domain.reminders.enums import ReminderStatus

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 12, 18, 0, tzinfo=timezone.utc)


def _task(**changes) -> Task:
    values = {
        "title": "Preparar respaldo",
        "description": "Crear respaldo validado",
        "importance": 5,
        "urgency": 5,
        "created_at": NOW,
        "updated_at": NOW,
        "task_id": "task-1",
    }
    values.update(changes)
    return Task(**values)


def _goal(**changes) -> HouseholdGoal:
    values = {
        "name": "Mantener continuidad",
        "created_at": NOW,
        "updated_at": NOW,
        "goal_id": "goal-1",
    }
    values.update(changes)
    return HouseholdGoal(**values)


def _project(**changes) -> HouseholdProject:
    values = {
        "name": "ROBY",
        "created_at": NOW,
        "updated_at": NOW,
        "project_id": "project-1",
    }
    values.update(changes)
    return HouseholdProject(**values)


def _reminder(**changes) -> Reminder:
    values = {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "title": "Revisar documentación",
        "description": None,
        "due_at": datetime(2026, 8, 13, 18, 0, tzinfo=timezone.utc),
        "status": ReminderStatus.PENDING,
        "recurrence": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    values.update(changes)
    return Reminder(**values)


def test_projection_preserves_governed_identity() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    assert projection.CANONICAL_AUTHORITY == "PersonalOrganizationAuthority"
    assert projection.TARGET_CONTRACT == "M391.5"


@pytest.mark.parametrize(
    ("value", "expected"),
    ((1, 0.1), (5, 0.5), (10, 1.0)),
)
def test_task_importance_normalizes_exactly(value: int, expected: float) -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(
        _task(importance=value)
    )
    assert item.importance == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    ((1, 0.1), (5, 0.5), (10, 1.0)),
)
def test_task_urgency_normalizes_exactly(value: int, expected: float) -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(_task(urgency=value))
    assert item.urgency == expected


def test_task_blocked_is_only_explicit_task_status() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    assert projection.project_task(_task(status=TaskStatus.BLOCKED)).blocked is True
    assert projection.project_task(_task(status=TaskStatus.PENDING)).blocked is False
    in_progress = projection.project_task(_task(status=TaskStatus.IN_PROGRESS))
    assert in_progress.blocked is False


def test_task_projection_does_not_import_derived_priority_score() -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(
        _task(importance=10, urgency=10)
    )
    assert item.importance == 1.0
    assert item.urgency == 1.0
    assert item.deadline_proximity == 0.0
    assert item.goal_alignment == 0.0
    assert item.context_relevance == 0.0
    assert item.safety_risk == 0.0
    assert item.user_declared is False
    assert item.conflicting is False


@pytest.mark.parametrize(
    "item",
    (
        _goal(progress_percent=90),
        _project(next_step="Continuar"),
        _reminder(),
    ),
)
def test_non_task_sources_remain_cognitively_neutral(item) -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    if isinstance(item, HouseholdGoal):
        projected = projection.project_goal(item)
    elif isinstance(item, HouseholdProject):
        projected = projection.project_project(item)
    else:
        projected = projection.project_reminder(item)
    assert projected.urgency == 0.0
    assert projected.importance == 0.0
    assert projected.goal_alignment == 0.0
    assert projected.context_relevance == 0.0
    assert projected.deadline_proximity == 0.0
    assert projected.safety_risk == 0.0
    assert projected.user_declared is False
    assert projected.blocked is False
    assert projected.conflicting is False


def test_projection_preserves_source_provenance() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    assert projection.project_task(_task()).source_reference == "task:task-1"
    assert projection.project_goal(_goal()).source_reference == "goal:goal-1"
    projected_project = projection.project_project(_project())
    assert projected_project.source_reference == "project:project-1"
    assert projection.project_reminder(_reminder()).source_reference == (
        "reminder:00000000-0000-0000-0000-000000000001"
    )


def test_projection_filters_terminal_and_non_admitted_states() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    completed_task = _task(
        task_id="done-task",
        status=TaskStatus.COMPLETED,
        completed_at=NOW,
    )
    draft_task = _task(task_id="draft-task", status=TaskStatus.DRAFT)
    items = projection.project(
        tasks=(completed_task, draft_task, _task()),
        goals=(
            _goal(goal_id="goal-active"),
            _goal(goal_id="goal-paused", status=GoalStatus.PAUSED),
            _goal(goal_id="goal-done", status=GoalStatus.COMPLETED),
        ),
        projects=(
            _project(project_id="project-active"),
            _project(project_id="project-paused", status=ProjectStatus.PAUSED),
            _project(project_id="project-done", status=ProjectStatus.COMPLETED),
        ),
        reminders=(
            _reminder(),
            _reminder(
                id=UUID("00000000-0000-0000-0000-000000000002"),
                status=ReminderStatus.SNOOZED,
            ),
        ),
    )
    assert {item.item_id for item in items} == {
        "task-1",
        "goal-active",
        "goal-paused",
        "project-active",
        "project-paused",
        "00000000-0000-0000-0000-000000000001",
    }


def test_projection_is_deterministic_and_stably_ordered() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    inputs = {
        "tasks": (_task(task_id="z"), _task(task_id="a")),
        "goals": (_goal(goal_id="g"),),
        "projects": (_project(project_id="p"),),
        "reminders": (_reminder(),),
    }
    first = projection.project(**inputs)
    second = projection.project(**inputs)
    assert first == second
    assert tuple((item.capability.value, item.item_id) for item in first) == tuple(
        sorted((item.capability.value, item.item_id) for item in first)
    )


def test_projection_rejects_cross_domain_duplicate_item_ids() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    with pytest.raises(ValueError, match="ids must be unique"):
        projection.project(
            tasks=(_task(task_id="same"),),
            goals=(_goal(goal_id="same"),),
        )


def test_projection_feeds_m391_5_without_decision_or_action() -> None:
    from core.intelligent_personal_organization import (
        IntelligentPersonalOrganizationView,
    )

    items = ProductiveOrganizationEvidenceProjection().project(
        tasks=(_task(importance=10, urgency=10),),
        goals=(_goal(),),
        projects=(_project(),),
        reminders=(_reminder(),),
    )
    report = IntelligentPersonalOrganizationView().organize(items)
    assert report.read_only is True
    assert report.executes_actions is False
    assert report.persists_results is False
    assert report.grants_authority is False
    assert report.ordered_ids == ("task-1",)


def test_projection_has_no_repository_runtime_or_higher_cognition_dependencies() -> (
    None
):
    path = ROOT / "core" / "productive_organization_evidence_projection.py"
    source = path.read_text(encoding="utf-8")
    folded = source.casefold()
    for forbidden in (
        "sqlite",
        "repository",
        ".roby",
        "threading",
        "asyncio",
        "canonicaldecisionfacade",
        "governedinitiative",
        "proactivecare",
        "priorityreasoning",
        "intelligentpersonalorganizationview",
    ):
        assert forbidden not in folded

    tree = ast.parse(source, filename=str(path))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "core.governed_decision_advisory" not in imported_modules


def test_projection_documentation_records_frozen_boundaries() -> None:
    document = (
        ROOT / "docs" / "POST_M409_1_PRODUCTIVE_ORGANIZATION_EVIDENCE_PROJECTION_V1.md"
    )
    text = document.read_text(encoding="utf-8")
    assert "PersonalOrganizationAuthority" in text
    assert "M391.5" in text
    assert "M391.6" in text
    assert "NO-GO" in text
    assert "read-only" in text
