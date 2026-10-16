from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from core.agenda_evidence import AgendaEventEvidence
from core.household_goals import HouseholdGoal
from core.household_projects import HouseholdProject
from core.intelligent_personal_organization import PersonalOrganizationItem
from core.personal_knowledge_base import KnowledgeItem
from core.personal_organization import PersonalOrganizationCapability
from core.productive_organization_evidence_projection import (
    ProductiveOrganizationEvidenceProjection,
)
from core.task_intelligence import Task
from domain.reminders.entities import Reminder


class OrganizationSourceKind(StrEnum):
    GOALS = "goals"
    PROJECTS = "projects"
    REMINDERS = "reminders"
    TASKS = "tasks"
    AGENDA = "agenda"
    NOTES = "notes"


class OrganizationSourceAvailability(StrEnum):
    AVAILABLE = "available"
    EMPTY = "empty"
    UNAVAILABLE = "unavailable"


class OrganizationSourceUnavailableError(RuntimeError):
    """Explicit signal that a configured productive read source is unavailable."""


class HouseholdGoalReadPort(Protocol):
    def list_goals(self) -> tuple[HouseholdGoal, ...]: ...


class HouseholdProjectReadPort(Protocol):
    def list_projects(self) -> tuple[HouseholdProject, ...]: ...


class ReminderReadPort(Protocol):
    def list_pending_reminders(self) -> tuple[Reminder, ...]: ...


class TaskReadPort(Protocol):
    def list_tasks(self) -> tuple[Task, ...]: ...


class AgendaReadPort(Protocol):
    def list_agenda_events(self) -> tuple[AgendaEventEvidence, ...]: ...


class NotesReadPort(Protocol):
    def list_notes(self) -> tuple[KnowledgeItem, ...]: ...


@dataclass(frozen=True)
class OrganizationSourceSnapshot:
    source_kind: OrganizationSourceKind
    availability: OrganizationSourceAvailability
    item_ids: tuple[str, ...]
    source_fingerprint: str

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("organization source fingerprint must not be blank")
        if self.availability is OrganizationSourceAvailability.AVAILABLE:
            if not self.item_ids:
                raise ValueError("available organization source requires items")
        elif self.item_ids:
            raise ValueError("empty/unavailable organization source cannot carry items")
        if len(self.item_ids) != len(set(self.item_ids)):
            raise ValueError("organization source item ids must be unique")


def _unavailable_agenda_source() -> OrganizationSourceSnapshot:
    return OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.AGENDA,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint=_source_fingerprint(
            OrganizationSourceKind.AGENDA,
            OrganizationSourceAvailability.UNAVAILABLE,
            (),
        ),
    )


def _unavailable_notes_source() -> OrganizationSourceSnapshot:
    return OrganizationSourceSnapshot(
        source_kind=OrganizationSourceKind.NOTES,
        availability=OrganizationSourceAvailability.UNAVAILABLE,
        item_ids=(),
        source_fingerprint=_source_fingerprint(
            OrganizationSourceKind.NOTES,
            OrganizationSourceAvailability.UNAVAILABLE,
            (),
        ),
    )


