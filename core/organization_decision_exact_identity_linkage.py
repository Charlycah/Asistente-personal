from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)
from core.explicit_organization_reference_acquisition import (
    ExplicitOrganizationReferenceAcquisition,
    ExplicitOrganizationReferenceEvidence,
)
from core.governed_decision_advisory import GovernedDecisionOption
from core.partial_canonical_organization_snapshot import (
    OrganizationSourceAvailability,
    OrganizationSourceKind,
    PartialCanonicalOrganizationSnapshot,
)


class OrganizationDecisionIdentityKind(StrEnum):
    EXPLICIT_ITEM_ID = "explicit_item_id"
    EXPLICIT_SOURCE_REFERENCE = "explicit_source_reference"


class OrganizationDecisionOptionLinkageOutcome(StrEnum):
    LINKED = "linked"
    NO_REFERENCE = "no_reference"
    UNKNOWN_REFERENCE = "unknown_reference"
    SOURCE_UNAVAILABLE = "source_unavailable"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"
    CONFLICTING_REFERENCE = "conflicting_reference"


@dataclass(frozen=True)
class OrganizationDecisionEvidenceBinding:
    option_id: str
    organization_item_id: str
    organization_source_reference: str
    identity_kind: OrganizationDecisionIdentityKind
    organization_fingerprint: str

    def __post_init__(self) -> None:
        if any(
            not value.strip()
            for value in (
                self.option_id,
                self.organization_item_id,
                self.organization_source_reference,
                self.organization_fingerprint,
            )
        ):
            raise ValueError("organization decision binding requires provenance")


@dataclass(frozen=True)
class OrganizationDecisionOptionLinkage:
    option_id: str
    outcome: OrganizationDecisionOptionLinkageOutcome
    organization_item_id: str | None = None

    def __post_init__(self) -> None:
        if not self.option_id.strip():
            raise ValueError("organization decision linkage requires option id")
        if self.outcome is OrganizationDecisionOptionLinkageOutcome.LINKED:
            if self.organization_item_id is None:
                raise ValueError("linked outcome requires organization item id")
        elif self.organization_item_id is not None:
            raise ValueError("non-linked outcome cannot carry organization item id")


