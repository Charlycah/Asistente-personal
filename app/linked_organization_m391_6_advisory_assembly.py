from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from app.canonical_decision_facade import CanonicalDecisionFacade
from core.governed_decision_advisory import GovernedDecisionAdvisoryReport
from core.organization_decision_exact_identity_linkage import (
    OrganizationDecisionLinkageResult,
    OrganizationDecisionOptionLinkageOutcome,
)
from core.partial_organization_m391_5_consumption import (
    PartialOrganizationM3915Consumption,
)


@dataclass(frozen=True)
class LinkedOrganizationM3916AdvisoryAssembly:
    """Read-only M391.6 advisory assembled from certified organization evidence."""

    advisory: GovernedDecisionAdvisoryReport
    organization_linkage_fingerprint: str
    organization_consumption_fingerprint: str
    source_fingerprint: str
    schema_version: str = "post-m409.1-linked-organization-m391.6-assembly-v1"
    canonical_facade: str = "CanonicalDecisionFacade"
    read_only: bool = True
    advisory_only: bool = True
    partial_organization: bool = True
    tasks_available: bool = False
    agenda_available: bool = False
    notes_available: bool = False
    persists_results: bool = False
    modifies_organization: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if self.canonical_facade != "CanonicalDecisionFacade":
            raise ValueError("M391.6 canonical decision facade must be preserved")
        if not self.organization_linkage_fingerprint.strip():
            raise ValueError("organization linkage fingerprint must not be blank")
        if not self.organization_consumption_fingerprint.strip():
            raise ValueError("organization consumption fingerprint must not be blank")
        if not self.source_fingerprint.strip():
            raise ValueError(
                "organization advisory assembly fingerprint must not be blank"
            )
        if self.advisory.schema_version != "m391.6":
            raise ValueError("assembly must preserve M391.6 advisory schema")
        if self.advisory.canonical_facade != self.canonical_facade:
            raise ValueError("assembly advisory must use canonical decision facade")
        if any(
            (
                not self.read_only,
                not self.advisory_only,
                not self.partial_organization,
                self.persists_results,
                self.modifies_organization,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            ),
        ):
            raise ValueError("organization advisory assembly violates governed limits")


@dataclass(frozen=True)
class LinkedOrganizationM3916AdvisoryAssembler:
    """Delegate linked partial organization evidence to existing M391.6 only."""

    def assemble(
        self,
        linkage: OrganizationDecisionLinkageResult,
        consumption: PartialOrganizationM3915Consumption,
    ) -> LinkedOrganizationM3916AdvisoryAssembly:
        self._validate_inputs(linkage, consumption)
        advisory = CanonicalDecisionFacade().advise(
            linkage.options,
            organization=consumption.organization,
        )
        fingerprint = sha256(
            "\n".join(
                (
                    "post-m409.1-linked-organization-m391.6-assembly-v1",
                    linkage.organization_fingerprint,
                    consumption.source_fingerprint,
                    advisory.source_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return LinkedOrganizationM3916AdvisoryAssembly(
            advisory=advisory,
            organization_linkage_fingerprint=linkage.organization_fingerprint,
            organization_consumption_fingerprint=consumption.source_fingerprint,
            source_fingerprint=fingerprint,
            tasks_available=consumption.tasks_available,
            agenda_available=consumption.agenda_available,
            notes_available=consumption.notes_available,
        )

    @staticmethod
    def _validate_inputs(
        linkage: OrganizationDecisionLinkageResult,
        consumption: PartialOrganizationM3915Consumption,
    ) -> None:
        if (
            linkage.organization_fingerprint
            != consumption.organization_snapshot_fingerprint
        ):
            raise ValueError("linkage and M391.5 consumption must share one snapshot")
        if not consumption.read_only or not consumption.partial:
            raise ValueError("M391.6 assembly requires governed partial organization")

        recommendation_ids = {
            item.item_id for item in consumption.organization.recommendations
        }
        linked_ids = {
            outcome.organization_item_id
            for outcome in linkage.outcomes
            if outcome.outcome is OrganizationDecisionOptionLinkageOutcome.LINKED
        }
        if None in linked_ids or not linked_ids.issubset(recommendation_ids):
            raise ValueError("linked organization evidence is missing from M391.5")

        if any(
            option.scenario_hypothesis_id is not None
            or option.causal_relation_id is not None
            or option.explicit_preference != 0.0
            for option in linkage.options
        ):
            raise ValueError(
                "organization advisory assembly v1 accepts organization evidence only"
            )
