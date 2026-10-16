from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import pytest

from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    OrganizationSourceSnapshot,
    OrganizationSourceUnavailableError,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from domain.reminders.entities import Reminder
from domain.reminders.enums import ReminderStatus

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 13, 9, 0, tzinfo=timezone.utc)


class GoalsPort:
    def __init__(self, values=()):
        self.values = tuple(values)
        self.calls = 0

    def list_goals(self):
        self.calls += 1
        return self.values


class ProjectsPort:
    def __init__(self, values=()):
        self.values = tuple(values)
        self.calls = 0

    def list_projects(self):
        self.calls += 1
        return self.values


class RemindersPort:
    def __init__(self, values=()):
        self.values = tuple(values)
        self.calls = 0

    def list_pending_reminders(self):
        self.calls += 1
        return self.values


class UnavailableGoalsPort:
    def list_goals(self):
        raise OrganizationSourceUnavailableError("not available")


def _goal(goal_id="g1"):
    return HouseholdGoal(
        name="Continuidad",
        goal_id=goal_id,
        created_at=NOW,
        updated_at=NOW,
    )


def _project(project_id="p1"):
    return HouseholdProject(
        name="ROBY",
        project_id=project_id,
        created_at=NOW,
        updated_at=NOW,
    )


def _reminder(value=1):
    return Reminder(
        id=UUID(int=value),
        title="Revisar documentación",
        description=None,
        due_at=datetime(2026, 8, 14, 9, 0, tzinfo=timezone.utc),
        status=ReminderStatus.PENDING,
        recurrence=None,
        created_at=NOW,
        updated_at=NOW,
    )


def test_snapshot_reads_each_port_once_and_projects_existing_contract() -> None:
    goals = GoalsPort((_goal(),))
    projects = ProjectsPort((_project(),))
    reminders = RemindersPort((_reminder(),))
    snapshot = PartialCanonicalOrganizationSnapshotBuilder(
        goals,
        projects,
        reminders,
    ).build()
    assert (goals.calls, projects.calls, reminders.calls) == (1, 1, 1)
    assert tuple(item.source_reference for item in snapshot.items) == (
        "goal:g1",
        "project:p1",
        "reminder:00000000-0000-0000-0000-000000000001",
    )


def test_available_empty_unavailable_semantics_are_distinct() -> None:
    snapshot = PartialCanonicalOrganizationSnapshotBuilder(
        GoalsPort((_goal(),)),
        ProjectsPort(()),
        None,
    ).build()
    assert snapshot.goals.availability is OrganizationSourceAvailability.AVAILABLE
    assert snapshot.projects.availability is OrganizationSourceAvailability.EMPTY
    assert snapshot.reminders.availability is OrganizationSourceAvailability.UNAVAILABLE
    assert snapshot.tasks.availability is OrganizationSourceAvailability.UNAVAILABLE


def test_tasks_remain_unavailable_by_contract() -> None:
    snapshot = PartialCanonicalOrganizationSnapshotBuilder().build()
    assert snapshot.tasks.source_kind is OrganizationSourceKind.TASKS
    assert snapshot.tasks.availability is OrganizationSourceAvailability.UNAVAILABLE
    assert snapshot.tasks.item_ids == ()


def test_explicit_source_unavailability_is_not_empty() -> None:
    unavailable = PartialCanonicalOrganizationSnapshotBuilder(
        UnavailableGoalsPort()
    ).build()
    empty = PartialCanonicalOrganizationSnapshotBuilder(GoalsPort(())).build()
    assert unavailable.goals.availability is OrganizationSourceAvailability.UNAVAILABLE
    assert empty.goals.availability is OrganizationSourceAvailability.EMPTY
    assert unavailable.source_fingerprint != empty.source_fingerprint


def test_snapshot_fingerprint_is_stable_across_repository_order() -> None:
    first = PartialCanonicalOrganizationSnapshotBuilder(
        GoalsPort((_goal("g2"), _goal("g1"))),
    ).build()
    second = PartialCanonicalOrganizationSnapshotBuilder(
        GoalsPort((_goal("g1"), _goal("g2"))),
    ).build()
    assert first == second


def test_snapshot_is_partial_read_only_and_transient() -> None:
    snapshot = PartialCanonicalOrganizationSnapshotBuilder().build()
    assert snapshot.partial is True
    assert snapshot.read_only is True
    assert snapshot.persists_results is False
    assert snapshot.modifies_organization is False
    assert snapshot.executes_actions is False
    assert snapshot.grants_authority is False
    with pytest.raises(FrozenInstanceError):
        snapshot.source_fingerprint = "changed"  # type: ignore[misc]


def test_invalid_source_status_payload_combinations_fail_closed() -> None:
    with pytest.raises(ValueError):
        OrganizationSourceSnapshot(
            OrganizationSourceKind.GOALS,
            OrganizationSourceAvailability.AVAILABLE,
            (),
            "fingerprint",
        )
    with pytest.raises(ValueError):
        OrganizationSourceSnapshot(
            OrganizationSourceKind.GOALS,
            OrganizationSourceAvailability.UNAVAILABLE,
            ("g1",),
            "fingerprint",
        )


def test_snapshot_rejects_duplicate_ids_across_capabilities() -> None:
    with pytest.raises(ValueError):
        PartialCanonicalOrganizationSnapshotBuilder(
            GoalsPort((_goal("same"),)),
            ProjectsPort((_project("same"),)),
        ).build()


def test_snapshot_module_has_no_sqlite_gateway_runtime_or_task_manager() -> None:
    path = ROOT / "core" / "partial_canonical_organization_snapshot.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert "sqlite3" not in source
    assert "TaskIntelligenceManager" not in source
    assert not any(item.startswith("app.") for item in imports)
    assert "official_conversation_gateway" not in source
    assert "runtime_root_factory" not in source
