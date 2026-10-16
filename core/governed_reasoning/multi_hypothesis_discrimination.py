from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from itertools import combinations

from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
    HypothesisEvidenceAssessment,
)


class HypothesisPairRelation(StrEnum):
    INDISTINGUISHABLE = "indistinguishable"
    PARTIALLY_DISCRIMINATED = "partially_discriminated"


class MultiHypothesisDiscriminationStatus(StrEnum):
    COMPLETE = "complete"
    DISCRIMINATION_REQUIREMENTS_PRESENT = "discrimination_requirements_present"
    INSUFFICIENT_HYPOTHESES = "insufficient_hypotheses"
    SOURCE_REVIEW_REQUIRED = "source_review_required"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class HypothesisPairComparison:
    left_hypothesis_id: str
    right_hypothesis_id: str
    relation: HypothesisPairRelation
    shared_evidence_references: tuple[str, ...]
    left_only_evidence_references: tuple[str, ...]
    right_only_evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    establishes_truth: bool = False
    establishes_falsity: bool = False

    def __post_init__(self) -> None:
        if not self.left_hypothesis_id.strip() or not self.right_hypothesis_id.strip():
            raise ValueError("pair comparison requires hypothesis identities")
        if self.left_hypothesis_id == self.right_hypothesis_id:
            raise ValueError("pair comparison requires distinct hypotheses")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("pair comparison requires rationale codes")
        if self.establishes_truth or self.establishes_falsity:
            raise ValueError("comparison cannot establish truth or falsity")


@dataclass(frozen=True)
class DiscriminatingEvidenceRequirement:
    requirement_id: str
    hypothesis_ids: tuple[str, str]
    source_reference: str
    world_snapshot_id: str
    known_elements: tuple[str, ...]
    missing_evidence_descriptions: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    source_report_id: str = ""
    read_only: bool = True
    creates_acquisition_plan: bool = False
    acquires_evidence: bool = False
    creates_question: bool = False
    modifies_memory: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        if not self.requirement_id.startswith("discrimination-requirement-"):
            raise ValueError("discrimination requirement identifier is invalid")
        if len(set(self.hypothesis_ids)) != 2:
            raise ValueError("discrimination requirement needs two hypotheses")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("discrimination requirement requires source lineage")
        if not self.missing_evidence_descriptions or any(
            not item.strip() for item in self.missing_evidence_descriptions
        ):
            raise ValueError("discrimination requirement needs missing evidence")
        if not self.evidence_codes or any(
            not item.strip() for item in self.evidence_codes
        ):
            raise ValueError("discrimination requirement needs evidence codes")
        if not self.read_only or any(
            (
                self.creates_acquisition_plan,
                self.acquires_evidence,
                self.creates_question,
                self.modifies_memory,
                self.executes_actions,
            )
        ):
            raise ValueError("discrimination requirement violates governed limits")


class DiscriminatingTestProposalStatus(StrEnum):
    PROPOSED = "proposed"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class HypothesisExpectedObservation:
    hypothesis_id: str
    observation: str

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.observation.strip():
            raise ValueError("expected observation fields must not be blank")


