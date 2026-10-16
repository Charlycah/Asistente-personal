from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdaptation,
)


class ExplicitOrganizationReferenceAcquisitionKind(StrEnum):
    CALLER_STRUCTURED_REFERENCE = "caller_structured_reference"
    UI_STRUCTURED_REFERENCE = "ui_structured_reference"


@dataclass(frozen=True)
class ExplicitOrganizationReference:
    alternative_ordinal: int
    organization_item_id: str | None = None
    organization_source_reference: str | None = None
    acquisition_kind: ExplicitOrganizationReferenceAcquisitionKind = (
        ExplicitOrganizationReferenceAcquisitionKind.CALLER_STRUCTURED_REFERENCE
    )

    def __post_init__(self) -> None:
        if self.alternative_ordinal < 0:
            raise ValueError("organization reference ordinal must be non-negative")
        item_id = self.organization_item_id
        source_reference = self.organization_source_reference
        if (item_id is None) == (source_reference is None):
            raise ValueError("organization reference requires exactly one identity")
        if item_id is not None and not item_id.strip():
            raise ValueError("organization item id must not be blank")
        if source_reference is not None and not source_reference.strip():
            raise ValueError("organization source reference must not be blank")
        ExplicitOrganizationReferenceAcquisitionKind(self.acquisition_kind)


@dataclass(frozen=True)
class ExplicitOrganizationReferenceEvidence:
    option_id: str
    alternative_ordinal: int
    source_fingerprint: str
    organization_item_id: str | None
    organization_source_reference: str | None
    acquisition_kind: ExplicitOrganizationReferenceAcquisitionKind

    def __post_init__(self) -> None:
        if not self.option_id.strip() or not self.source_fingerprint.strip():
            raise ValueError("organization reference evidence requires provenance")
        if self.alternative_ordinal < 0:
            raise ValueError("organization reference evidence ordinal is invalid")
        if (self.organization_item_id is None) == (
            self.organization_source_reference is None
        ):
            raise ValueError("organization reference evidence requires one identity")


@dataclass(frozen=True)
class ExplicitOrganizationReferenceAcquisition:
    references: tuple[ExplicitOrganizationReferenceEvidence, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-explicit-organization-reference-v1"
    read_only: bool = True
    infers_identity: bool = False
    queries_organization: bool = False
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.source_fingerprint.strip():
            raise ValueError("organization acquisition fingerprint must not be blank")
        ordinals = tuple(item.alternative_ordinal for item in self.references)
        if ordinals != tuple(sorted(ordinals)):
            raise ValueError("organization acquisition references must be ordered")
        if len(ordinals) != len(set(ordinals)):
            raise ValueError("organization acquisition ordinals must be unique")
        if any(
            (
                not self.read_only,
                self.infers_identity,
                self.queries_organization,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("organization acquisition violates governed limits")


@dataclass(frozen=True)
class ExplicitOrganizationReferenceAcquirer:
    """Bind caller-supplied organization references to certified option identity."""

    def acquire(
        self,
        adaptation: ExplicitDeliberationDecisionOptionAdaptation,
        references: tuple[ExplicitOrganizationReference, ...] = (),
    ) -> ExplicitOrganizationReferenceAcquisition:
        by_ordinal = {
            binding.alternative_ordinal: binding for binding in adaptation.bindings
        }
        if len(by_ordinal) != len(adaptation.bindings):
            raise ValueError("decision option binding ordinals must be unique")
        supplied_ordinals = tuple(item.alternative_ordinal for item in references)
        if len(supplied_ordinals) != len(set(supplied_ordinals)):
            raise ValueError("organization reference ordinals must be unique")

        evidence: list[ExplicitOrganizationReferenceEvidence] = []
        for reference in sorted(references, key=lambda item: item.alternative_ordinal):
            binding = by_ordinal.get(reference.alternative_ordinal)
            if binding is None:
                raise ValueError("organization reference ordinal is unknown")
            evidence.append(
                ExplicitOrganizationReferenceEvidence(
                    option_id=binding.option_id,
                    alternative_ordinal=reference.alternative_ordinal,
                    source_fingerprint=adaptation.source_fingerprint,
                    organization_item_id=reference.organization_item_id,
                    organization_source_reference=(
                        reference.organization_source_reference
                    ),
                    acquisition_kind=reference.acquisition_kind,
                )
            )

        fingerprint = self._fingerprint(adaptation.source_fingerprint, tuple(evidence))
        return ExplicitOrganizationReferenceAcquisition(
            references=tuple(evidence),
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _fingerprint(
        adaptation_fingerprint: str,
        references: tuple[ExplicitOrganizationReferenceEvidence, ...],
    ) -> str:
        rows = [f"adaptation:{adaptation_fingerprint}"]
        rows.extend(
            "|".join(
                (
                    str(item.alternative_ordinal),
                    item.option_id,
                    item.organization_item_id or "",
                    item.organization_source_reference or "",
                    item.acquisition_kind.value,
                )
            )
            for item in references
        )
        return sha256("\n".join(rows).encode("utf-8")).hexdigest()