@dataclass(frozen=True)
class OrganizationDecisionLinkageResult:
    options: tuple[GovernedDecisionOption, ...]
    bindings: tuple[OrganizationDecisionEvidenceBinding, ...]
    outcomes: tuple[OrganizationDecisionOptionLinkage, ...]
    organization_fingerprint: str
    schema_version: str = "post-m409.1-organization-decision-exact-linkage-v1"
    read_only: bool = True
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.organization_fingerprint.strip():
            raise ValueError("organization linkage fingerprint must not be blank")
        if len(self.options) != len(self.outcomes):
            raise ValueError("organization linkage requires one outcome per option")
        if tuple(item.option_id for item in self.options) != tuple(
            item.option_id for item in self.outcomes
        ):
            raise ValueError("organization linkage must preserve option order")
        linked_ids = {
            outcome.option_id
            for outcome in self.outcomes
            if outcome.outcome is OrganizationDecisionOptionLinkageOutcome.LINKED
        }
        if {binding.option_id for binding in self.bindings} != linked_ids:
            raise ValueError("organization linkage bindings must cover linked outcomes")
        if any(
            (
                not self.read_only,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("organization linkage violates governed limits")


@dataclass(frozen=True)
class OrganizationDecisionExactIdentityLinker:
    """Verify only exact explicit Organization identity for decision options."""

    def link(
        self,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        acquisition: ExplicitOrganizationReferenceAcquisition,
        snapshot: PartialCanonicalOrganizationSnapshot,
    ) -> OrganizationDecisionLinkageResult:
        references = {item.option_id: item for item in acquisition.references}
        adaptation_option_ids = {item.option_id for item in adaptation.options}
        if not set(references).issubset(adaptation_option_ids):
            raise ValueError("organization acquisition references unknown options")

        resolved = []
        for option in adaptation.options:
            outcome, item, identity_kind = self._resolve(
                references.get(option.option_id),
                snapshot,
            )
            resolved.append((option, outcome, item, identity_kind))

        resolved_item_ids = [
            item.item_id for _, _, item, _ in resolved if item is not None
        ]
        duplicated_item_ids = {
            item_id
            for item_id in resolved_item_ids
            if resolved_item_ids.count(item_id) > 1
        }

        options: list[GovernedDecisionOption] = []
        bindings: list[OrganizationDecisionEvidenceBinding] = []
        outcomes: list[OrganizationDecisionOptionLinkage] = []
        for option, outcome, item, identity_kind in resolved:
            if item is not None and item.item_id in duplicated_item_ids:
                outcome = OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE
                item = None
                identity_kind = None
            if item is not None:
                options.append(replace(option, organization_item_id=item.item_id))
                bindings.append(
                    OrganizationDecisionEvidenceBinding(
                        option_id=option.option_id,
                        organization_item_id=item.item_id,
                        organization_source_reference=item.source_reference or "",
                        identity_kind=identity_kind,
                        organization_fingerprint=snapshot.source_fingerprint,
                    )
                )
                outcomes.append(
                    OrganizationDecisionOptionLinkage(
                        option_id=option.option_id,
                        outcome=OrganizationDecisionOptionLinkageOutcome.LINKED,
                        organization_item_id=item.item_id,
                    )
                )
            else:
                options.append(option)
                outcomes.append(
                    OrganizationDecisionOptionLinkage(
                        option_id=option.option_id,
                        outcome=outcome,
                    )
                )

        return OrganizationDecisionLinkageResult(
            options=tuple(options),
            bindings=tuple(bindings),
            outcomes=tuple(outcomes),
            organization_fingerprint=snapshot.source_fingerprint,
        )

    def _resolve(
        self,
        reference: ExplicitOrganizationReferenceEvidence | None,
        snapshot: PartialCanonicalOrganizationSnapshot,
    ):
        if reference is None:
            return OrganizationDecisionOptionLinkageOutcome.NO_REFERENCE, None, None
        if reference.organization_source_reference is not None:
            source_kind = self._source_kind(reference.organization_source_reference)
            source = snapshot.source_for(source_kind)
            if source.availability is OrganizationSourceAvailability.UNAVAILABLE:
                return (
                    OrganizationDecisionOptionLinkageOutcome.SOURCE_UNAVAILABLE,
                    None,
                    None,
                )
            matches = tuple(
                item
                for item in snapshot.items
                if item.source_reference == reference.organization_source_reference
            )
            if len(matches) == 1:
                return (
                    OrganizationDecisionOptionLinkageOutcome.LINKED,
                    matches[0],
                    OrganizationDecisionIdentityKind.EXPLICIT_SOURCE_REFERENCE,
                )
            if len(matches) > 1:
                return (
                    OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE,
                    None,
                    None,
                )
            return (
                OrganizationDecisionOptionLinkageOutcome.UNKNOWN_REFERENCE,
                None,
                None,
            )

        item_id = reference.organization_item_id
        matches = tuple(item for item in snapshot.items if item.item_id == item_id)
        if len(matches) == 1:
            return (
                OrganizationDecisionOptionLinkageOutcome.LINKED,
                matches[0],
                OrganizationDecisionIdentityKind.EXPLICIT_ITEM_ID,
            )
        if len(matches) > 1:
            return (
                OrganizationDecisionOptionLinkageOutcome.AMBIGUOUS_REFERENCE,
                None,
                None,
            )
        return OrganizationDecisionOptionLinkageOutcome.UNKNOWN_REFERENCE, None, None

    @staticmethod
    def _source_kind(source_reference: str) -> OrganizationSourceKind:
        namespace, separator, remainder = source_reference.partition(":")
        if not separator:
            raise ValueError("organization source reference requires namespace")
        if namespace == "knowledge":
            subtype, subtype_separator, _ = remainder.partition(":")
            if subtype_separator and subtype == "note":
                return OrganizationSourceKind.NOTES
        mapping = {
            "goal": OrganizationSourceKind.GOALS,
            "project": OrganizationSourceKind.PROJECTS,
            "reminder": OrganizationSourceKind.REMINDERS,
            "task": OrganizationSourceKind.TASKS,
            "calendar": OrganizationSourceKind.AGENDA,
        }
        try:
            return mapping[namespace]
        except KeyError as exc:
            raise ValueError(
                "organization source reference namespace is unsupported"
            ) from exc
