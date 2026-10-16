from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessment,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningStatus,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsReport,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminationReport,
)


class GovernedReasoningQualityStatus(StrEnum):
    ADEQUATE = "adequate"
    LIMITED = "limited"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedReasoningQualityAssessment:
    assessment_id: str
    status: GovernedReasoningQualityStatus
    source_hypothesis_deepening_report_id: str
    source_epistemic_sufficiency_assessment_id: str
    source_hypothesis_update_semantics_report_id: str | None
    source_multi_hypothesis_discrimination_report_id: str | None
    source_reference: str
    world_snapshot_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-reasoning-quality-v1"
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
    corrects_reasoning: bool = False
    reruns_reasoning: bool = False
    changes_conclusion: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("reasoning-quality-"):
            raise ValueError("reasoning quality identifier is invalid")
        if not self.source_hypothesis_deepening_report_id.strip():
            raise ValueError("reasoning quality requires deepening lineage")
        if not self.source_epistemic_sufficiency_assessment_id.strip():
            raise ValueError("reasoning quality requires sufficiency lineage")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("reasoning quality requires source lineage")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("reasoning quality requires rationale codes")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("reasoning quality must preserve reasoning authority")
        if not self.read_only or not self.consultative or not self.derivational:
            raise ValueError("reasoning quality must remain derived and read-only")
        if not self.contextual:
            raise ValueError("reasoning quality must remain contextual")
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
                self.corrects_reasoning,
                self.reruns_reasoning,
                self.changes_conclusion,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("reasoning quality violates governed limits")


