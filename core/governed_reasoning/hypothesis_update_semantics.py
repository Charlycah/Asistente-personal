from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.hypothesis_deepening import (
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisEpistemicDelta,
    GovernedHypothesisEpistemicDeltaReport,
    GovernedHypothesisEpistemicDeltaStatus,
    HypothesisEpistemicDeltaKind,
)


class HypothesisUpdateSemantic(StrEnum):
    STRENGTHENED = "strengthened"
    WEAKENED = "weakened"
    UNCHANGED = "unchanged"
    INDETERMINATE = "indeterminate"
    REVIEW_REQUIRED = "review_required"


class GovernedHypothesisUpdateSemanticsStatus(StrEnum):
    COMPLETE = "complete"
    REVIEW_REQUIRED = "review_required"
    SOURCE_REVIEW_REQUIRED = "source_review_required"


@dataclass(frozen=True)
class GovernedHypothesisSemanticUpdate:
    hypothesis_id: str
    delta_kind: HypothesisEpistemicDeltaKind
    semantic: HypothesisUpdateSemantic
    before_relation: HypothesisEvidenceRelation | None
    after_relation: HypothesisEvidenceRelation | None
    triggering_evidence_references: tuple[str, ...]
    added_evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    establishes_truth: bool = False
    establishes_falsity: bool = False
    assigns_probability: bool = False
    modifies_hypothesis: bool = False
    deletes_hypothesis: bool = False

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ValueError("semantic update requires hypothesis identity")
        if not self.triggering_evidence_references:
            raise ValueError("semantic update requires triggering evidence")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("semantic update requires rationale codes")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.assigns_probability,
                self.modifies_hypothesis,
                self.deletes_hypothesis,
            )
        ):
            raise ValueError("semantic update violates governed limits")


