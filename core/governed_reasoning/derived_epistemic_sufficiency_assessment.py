from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)


@dataclass(frozen=True)
class GovernedDerivedEpistemicSufficiencyContextAssessment:
    """Read-only sufficiency assessment exposed through reasoning context."""

    assessment_id: str
    sufficiency_assessment_id: str
    status: EpistemicSufficiencyStatus
    source_reference: str
    world_snapshot_id: str
    hypothesis_ids: tuple[str, ...]
    unresolved_hypothesis_ids: tuple[str, ...]
    epistemic_gap_ids: tuple[str, ...]
    discrimination_requirement_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-derived-epistemic-sufficiency-context-v1"
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    is_claim: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    closes_reasoning: bool = False
    authorizes_stopping: bool = False
    invokes_reasoning: bool = False
    invokes_curiosity: bool = False
    invokes_planning: bool = False
    invokes_execution: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("derived-epistemic-sufficiency-"):
            raise ValueError("derived sufficiency context identifier is invalid")
        if not self.sufficiency_assessment_id.startswith("epistemic-sufficiency-"):
            raise ValueError("derived sufficiency requires assessment lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("derived sufficiency requires source lineage")
        if not self.rationale_codes:
            raise ValueError("derived sufficiency requires rationale")
        if len(self.source_fingerprint) != 64:
            raise ValueError("derived sufficiency fingerprint must be SHA-256")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("derived sufficiency must preserve reasoning authority")
        if not self.derived or not self.read_only or self.is_evidence or self.is_claim:
            raise ValueError("derived sufficiency must remain non-evidence context")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.closes_reasoning,
                self.authorizes_stopping,
                self.invokes_reasoning,
                self.invokes_curiosity,
                self.invokes_planning,
                self.invokes_execution,
                self.creates_memory,
                self.creates_learning_candidate,
                self.grants_authority,
            )
        ):
            raise ValueError("derived sufficiency context violates governed limits")

    @classmethod
    def from_assessment(
        cls,
        assessment: GovernedEpistemicSufficiencyAssessment,
    ) -> GovernedDerivedEpistemicSufficiencyContextAssessment:
        payload = repr(
            (
                assessment.assessment_id,
                assessment.status.value,
                assessment.source_reference,
                assessment.world_snapshot_id,
                assessment.hypothesis_ids,
                assessment.unresolved_hypothesis_ids,
                assessment.epistemic_gap_ids,
                assessment.discrimination_requirement_ids,
                assessment.rationale_codes,
                assessment.source_fingerprint,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return cls(
            assessment_id=f"derived-epistemic-sufficiency-{fingerprint[:24]}",
            sufficiency_assessment_id=assessment.assessment_id,
            status=assessment.status,
            source_reference=assessment.source_reference,
            world_snapshot_id=assessment.world_snapshot_id,
            hypothesis_ids=assessment.hypothesis_ids,
            unresolved_hypothesis_ids=assessment.unresolved_hypothesis_ids,
            epistemic_gap_ids=assessment.epistemic_gap_ids,
            discrimination_requirement_ids=assessment.discrimination_requirement_ids,
            rationale_codes=assessment.rationale_codes,
            source_fingerprint=fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "derived_epistemic_sufficiency_assessment",
            "sufficiency_assessment_id": self.sufficiency_assessment_id,
            "status": self.status.value,
            "source_reference": self.source_reference,
            "world_snapshot_id": self.world_snapshot_id,
            "hypothesis_ids": list(self.hypothesis_ids),
            "unresolved_hypothesis_ids": list(self.unresolved_hypothesis_ids),
            "epistemic_gap_ids": list(self.epistemic_gap_ids),
            "discrimination_requirement_ids": list(
                self.discrimination_requirement_ids
            ),
            "rationale_codes": list(self.rationale_codes),
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "establishes_truth": self.establishes_truth,
            "establishes_falsity": self.establishes_falsity,
            "closes_reasoning": self.closes_reasoning,
            "authorizes_stopping": self.authorizes_stopping,
        }

