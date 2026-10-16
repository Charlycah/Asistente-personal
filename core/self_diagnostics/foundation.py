from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from .hypothesis import _assess_diagnostic_hypothesis
from .models import (
    DiagnosticAnomaly,
    DiagnosticAnomalyStatus,
    DiagnosticConfidencePolicy,
    DiagnosticHumanDecision,
    DiagnosticHypothesis,
    DiagnosticHypothesisAssessment,
    DiagnosticObservation,
    DiagnosticProofResult,
    DiagnosticProofSpecification,
    DiagnosticProposal,
    DiagnosticProposalRequest,
    DiagnosticReviewPackage,
    DiagnosticSandboxRequest,
    DiagnosticSandboxResult,
    DiagnosticThreshold,
    DiagnosticThresholdDirection,
    DiagnosticTrend,
    DiagnosticTrendDirection,
    SelfDiagnosticReport,
)
from .proof import _prepare_reproducible_proof, _run_reproducible_proof
from .proposal import _prepare_isolated_proposal, _write_isolated_proposal
from .review import (
    _prepare_diagnostic_review,
    _record_human_decision,
    _write_diagnostic_review,
)
from .sandbox import _validate_diagnostic_sandbox


class GovernedSelfDiagnostics:
    """Read-only authority for technical observation, trend and anomaly evidence."""

    AUTHORITY_ID = "self_diagnostics"

    @property
    def authority_id(self) -> str:
        return self.AUTHORITY_ID

    def diagnose(
        self,
        observations: Iterable[DiagnosticObservation],
        *,
        threshold: DiagnosticThreshold | None = None,
    ) -> SelfDiagnosticReport:
        ordered = tuple(sorted(observations, key=lambda item: item.observed_at))
        if not ordered:
            raise ValueError("self diagnostics requires explicit observations")
        source_authority = ordered[0].source_authority
        metric = ordered[0].metric
        if any(item.source_authority != source_authority for item in ordered):
            raise ValueError("self diagnostics cannot merge source authorities")
        if any(item.metric != metric for item in ordered):
            raise ValueError("self diagnostics cannot merge different metrics")
        observation_ids = tuple(item.observation_id for item in ordered)
        if len(set(observation_ids)) != len(observation_ids):
            raise ValueError("diagnostic observation ids must be unique")
        if threshold is not None and threshold.metric != metric:
            raise ValueError("diagnostic threshold metric must match observations")

        trend = self._trend(ordered)
        anomaly = None if threshold is None else self._anomaly(ordered, threshold)
        return SelfDiagnosticReport(
            source_authority=source_authority,
            metric=metric,
            observations=ordered,
            trend=trend,
            anomaly=anomaly,
        )

    def assess_hypothesis(
        self,
        report: SelfDiagnosticReport,
        hypothesis: DiagnosticHypothesis,
        *,
        policy: DiagnosticConfidencePolicy | None = None,
    ) -> DiagnosticHypothesisAssessment:
        return _assess_diagnostic_hypothesis(report, hypothesis, policy=policy)

    def prepare_reproducible_proof(
        self,
        report: SelfDiagnosticReport,
        assessment: DiagnosticHypothesisAssessment,
        *,
        proof_id: str,
    ) -> DiagnosticProofSpecification:
        return _prepare_reproducible_proof(
            report,
            assessment,
            proof_id=proof_id,
        )

    def run_reproducible_proof(
        self,
        report: SelfDiagnosticReport,
        proof: DiagnosticProofSpecification,
    ) -> DiagnosticProofResult:
        return _run_reproducible_proof(report, proof)

    def prepare_isolated_proposal(
        self,
        proof: DiagnosticProofSpecification,
        result: DiagnosticProofResult,
        request: DiagnosticProposalRequest,
    ) -> DiagnosticProposal:
        return _prepare_isolated_proposal(proof, result, request)

    def write_isolated_proposal(
        self,
        proposal: DiagnosticProposal,
        *,
        project_root: Path,
    ) -> Path:
        return _write_isolated_proposal(proposal, project_root=project_root)

    def validate_in_sandbox(
        self,
        proposal: DiagnosticProposal,
        request: DiagnosticSandboxRequest,
        *,
        project_root: Path,
    ) -> DiagnosticSandboxResult:
        return _validate_diagnostic_sandbox(
            proposal,
            request,
            project_root=project_root,
        )

    def prepare_human_review(
        self,
        proposal: DiagnosticProposal,
        sandbox: DiagnosticSandboxResult,
        *,
        project_root: Path,
        review_id: str,
    ) -> DiagnosticReviewPackage:
        return _prepare_diagnostic_review(
            proposal,
            sandbox,
            project_root=project_root,
            review_id=review_id,
        )

    def write_human_review(
        self,
        review: DiagnosticReviewPackage,
        *,
        project_root: Path,
    ) -> Path:
        return _write_diagnostic_review(review, project_root=project_root)

    def record_human_decision(
        self,
        review: DiagnosticReviewPackage,
        decision: DiagnosticHumanDecision,
        *,
        project_root: Path,
    ) -> Path:
        return _record_human_decision(
            review,
            decision,
            project_root=project_root,
        )

    @staticmethod
    def _trend(observations: tuple[DiagnosticObservation, ...]) -> DiagnosticTrend:
        ids = tuple(item.observation_id for item in observations)
        if len(observations) < 2:
            direction = DiagnosticTrendDirection.INSUFFICIENT_EVIDENCE
        else:
            first = observations[0].value
            last = observations[-1].value
            if last > first:
                direction = DiagnosticTrendDirection.INCREASING
            elif last < first:
                direction = DiagnosticTrendDirection.DECREASING
            else:
                direction = DiagnosticTrendDirection.STABLE
        return DiagnosticTrend(
            source_authority=observations[0].source_authority,
            metric=observations[0].metric,
            direction=direction,
            sample_count=len(observations),
            first_value=observations[0].value,
            last_value=observations[-1].value,
            observation_ids=ids,
        )

    @staticmethod
    def _anomaly(
        observations: tuple[DiagnosticObservation, ...],
        threshold: DiagnosticThreshold,
    ) -> DiagnosticAnomaly:
        violating: list[DiagnosticObservation] = []
        for observation in reversed(observations):
            if _violates(observation.value, threshold):
                violating.append(observation)
            else:
                break
        violating.reverse()
        count = len(violating)
        observed = count >= threshold.minimum_consecutive_samples
        return DiagnosticAnomaly(
            source_authority=observations[0].source_authority,
            metric=observations[0].metric,
            status=(
                DiagnosticAnomalyStatus.OBSERVED
                if observed
                else DiagnosticAnomalyStatus.CLEAR
            ),
            threshold=threshold,
            consecutive_violations=count,
            observation_ids=tuple(item.observation_id for item in violating),
            rationale=(
                "explicit_threshold_violation_reproduced"
                if observed
                else "explicit_threshold_not_reproducibly_violated",
                "observation_evidence_preserved",
                "no_cause_inferred",
                "no_corrective_action_performed",
            ),
        )


def _violates(value: float, threshold: DiagnosticThreshold) -> bool:
    if threshold.direction is DiagnosticThresholdDirection.ABOVE:
        return value > threshold.limit
    return value < threshold.limit
