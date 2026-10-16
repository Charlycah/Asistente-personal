from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningStatus,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsReport,
    GovernedHypothesisUpdateSemanticsStatus,
    HypothesisUpdateSemantic,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
    MultiHypothesisDiscriminationStatus,
)


class EpistemicSufficiencyStatus(StrEnum):
    SUFFICIENT = "sufficient"
    INSUFFICIENT = "insufficient"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class GovernedEpistemicSufficiencyAssessment:
    assessment_id: str
    status: EpistemicSufficiencyStatus
    source_hypothesis_deepening_report_id: str
    source_multi_hypothesis_discrimination_report_id: str | None
    source_hypothesis_update_semantics_report_id: str | None
    source_reference: str
    world_snapshot_id: str
    hypothesis_ids: tuple[str, ...]
    unresolved_hypothesis_ids: tuple[str, ...]
    epistemic_gap_ids: tuple[str, ...]
    discrimination_requirement_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-epistemic-sufficiency-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    derivational: bool = True
    contextual: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    assigns_probability: bool = False
    closes_reasoning: bool = False
    authorizes_stopping: bool = False
    invokes_reasoning: bool = False
    invokes_comparison: bool = False
    invokes_curiosity: bool = False
    invokes_planning: bool = False
    invokes_capabilities: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    modifies_hypotheses: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("epistemic-sufficiency-"):
            raise ValueError("epistemic sufficiency identifier is invalid")
        if not self.source_hypothesis_deepening_report_id.strip():
            raise ValueError("epistemic sufficiency requires deepening lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("epistemic sufficiency requires source lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("epistemic sufficiency requires rationale codes")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("epistemic sufficiency must preserve reasoning authority")
        if not self.read_only or not self.consultative or not self.derivational:
            raise ValueError("epistemic sufficiency must remain derived and read-only")
        if not self.contextual:
            raise ValueError("epistemic sufficiency must remain contextual")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.assigns_probability,
                self.closes_reasoning,
                self.authorizes_stopping,
                self.invokes_reasoning,
                self.invokes_comparison,
                self.invokes_curiosity,
                self.invokes_planning,
                self.invokes_capabilities,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.modifies_hypotheses,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("epistemic sufficiency violates governed limits")


class GovernedEpistemicSufficiencyAssessmentFoundationV1:
    """Compose existing governed epistemic products into contextual sufficiency."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def assess(
        self,
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None = None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None = None,
    ) -> GovernedEpistemicSufficiencyAssessment:
        self._validate_deepening(deepening)
        self._validate_discrimination(deepening, discrimination)
        self._validate_update_semantics(deepening, update_semantics)

        hypothesis_ids = tuple(item.hypothesis_id for item in deepening.assessments)
        unresolved = tuple(
            item.hypothesis_id
            for item in deepening.assessments
            if item.relation is HypothesisEvidenceRelation.UNRESOLVED
        )
        gap_ids = tuple(item.gap_id for item in deepening.epistemic_gaps)
        requirement_ids = (
            tuple(
                item.requirement_id
                for item in discrimination.discrimination_requirements
            )
            if discrimination is not None
            else ()
        )

        status, rationale = self._derive_status(
            deepening,
            discrimination=discrimination,
            update_semantics=update_semantics,
            unresolved=unresolved,
            gap_ids=gap_ids,
            requirement_ids=requirement_ids,
        )
        return self._report(
            deepening,
            discrimination=discrimination,
            update_semantics=update_semantics,
            status=status,
            hypothesis_ids=hypothesis_ids,
            unresolved=unresolved,
            gap_ids=gap_ids,
            requirement_ids=requirement_ids,
            rationale_codes=rationale,
        )

    @staticmethod
    def _derive_status(
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        unresolved: tuple[str, ...],
        gap_ids: tuple[str, ...],
        requirement_ids: tuple[str, ...],
    ) -> tuple[EpistemicSufficiencyStatus, tuple[str, ...]]:
        if deepening.status in {
            HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
            HypothesisDeepeningStatus.DEGRADED,
        }:
            return (
                EpistemicSufficiencyStatus.INDETERMINATE,
                ("epistemic_sufficiency:deepening_source_not_resolved",),
            )

        if deepening.status is HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT:
            return (
                EpistemicSufficiencyStatus.INSUFFICIENT,
                ("epistemic_sufficiency:epistemic_gaps_present",),
            )

        if discrimination is not None and discrimination.status in {
            MultiHypothesisDiscriminationStatus.SOURCE_REVIEW_REQUIRED,
            MultiHypothesisDiscriminationStatus.DEGRADED,
        }:
            return (
                EpistemicSufficiencyStatus.INDETERMINATE,
                ("epistemic_sufficiency:comparison_source_not_resolved",),
            )

        if update_semantics is not None and update_semantics.status in {
            GovernedHypothesisUpdateSemanticsStatus.SOURCE_REVIEW_REQUIRED,
            GovernedHypothesisUpdateSemanticsStatus.REVIEW_REQUIRED,
        }:
            return (
                EpistemicSufficiencyStatus.INDETERMINATE,
                ("epistemic_sufficiency:update_semantics_requires_review",),
            )
        if update_semantics is not None and any(
            item.semantic
            in {
                HypothesisUpdateSemantic.INDETERMINATE,
                HypothesisUpdateSemantic.REVIEW_REQUIRED,
            }
            for item in update_semantics.updates
        ):
            return (
                EpistemicSufficiencyStatus.INDETERMINATE,
                ("epistemic_sufficiency:update_semantics_not_resolved",),
            )

        if unresolved or gap_ids or requirement_ids:
            rationale = ["epistemic_sufficiency:material_epistemic_impediment_present"]
            if unresolved:
                rationale.append("epistemic_sufficiency:unresolved_hypotheses_present")
            if gap_ids:
                rationale.append("epistemic_sufficiency:epistemic_gaps_present")
            if requirement_ids:
                rationale.append(
                    "epistemic_sufficiency:discrimination_requirements_present"
                )
            return EpistemicSufficiencyStatus.INSUFFICIENT, tuple(rationale)

        if len(deepening.assessments) > 1:
            if discrimination is None:
                return (
                    EpistemicSufficiencyStatus.INDETERMINATE,
                    ("epistemic_sufficiency:comparison_not_supplied",),
                )
            if (
                discrimination.status
                is not MultiHypothesisDiscriminationStatus.COMPLETE
            ):
                return (
                    EpistemicSufficiencyStatus.INDETERMINATE,
                    ("epistemic_sufficiency:comparison_not_complete",),
                )

        if not deepening.assessments:
            return (
                EpistemicSufficiencyStatus.INDETERMINATE,
                ("epistemic_sufficiency:no_hypothesis_assessments",),
            )

        return (
            EpistemicSufficiencyStatus.SUFFICIENT,
            (
                "epistemic_sufficiency:no_material_known_impediment",
                "epistemic_sufficiency:contextual_not_truth_promotion",
                "epistemic_sufficiency:does_not_close_or_stop_reasoning",
            ),
        )

    @staticmethod
    def _validate_deepening(deepening: GovernedHypothesisDeepeningReport) -> None:
        if deepening.canonical_authority != "governed_reasoning":
            raise ValueError("sufficiency requires governed reasoning authority")
        if not deepening.read_only or not deepening.consultative:
            raise ValueError("sufficiency requires read-only deepening")
        if any(
            (
                deepening.creates_facts,
                deepening.modifies_memory,
                deepening.modifies_learning,
                deepening.modifies_planning,
                deepening.executes_actions,
                deepening.grants_authority,
            )
        ):
            raise ValueError("sufficiency requires governed deepening")

    @staticmethod
    def _validate_discrimination(
        deepening: GovernedHypothesisDeepeningReport,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
    ) -> None:
        if discrimination is None:
            return
        if discrimination.canonical_authority != "governed_reasoning":
            raise ValueError("sufficiency comparison must preserve reasoning authority")
        if not discrimination.read_only or not discrimination.consultative:
            raise ValueError("sufficiency requires read-only comparison")
        if discrimination.source_reference != deepening.source_reference:
            raise ValueError("sufficiency comparison source lineage mismatch")
        if discrimination.world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("sufficiency comparison snapshot lineage mismatch")

    @staticmethod
    def _validate_update_semantics(
        deepening: GovernedHypothesisDeepeningReport,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
    ) -> None:
        if update_semantics is None:
            return
        if update_semantics.canonical_authority != "governed_reasoning":
            raise ValueError("sufficiency update must preserve reasoning authority")
        if not update_semantics.read_only or not update_semantics.consultative:
            raise ValueError("sufficiency requires read-only update semantics")
        if update_semantics.source_reference != deepening.source_reference:
            raise ValueError("sufficiency update source lineage mismatch")
        if update_semantics.after_world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("sufficiency update snapshot lineage mismatch")

    @staticmethod
    def _report(
        deepening: GovernedHypothesisDeepeningReport,
        *,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        status: EpistemicSufficiencyStatus,
        hypothesis_ids: tuple[str, ...],
        unresolved: tuple[str, ...],
        gap_ids: tuple[str, ...],
        requirement_ids: tuple[str, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedEpistemicSufficiencyAssessment:
        discrimination_id = discrimination.report_id if discrimination else None
        update_id = update_semantics.report_id if update_semantics else None
        fingerprint = sha256(
            repr(
                (
                    deepening.report_id,
                    discrimination_id,
                    update_id,
                    status.value,
                    hypothesis_ids,
                    unresolved,
                    gap_ids,
                    requirement_ids,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedEpistemicSufficiencyAssessment(
            assessment_id=f"epistemic-sufficiency-{fingerprint[:24]}",
            status=status,
            source_hypothesis_deepening_report_id=deepening.report_id,
            source_multi_hypothesis_discrimination_report_id=discrimination_id,
            source_hypothesis_update_semantics_report_id=update_id,
            source_reference=deepening.source_reference,
            world_snapshot_id=deepening.world_snapshot_id,
            hypothesis_ids=hypothesis_ids,
            unresolved_hypothesis_ids=unresolved,
            epistemic_gap_ids=gap_ids,
            discrimination_requirement_ids=requirement_ids,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
