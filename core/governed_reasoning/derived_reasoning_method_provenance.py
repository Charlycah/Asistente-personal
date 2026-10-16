from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from core.governed_reasoning.reasoning_method_provenance import (
    GovernedReasoningMethodOperationKind,
    GovernedReasoningMethodProvenance,
)


@dataclass(frozen=True)
class GovernedReasoningMethodProvenanceContextItem:
    """Neutral read-only projection of reasoning method provenance into context."""

    assessment_id: str
    provenance_id: str
    source_kind: str
    source_reference: str
    world_snapshot_id: str
    operation_kinds: tuple[GovernedReasoningMethodOperationKind, ...]
    source_hypothesis_deepening_report_id: str
    source_multi_hypothesis_discrimination_report_id: str | None
    source_hypothesis_epistemic_delta_report_id: str | None
    source_hypothesis_update_semantics_report_id: str | None
    source_epistemic_sufficiency_assessment_id: str | None
    source_reasoning_quality_assessment_id: str | None
    method_fingerprint: str
    source_fingerprint: str
    schema_version: str = "post-m409.1-reasoning-method-provenance-context-v1"
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    is_claim: bool = False
    evaluates_effectiveness: bool = False
    ranks_methods: bool = False
    selects_method: bool = False
    recommends_method: bool = False
    establishes_causality: bool = False
    establishes_truth: bool = False
    assigns_probability: bool = False
    modifies_reasoning: bool = False
    reruns_reasoning: bool = False
    invokes_curiosity: bool = False
    invokes_reflection: bool = False
    creates_learning_candidate: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("reasoning-method-context-"):
            raise ValueError("reasoning method context identifier is invalid")
        if not self.provenance_id.startswith("reasoning-method-provenance-"):
            raise ValueError("reasoning method context requires provenance lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("reasoning method context requires source lineage")
        if not self.operation_kinds:
            raise ValueError("reasoning method context requires operations")
        if not self.method_fingerprint.strip() or not self.source_fingerprint.strip():
            raise ValueError("reasoning method context requires fingerprints")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("reasoning method context must preserve authority")
        if not self.derived or not self.read_only or self.is_evidence or self.is_claim:
            raise ValueError("reasoning method context must remain derived context")
        if any(
            (
                self.evaluates_effectiveness,
                self.ranks_methods,
                self.selects_method,
                self.recommends_method,
                self.establishes_causality,
                self.establishes_truth,
                self.assigns_probability,
                self.modifies_reasoning,
                self.reruns_reasoning,
                self.invokes_curiosity,
                self.invokes_reflection,
                self.creates_learning_candidate,
                self.persists_results,
                self.creates_memory,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("reasoning method context violates governed limits")

    @classmethod
    def from_provenance(
        cls,
        provenance: GovernedReasoningMethodProvenance,
    ) -> GovernedReasoningMethodProvenanceContextItem:
        fingerprint = sha256(
            repr(
                (
                    provenance.provenance_id,
                    provenance.source_fingerprint,
                    provenance.method_fingerprint,
                )
            ).encode("utf-8")
        ).hexdigest()
        return cls(
            assessment_id=f"reasoning-method-context-{fingerprint[:24]}",
            provenance_id=provenance.provenance_id,
            source_kind=provenance.source_kind.value,
            source_reference=provenance.source_reference,
            world_snapshot_id=provenance.world_snapshot_id,
            operation_kinds=provenance.operation_kinds,
            source_hypothesis_deepening_report_id=(
                provenance.source_hypothesis_deepening_report_id
            ),
            source_multi_hypothesis_discrimination_report_id=(
                provenance.source_multi_hypothesis_discrimination_report_id
            ),
            source_hypothesis_epistemic_delta_report_id=(
                provenance.source_hypothesis_epistemic_delta_report_id
            ),
            source_hypothesis_update_semantics_report_id=(
                provenance.source_hypothesis_update_semantics_report_id
            ),
            source_epistemic_sufficiency_assessment_id=(
                provenance.source_epistemic_sufficiency_assessment_id
            ),
            source_reasoning_quality_assessment_id=(
                provenance.source_reasoning_quality_assessment_id
            ),
            method_fingerprint=provenance.method_fingerprint,
            source_fingerprint=provenance.source_fingerprint,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "reasoning_method_provenance",
            "provenance_id": self.provenance_id,
            "source_kind": self.source_kind,
            "source_reference": self.source_reference,
            "world_snapshot_id": self.world_snapshot_id,
            "operation_kinds": [item.value for item in self.operation_kinds],
            "source_hypothesis_deepening_report_id": (
                self.source_hypothesis_deepening_report_id
            ),
            "source_multi_hypothesis_discrimination_report_id": (
                self.source_multi_hypothesis_discrimination_report_id
            ),
            "source_hypothesis_epistemic_delta_report_id": (
                self.source_hypothesis_epistemic_delta_report_id
            ),
            "source_hypothesis_update_semantics_report_id": (
                self.source_hypothesis_update_semantics_report_id
            ),
            "source_epistemic_sufficiency_assessment_id": (
                self.source_epistemic_sufficiency_assessment_id
            ),
            "source_reasoning_quality_assessment_id": (
                self.source_reasoning_quality_assessment_id
            ),
            "method_fingerprint": self.method_fingerprint,
            "source_fingerprint": self.source_fingerprint,
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "evaluates_effectiveness": self.evaluates_effectiveness,
            "ranks_methods": self.ranks_methods,
            "selects_method": self.selects_method,
            "recommends_method": self.recommends_method,
            "establishes_causality": self.establishes_causality,
            "establishes_truth": self.establishes_truth,
            "assigns_probability": self.assigns_probability,
            "modifies_reasoning": self.modifies_reasoning,
            "reruns_reasoning": self.reruns_reasoning,
        }

