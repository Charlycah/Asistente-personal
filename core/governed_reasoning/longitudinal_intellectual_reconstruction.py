from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Any


class LongitudinalIntellectualReconstructionDimensionStatus(StrEnum):
    AVAILABLE = "available"
    SUPPORTED = "supported"
    INSUFFICIENT = "insufficient"
    NOT_RECONSTRUCTABLE = "not_reconstructable"
    NOT_COMPARABLE = "not_comparable"
    CHANGED = "changed"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class LongitudinalIntellectualPriorEstablishedEpistemicSupport:
    status: str
    evidence_references: tuple[str, ...]
    source_reference: str
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    modifies_world_model: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.status.strip():
            raise ValueError("prior epistemic support requires status")
        if not self.evidence_references:
            raise ValueError("prior epistemic support requires evidence")
        if not self.source_reference.strip():
            raise ValueError("prior epistemic support requires source")
        if len(self.source_fingerprint) != 64:
            raise ValueError("prior epistemic support fingerprint must be SHA-256")


@dataclass(frozen=True)
class LongitudinalIntellectualCurrentEpistemicView:
    assessment_id: str
    status: str
    evidence_references: tuple[str, ...]
    open_state_references: tuple[str, ...]
    source_reference: str
    source_fingerprint: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.assessment_id, "assessment"),
            (self.status, "status"),
            (self.source_reference, "source"),
        ):
            if not value.strip():
                raise ValueError(f"current epistemic view requires {label}")
        if len(self.source_fingerprint) != 64:
            raise ValueError("current epistemic view fingerprint must be SHA-256")


@dataclass(frozen=True)
class GovernedLongitudinalIntellectualReconstruction:
    prior_antecedent_status: LongitudinalIntellectualReconstructionDimensionStatus
    previously_established_status: LongitudinalIntellectualReconstructionDimensionStatus
    uncertainty_status: LongitudinalIntellectualReconstructionDimensionStatus
    change_status: LongitudinalIntellectualReconstructionDimensionStatus
    open_status: LongitudinalIntellectualReconstructionDimensionStatus
    evidence_references: tuple[str, ...]
    source_references: tuple[str, ...]
    source_fingerprint: str
    assessment_id: str = ""
    schema_version: str = "post-integration-longitudinal-intellectual-reconstruction-v1"
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    is_claim: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    invokes_investigation: bool = False
    invokes_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False
    authorizes_longitudinal_identity: bool = False
    authorizes_autonomous_continuation: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "longitudinal_intellectual_reconstruction",
            "prior_antecedent_status": self.prior_antecedent_status.value,
            "previously_established_status": self.previously_established_status.value,
            "uncertainty_status": self.uncertainty_status.value,
            "change_status": self.change_status.value,
            "open_status": self.open_status.value,
            "evidence_references": list(self.evidence_references),
            "source_references": list(self.source_references),
            "source_fingerprint": self.source_fingerprint,
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "establishes_truth": self.establishes_truth,
            "establishes_falsity": self.establishes_falsity,
        }


@dataclass(frozen=True)
class GovernedRecalledAntecedentAdmission:
    antecedent_reference: str
    antecedent_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    authorizes_longitudinal_identity: bool = False


