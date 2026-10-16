from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationReport,
    IntelligentPersonalOrganizationView,
)
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    PartialCanonicalOrganizationSnapshot,
)


@dataclass(frozen=True)
class PartialOrganizationM3915Consumption:
    """Read-only M391.5 consumption of an already acquired partial snapshot."""

    organization: IntelligentPersonalOrganizationReport
    organization_snapshot_fingerprint: str
    source_availability: tuple[
        tuple[OrganizationSourceKind, OrganizationSourceAvailability], ...
    ]
    source_fingerprint: str
    schema_version: str = "post-m409.1-partial-organization-m391.5-consumption-v2"
    canonical_authority: str = "PersonalOrganizationAuthority"
    read_only: bool = True
    partial: bool = True
    tasks_available: bool = False
    agenda_available: bool = False
    notes_available: bool = False
    persists_results: bool = False
    modifies_organization: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "PersonalOrganizationAuthority":
            raise ValueError("M391.5 canonical authority must be preserved")
        if not self.organization_snapshot_fingerprint.strip():
            raise ValueError("organization snapshot fingerprint must not be blank")
        if not self.source_fingerprint.strip():
            raise ValueError("organization consumption fingerprint must not be blank")
        source_kinds = tuple(kind for kind, _ in self.source_availability)
        canonical = tuple(OrganizationSourceKind)
        historical = tuple(
            kind for kind in OrganizationSourceKind
            if kind is not OrganizationSourceKind.NOTES
        )
        if source_kinds not in (canonical, historical):
            raise ValueError("organization consumption sources are not canonical")
        tasks = dict(self.source_availability)[OrganizationSourceKind.TASKS]
        expected_tasks_available = (
            tasks is not OrganizationSourceAvailability.UNAVAILABLE
        )
        if self.tasks_available is not expected_tasks_available:
            raise ValueError("tasks availability must match the canonical snapshot")
        agenda = dict(self.source_availability)[OrganizationSourceKind.AGENDA]
        expected_agenda_available = (
            agenda is not OrganizationSourceAvailability.UNAVAILABLE
        )
        if self.agenda_available is not expected_agenda_available:
            raise ValueError("agenda availability must match the canonical snapshot")
        availability = dict(self.source_availability)
        notes = availability.get(
            OrganizationSourceKind.NOTES,
            OrganizationSourceAvailability.UNAVAILABLE,
        )
        expected_notes_available = (
            notes is not OrganizationSourceAvailability.UNAVAILABLE
        )
        if self.notes_available is not expected_notes_available:
            raise ValueError("notes availability must match the canonical snapshot")
        if any(
            (
                not self.read_only,
                not self.partial,
                self.tasks_available
                and tasks is OrganizationSourceAvailability.UNAVAILABLE,
                self.agenda_available
                and agenda is OrganizationSourceAvailability.UNAVAILABLE,
                self.notes_available
                and notes is OrganizationSourceAvailability.UNAVAILABLE,
                self.persists_results,
                self.modifies_organization,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("organization consumption violates governed limits")


@dataclass(frozen=True)
class PartialOrganizationM3915Consumer:
    """Consume partial organization evidence through existing M391.5 only."""

    def consume(
        self,
        snapshot: PartialCanonicalOrganizationSnapshot,
    ) -> PartialOrganizationM3915Consumption:
        if not snapshot.read_only or not snapshot.partial:
            raise ValueError("M391.5 consumption requires a read-only partial snapshot")
        organization = IntelligentPersonalOrganizationView().organize(snapshot.items)
        availability = tuple(
            (kind, snapshot.source_for(kind).availability)
            for kind in OrganizationSourceKind
        )
        fingerprint = sha256(
            "\n".join(
                (
                    "post-m409.1-partial-organization-m391.5-consumption-v2",
                    snapshot.source_fingerprint,
                    organization.source_fingerprint,
                    *(f"{kind.value}:{state.value}" for kind, state in availability),
                )
            ).encode("utf-8")
        ).hexdigest()
        return PartialOrganizationM3915Consumption(
            organization=organization,
            organization_snapshot_fingerprint=snapshot.source_fingerprint,
            source_availability=availability,
            source_fingerprint=fingerprint,
            tasks_available=(
                snapshot.tasks.availability
                is not OrganizationSourceAvailability.UNAVAILABLE
            ),
            agenda_available=(
                snapshot.source_for(OrganizationSourceKind.AGENDA).availability
                is not OrganizationSourceAvailability.UNAVAILABLE
            ),
            notes_available=(
                snapshot.source_for(OrganizationSourceKind.NOTES).availability
                is not OrganizationSourceAvailability.UNAVAILABLE
            ),
        )
