from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityAssessment,
    GovernedReasoningQualityStatus,
)


@dataclass(frozen=True)
class GovernedDerivedReasoningQualityContextAssessment:
    """Read-only reasoning-quality assessment exposed through reasoning context."""

    assessment_id: str
    quality_assessment_id: str
    status: GovernedReasoningQualityStatus
    source_hypothesis_deepening_report_id: str
    source_epistemic_sufficiency_assessment_id: str
    source_hypothesis_update_semantics_report_id: str | None
    source_multi_hypothesis_discrimination_report_id: str | None
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-derived-reasoning-quality-context-v1"
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
    invokes_reflection: bool = False
    invokes_curiosity: bool = False
    invokes_planning: bool = False
    invokes_execution: bool = False
    invokes_learning: bool = False
    corrects_reasoning: bool = False
    reruns_reasoning: bool = False
    changes_conclusion: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("derived-reasoning-quality-"):
            raise ValueError("derived reasoning quality context identifier is invalid")
        if not self.quality_assessment_id.startswith("reasoning-quality-"):
            raise ValueError("derived reasoning quality requires assessment lineage")
        if not self.source_hypothesis_deepening_report_id.strip():
            raise ValueError("derived reasoning quality requires deepening lineage")
        if not self.source_epistemic_sufficiency_assessment_id.strip():
            raise ValueError("derived reasoning quality requires sufficiency lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("derived reasoning quality requires source lineage")
        if not self.rationale_codes:
            raise ValueError("derived reasoning quality requires rationale")
        if len(self.source_fingerprint) != 64:
            raise ValueError("derived reasoning quality fingerprint must be SHA-256")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "derived reasoning quality must preserve reasoning authority"
            )
        if not self.derived or not self.read_only or self.is_evidence or self.is_claim:
            raise ValueError(
                "derived reasoning quality must remain non-evidence context"
            )
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.closes_reasoning,
                self.authorizes_stopping,
                self.invokes_reasoning,
                self.invokes_reflection,
                self.invokes_curiosity,
                self.invokes_planning,
                self.invokes_execution,
                self.invokes_learning,
                self.corrects_reasoning,
                self.reruns_reasoning,
                self.changes_conclusion,
                self.creates_memory,
                self.creates_learning_candidate,
                self.grants_authority,
            )
        ):
            raise ValueError(
                "derived reasoning quality context violates governed limits"
            )

    @classmethod
    def from_assessment(
        cls,
        assessment: GovernedReasoningQualityAssessment,
    ) -> GovernedDerivedReasoningQualityContextAssessment:
        payload = repr(
            (
                assessment.assessment_id,
                assessment.status.value,
                assessment.source_hypothesis_deepening_report_id,
                assessment.source_epistemic_sufficiency_assessment_id,
                assessment.source_hypothesis_update_semantics_report_id,
                assessment.source_multi_hypothesis_discrimination_report_id,
                assessment.source_reference,
                assessment.world_snapshot_id,
                assessment.rationale_codes,
                assessment.source_fingerprint,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return cls(
            assessment_id=f"derived-reasoning-quality-{fingerprint[:24]}",
            quality_assessment_id=assessment.assessment_id,
            status=assessment.status,
            source_hypothesis_deepening_report_id=(
                assessment.source_hypothesis_deepening_report_id
            ),
            source_epistemic_sufficiency_assessment_id=(
                assessment.source_epistemic_sufficiency_assessment_id
            ),
            source_hypothesis_update_semantics_report_id=(
                assessment.source_hypothesis_update_semantics_report_id
            ),
            source_multi_hypothesis_discrimination_report_id=(
                assessment.source_multi_hypothesis_discrimination_report_id
            ),
            source_reference=assessment.source_reference,
            world_snapshot_id=assessment.world_snapshot_id,
            rationale_codes=assessment.rationale_codes,
            source_fingerprint=fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "derived_reasoning_quality_assessment",
            "quality_assessment_id": self.quality_assessment_id,
            "status": self.status.value,
            "source_hypothesis_deepening_report_id": (
                self.source_hypothesis_deepening_report_id
            ),
            "source_epistemic_sufficiency_assessment_id": (
                self.source_epistemic_sufficiency_assessment_id
            ),
            "source_hypothesis_update_semantics_report_id": (
                self.source_hypothesis_update_semantics_report_id
            ),
            "source_multi_hypothesis_discrimination_report_id": (
                self.source_multi_hypothesis_discrimination_report_id
            ),
            "source_reference": self.source_reference,
            "world_snapshot_id": self.world_snapshot_id,
            "rationale_codes": list(self.rationale_codes),
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "establishes_truth": self.establishes_truth,
            "establishes_falsity": self.establishes_falsity,
            "closes_reasoning": self.closes_reasoning,
            "authorizes_stopping": self.authorizes_stopping,
            "invokes_reflection": self.invokes_reflection,
            "corrects_reasoning": self.corrects_reasoning,
            "reruns_reasoning": self.reruns_reasoning,
            "changes_conclusion": self.changes_conclusion,
        }