@dataclass(frozen=True)
class PartialCanonicalOrganizationSnapshot:
    items: tuple[PersonalOrganizationItem, ...]
    goals: OrganizationSourceSnapshot
    projects: OrganizationSourceSnapshot
    reminders: OrganizationSourceSnapshot
    tasks: OrganizationSourceSnapshot
    source_fingerprint: str
    agenda: OrganizationSourceSnapshot = field(
        default_factory=_unavailable_agenda_source
    )
    notes: OrganizationSourceSnapshot = field(
        default_factory=_unavailable_notes_source
    )
    schema_version: str = "post-m409.1-partial-organization-snapshot-v4"
    read_only: bool = True
    partial: bool = True
    persists_results: bool = False
    modifies_organization: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        sources = (
            self.goals,
            self.projects,
            self.reminders,
            self.tasks,
            self.agenda,
            self.notes,
        )
        if tuple(item.source_kind for item in sources) != tuple(OrganizationSourceKind):
            raise ValueError("organization snapshot sources are not canonical")
        item_ids = tuple(item.item_id for item in self.items)
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("organization snapshot item ids must be unique")
        references = tuple(item.source_reference for item in self.items)
        present_references = tuple(value for value in references if value is not None)
        if len(present_references) != len(set(present_references)):
            raise ValueError("organization source references must be unique")
        if tuple(sorted(self.items, key=_item_sort_key)) != self.items:
            raise ValueError("organization snapshot items must be canonically ordered")
        expected = {
            capability: tuple(
                item.item_id
                for item in self.items
                if item.normalized_capability is capability
            )
            for capability in (
                PersonalOrganizationCapability.GOALS,
                PersonalOrganizationCapability.PROJECTS,
                PersonalOrganizationCapability.REMINDERS,
                PersonalOrganizationCapability.TASKS,
                PersonalOrganizationCapability.AGENDA,
                PersonalOrganizationCapability.NOTES,
            )
        }
        if self.goals.item_ids != expected[PersonalOrganizationCapability.GOALS]:
            raise ValueError("goal source snapshot does not match canonical items")
        if self.projects.item_ids != expected[PersonalOrganizationCapability.PROJECTS]:
            raise ValueError("project source snapshot does not match canonical items")
        if (
            self.reminders.item_ids
            != expected[PersonalOrganizationCapability.REMINDERS]
        ):
            raise ValueError("reminder source snapshot does not match canonical items")
        if self.tasks.item_ids != expected[PersonalOrganizationCapability.TASKS]:
            raise ValueError("task source snapshot does not match canonical items")
        if self.agenda.item_ids != expected[PersonalOrganizationCapability.AGENDA]:
            raise ValueError("agenda source snapshot does not match canonical items")
        if self.notes.item_ids != expected[PersonalOrganizationCapability.NOTES]:
            raise ValueError("notes source snapshot does not match canonical items")
        if not self.source_fingerprint.strip():
            raise ValueError("organization snapshot fingerprint must not be blank")
        if any(
            (
                not self.read_only,
                not self.partial,
                self.persists_results,
                self.modifies_organization,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("organization snapshot violates governed limits")

    def source_for(self, kind: OrganizationSourceKind) -> OrganizationSourceSnapshot:
        normalized = OrganizationSourceKind(kind)
        if normalized is OrganizationSourceKind.AGENDA:
            return getattr(self, "agenda", _unavailable_agenda_source())
        if normalized is OrganizationSourceKind.NOTES:
            return getattr(self, "notes", _unavailable_notes_source())
        return {
            OrganizationSourceKind.GOALS: self.goals,
            OrganizationSourceKind.PROJECTS: self.projects,
            OrganizationSourceKind.REMINDERS: self.reminders,
            OrganizationSourceKind.TASKS: self.tasks,
        }[normalized]


@dataclass(frozen=True)
class PartialCanonicalOrganizationSnapshotBuilder:
    goals_port: HouseholdGoalReadPort | None = None
    projects_port: HouseholdProjectReadPort | None = None
    reminders_port: ReminderReadPort | None = None
    tasks_port: TaskReadPort | None = None
    agenda_port: AgendaReadPort | None = None
    notes_port: NotesReadPort | None = None

    def build(self) -> PartialCanonicalOrganizationSnapshot:
        goals, goals_available = self._read_goals()
        projects, projects_available = self._read_projects()
        reminders, reminders_available = self._read_reminders()
        tasks, tasks_available = self._read_tasks()
        agenda_events, agenda_available = self._read_agenda()
        knowledge_notes, notes_available = self._read_notes()

        items = ProductiveOrganizationEvidenceProjection().project(
            tasks=tasks,
            goals=goals,
            projects=projects,
            reminders=reminders,
            agenda_events=agenda_events,
            knowledge_notes=knowledge_notes,
        )
        items = tuple(sorted(items, key=_item_sort_key))
        goals_snapshot = self._source_snapshot(
            OrganizationSourceKind.GOALS,
            PersonalOrganizationCapability.GOALS,
            goals_available,
            items,
        )
        projects_snapshot = self._source_snapshot(
            OrganizationSourceKind.PROJECTS,
            PersonalOrganizationCapability.PROJECTS,
            projects_available,
            items,
        )
        reminders_snapshot = self._source_snapshot(
            OrganizationSourceKind.REMINDERS,
            PersonalOrganizationCapability.REMINDERS,
            reminders_available,
            items,
        )
        tasks_snapshot = self._source_snapshot(
            OrganizationSourceKind.TASKS,
            PersonalOrganizationCapability.TASKS,
            tasks_available,
            items,
        )
        agenda_snapshot = self._source_snapshot(
            OrganizationSourceKind.AGENDA,
            PersonalOrganizationCapability.AGENDA,
            agenda_available,
            items,
        )
        notes_snapshot = self._source_snapshot(
            OrganizationSourceKind.NOTES,
            PersonalOrganizationCapability.NOTES,
            notes_available,
            items,
        )
        fingerprint = self._snapshot_fingerprint(
            items,
            (
                goals_snapshot,
                projects_snapshot,
                reminders_snapshot,
                tasks_snapshot,
                agenda_snapshot,
                notes_snapshot,
            ),
        )
        return PartialCanonicalOrganizationSnapshot(
            items=items,
            goals=goals_snapshot,
            projects=projects_snapshot,
            reminders=reminders_snapshot,
            tasks=tasks_snapshot,
            source_fingerprint=fingerprint,
            agenda=agenda_snapshot,
            notes=notes_snapshot,
        )

    def _read_goals(self) -> tuple[tuple[HouseholdGoal, ...], bool]:
        if self.goals_port is None:
            return (), False
        try:
            return tuple(self.goals_port.list_goals()), True
        except OrganizationSourceUnavailableError:
            return (), False

    def _read_projects(self) -> tuple[tuple[HouseholdProject, ...], bool]:
        if self.projects_port is None:
            return (), False
        try:
            return tuple(self.projects_port.list_projects()), True
        except OrganizationSourceUnavailableError:
            return (), False

    def _read_reminders(self) -> tuple[tuple[Reminder, ...], bool]:
        if self.reminders_port is None:
            return (), False
        try:
            return tuple(self.reminders_port.list_pending_reminders()), True
        except OrganizationSourceUnavailableError:
            return (), False

    def _read_tasks(self) -> tuple[tuple[Task, ...], bool]:
        if self.tasks_port is None:
            return (), False
        try:
            return tuple(self.tasks_port.list_tasks()), True
        except OrganizationSourceUnavailableError:
            return (), False

    def _read_agenda(self) -> tuple[tuple[AgendaEventEvidence, ...], bool]:
        if self.agenda_port is None:
            return (), False
        try:
            return tuple(self.agenda_port.list_agenda_events()), True
        except OrganizationSourceUnavailableError:
            return (), False

    def _read_notes(self) -> tuple[tuple[KnowledgeItem, ...], bool]:
        if self.notes_port is None:
            return (), False
        try:
            return tuple(self.notes_port.list_notes()), True
        except OrganizationSourceUnavailableError:
            return (), False

    @staticmethod
    def _source_snapshot(
        kind: OrganizationSourceKind,
        capability: PersonalOrganizationCapability,
        source_available: bool,
        items: tuple[PersonalOrganizationItem, ...],
    ) -> OrganizationSourceSnapshot:
        selected = tuple(
            item for item in items if item.normalized_capability is capability
        )
        if not source_available:
            availability = OrganizationSourceAvailability.UNAVAILABLE
            selected = ()
        elif selected:
            availability = OrganizationSourceAvailability.AVAILABLE
        else:
            availability = OrganizationSourceAvailability.EMPTY
        item_ids = tuple(item.item_id for item in selected)
        fingerprint = _source_fingerprint(kind, availability, selected)
        return OrganizationSourceSnapshot(
            source_kind=kind,
            availability=availability,
            item_ids=item_ids,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _snapshot_fingerprint(
        items: tuple[PersonalOrganizationItem, ...],
        sources: tuple[OrganizationSourceSnapshot, ...],
    ) -> str:
        rows = ["post-m409.1-partial-organization-snapshot-v4"]
        rows.extend(
            f"{source.source_kind.value}|{source.availability.value}|"
            f"{source.source_fingerprint}"
            for source in sources
        )
        rows.extend(_serialize_item(item) for item in items)
        return sha256("\n".join(rows).encode("utf-8")).hexdigest()


def _item_sort_key(item: PersonalOrganizationItem) -> tuple[str, str]:
    return item.normalized_capability.value, item.item_id


def _serialize_item(item: PersonalOrganizationItem) -> str:
    return "|".join(
        (
            item.normalized_capability.value,
            item.item_id,
            item.title,
            format(float(item.urgency), ".17g"),
            format(float(item.importance), ".17g"),
            format(float(item.goal_alignment), ".17g"),
            format(float(item.context_relevance), ".17g"),
            format(float(item.deadline_proximity), ".17g"),
            format(float(item.safety_risk), ".17g"),
            "1" if item.user_declared else "0",
            "1" if item.blocked else "0",
            "1" if item.conflicting else "0",
            item.source_reference or "",
        )
    )


def _source_fingerprint(
    kind: OrganizationSourceKind,
    availability: OrganizationSourceAvailability,
    items: tuple[PersonalOrganizationItem, ...],
) -> str:
    rows = [kind.value, availability.value]
    rows.extend(_serialize_item(item) for item in items)
    return sha256("\n".join(rows).encode("utf-8")).hexdigest()
