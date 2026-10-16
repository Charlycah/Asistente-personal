from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.governed_reasoning.hypothesis_deepening import (
        HypothesisEvidenceRelation,
    )
    from core.governed_reasoning.hypothesis_epistemic_delta import (
        HypothesisEpistemicDeltaKind,
    )
    from core.governed_reasoning.hypothesis_update_semantics import (
        HypothesisUpdateSemantic,
    )


@dataclass(frozen=True)
class GovernedDerivedEpistemicAssessment:
    """Derived hypothesis update made available to governed reasoning context."""

    assessment_id: str
    semantic_report_id: str
    hypothesis_id: str
    delta_kind: HypothesisEpistemicDeltaKind
    semantic: HypothesisUpdateSemantic
    before_relation: HypothesisEvidenceRelation | None
    after_relation: HypothesisEvidenceRelation | None
    triggering_evidence_references: tuple[str, ...]
    added_evidence_references: tuple[str, ...]
    source_reference: str
    before_world_snapshot_id: str
    after_world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-derived-epistemic-assessment-v1"
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    is_claim: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    assigns_probability: bool = False
    modifies_hypothesis: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("derived-epistemic-assessment-"):
            raise ValueError("derived assessment identifier is invalid")
        for value, label in (
            (self.semantic_report_id, "semantic report"),
            (self.hypothesis_id, "hypothesis"),
            (self.source_reference, "source"),
            (self.before_world_snapshot_id, "before snapshot"),
            (self.after_world_snapshot_id, "after snapshot"),
        ):
            if not value.strip():
                raise ValueError(f"derived assessment requires {label} lineage")
        if not self.triggering_evidence_references:
            raise ValueError("derived assessment requires triggering evidence")
        if not self.rationale_codes:
            raise ValueError("derived assessment requires rationale codes")
        if len(self.source_fingerprint) != 64:
            raise ValueError("derived assessment fingerprint must be SHA-256")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("derived assessment must preserve reasoning authority")
        if not self.derived or not self.read_only or self.is_evidence or self.is_claim:
            raise ValueError("derived assessment must remain non-evidence context")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.assigns_probability,
                self.modifies_hypothesis,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.grants_authority,
            )
        ):
            raise ValueError("derived assessment violates governed limits")

    @classmethod
    def build(
        cls,
        *,
        semantic_report_id: str,
        hypothesis_id: str,
        delta_kind: HypothesisEpistemicDeltaKind,
        semantic: HypothesisUpdateSemantic,
        before_relation: HypothesisEvidenceRelation | None,
        after_relation: HypothesisEvidenceRelation | None,
        triggering_evidence_references: tuple[str, ...],
        added_evidence_references: tuple[str, ...],
        source_reference: str,
        before_world_snapshot_id: str,
        after_world_snapshot_id: str,
        rationale_codes: tuple[str, ...],
    ) -> GovernedDerivedEpistemicAssessment:
        payload = repr(
            (
                semantic_report_id,
                hypothesis_id,
                delta_kind.value,
                semantic.value,
                before_relation.value if before_relation is not None else None,
                after_relation.value if after_relation is not None else None,
                triggering_evidence_references,
                added_evidence_references,
                source_reference,
                before_world_snapshot_id,
                after_world_snapshot_id,
                rationale_codes,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return cls(
            assessment_id=f"derived-epistemic-assessment-{fingerprint[:24]}",
            semantic_report_id=semantic_report_id,
            hypothesis_id=hypothesis_id,
            delta_kind=delta_kind,
            semantic=semantic,
            before_relation=before_relation,
            after_relation=after_relation,
            triggering_evidence_references=triggering_evidence_references,
            added_evidence_references=added_evidence_references,
            source_reference=source_reference,
            before_world_snapshot_id=before_world_snapshot_id,
            after_world_snapshot_id=after_world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "derived_epistemic_assessment",
            "semantic_report_id": self.semantic_report_id,
            "hypothesis_id": self.hypothesis_id,
            "delta_kind": self.delta_kind.value,
            "semantic": self.semantic.value,
            "before_relation": (
                self.before_relation.value if self.before_relation is not None else None
            ),
            "after_relation": (
                self.after_relation.value if self.after_relation is not None else None
            ),
            "triggering_evidence_references": list(
                self.triggering_evidence_references
            ),
            "added_evidence_references": list(self.added_evidence_references),
            "source_reference": self.source_reference,
            "before_world_snapshot_id": self.before_world_snapshot_id,
            "after_world_snapshot_id": self.after_world_snapshot_id,
            "rationale_codes": list(self.rationale_codes),
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "establishes_truth": self.establishes_truth,
            "establishes_falsity": self.establishes_falsity,
        }