class GovernedLongitudinalIntellectualReconstructionFoundationV1:
    CANONICAL_AUTHORITY = "governed_reasoning"

    def admit_recalled_antecedent(
        self, *, candidates: tuple[Any, ...]
    ) -> GovernedRecalledAntecedentAdmission | None:
        """Admit only one exact recalled candidate; otherwise abstain."""
        if len(candidates) != 1:
            return None
        candidate = candidates[0]
        reference = getattr(candidate, "scoped_memory_reference", "")
        fingerprint = getattr(candidate, "content_fingerprint", "")
        if not isinstance(reference, str) or not reference.strip():
            return None
        if not isinstance(fingerprint, str) or len(fingerprint) != 64:
            return None
        return GovernedRecalledAntecedentAdmission(
            antecedent_reference=reference,
            antecedent_fingerprint=fingerprint,
        )

    def reconstruct(
        self,
        *,
        recalled_antecedent_reference: str,
        recalled_antecedent_fingerprint: str,
        recalled_evidence_references: tuple[str, ...],
        current_epistemic_assessment: (
            LongitudinalIntellectualCurrentEpistemicView | None
        ),
        epistemic_delta: Any | None,
        open_state_references: tuple[str, ...],
        prior_established_epistemic_support: (
            LongitudinalIntellectualPriorEstablishedEpistemicSupport | None
        ) = None,
    ) -> GovernedLongitudinalIntellectualReconstruction:
        if not recalled_antecedent_reference.strip():
            raise ValueError("reconstruction requires a recalled antecedent reference")
        if len(recalled_antecedent_fingerprint) != 64:
            raise ValueError("recalled antecedent fingerprint must be SHA-256")

        evidence = list(recalled_evidence_references)
        sources = [recalled_antecedent_reference]
        previously_established = (
            LongitudinalIntellectualReconstructionDimensionStatus.NOT_RECONSTRUCTABLE
        )
        if prior_established_epistemic_support is not None:
            evidence.extend(prior_established_epistemic_support.evidence_references)
            sources.append(prior_established_epistemic_support.source_reference)
            prior_status = prior_established_epistemic_support.status.strip().lower()
            if prior_status == "supported":
                previously_established = (
                    LongitudinalIntellectualReconstructionDimensionStatus.SUPPORTED
                )
            else:
                previously_established = (
                    LongitudinalIntellectualReconstructionDimensionStatus.INSUFFICIENT
                )
        uncertainty = LongitudinalIntellectualReconstructionDimensionStatus.INSUFFICIENT
        open_status = LongitudinalIntellectualReconstructionDimensionStatus.INSUFFICIENT

        if current_epistemic_assessment is not None:
            evidence.extend(current_epistemic_assessment.evidence_references)
            sources.append(current_epistemic_assessment.source_reference)
            if current_epistemic_assessment.status.strip().lower() in {
                "insufficient",
                "indeterminate",
                "uncertain",
            }:
                uncertainty = (
                    LongitudinalIntellectualReconstructionDimensionStatus.SUPPORTED
                )
            current_open = set(current_epistemic_assessment.open_state_references)
            if current_open.intersection(open_state_references):
                open_status = (
                    LongitudinalIntellectualReconstructionDimensionStatus.SUPPORTED
                )
                sources.extend(
                    item for item in open_state_references if item in current_open
                )

        change_status = (
            LongitudinalIntellectualReconstructionDimensionStatus.NOT_COMPARABLE
        )
        if epistemic_delta is not None:
            kind = getattr(epistemic_delta, "kind", None)
            kind_value = getattr(kind, "value", kind)
            if kind_value == "unchanged":
                change_status = (
                    LongitudinalIntellectualReconstructionDimensionStatus.UNCHANGED
                )
            elif kind_value is not None:
                change_status = (
                    LongitudinalIntellectualReconstructionDimensionStatus.CHANGED
                )
            for name in (
                "before_evidence_references",
                "after_evidence_references",
                "triggering_evidence_references",
            ):
                evidence.extend(getattr(epistemic_delta, name, ()) or ())

        evidence_tuple = tuple(dict.fromkeys(evidence))
        source_tuple = tuple(dict.fromkeys(sources))
        payload = repr(
            (
                recalled_antecedent_reference,
                recalled_antecedent_fingerprint,
                evidence_tuple,
                source_tuple,
                uncertainty.value,
                change_status.value,
                open_status.value,
                previously_established.value,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return GovernedLongitudinalIntellectualReconstruction(
            assessment_id=(
                f"longitudinal-intellectual-reconstruction-{fingerprint[:24]}"
            ),
            prior_antecedent_status=(
                LongitudinalIntellectualReconstructionDimensionStatus.AVAILABLE
            ),
            previously_established_status=previously_established,
            uncertainty_status=uncertainty,
            change_status=change_status,
            open_status=open_status,
            evidence_references=evidence_tuple,
            source_references=source_tuple,
            source_fingerprint=fingerprint,
        )
