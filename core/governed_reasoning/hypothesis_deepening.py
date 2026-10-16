from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.causal_prediction import (
    CausalAssessmentKind,
    GovernedCausalPredictionReport,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulationReport,
    ScenarioOutcomeKind,
)


class HypothesisDeepeningSourceKind(StrEnum):
    SCENARIO_SIMULATION = "scenario_simulation"
    CAUSAL_PREDICTION = "causal_prediction"


class HypothesisEvidenceRelation(StrEnum):
    COMPATIBLE = "compatible"
    CONTRADICTED = "contradicted"
    UNRESOLVED = "unresolved"


class HypothesisDeepeningStatus(StrEnum):
    COMPLETE = "complete"
    EPISTEMIC_GAPS_PRESENT = "epistemic_gaps_present"
    SOURCE_REVIEW_REQUIRED = "source_review_required"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class HypothesisEvidenceAssessment:
    hypothesis_id: str
    proposition: str
    relation: HypothesisEvidenceRelation
    evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    epistemic_level: EpistemicLevel = EpistemicLevel.HYPOTHESIS
    establishes_fact: bool = False
    establishes_causality: bool = False

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.proposition.strip():
            raise ValueError("hypothesis assessment requires identity and proposition")
        if any(not item.strip() for item in self.evidence_references):
            raise ValueError("hypothesis evidence references must not be blank")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("hypothesis assessment requires rationale codes")
        if self.epistemic_level is not EpistemicLevel.HYPOTHESIS:
            raise ValueError("deepened hypotheses must remain hypotheses")
        if self.establishes_fact or self.establishes_causality:
            raise ValueError("hypothesis deepening cannot establish facts or causality")


@dataclass(frozen=True)
class HypothesisEpistemicGap:
    gap_id: str
    hypothesis_id: str
    subject: str
    source_kind: HypothesisDeepeningSourceKind
    source_reference: str
    known_elements: tuple[str, ...]
    unknown_element: str
    evidence_codes: tuple[str, ...]
    hypothesis: str
    epistemic_level: EpistemicLevel = EpistemicLevel.UNKNOWN
    read_only: bool = True
    persists_results: bool = False
    creates_question: bool = False
    creates_learning_candidate: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        for value, label in (
            (self.gap_id, "gap id"),
            (self.hypothesis_id, "hypothesis id"),
            (self.subject, "subject"),
            (self.source_reference, "source reference"),
            (self.unknown_element, "unknown element"),
            (self.hypothesis, "hypothesis"),
        ):
            if not value.strip():
                raise ValueError(f"epistemic gap {label} must not be blank")
        if not self.gap_id.startswith("hypothesis-gap-"):
            raise ValueError("epistemic gap identifier is invalid")
        if any(not item.strip() for item in self.known_elements):
            raise ValueError("epistemic gap known elements must not be blank")
        if not self.evidence_codes or any(
            not item.strip() for item in self.evidence_codes
        ):
            raise ValueError("epistemic gap requires explicit evidence codes")
        if self.epistemic_level is not EpistemicLevel.UNKNOWN:
            raise ValueError("epistemic gaps must remain unknown knowledge")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_question,
                self.creates_learning_candidate,
                self.modifies_memory,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("epistemic gap violates governed limits")