@dataclass(frozen=True)
class GovernedDiscriminatingTestProposal:
    proposal_id: str
    status: DiscriminatingTestProposalStatus
    requirement_id: str
    hypothesis_ids: tuple[str, str]
    source_reference: str
    world_snapshot_id: str
    source_report_id: str
    evidence_codes: tuple[str, ...]
    expected_observations: tuple[HypothesisExpectedObservation, ...]
    rationale_codes: tuple[str, ...]
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    creates_acquisition_plan: bool = False
    acquires_evidence: bool = False
    creates_question: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    modifies_learning: bool = False
    modifies_planning: bool = False
    grants_authority: bool = False
    executes_actions: bool = False
    establishes_truth: bool = False
    establishes_falsity: bool = False
    persists_results: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.proposal_id.startswith("discriminating-test-proposal-"):
            raise ValueError("discriminating test proposal identifier is invalid")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("discriminating test must preserve reasoning authority")
        if not self.read_only or not self.consultative:
            raise ValueError("discriminating test proposal must be consultative")
        governed_limits = (
            self.creates_acquisition_plan,
            self.acquires_evidence,
            self.creates_question,
            self.modifies_memory,
            self.modifies_world_model,
            self.modifies_learning,
            self.modifies_planning,
            self.grants_authority,
            self.executes_actions,
            self.establishes_truth,
            self.establishes_falsity,
            self.persists_results,
            self.starts_background_process,
        )
        if any(governed_limits):
            raise ValueError("discriminating test proposal violates governed limits")
        if self.status is DiscriminatingTestProposalStatus.PROPOSED:
            expected_ids = tuple(
                item.hypothesis_id for item in self.expected_observations
            )
            if set(expected_ids) != set(self.hypothesis_ids):
                raise ValueError("proposal must cover exactly both hypotheses")
            if len(expected_ids) != len(set(expected_ids)):
                raise ValueError("proposal observations must be unique by hypothesis")
        elif self.expected_observations:
            raise ValueError("review-required proposal cannot expose observations")


