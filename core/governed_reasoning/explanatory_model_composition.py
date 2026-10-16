from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningStatus,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
    HypothesisPairRelation,
    MultiHypothesisDiscriminationStatus,
)


class ExplanatoryModelCompositionStatus(StrEnum):
    MODEL_CANDIDATE = "model_candidate"
    INSUFFICIENT_HYPOTHESES = "insufficient_hypotheses"
    SOURCE_REVIEW_REQUIRED = "source_review_required"
    DEGRADED = "degraded"
    LINEAGE_MISMATCH = "lineage_mismatch"


@dataclass(frozen=True)
class ExplanatoryHypothesisComponent:
    hypothesis_id: str
    proposition: str
    evidence_relation: HypothesisEvidenceRelation
    evidence_references: tuple[str, ...]
    unresolved_gap_ids: tuple[str, ...]


@dataclass(frozen=True)
class ExplanatoryHypothesisRelation:
    left_hypothesis_id: str
    right_hypothesis_id: str
    relation: HypothesisPairRelation


@dataclass(frozen=True)
class GovernedExplanatoryModelCandidate:
    model_id: str
    status: ExplanatoryModelCompositionStatus
    source_report_id: str
    discrimination_report_id: str
    source_reference: str
    world_snapshot_id: str
    components: tuple[ExplanatoryHypothesisComponent, ...]
    relations: tuple[ExplanatoryHypothesisRelation, ...]
    unresolved_requirement_ids: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    establishes_truth: bool = False
    establishes_causality: bool = False
    creates_questions: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    executes_transfer: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.model_id.startswith("explanatory-model-"):
            raise ValueError("explanatory model identifier is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("explanatory model must preserve reasoning authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_facts,
                self.establishes_truth,
                self.establishes_causality,
                self.creates_questions,
                self.creates_learning,
                self.modifies_memory,
                self.modifies_world_model,
                self.executes_transfer,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("explanatory model violates governed limits")
        component_ids = tuple(item.hypothesis_id for item in self.components)
        if len(component_ids) != len(set(component_ids)):
            raise ValueError("explanatory model components must be unique")
        if any(
            item.left_hypothesis_id not in component_ids
            or item.right_hypothesis_id not in component_ids
            for item in self.relations
        ):
            raise ValueError("explanatory relations must reference model components")
        if self.status is ExplanatoryModelCompositionStatus.MODEL_CANDIDATE:
            if len(self.components) < 2:
                raise ValueError("explanatory model requires multiple hypotheses")


class GovernedExplanatoryModelComposer:
    """Compose a bounded explanatory model from already-governed hypotheses."""

    def compose(
        self,
        source: GovernedHypothesisDeepeningReport,
        discrimination: GovernedMultiHypothesisDiscriminationReport,
    ) -> GovernedExplanatoryModelCandidate:
        if (
            source.source_reference != discrimination.source_reference
            or source.world_snapshot_id != discrimination.world_snapshot_id
        ):
            return self._empty(
                source,
                discrimination,
                ExplanatoryModelCompositionStatus.LINEAGE_MISMATCH,
            )
        if source.status is HypothesisDeepeningStatus.DEGRADED or (
            discrimination.status is MultiHypothesisDiscriminationStatus.DEGRADED
        ):
            return self._empty(
                source,
                discrimination,
                ExplanatoryModelCompositionStatus.DEGRADED,
            )
        if source.status is HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED or (
            discrimination.status
            is MultiHypothesisDiscriminationStatus.SOURCE_REVIEW_REQUIRED
        ):
            return self._empty(
                source,
                discrimination,
                ExplanatoryModelCompositionStatus.SOURCE_REVIEW_REQUIRED,
            )
        if len(source.assessments) < 2 or (
            discrimination.status
            is MultiHypothesisDiscriminationStatus.INSUFFICIENT_HYPOTHESES
        ):
            return self._empty(
                source,
                discrimination,
                ExplanatoryModelCompositionStatus.INSUFFICIENT_HYPOTHESES,
            )

        gaps = {}
        for gap in source.epistemic_gaps:
            gaps.setdefault(gap.hypothesis_id, []).append(gap.gap_id)
        components = tuple(
            ExplanatoryHypothesisComponent(
                hypothesis_id=item.hypothesis_id,
                proposition=item.proposition,
                evidence_relation=item.relation,
                evidence_references=tuple(sorted(item.evidence_references)),
                unresolved_gap_ids=tuple(sorted(gaps.get(item.hypothesis_id, ()))),
            )
            for item in sorted(
                source.assessments,
                key=lambda value: value.hypothesis_id,
            )
        )
        relations = tuple(
            ExplanatoryHypothesisRelation(
                left_hypothesis_id=item.left_hypothesis_id,
                right_hypothesis_id=item.right_hypothesis_id,
                relation=item.relation,
            )
            for item in sorted(
                discrimination.comparisons,
                key=lambda value: (
                    value.left_hypothesis_id,
                    value.right_hypothesis_id,
                ),
            )
        )
        requirements = tuple(
            sorted(
                item.requirement_id
                for item in discrimination.discrimination_requirements
            )
        )
        fingerprint = self._fingerprint(
            source,
            discrimination,
            components,
            relations,
            requirements,
        )
        return GovernedExplanatoryModelCandidate(
            model_id=f"explanatory-model-{fingerprint[:24]}",
            status=ExplanatoryModelCompositionStatus.MODEL_CANDIDATE,
            source_report_id=source.report_id,
            discrimination_report_id=discrimination.report_id,
            source_reference=source.source_reference,
            world_snapshot_id=source.world_snapshot_id,
            components=components,
            relations=relations,
            unresolved_requirement_ids=requirements,
            source_fingerprint=fingerprint,
        )

    def _empty(self, source, discrimination, status):
        fingerprint = self._fingerprint(
            source,
            discrimination,
            (),
            (),
            (),
            status.value,
        )
        return GovernedExplanatoryModelCandidate(
            model_id=f"explanatory-model-{fingerprint[:24]}",
            status=status,
            source_report_id=source.report_id,
            discrimination_report_id=discrimination.report_id,
            source_reference=source.source_reference,
            world_snapshot_id=source.world_snapshot_id,
            components=(),
            relations=(),
            unresolved_requirement_ids=(),
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _fingerprint(
        source,
        discrimination,
        components,
        relations,
        requirements,
        extra="",
    ):
        return sha256(
            repr(
                (
                    source.report_id,
                    discrimination.report_id,
                    source.source_reference,
                    source.world_snapshot_id,
                    components,
                    relations,
                    requirements,
                    extra,
                )
            ).encode("utf-8")
        ).hexdigest()