@dataclass(frozen=True)
class GovernedHypothesisDeepeningReport:
    report_id: str
    status: HypothesisDeepeningStatus
    source_kind: HypothesisDeepeningSourceKind
    source_reference: str
    world_snapshot_id: str
    assessments: tuple[HypothesisEvidenceAssessment, ...]
    epistemic_gaps: tuple[HypothesisEpistemicGap, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-hypothesis-deepening-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    creates_questions: bool = False
    creates_learning_candidates: bool = False
    modifies_world_model: bool = False
    modifies_memory: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("hypothesis-deepening-"):
            raise ValueError("hypothesis deepening report identifier is invalid")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("hypothesis deepening requires explicit source lineage")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("hypothesis deepening must preserve reasoning authority")
        assessment_ids = tuple(item.hypothesis_id for item in self.assessments)
        if len(assessment_ids) != len(set(assessment_ids)):
            raise ValueError("deepened hypothesis identifiers must be unique")
        if any(gap.hypothesis_id not in assessment_ids for gap in self.epistemic_gaps):
            raise ValueError("epistemic gaps must reference assessed hypotheses")
        if any(
            gap.source_reference != self.source_reference
            or gap.source_kind is not self.source_kind
            for gap in self.epistemic_gaps
        ):
            raise ValueError("epistemic gaps must preserve source lineage")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_facts,
                self.creates_questions,
                self.creates_learning_candidates,
                self.modifies_world_model,
                self.modifies_memory,
                self.modifies_learning,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("hypothesis deepening violates governed limits")


class GovernedHypothesisDeepener:
    """Read-only deepening over explicit M391.3/M391.4 reasoning reports."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def deepen_scenarios(
        self,
        report: GovernedScenarioSimulationReport,
    ) -> GovernedHypothesisDeepeningReport:
        propositions = {
            item.hypothesis_id: item.proposition for item in report.hypotheses
        }
        assessments = tuple(
            HypothesisEvidenceAssessment(
                hypothesis_id=outcome.hypothesis_id,
                proposition=propositions[outcome.hypothesis_id],
                relation=self._scenario_relation(outcome.kind),
                evidence_references=outcome.matched_fact_ids,
                rationale_codes=outcome.rationale_codes,
            )
            for outcome in report.outcomes
        )
        gaps = tuple(
            self._gap(
                source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
                source_reference=report.simulation_id,
                hypothesis_id=assessment.hypothesis_id,
                proposition=assessment.proposition,
                known_elements=assessment.evidence_references,
                evidence_codes=tuple(
                    dict.fromkeys((*report.evidence_codes, *assessment.rationale_codes))
                ),
                unknown_element=(
                    "explicit evidence sufficient to discriminate this scenario "
                    "hypothesis"
                ),
            )
            for assessment in assessments
            if assessment.relation is HypothesisEvidenceRelation.UNRESOLVED
        )
        return self._report(
            source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
            source_reference=report.simulation_id,
            world_snapshot_id=report.world_snapshot_id,
            assessments=assessments,
            gaps=gaps,
            evidence_codes=report.evidence_codes,
            risk_codes=report.risk_codes,
            source_fingerprint=report.source_fingerprint,
            source_review_required=(
                report.status.value == "world_conflict_review_required"
            ),
        )

    def deepen_causal_predictions(
        self,
        report: GovernedCausalPredictionReport,
    ) -> GovernedHypothesisDeepeningReport:
        propositions = {
            item.relation_id: item.proposition for item in report.hypotheses
        }
        assessments = tuple(
            HypothesisEvidenceAssessment(
                hypothesis_id=assessment.relation_id,
                proposition=propositions[assessment.relation_id],
                relation=self._causal_relation(assessment.kind),
                evidence_references=tuple(
                    dict.fromkeys(
                        (*assessment.cause_fact_ids, *assessment.effect_fact_ids)
                    )
                ),
                rationale_codes=assessment.rationale_codes,
            )
            for assessment in report.assessments
        )
        gaps = tuple(
            self._gap(
                source_kind=HypothesisDeepeningSourceKind.CAUSAL_PREDICTION,
                source_reference=report.analysis_id,
                hypothesis_id=assessment.hypothesis_id,
                proposition=assessment.proposition,
                known_elements=assessment.evidence_references,
                evidence_codes=tuple(
                    dict.fromkeys((*report.evidence_codes, *assessment.rationale_codes))
                ),
                unknown_element=(
                    "explicit evidence sufficient to discriminate this causal "
                    "hypothesis without treating association as causation"
                ),
            )
            for assessment in assessments
            if assessment.relation is HypothesisEvidenceRelation.UNRESOLVED
        )
        return self._report(
            source_kind=HypothesisDeepeningSourceKind.CAUSAL_PREDICTION,
            source_reference=report.analysis_id,
            world_snapshot_id=report.world_snapshot_id,
            assessments=assessments,
            gaps=gaps,
            evidence_codes=report.evidence_codes,
            risk_codes=tuple(
                dict.fromkeys((*report.risk_codes, "causality_not_established"))
            ),
            source_fingerprint=report.source_fingerprint,
            source_review_required=(
                report.status.value == "world_conflict_review_required"
            ),
        )

    def reassess_with_governed_evidence(
        self,
        previous_report: GovernedHypothesisDeepeningReport,
        *,
        source_report_id: str,
        evidence_id: str,
        hypothesis_ids: tuple[str, ...],
    ) -> GovernedHypothesisDeepeningReport:
        """Reassess the same governed hypotheses with one admitted evidence id."""
        if source_report_id != previous_report.report_id:
            raise ValueError("reassessment requires exact previous report lineage")
        if not evidence_id.strip():
            raise ValueError("reassessment requires governed evidence identity")
        requested = set(hypothesis_ids)
        previous_ids = {item.hypothesis_id for item in previous_report.assessments}
        if not requested or not requested.issubset(previous_ids):
            raise ValueError("reassessment hypotheses must belong to previous report")

        assessments = tuple(
            HypothesisEvidenceAssessment(
                hypothesis_id=item.hypothesis_id,
                proposition=item.proposition,
                relation=item.relation,
                evidence_references=(
                    tuple(dict.fromkeys((*item.evidence_references, evidence_id)))
                    if item.hypothesis_id in requested
                    else item.evidence_references
                ),
                rationale_codes=(
                    tuple(
                        dict.fromkeys(
                            (
                                *item.rationale_codes,
                                "reassessment:governed_evidence_considered",
                            )
                        )
                    )
                    if item.hypothesis_id in requested
                    else item.rationale_codes
                ),
            )
            for item in previous_report.assessments
        )
        return self._report(
            source_kind=previous_report.source_kind,
            source_reference=previous_report.source_reference,
            world_snapshot_id=previous_report.world_snapshot_id,
            assessments=assessments,
            gaps=previous_report.epistemic_gaps,
            evidence_codes=tuple(
                dict.fromkeys(
                    (*previous_report.evidence_codes, "reassessment:governed_evidence")
                )
            ),
            risk_codes=previous_report.risk_codes,
            source_fingerprint=previous_report.source_fingerprint,
            source_review_required=(
                previous_report.status
                is HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED
            ),
        )

    def deepen_scenarios_safely(
        self,
        report: GovernedScenarioSimulationReport,
    ) -> GovernedHypothesisDeepeningReport:
        try:
            return self.deepen_scenarios(report)
        except Exception:
            return self._degraded(
                HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
                report.simulation_id,
                report.world_snapshot_id,
                report.source_fingerprint,
            )

    def deepen_causal_predictions_safely(
        self,
        report: GovernedCausalPredictionReport,
    ) -> GovernedHypothesisDeepeningReport:
        try:
            return self.deepen_causal_predictions(report)
        except Exception:
            return self._degraded(
                HypothesisDeepeningSourceKind.CAUSAL_PREDICTION,
                report.analysis_id,
                report.world_snapshot_id,
                report.source_fingerprint,
            )

    @staticmethod
    def _scenario_relation(kind: ScenarioOutcomeKind) -> HypothesisEvidenceRelation:
        return {
            ScenarioOutcomeKind.CONSISTENT: HypothesisEvidenceRelation.COMPATIBLE,
            ScenarioOutcomeKind.CONTRADICTED: HypothesisEvidenceRelation.CONTRADICTED,
            ScenarioOutcomeKind.UNRESOLVED: HypothesisEvidenceRelation.UNRESOLVED,
        }[kind]

    @staticmethod
    def _causal_relation(
        kind: CausalAssessmentKind,
    ) -> HypothesisEvidenceRelation:
        if kind is CausalAssessmentKind.ASSOCIATION_COMPATIBLE:
            return HypothesisEvidenceRelation.COMPATIBLE
        if kind in {
            CausalAssessmentKind.CAUSE_CONTRADICTED,
            CausalAssessmentKind.EFFECT_CONTRADICTED,
        }:
            return HypothesisEvidenceRelation.CONTRADICTED
        return HypothesisEvidenceRelation.UNRESOLVED

    @staticmethod
    def _gap(
        *,
        source_kind: HypothesisDeepeningSourceKind,
        source_reference: str,
        hypothesis_id: str,
        proposition: str,
        known_elements: tuple[str, ...],
        evidence_codes: tuple[str, ...],
        unknown_element: str,
    ) -> HypothesisEpistemicGap:
        fingerprint = sha256(
            repr(
                (
                    source_kind.value,
                    source_reference,
                    hypothesis_id,
                    proposition,
                    known_elements,
                    evidence_codes,
                    unknown_element,
                )
            ).encode("utf-8")
        ).hexdigest()
        return HypothesisEpistemicGap(
            gap_id=f"hypothesis-gap-{fingerprint[:16]}",
            hypothesis_id=hypothesis_id,
            subject=proposition,
            source_kind=source_kind,
            source_reference=source_reference,
            known_elements=known_elements,
            unknown_element=unknown_element,
            evidence_codes=evidence_codes,
            hypothesis=proposition,
        )

    @staticmethod
    def _report(
        *,
        source_kind: HypothesisDeepeningSourceKind,
        source_reference: str,
        world_snapshot_id: str,
        assessments: tuple[HypothesisEvidenceAssessment, ...],
        gaps: tuple[HypothesisEpistemicGap, ...],
        evidence_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
        source_fingerprint: str,
        source_review_required: bool,
    ) -> GovernedHypothesisDeepeningReport:
        if source_review_required:
            status = HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED
        elif gaps:
            status = HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT
        else:
            status = HypothesisDeepeningStatus.COMPLETE
        fingerprint = sha256(
            repr(
                (
                    source_kind.value,
                    source_reference,
                    source_fingerprint,
                    tuple(
                        (
                            item.hypothesis_id,
                            item.relation.value,
                            item.evidence_references,
                            item.rationale_codes,
                        )
                        for item in assessments
                    ),
                    tuple(item.gap_id for item in gaps),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisDeepeningReport(
            report_id=f"hypothesis-deepening-{fingerprint[:16]}",
            status=status,
            source_kind=source_kind,
            source_reference=source_reference,
            world_snapshot_id=world_snapshot_id,
            assessments=assessments,
            epistemic_gaps=gaps,
            evidence_codes=evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _degraded(
        source_kind: HypothesisDeepeningSourceKind,
        source_reference: str,
        world_snapshot_id: str,
        source_fingerprint: str,
    ) -> GovernedHypothesisDeepeningReport:
        fingerprint = sha256(
            repr(
                (
                    source_kind.value,
                    source_reference,
                    world_snapshot_id,
                    source_fingerprint,
                    "hypothesis_deepening_failure",
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedHypothesisDeepeningReport(
            report_id=f"hypothesis-deepening-{fingerprint[:16]}",
            status=HypothesisDeepeningStatus.DEGRADED,
            source_kind=source_kind,
            source_reference=source_reference,
            world_snapshot_id=world_snapshot_id,
            assessments=(),
            epistemic_gaps=(),
            evidence_codes=(f"source:{source_reference}",),
            risk_codes=("hypothesis_deepening_failure",),
            source_fingerprint=fingerprint,
        )