class GovernedDiscriminatingTestProposer:
    """Pure N4 proposal subordinate to existing governed_reasoning authority."""

    def propose(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        *,
        expected_observations: tuple[HypothesisExpectedObservation, ...],
    ) -> GovernedDiscriminatingTestProposal:
        expected_ids = tuple(item.hypothesis_id for item in expected_observations)
        if (
            len(expected_observations) != 2
            or len(set(expected_ids)) != 2
            or set(expected_ids) != set(requirement.hypothesis_ids)
        ):
            raise ValueError("expected observations must cover exact hypotheses")
        return self._result(
            requirement,
            DiscriminatingTestProposalStatus.PROPOSED,
            expected_observations,
            ("n4:bounded_discriminating_test_proposed",),
        )

    def propose_safely(
        self,
        requirement: DiscriminatingEvidenceRequirement,
        *,
        expected_observations: tuple[HypothesisExpectedObservation, ...],
    ) -> GovernedDiscriminatingTestProposal:
        try:
            return self.propose(
                requirement,
                expected_observations=expected_observations,
            )
        except (TypeError, ValueError):
            return self._result(
                requirement,
                DiscriminatingTestProposalStatus.REVIEW_REQUIRED,
                (),
                ("n4:expected_observation_lineage_review_required",),
            )

    @staticmethod
    def _result(
        requirement: DiscriminatingEvidenceRequirement,
        status: DiscriminatingTestProposalStatus,
        expected_observations: tuple[HypothesisExpectedObservation, ...],
        rationale_codes: tuple[str, ...],
    ) -> GovernedDiscriminatingTestProposal:
        fingerprint = sha256(
            repr(
                (
                    requirement.requirement_id,
                    requirement.hypothesis_ids,
                    requirement.source_reference,
                    requirement.world_snapshot_id,
                    expected_observations,
                    status.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedDiscriminatingTestProposal(
            proposal_id=f"discriminating-test-proposal-{fingerprint[:16]}",
            status=status,
            requirement_id=requirement.requirement_id,
            hypothesis_ids=requirement.hypothesis_ids,
            source_reference=requirement.source_reference,
            world_snapshot_id=requirement.world_snapshot_id,
            source_report_id=requirement.source_report_id,
            evidence_codes=requirement.evidence_codes,
            expected_observations=expected_observations,
            rationale_codes=rationale_codes,
        )


@dataclass(frozen=True)
class GovernedMultiHypothesisDiscriminationReport:
    report_id: str
    status: MultiHypothesisDiscriminationStatus
    source_reference: str
    world_snapshot_id: str
    comparisons: tuple[HypothesisPairComparison, ...]
    discrimination_requirements: tuple[DiscriminatingEvidenceRequirement, ...]
    evidence_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-multi-hypothesis-discrimination-v1"
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    persists_results: bool = False
    creates_facts: bool = False
    creates_questions: bool = False
    creates_acquisition_plans: bool = False
    acquires_evidence: bool = False
    modifies_memory: bool = False
    modifies_planning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("multi-hypothesis-discrimination-"):
            raise ValueError("multi-hypothesis report identifier is invalid")
        if not self.source_reference.strip() or not self.world_snapshot_id.strip():
            raise ValueError("multi-hypothesis report requires source lineage")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("multi-hypothesis comparison must preserve authority")
        if not self.read_only or not self.consultative or any(
            (
                self.persists_results,
                self.creates_facts,
                self.creates_questions,
                self.creates_acquisition_plans,
                self.acquires_evidence,
                self.modifies_memory,
                self.modifies_planning,
                self.executes_actions,
                self.grants_authority,
                self.starts_background_process,
            )
        ):
            raise ValueError("multi-hypothesis comparison violates governed limits")


class GovernedMultiHypothesisDiscriminator:
    """Read-only comparison over one governed hypothesis-deepening report."""

    CANONICAL_AUTHORITY = "governed_reasoning"

    def compare(
        self,
        report: GovernedHypothesisDeepeningReport,
    ) -> GovernedMultiHypothesisDiscriminationReport:
        if report.status is HypothesisDeepeningStatus.DEGRADED:
            return self._empty_report(
                report,
                MultiHypothesisDiscriminationStatus.DEGRADED,
                "source_hypothesis_deepening_degraded",
            )
        if report.status is HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED:
            return self._empty_report(
                report,
                MultiHypothesisDiscriminationStatus.SOURCE_REVIEW_REQUIRED,
                "source_review_required",
            )
        if len(report.assessments) < 2:
            return self._empty_report(
                report,
                MultiHypothesisDiscriminationStatus.INSUFFICIENT_HYPOTHESES,
                "insufficient_hypotheses_for_comparison",
            )

        gaps_by_hypothesis = {
            gap.hypothesis_id: gap for gap in report.epistemic_gaps
        }
        comparisons = []
        requirements = []
        for left, right in combinations(report.assessments, 2):
            comparison = self._compare_pair(left, right)
            comparisons.append(comparison)
            if comparison.relation is HypothesisPairRelation.INDISTINGUISHABLE:
                requirements.append(
                    self._requirement(
                        report,
                        left,
                        right,
                        gaps_by_hypothesis.get(left.hypothesis_id),
                        gaps_by_hypothesis.get(right.hypothesis_id),
                        comparison,
                    )
                )

        status = (
            MultiHypothesisDiscriminationStatus.DISCRIMINATION_REQUIREMENTS_PRESENT
            if requirements
            else MultiHypothesisDiscriminationStatus.COMPLETE
        )
        return self._report(
            report,
            status,
            tuple(comparisons),
            tuple(requirements),
            risk_codes=(
                "comparison_does_not_establish_truth",
                "shared_evidence_is_not_discriminating_evidence",
            ),
        )

    @staticmethod
    def _compare_pair(
        left: HypothesisEvidenceAssessment,
        right: HypothesisEvidenceAssessment,
    ) -> HypothesisPairComparison:
        left_refs = set(left.evidence_references)
        right_refs = set(right.evidence_references)
        shared = tuple(sorted(left_refs & right_refs))
        left_only = tuple(sorted(left_refs - right_refs))
        right_only = tuple(sorted(right_refs - left_refs))
        distinguishable = bool(
            left_only or right_only or left.relation is not right.relation
        )
        relation = (
            HypothesisPairRelation.PARTIALLY_DISCRIMINATED
            if distinguishable
            else HypothesisPairRelation.INDISTINGUISHABLE
        )
        rationale = [f"comparison:{relation.value}"]
        if shared:
            rationale.append("comparison:shared_evidence_present")
        if left_only or right_only:
            rationale.append("comparison:differential_evidence_present")
        if left.relation is not right.relation:
            rationale.append("comparison:epistemic_relation_differs")
        return HypothesisPairComparison(
            left_hypothesis_id=left.hypothesis_id,
            right_hypothesis_id=right.hypothesis_id,
            relation=relation,
            shared_evidence_references=shared,
            left_only_evidence_references=left_only,
            right_only_evidence_references=right_only,
            rationale_codes=tuple(rationale),
        )

    @staticmethod
    def _requirement(
        report: GovernedHypothesisDeepeningReport,
        left: HypothesisEvidenceAssessment,
        right: HypothesisEvidenceAssessment,
        left_gap: HypothesisEpistemicGap | None,
        right_gap: HypothesisEpistemicGap | None,
        comparison: HypothesisPairComparison,
    ) -> DiscriminatingEvidenceRequirement:
        descriptions = tuple(
            dict.fromkeys(
                item
                for item in (
                    getattr(left_gap, "unknown_element", ""),
                    getattr(right_gap, "unknown_element", ""),
                )
                if item.strip()
            )
        )
        if not descriptions:
            descriptions = (
                "explicit evidence that differentiates the compared hypotheses",
            )
        known_elements = tuple(
            dict.fromkeys(
                (
                    *comparison.shared_evidence_references,
                    *comparison.left_only_evidence_references,
                    *comparison.right_only_evidence_references,
                )
            )
        )
        evidence_codes = tuple(
            dict.fromkeys(
                (
                    *report.evidence_codes,
                    *left.rationale_codes,
                    *right.rationale_codes,
                    *comparison.rationale_codes,
                )
            )
        )
        fingerprint = sha256(
            repr(
                (
                    report.source_reference,
                    report.world_snapshot_id,
                    left.hypothesis_id,
                    right.hypothesis_id,
                    known_elements,
                    descriptions,
                )
            ).encode("utf-8")
        ).hexdigest()
        return DiscriminatingEvidenceRequirement(
            requirement_id=f"discrimination-requirement-{fingerprint[:16]}",
            hypothesis_ids=(left.hypothesis_id, right.hypothesis_id),
            source_reference=report.source_reference,
            world_snapshot_id=report.world_snapshot_id,
            known_elements=known_elements,
            missing_evidence_descriptions=descriptions,
            evidence_codes=evidence_codes,
            source_report_id=report.report_id,
        )

    @staticmethod
    def _report(
        source: GovernedHypothesisDeepeningReport,
        status: MultiHypothesisDiscriminationStatus,
        comparisons: tuple[HypothesisPairComparison, ...],
        requirements: tuple[DiscriminatingEvidenceRequirement, ...],
        *,
        risk_codes: tuple[str, ...],
    ) -> GovernedMultiHypothesisDiscriminationReport:
        fingerprint = sha256(
            repr(
                (
                    source.report_id,
                    source.source_reference,
                    source.world_snapshot_id,
                    tuple(
                        (
                            item.left_hypothesis_id,
                            item.right_hypothesis_id,
                            item.relation.value,
                        )
                        for item in comparisons
                    ),
                    tuple(item.requirement_id for item in requirements),
                )
            ).encode("utf-8")
        ).hexdigest()
        return GovernedMultiHypothesisDiscriminationReport(
            report_id=f"multi-hypothesis-discrimination-{fingerprint[:16]}",
            status=status,
            source_reference=source.source_reference,
            world_snapshot_id=source.world_snapshot_id,
            comparisons=comparisons,
            discrimination_requirements=requirements,
            evidence_codes=source.evidence_codes,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    def _empty_report(
        self,
        source: GovernedHypothesisDeepeningReport,
        status: MultiHypothesisDiscriminationStatus,
        risk_code: str,
    ) -> GovernedMultiHypothesisDiscriminationReport:
        return self._report(
            source,
            status,
            (),
            (),
            risk_codes=(risk_code, "comparison_does_not_establish_truth"),
        )
