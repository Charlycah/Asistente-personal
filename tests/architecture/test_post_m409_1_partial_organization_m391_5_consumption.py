from datetime import datetime, timezone
from uuid import UUID

from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumer,
)
from domain.reminders import Reminder, ReminderStatus

NOW = datetime(2026, 8, 13, tzinfo=timezone.utc)


class Goals:
    def list_goals(self):
        return (
            HouseholdGoal(
                goal_id="g1",
                name="Goal",
                created_at=NOW,
                updated_at=NOW,
            ),
        )


class Projects:
    def list_projects(self):
        return (
            HouseholdProject(
                project_id="p1", name="Project", created_at=NOW, updated_at=NOW
            ),
        )


class Reminders:
    def list_pending_reminders(self):
        return (
            Reminder(
                id=UUID("00000000-0000-0000-0000-000000000001"),
                title="Reminder",
                description="",
                status=ReminderStatus.PENDING,
                recurrence=None,
                due_at=NOW,
                created_at=NOW,
                updated_at=NOW,
            ),
        )


def _snapshot():
    return PartialCanonicalOrganizationSnapshotBuilder(
        goals_port=Goals(), projects_port=Projects(), reminders_port=Reminders()
    ).build()


def test_consumes_partial_snapshot_through_existing_m391_5_authority():
    snapshot = _snapshot()
    result = PartialOrganizationM3915Consumer().consume(snapshot)

    assert result.canonical_authority == "PersonalOrganizationAuthority"
    assert result.organization.canonical_authority == "PersonalOrganizationAuthority"
    assert result.organization.schema_version == "m391.5"
    assert {item.item_id for item in result.organization.recommendations} == {
        "g1",
        "p1",
        "00000000-0000-0000-0000-000000000001",
    }
    assert result.organization_snapshot_fingerprint == snapshot.source_fingerprint
    assert result.read_only is True
    assert result.partial is True
    assert result.tasks_available is False
    assert result.persists_results is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_preserves_source_availability_and_tasks_unavailable():
    result = PartialOrganizationM3915Consumer().consume(_snapshot())
    availability = dict(result.source_availability)

    assert (
        availability[OrganizationSourceKind.GOALS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.PROJECTS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.REMINDERS]
        is OrganizationSourceAvailability.AVAILABLE
    )
    assert (
        availability[OrganizationSourceKind.TASKS]
        is OrganizationSourceAvailability.UNAVAILABLE
    )


def test_consumption_is_deterministic_and_does_not_mutate_snapshot():
    snapshot = _snapshot()
    before = snapshot
    first = PartialOrganizationM3915Consumer().consume(snapshot)
    second = PartialOrganizationM3915Consumer().consume(snapshot)

    assert first == second
    assert snapshot == before
    assert first.source_fingerprint == second.source_fingerprint


def test_accepts_empty_task_source_without_claiming_task_items():
    snapshot = _snapshot()
    lifted = type(snapshot)(
        items=snapshot.items,
        goals=snapshot.goals,
        projects=snapshot.projects,
        reminders=snapshot.reminders,
        tasks=type(snapshot.tasks)(
            source_kind=OrganizationSourceKind.TASKS,
            availability=OrganizationSourceAvailability.EMPTY,
            item_ids=(),
            source_fingerprint=snapshot.tasks.source_fingerprint,
        ),
        source_fingerprint=snapshot.source_fingerprint,
    )

    result = PartialOrganizationM3915Consumer().consume(lifted)

    assert result.tasks_available is True
    assert (
        result.organization
        == PartialOrganizationM3915Consumer().consume(snapshot).organization
    )
