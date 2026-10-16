from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.organized_work import OrganizedWorkAuthority, OrganizedWorkSnapshot


class PersonalOrganizationCapability(str, Enum):
    AGENDA = "agenda"
    TASKS = "tasks"
    REMINDERS = "reminders"
    GOALS = "goals"
    PROJECTS = "projects"
    NOTES = "notes"
    PRIORITIZATION = "prioritization"


class PersonalOrganizationReadiness(str, Enum):
    EXISTING = "existing"
    PARTIAL = "partial"
    FOUNDATION_ONLY = "foundation_only"


@dataclass(frozen=True)
class PersonalOrganizationBinding:
    """Vincula una capacidad personal con una autoridad ya existente."""

    capability: PersonalOrganizationCapability | str
    authority_name: str
    implementation_path: str
    readiness: PersonalOrganizationReadiness | str
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        PersonalOrganizationCapability(self.capability)
        PersonalOrganizationReadiness(self.readiness)
        if not self.authority_name.strip():
            raise ValueError("authority_name must not be blank")
        if not self.implementation_path.strip():
            raise ValueError("implementation_path must not be blank")
        if any(not note.strip() for note in self.notes):
            raise ValueError("notes must not contain blank values")

    @property
    def normalized_capability(self) -> PersonalOrganizationCapability:
        return PersonalOrganizationCapability(self.capability)

    @property
    def normalized_readiness(self) -> PersonalOrganizationReadiness:
        return PersonalOrganizationReadiness(self.readiness)


@dataclass(frozen=True)
class PersonalOrganizationSnapshot:
    """Inventario gobernado del dominio de organización personal."""

    bindings: tuple[PersonalOrganizationBinding, ...]
    unified_core: bool = True
    creates_parallel_brain: bool = False
    replaces_existing_authorities: bool = False
    runtime_changed: bool = False

    def __post_init__(self) -> None:
        capabilities = tuple(binding.normalized_capability for binding in self.bindings)
        expected = set(PersonalOrganizationCapability)
        if set(capabilities) != expected:
            raise ValueError("snapshot must cover every organization capability")
        if len(capabilities) != len(set(capabilities)):
            raise ValueError("capabilities must not be duplicated")
        if not self.unified_core:
            raise ValueError("personal organization must use the unified core")
        if self.creates_parallel_brain:
            raise ValueError("M379 cannot create a parallel brain")
        if self.replaces_existing_authorities:
            raise ValueError("M379 must integrate before replacing authorities")
        if self.runtime_changed:
            raise ValueError("M379 does not change the runtime")

    def binding_for(
        self, capability: PersonalOrganizationCapability | str
    ) -> PersonalOrganizationBinding:
        normalized = PersonalOrganizationCapability(capability)
        for binding in self.bindings:
            if binding.normalized_capability is normalized:
                return binding
        raise KeyError(normalized.value)


class PersonalOrganizationAuthority:
    """Única fachada gobernada para el dominio de organización personal."""

    def __init__(self) -> None:
        self._organized_work = OrganizedWorkAuthority()
        self._snapshot = PersonalOrganizationSnapshot(
            bindings=(
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.AGENDA,
                    "CognitiveAgendaManager",
                    "app.cognitive_agenda_manager:CognitiveAgendaManager",
                    PersonalOrganizationReadiness.EXISTING,
                    ("calendar providers remain external gateways",),
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.TASKS,
                    "TaskIntelligenceManager",
                    "core.task_intelligence:TaskIntelligenceManager",
                    PersonalOrganizationReadiness.EXISTING,
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.REMINDERS,
                    "ReminderService",
                    "domain.reminders.services:ReminderService",
                    PersonalOrganizationReadiness.EXISTING,
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.GOALS,
                    "HouseholdGoalManager",
                    "core.household_goals:HouseholdGoalManager",
                    PersonalOrganizationReadiness.EXISTING,
                    (
                        "personal/household goals remain owned by the existing "
                        "HouseholdGoalManager; cognitive goals remain separate",
                    ),
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.PROJECTS,
                    "HouseholdProjectService",
                    "app.household_projects:HouseholdProjectService",
                    PersonalOrganizationReadiness.PARTIAL,
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.NOTES,
                    "PersonalKnowledgeBaseManager",
                    "core.personal_knowledge_base:PersonalKnowledgeBaseManager",
                    PersonalOrganizationReadiness.EXISTING,
                    ("KnowledgeKind.NOTE remains distinct from cognitive memory",),
                ),
                PersonalOrganizationBinding(
                    PersonalOrganizationCapability.PRIORITIZATION,
                    "PriorityReasoning",
                    "app.priority_reasoning:PriorityReasoning",
                    PersonalOrganizationReadiness.EXISTING,
                ),
            )
        )

    def snapshot(self) -> PersonalOrganizationSnapshot:
        return self._snapshot

    def binding_for(
        self, capability: PersonalOrganizationCapability | str
    ) -> PersonalOrganizationBinding:
        return self._snapshot.binding_for(capability)

    def organized_work_snapshot(self) -> OrganizedWorkSnapshot:
        return self._organized_work.snapshot()