@dataclass(frozen=True)
class GovernedHypothesisUpdateSemanticsReport:
    report_id: str
    status: GovernedHypothesisUpdateSemanticsStatus
    source_delta_report_id: str
    source_reference: str
    before_world_snapshot_id: str
    after_world_snapshot_id: str
    triggering_evidence_references: tuple[str, ...]
    updates: tuple[GovernedHypothesisSemanticUpdate, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-hypothesis-update-semantics-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    derivational: bool = True
    establishes_truth: bool = False
    establishes_falsity: bool = False
    assigns_probability: bool = False
    modifies_hypotheses: bool = False
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_world_model: bool = False
    invokes_reasoning: bool = False
    invokes_comparison: bool = False
    invokes_curiosity: bool = False
    invokes_planning: bool = False
    invokes_capabilities: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("hypothesis-update-semantics-"):
            raise ValueError("hypothesis update semantics identifier is invalid")
        if not self.source_delta_report_id.strip():
            raise ValueError("semantic report requires delta lineage")
        if not self.source_reference.strip():
            raise ValueError("semantic report requires source lineage")
        if (
            not self.before_world_snapshot_id.strip()
            or not self.after_world_snapshot_id.strip()
        ):
            raise ValueError("semantic report requires snapshot lineage")
        if not self.triggering_evidence_references:
            raise ValueError("semantic report requires triggering evidence")
        if not self.rationale_codes:
            raise ValueError("semantic report requires rationale codes")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("semantic report must preserve reasoning authority")
        if not self.read_only or not self.consultative or not self.derivational:
            raise ValueError("semantic report must remain read-only and derivational")
        if any(
            (
                self.establishes_truth,
                self.establishes_falsity,
                self.assigns_probability,
                self.modifies_hypotheses,
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_world_model,
                self.invokes_reasoning,
                self.invokes_comparison,
                self.invokes_curiosity,
                self.invokes_planning,
                self.invokes_capabilities,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("hypothesis update semantics violates governed limits")


class GovernedHypothesisUpdateSemanticsFoundationV1:
    """Classify certified structural deltas without deciding truth or belief."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    _TRANSITIONS = {
        (
            HypothesisEvidenceRelation.UNRESOLVED,
            HypothesisEvidenceRelation.COMPATIBLE,
        ): HypothesisUpdateSemantic.STRENGTHENED,
        (
            HypothesisEvidenceRelation.UNRESOLVED,
            HypothesisEvidenceRelation.CONTRADICTED,
        ): HypothesisUpdateSemantic.WEAKENED,
        (
            HypothesisEvidenceRelation.COMPATIBLE,
            HypothesisEvidenceRelation.CONTRADICTED,
        ): HypothesisUpdateSemantic.WEAKENED,
        (
            HypothesisEvidenceRelation.CONTRADICTED,
            HypothesisEvidenceRelation.COMPATIBLE,
        ): HypothesisUpdateSemantic.STRENGTHENED,
    }

    def classify(
        self,
        delta_report: GovernedHypothesisEpistemicDeltaReport,
    ) -> GovernedHypothesisUpdateSemanticsReport:
        self._validate_source(delta_report)
        if (
            delta_report.status
            is GovernedHypothesisEpistemicDeltaStatus.SOURCE_REVIEW_REQUIRED
        ):
            return self._report(
                delta_report,
                GovernedHypothesisUpdateSemanticsStatus.SOURCE_REVIEW_REQUIRED,
                (),
                ("hypothesis_update_semantics:source_review_required",),
            )

        updates = tuple(self._classify_delta(item) for item in delta_report.deltas)
        review_required = (
            delta_report.status
            is GovernedHypothesisEpistemicDeltaStatus.REVIEW_REQUIRED
            or any(
                item.semantic is HypothesisUpdateSemantic.REVIEW_REQUIRED
                for item in updates
            )
        )
        status = (
            GovernedHypothesisUpdateSemanticsStatus.REVIEW_REQUIRED
            if review_required
            else GovernedHypothesisUpdateSemanticsStatus.COMPLETE
        )
        rationale = (
            "hypothesis_update_semantics:closed_transition_table_applied",
            "hypothesis_update_semantics:no_truth_or_falsity_promotion",
            "hypothesis_update_semantics:no_probability_assignment",
        )
        if review_required:
            rationale = (*rationale, "hypothesis_update_semantics:review_required")
        return self._report(delta_report, status, updates, rationale)

    @classmethod
    def _classify_delta(
        cls,
        delta: GovernedHypothesisEpistemicDelta,
    ) -> GovernedHypothesisSemanticUpdate:
        if delta.kind in {
            HypothesisEpistemicDeltaKind.MISSING_FROM_AFTER,
            HypothesisEpistemicDeltaKind.PROPOSITION_CONFLICT,
        }:
            semantic = HypothesisUpdateSemantic.REVIEW_REQUIRED
            rationale = (
                "hypothesis_update_semantics:structural_conflict_requires_review",
            )
        elif delta.kind is HypothesisEpistemicDeltaKind.NEW_HYPOTHESIS:
            semantic = HypothesisUpdateSemantic.INDETERMINATE
            rationale = (
                "hypothesis_update_semantics:no_prior_assessment",
            )
        elif delta.kind is HypothesisEpistemicDeltaKind.UNCHANGED:
            semantic = HypothesisUpdateSemantic.UNCHANGED
            rationale = (
                "hypothesis_update_semantics:no_semantic_change",
            )
        elif delta.kind is HypothesisEpistemicDeltaKind.EVIDENCE_CHANGED:
            semantic = HypothesisUpdateSemantic.INDETERMINATE
            rationale = (
                "hypothesis_update_semantics:evidence_change_alone_is_not_strength",
            )
        else:
            semantic = cls._TRANSITIONS.get(
                (delta.before_relation, delta.after_relation),
                HypothesisUpdateSemantic.INDETERMINATE,
            )
            rationale = (
                "hypothesis_update_semantics:explicit_relation_transition",
                f"hypothesis_update_semantics:{semantic.value}",
            )
            if semantic is HypothesisUpdateSemantic.INDETERMINATE:
                rationale = (
                    "hypothesis_update_semantics:unmapped_transition_is_indeterminate",
                )
        return GovernedHypothesisSemanticUpdate(
            hypothesis_id=delta.hypothesis_id,
            delta_kind=delta.kind,
            semantic=semantic,
            before_relation=delta.before_relation,
            after_relation=delta.after_relation,
            triggering_evidence_references=delta.triggering_evidence_references,
            added_evidence_references=delta.added_evidence_references,
            rationale_codes=rationale,
        )

    @staticmethod
    def _validate_source(
        delta_report: GovernedHypothesisEpistemicDeltaReport,
    ) -> None:
        if delta_report.canonical_authority != "governed_reasoning":
            raise ValueError("semantic classification requires reasoning authority")
        if not delta_report.read_only or not delta_report.consultative:
            raise ValueError("semantic classification requires read-only delta")
        if any(
            (
                delta_report.establishes_truth,
                delta_report.establishes_falsity,
                delta_report.modifies_hypotheses,
                delta_report.persists_results,
                delta_report.grants_authority,
            )
        ):
            raise ValueError("semantic classification requires governed delta")

    @staticmethod
    def _report(delta_report, status, updates, rationale_codes):
        fingerprint = sha256(
            repr(
                (
                    delta_report.report_id,
                    status.value,
                    tuple(
                        (
                            item.hypothesis_id,
                            item.delta_kind.value,
                            item.semantic.value,
                            item.before_relation.value
                            if item.before_relation is not None
                            else None,
                            item.after_relation.value
                            if item.after_relation is not None
                            else None,
                        )
                        for item in updates
                    ),
                    rationale_codes,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisUpdateSemanticsReport(
            report_id=f"hypothesis-update-semantics-{fingerprint[:24]}",
            status=status,
            source_delta_report_id=delta_report.report_id,
            source_reference=delta_report.source_reference,
            before_world_snapshot_id=delta_report.before_world_snapshot_id,
            after_world_snapshot_id=delta_report.after_world_snapshot_id,
            triggering_evidence_references=(
                delta_report.triggering_evidence_references
            ),
            updates=updates,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )


class GovernedReconsiderationCandidateStatus(StrEnum):
    NOT_REQUIRED = "not_required"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class GovernedReconsiderationCandidate:
    candidate_id: str
    status: GovernedReconsiderationCandidateStatus
    source_semantics_report_id: str
    source_delta_report_id: str
    source_reference: str
    before_world_snapshot_id: str
    after_world_snapshot_id: str
    triggering_evidence_references: tuple[str, ...]
    affected_hypothesis_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True

    def __post_init__(self) -> None:
        if not self.candidate_id.startswith("reconsideration-candidate-"):
            raise ValueError("reconsideration candidate identifier is invalid")
        if not self.source_semantics_report_id.strip():
            raise ValueError("reconsideration requires semantic lineage")
        if not self.source_delta_report_id.strip():
            raise ValueError("reconsideration requires delta lineage")
        if not self.source_reference.strip():
            raise ValueError("reconsideration requires source lineage")
        if (
            not self.before_world_snapshot_id.strip()
            or not self.after_world_snapshot_id.strip()
        ):
            raise ValueError("reconsideration requires snapshot lineage")
        if not self.triggering_evidence_references:
            raise ValueError("reconsideration requires triggering evidence")
        if len(self.affected_hypothesis_ids) != len(
            set(self.affected_hypothesis_ids)
        ):
            raise ValueError("affected hypotheses must be unique")
        if not self.rationale_codes:
            raise ValueError("reconsideration requires rationale")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("reconsideration must preserve reasoning authority")
        if not self.read_only or not self.consultative:
            raise ValueError("reconsideration must remain bounded")
        if (
            self.status is GovernedReconsiderationCandidateStatus.REVIEW_REQUIRED
            and not self.affected_hypothesis_ids
        ):
            raise ValueError("review-required reconsideration needs a target")
        if (
            self.status is GovernedReconsiderationCandidateStatus.NOT_REQUIRED
            and self.affected_hypothesis_ids
        ):
            raise ValueError("non-required reconsideration cannot target hypotheses")


class GovernedReconsiderationCandidateProjector:
    """Project bounded review need from existing governed update semantics."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def project(
        self,
        report: GovernedHypothesisUpdateSemanticsReport,
    ) -> GovernedReconsiderationCandidate:
        self._validate_source(report)
        affected = tuple(
            sorted(
                item.hypothesis_id
                for item in report.updates
                if item.semantic
                in {
                    HypothesisUpdateSemantic.WEAKENED,
                    HypothesisUpdateSemantic.REVIEW_REQUIRED,
                }
            )
        )
        status = (
            GovernedReconsiderationCandidateStatus.REVIEW_REQUIRED
            if affected
            else GovernedReconsiderationCandidateStatus.NOT_REQUIRED
        )
        rationale = (
            "reconsideration:existing_update_semantics_projected",
            f"reconsideration:{status.value}",
        )
        fingerprint = sha256(
            repr(
                (
                    report.report_id,
                    report.source_delta_report_id,
                    report.source_reference,
                    report.before_world_snapshot_id,
                    report.after_world_snapshot_id,
                    report.triggering_evidence_references,
                    affected,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedReconsiderationCandidate(
            candidate_id=f"reconsideration-candidate-{fingerprint[:24]}",
            status=status,
            source_semantics_report_id=report.report_id,
            source_delta_report_id=report.source_delta_report_id,
            source_reference=report.source_reference,
            before_world_snapshot_id=report.before_world_snapshot_id,
            after_world_snapshot_id=report.after_world_snapshot_id,
            triggering_evidence_references=(
                report.triggering_evidence_references
            ),
            affected_hypothesis_ids=affected,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _validate_source(
        report: GovernedHypothesisUpdateSemanticsReport,
    ) -> None:
        if report.canonical_authority != "governed_reasoning":
            raise ValueError("reconsideration requires governed reasoning source")
        if not report.read_only or not report.consultative:
            raise ValueError("reconsideration requires bounded semantic source")
        if any(
            (
                report.establishes_truth,
                report.establishes_falsity,
                report.assigns_probability,
                report.modifies_hypotheses,
                report.persists_results,
                report.creates_memory,
                report.creates_learning_candidate,
                report.modifies_world_model,
                report.invokes_planning,
                report.invokes_capabilities,
                report.grants_authority,
                report.starts_background_process,
            )
        ):
            raise ValueError("reconsideration source violates governed limits")

