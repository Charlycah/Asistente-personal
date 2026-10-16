from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace

from app.productive_organization_advisory_wiring import (
    ProductiveOrganizationAdvisoryWiring,
)
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
)
from core.intelligent_personal_organization import IntelligentPersonalOrganizationView
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    OrganizationSourceSnapshot,
    PartialCanonicalOrganizationSnapshot,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumer,
)
from core.personal_organization import PersonalOrganizationCapability
from core.productive_organization_evidence_projection import (
    ProductiveOrganizationEvidenceProjection,
)
from core.task_intelligence import Task, TaskOwner, TaskStatus

NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)


def _task(
    *,
    task_id: str = "task-1",
    status: TaskStatus = TaskStatus.PENDING,
    importance: int = 8,
    urgency: int = 7,
    owner: TaskOwner = TaskOwner.CARLOS,
) -> Task:
    completed_at = NOW if status is TaskStatus.COMPLETED else None
    return Task(
        task_id=task_id,
        title=f"Task {task_id}",
        description="Tarea de validacion productiva.",
        owner=owner,
        importance=importance,
        urgency=urgency,
        status=status,
        created_at=NOW,
        updated_at=NOW,
        completed_at=completed_at,
    )


class TaskPort:
    def __init__(self, *tasks: Task) -> None:
        self.tasks = tuple(tasks)

    def list_tasks(self) -> tuple[Task, ...]:
        return self.tasks


def test_tps1_existing_projection_admits_pending_task() -> None:
    item = ProductiveOrganizationEvidenceProjection().project(
        tasks=(_task(),),
    )[0]

    assert item.item_id == "task-1"
    assert item.normalized_capability is PersonalOrganizationCapability.TASKS
    assert item.source_reference == "task:task-1"


def test_tps2_existing_projection_preserves_task_signals() -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(
        _task(
            status=TaskStatus.BLOCKED,
            importance=10,
            urgency=4,
        )
    )

    assert item.importance == 1.0
    assert item.urgency == 0.4
    assert item.blocked is True
    assert item.source_reference == "task:task-1"


def test_tps3_existing_m391_5_reasoning_already_consumes_tasks() -> None:
    projection = ProductiveOrganizationEvidenceProjection()
    low = projection.project_task(_task(task_id="low", importance=2, urgency=2))
    high = projection.project_task(_task(task_id="high", importance=10, urgency=10))

    report = IntelligentPersonalOrganizationView().organize((low, high))

    assert report.canonical_authority == "PersonalOrganizationAuthority"
    assert report.ordered_ids[0] == "high"
    assert report.modifies_items is False
    assert report.persists_results is False
    assert report.executes_actions is False


def test_tps4_snapshot_builder_exposes_existing_task_read_port() -> None:
    builder = PartialCanonicalOrganizationSnapshotBuilder(
        tasks_port=TaskPort(_task()),
    )
    snapshot = builder.build()

    assert snapshot.tasks.availability is OrganizationSourceAvailability.AVAILABLE
    assert snapshot.tasks.item_ids == ("task-1",)


def test_tps5_canonical_snapshot_allows_available_tasks() -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(_task())
    unavailable = OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.GOALS,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint="goals-unavailable",
    )
    projects = OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.PROJECTS,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint="projects-unavailable",
    )
    reminders = OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.REMINDERS,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint="reminders-unavailable",
    )
    tasks = OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.TASKS,
        availability=OrganizationSourceAvailability.AVAILABLE,
        item_ids=("task-1",),
        source_fingerprint="tasks-available",
    )

    snapshot = PartialCanonicalOrganizationSnapshot(
        items=(item,),
        goals=unavailable,
        projects=projects,
        reminders=reminders,
        tasks=tasks,
        source_fingerprint="snapshot-with-tasks",
    )

    assert snapshot.tasks.availability is OrganizationSourceAvailability.AVAILABLE


