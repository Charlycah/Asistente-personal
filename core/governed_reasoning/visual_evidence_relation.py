from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.governed_reasoning.evidence import EvidenceReference


class VisualEvidenceRelation(StrEnum):
    """Bounded relation between visual context and admitted evidence."""

    CONSISTENT = "consistent"
    TENSION = "tension"
    COMPLEMENTARY = "complementary"
    UNRESOLVED = "unresolved"
    REVIEW = "review"


@dataclass(frozen=True)
class VisualEvidenceRelationAssessment:
    """Read-only derived context; never evidence, a claim, or truth authority."""

    assessment_id: str
    proposition_id: str
    visual_reference_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    relation: VisualEvidenceRelation | str
    rationale_codes: tuple[str, ...]
    canonical_authority: str = "governed_reasoning"
    derived: bool = True
    read_only: bool = True
    is_evidence: bool = False
    is_claim: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    proves_causality: bool = False
    assigns_probability: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    persists_results: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        proposition_id = self.proposition_id.strip()
        relation = VisualEvidenceRelation(self.relation)
        visual_refs = tuple(dict.fromkeys(self.visual_reference_ids))
        evidence_ids = tuple(dict.fromkeys(self.evidence_ids))
        rationale = tuple(item.strip() for item in self.rationale_codes if item.strip())
        if not proposition_id:
            raise ValueError("visual-evidence proposition id must not be blank")
        if not visual_refs:
            raise ValueError("visual-evidence assessment requires visual lineage")
        if not evidence_ids:
            raise ValueError("visual-evidence assessment requires evidence lineage")
        if not rationale:
            raise ValueError("visual-evidence assessment requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "visual-evidence relation must preserve reasoning authority"
            )
        if not self.derived or not self.read_only or self.is_evidence or self.is_claim:
            raise ValueError("visual-evidence assessment must remain derived context")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.proves_causality,
                self.assigns_probability,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.persists_results,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("visual-evidence assessment violates governed limits")
        object.__setattr__(self, "proposition_id", proposition_id)
        object.__setattr__(self, "relation", relation)
        object.__setattr__(self, "visual_reference_ids", visual_refs)
        object.__setattr__(self, "evidence_ids", evidence_ids)
        object.__setattr__(self, "rationale_codes", rationale)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.assessment_id,
            "kind": "visual_evidence_relation_assessment",
            "proposition_id": self.proposition_id,
            "visual_reference_ids": list(self.visual_reference_ids),
            "evidence_ids": list(self.evidence_ids),
            "relation": self.relation.value,
            "rationale_codes": list(self.rationale_codes),
            "canonical_authority": self.canonical_authority,
            "derived": self.derived,
            "read_only": self.read_only,
            "is_evidence": self.is_evidence,
            "is_claim": self.is_claim,
            "establishes_truth": self.establishes_truth,
            "establishes_falsity": self.establishes_falsity,
            "proves_causality": self.proves_causality,
            "assigns_probability": self.assigns_probability,
            "modifies_world_model": self.modifies_world_model,
            "modifies_memory": self.modifies_memory,
            "modifies_learning": self.modifies_learning,
            "persists_results": self.persists_results,
            "executes_actions": self.executes_actions,
            "grants_authority": self.grants_authority,
        }


class GovernedVisualEvidenceRelationEvaluator:
    """Relate admitted visual context to selected evidence without truth claims."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def evaluate(
        self,
        *,
        proposition_id: str,
        owner: str,
        visual: CognitiveRuntimeContribution,
        evidence: tuple[EvidenceReference, ...],
    ) -> VisualEvidenceRelationAssessment:
        proposition = proposition_id.strip()
        normalized_owner = owner.strip()
        if not proposition:
            raise ValueError("visual-evidence proposition id must not be blank")
        if not normalized_owner:
            raise ValueError("visual-evidence owner must not be blank")
        self._validate_visual(visual)
        self._validate_evidence(normalized_owner, evidence)

        relation = VisualEvidenceRelation.UNRESOLVED
        rationale = ("visual_evidence:semantic_relation_not_established",)
        evidence_ids = tuple(item.evidence_id for item in evidence)
        payload = repr(
            (
                proposition,
                visual.reference_ids,
                evidence_ids,
                relation.value,
                rationale,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return VisualEvidenceRelationAssessment(
            assessment_id=f"visual-evidence-relation-{fingerprint[:24]}",
            proposition_id=proposition,
            visual_reference_ids=visual.reference_ids,
            evidence_ids=evidence_ids,
            relation=relation,
            rationale_codes=rationale,
        )

    @staticmethod
    def _validate_visual(visual: CognitiveRuntimeContribution) -> None:
        if visual.stage != "visual_context":
            raise ValueError("visual-evidence relation requires visual context")
        if visual.status is not CognitiveRuntimeStageStatus.APPLIED:
            raise ValueError("visual-evidence relation requires applied visual context")
        if not visual.prompt_lines or not visual.reference_ids:
            raise ValueError("visual-evidence relation requires visual lineage")

    @staticmethod
    def _validate_evidence(
        owner: str,
        evidence: tuple[EvidenceReference, ...],
    ) -> None:
        if not evidence:
            raise ValueError("visual-evidence relation requires selected evidence")
        if any(item.owner not in {owner, "shared"} for item in evidence):
            raise ValueError("visual-evidence relation cannot cross owner boundary")
