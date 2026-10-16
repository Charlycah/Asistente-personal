from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from core.agenda_evidence import AgendaEventEvidence
from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReference,
    ExplicitOrganizationReferenceAcquirer,
)
from core.organization_decision_exact_identity_linkage import (
    OrganizationDecisionExactIdentityLinker,
    OrganizationDecisionOptionLinkageOutcome,
)
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceUnavailableError,
    PartialCanonicalOrganizationSnapshotBuilder,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumer,
)
from core.personal_knowledge_base import (
    KnowledgeKind,
    KnowledgeOwner,
    KnowledgeStatus,
)
from infrastructure.calendar.calendar_contract import CalendarTimeRange

from .linked_organization_m391_6_advisory_assembly import (
    LinkedOrganizationM3916AdvisoryAssembler,
    LinkedOrganizationM3916AdvisoryAssembly,
)


@dataclass(frozen=True)
class _GoalReadAdapter:
    service: object

    def list_goals(self):
        return tuple(self.service.manager.list())


@dataclass(frozen=True)
class _ProjectReadAdapter:
    service: object

    def list_projects(self):
        return tuple(self.service.manager.list())


@dataclass(frozen=True)
class _TaskReadAdapter:
    service: object

    def list_tasks(self):
        return tuple(self.service.manager.repository.list_tasks())


@dataclass(frozen=True)
class _NotesReadAdapter:
    service: object

    def list_notes(self):
        owner = getattr(self.service, "owner", None)
        if owner is None:
            raise OrganizationSourceUnavailableError(
                "personal knowledge owner scope is unavailable"
            )
        normalized_owner = KnowledgeOwner(owner)
        allowed_owners = {normalized_owner, KnowledgeOwner.SHARED}
        return tuple(
            item
            for item in self.service.manager.repository.list_items()
            if item.normalized_kind is KnowledgeKind.NOTE
            and item.normalized_status is KnowledgeStatus.ACTIVE
            and item.normalized_owner in allowed_owners
        )


@dataclass(frozen=True)
class _AgendaReadAdapter:
    interceptor: object

    def list_agenda_events(self):
        runtime = getattr(self.interceptor, "runtime", None)
        if runtime is None:
            raise OrganizationSourceUnavailableError("calendar runtime is unavailable")
        snapshot = runtime.snapshot()
        if getattr(snapshot.state, "value", None) != "ready":
            raise OrganizationSourceUnavailableError("calendar runtime is not ready")
        provider = runtime.require_provider()
        now = datetime.now(timezone.utc)
        time_range = CalendarTimeRange(
            starts_at=now,
            ends_at=now + timedelta(days=30),
        )
        return tuple(
            AgendaEventEvidence(
                agenda_id=event.event_id,
                title=event.title,
                source_reference=f"calendar:event:{event.event_id}",
            )
            for event in provider.list_events(time_range)
        )


@dataclass(frozen=True)
class _ReminderReadAdapter:
    service: object

    def list_pending_reminders(self):
        connection, repository = self.service._repository()
        try:
            return tuple(repository.list_pending())
        finally:
            connection.close()


@dataclass(frozen=True)
class ProductiveOrganizationAdvisoryWiring:
    """Read-only bridge from official productive organization sources to M391.6."""

    runtime: object

    def assemble(
        self,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        references: tuple[ExplicitOrganizationReference, ...],
    ) -> LinkedOrganizationM3916AdvisoryAssembly | None:
        if not references:
            return None

        acquisition = ExplicitOrganizationReferenceAcquirer().acquire(
            adaptation,
            references,
        )
        snapshot = self._snapshot_builder().build()
        linkage = OrganizationDecisionExactIdentityLinker().link(
            adaptation,
            acquisition,
            snapshot,
        )
        outcomes = tuple(item.outcome for item in linkage.outcomes)
        if OrganizationDecisionOptionLinkageOutcome.LINKED not in outcomes:
            return None
        invalid = {
            OrganizationDecisionOptionLinkageOutcome.UNKNOWN_REFERENCE,
            OrganizationDecisionOptionLinkageOutcome.SOURCE_UNAVAILABLE,
            OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE,
            OrganizationDecisionOptionLinkageOutcome.CONFLICTING_REFERENCE,
        }
        if any(outcome in invalid for outcome in outcomes):
            return None

        consumption = PartialOrganizationM3915Consumer().consume(snapshot)
        return LinkedOrganizationM3916AdvisoryAssembler().assemble(
            linkage,
            consumption,
        )

    def _snapshot_builder(self) -> PartialCanonicalOrganizationSnapshotBuilder:
        registry = self._capability_registry()
        return PartialCanonicalOrganizationSnapshotBuilder(
            goals_port=self._read_adapter(
                registry, "household.goals", _GoalReadAdapter
            ),
            projects_port=self._read_adapter(
                registry,
                "household.projects",
                _ProjectReadAdapter,
            ),
            reminders_port=self._read_adapter(
                registry,
                "resident.reminders",
                _ReminderReadAdapter,
            ),
            tasks_port=self._read_adapter(
                registry,
                "resident.tasks",
                _TaskReadAdapter,
            ),
            agenda_port=self._calendar_read_adapter(registry),
            notes_port=self._read_adapter(
                registry,
                "resident.personal_knowledge",
                _NotesReadAdapter,
            ),
        )

    def _capability_registry(self):
        bootstrap = getattr(self.runtime, "bootstrap", None)
        root = getattr(bootstrap, "root", None)
        dependencies = getattr(root, "dependencies", None)
        return getattr(dependencies, "official_capability_registry", None)

    @staticmethod
    def _calendar_read_adapter(registry):
        if registry is None:
            return None
        registration = registry.registration_for("calendar.read")
        if registration is None:
            return None
        return _AgendaReadAdapter(registration.interceptor)

    @staticmethod
    def _read_adapter(registry, capability_name: str, adapter_type):
        if registry is None:
            return None
        registration = registry.registration_for(capability_name)
        if registration is None:
            return None
        interceptor = registration.interceptor
        service = getattr(interceptor, "service", None)
        if service is None:
            return None
        return adapter_type(service)