def test_tps6_partial_consumer_lifts_tasks_available_without_new_authority() -> None:
    item = ProductiveOrganizationEvidenceProjection.project_task(_task())

    snapshot = object.__new__(PartialCanonicalOrganizationSnapshot)
    object.__setattr__(snapshot, "items", (item,))
    object.__setattr__(
        snapshot,
        "goals",
        _source(OrganizationSourceKind.GOALS),
    )
    object.__setattr__(
        snapshot,
        "projects",
        _source(OrganizationSourceKind.PROJECTS),
    )
    object.__setattr__(
        snapshot,
        "reminders",
        _source(OrganizationSourceKind.REMINDERS),
    )
    object.__setattr__(
        snapshot,
        "tasks",
        OrganizationSourceSnapshot(
            source_kind=OrganizationSourceKind.TASKS,
            availability=OrganizationSourceAvailability.AVAILABLE,
            item_ids=("task-1",),
            source_fingerprint="tasks-available",
        ),
    )
    object.__setattr__(snapshot, "source_fingerprint", "snapshot-with-tasks")
    object.__setattr__(
        snapshot,
        "schema_version",
        "post-m409.1-partial-organization-snapshot-v1",
    )
    object.__setattr__(snapshot, "read_only", True)
    object.__setattr__(snapshot, "partial", True)
    object.__setattr__(snapshot, "persists_results", False)
    object.__setattr__(snapshot, "modifies_organization", False)
    object.__setattr__(snapshot, "executes_actions", False)
    object.__setattr__(snapshot, "grants_authority", False)

    result = PartialOrganizationM3915Consumer().consume(snapshot)

    assert result.tasks_available is True
    assert result.organization.recommendations[0].item_id == "task-1"
    assert (
        result.organization.recommendations[0].normalized_capability
        if hasattr(result.organization.recommendations[0], "normalized_capability")
        else result.organization.recommendations[0].capability
    ) is PersonalOrganizationCapability.TASKS
    assert result.canonical_authority == "PersonalOrganizationAuthority"


def _source(kind: OrganizationSourceKind) -> OrganizationSourceSnapshot:
    return OrganizationSourceSnapshot(
        source_kind=kind,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint=f"{kind.value}-unavailable",
    )


@dataclass(frozen=True)
class Registration:
    interceptor: object


class TaskService:
    def __init__(self, *tasks: Task) -> None:
        self.manager = SimpleNamespace(repository=TaskPort(*tasks))


class Registry:
    def __init__(self, *tasks: Task) -> None:
        self.services = {
            "resident.tasks": TaskService(*tasks),
        }

    def registration_for(self, name: str):
        service = self.services.get(name)
        if service is None:
            return None
        return Registration(SimpleNamespace(service=service))


class Runtime:
    def __init__(self, *tasks: Task) -> None:
        dependencies = SimpleNamespace(official_capability_registry=Registry(*tasks))
        root = SimpleNamespace(dependencies=dependencies)
        self.bootstrap = SimpleNamespace(root=root)


def test_tps7_productive_wiring_reads_registered_task_source() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(Runtime(_task()))
    snapshot = wiring._snapshot_builder().build()

    assert snapshot.tasks.availability is OrganizationSourceAvailability.AVAILABLE
    assert snapshot.tasks.item_ids == ("task-1",)


def _adaptation():
    evidence = ExplicitHumanDecisionDeliberationEvidenceProducer().analyze(
        "¿Task o descanso?"
    )
    return ExplicitDeliberationDecisionOptionAdapter().adapt(evidence)


def test_tps8_task_reference_reaches_existing_m391_6_advisory() -> None:
    wiring = ProductiveOrganizationAdvisoryWiring(Runtime(_task()))
    references = (
        ExplicitOrganizationReference(
            0,
            organization_source_reference="task:task-1",
        ),
    )

    result = wiring.assemble(_adaptation(), references)

    assert result is not None
    assert result.tasks_available is True
    assert result.advisory.schema_version == "m391.6"
    assert result.advisory.canonical_facade == "CanonicalDecisionFacade"