class GovernedReasoningQualityAssessmentFoundationV1:
    """Assess a completed governed epistemic episode without correcting it."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def assess(
        self,
        deepening: GovernedHypothesisDeepeningReport,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
        *,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None = None,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None = None,
    ) -> GovernedReasoningQualityAssessment:
        self._validate_deepening(deepening)
        self._validate_sufficiency(deepening, sufficiency)
        self._validate_update_semantics(sufficiency, update_semantics)
        self._validate_discrimination(sufficiency, discrimination)

        status, rationale = self._derive_status(deepening, sufficiency)
        return self._report(
            deepening,
            sufficiency,
            update_semantics=update_semantics,
            discrimination=discrimination,
            status=status,
            rationale_codes=rationale,
        )

    @staticmethod
    def _derive_status(
        deepening: GovernedHypothesisDeepeningReport,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> tuple[GovernedReasoningQualityStatus, tuple[str, ...]]:
        if deepening.status in {
            HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
            HypothesisDeepeningStatus.DEGRADED,
        }:
            return (
                GovernedReasoningQualityStatus.REVIEW_REQUIRED,
                ("reasoning_quality:upstream_deepening_requires_review",),
            )

        if sufficiency.status is EpistemicSufficiencyStatus.INDETERMINATE:
            return (
                GovernedReasoningQualityStatus.REVIEW_REQUIRED,
                ("reasoning_quality:sufficiency_indeterminate",),
            )

        if sufficiency.status is EpistemicSufficiencyStatus.INSUFFICIENT:
            return (
                GovernedReasoningQualityStatus.LIMITED,
                (
                    "reasoning_quality:explicit_epistemic_limits_preserved",
                    "reasoning_quality:insufficiency_is_not_reasoning_failure",
                ),
            )

        return (
            GovernedReasoningQualityStatus.ADEQUATE,
            (
                "reasoning_quality:lineage_coherent",
                "reasoning_quality:epistemic_result_contextually_adequate",
                "reasoning_quality:adequate_not_truth_or_correctness",
            ),
        )

    @staticmethod
    def _validate_deepening(deepening: GovernedHypothesisDeepeningReport) -> None:
        if deepening.canonical_authority != "governed_reasoning":
            raise ValueError("reasoning quality requires governed reasoning authority")
        if not deepening.read_only or not deepening.consultative:
            raise ValueError("reasoning quality requires read-only deepening")
        if any(
            (
                deepening.persists_results,
                deepening.creates_facts,
                deepening.creates_questions,
                deepening.creates_learning_candidates,
                deepening.modifies_world_model,
                deepening.modifies_memory,
                deepening.modifies_learning,
                deepening.modifies_planning,
                deepening.executes_actions,
                deepening.grants_authority,
                deepening.starts_background_process,
            )
        ):
            raise ValueError("reasoning quality requires governed deepening")

    @staticmethod
    def _validate_sufficiency(
        deepening: GovernedHypothesisDeepeningReport,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
    ) -> None:
        if sufficiency.canonical_authority != "governed_reasoning":
            raise ValueError("reasoning quality requires governed sufficiency")
        if not sufficiency.read_only or not sufficiency.consultative:
            raise ValueError("reasoning quality requires read-only sufficiency")
        if (
            sufficiency.source_hypothesis_deepening_report_id
            != deepening.report_id
        ):
            raise ValueError("reasoning quality deepening lineage mismatch")
        if sufficiency.source_reference != deepening.source_reference:
            raise ValueError("reasoning quality source lineage mismatch")
        if sufficiency.world_snapshot_id != deepening.world_snapshot_id:
            raise ValueError("reasoning quality snapshot lineage mismatch")

    @staticmethod
    def _validate_update_semantics(
        sufficiency: GovernedEpistemicSufficiencyAssessment,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
    ) -> None:
        if update_semantics is None:
            return
        if sufficiency.source_hypothesis_update_semantics_report_id is None:
            raise ValueError("reasoning quality unexpected update semantics lineage")
        if (
            sufficiency.source_hypothesis_update_semantics_report_id
            != update_semantics.report_id
        ):
            raise ValueError("reasoning quality update semantics lineage mismatch")
        if update_semantics.source_reference != sufficiency.source_reference:
            raise ValueError("reasoning quality update source lineage mismatch")
        if update_semantics.after_world_snapshot_id != sufficiency.world_snapshot_id:
            raise ValueError("reasoning quality update snapshot lineage mismatch")

    @staticmethod
    def _validate_discrimination(
        sufficiency: GovernedEpistemicSufficiencyAssessment,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
    ) -> None:
        if discrimination is None:
            return
        if sufficiency.source_multi_hypothesis_discrimination_report_id is None:
            raise ValueError("reasoning quality unexpected discrimination lineage")
        if (
            sufficiency.source_multi_hypothesis_discrimination_report_id
            != discrimination.report_id
        ):
            raise ValueError("reasoning quality discrimination lineage mismatch")
        if discrimination.source_reference != sufficiency.source_reference:
            raise ValueError("reasoning quality comparison source lineage mismatch")
        if discrimination.world_snapshot_id != sufficiency.world_snapshot_id:
            raise ValueError("reasoning quality comparison snapshot lineage mismatch")

    @staticmethod
    def _report(
        deepening: GovernedHypothesisDeepeningReport,
        sufficiency: GovernedEpistemicSufficiencyAssessment,
        *,
        update_semantics: GovernedHypothesisUpdateSemanticsReport | None,
        discrimination: GovernedMultiHypothesisDiscriminationReport | None,
        status: GovernedReasoningQualityStatus,
        rationale_codes: tuple[str, ...],
    ) -> GovernedReasoningQualityAssessment:
        update_id = update_semantics.report_id if update_semantics is not None else None
        discrimination_id = (
            discrimination.report_id if discrimination is not None else None
        )
        fingerprint = sha256(
            repr(
                (
                    deepening.report_id,
                    sufficiency.assessment_id,
                    update_id,
                    discrimination_id,
                    status.value,
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedReasoningQualityAssessment(
            assessment_id=f"reasoning-quality-{fingerprint[:24]}",
            status=status,
            source_hypothesis_deepening_report_id=deepening.report_id,
            source_epistemic_sufficiency_assessment_id=sufficiency.assessment_id,
            source_hypothesis_update_semantics_report_id=update_id,
            source_multi_hypothesis_discrimination_report_id=discrimination_id,
            source_reference=deepening.source_reference,
            world_snapshot_id=deepening.world_snapshot_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
