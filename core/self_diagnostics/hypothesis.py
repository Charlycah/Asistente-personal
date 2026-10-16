from __future__ import annotations

from .models import (
    DiagnosticConfidenceLevel,
    DiagnosticConfidencePolicy,
    DiagnosticHypothesis,
    DiagnosticHypothesisAssessment,
    SelfDiagnosticReport,
)


def _assess_diagnostic_hypothesis(
    report: SelfDiagnosticReport,
    hypothesis: DiagnosticHypothesis,
    *,
    policy: DiagnosticConfidencePolicy | None = None,
) -> DiagnosticHypothesisAssessment:
    """Assess an explicit candidate without inferring or acting on a cause."""

    if not report.anomaly_observed:
        raise ValueError("diagnostic hypothesis requires an observed anomaly")

    observation_ids = {item.observation_id for item in report.observations}
    referenced_ids = set(hypothesis.supporting_observation_ids).union(
        hypothesis.contradicting_observation_ids
    )
    unknown_ids = referenced_ids.difference(observation_ids)
    if unknown_ids:
        unknown = ", ".join(sorted(unknown_ids))
        raise ValueError(
            f"diagnostic hypothesis references unknown evidence: {unknown}"
        )

    effective_policy = policy or DiagnosticConfidencePolicy()
    supporting_count = len(hypothesis.supporting_observation_ids)
    contradicting_count = len(hypothesis.contradicting_observation_ids)
    evidence_count = supporting_count + contradicting_count
    support_ratio = supporting_count / evidence_count if evidence_count else 0.0

    if supporting_count < effective_policy.minimum_supporting_evidence:
        level = DiagnosticConfidenceLevel.INSUFFICIENT_EVIDENCE
        rationale = "supporting_evidence_below_explicit_minimum"
    elif support_ratio < effective_policy.minimum_supported_ratio:
        level = DiagnosticConfidenceLevel.LOW
        rationale = "contradicting_evidence_limits_confidence"
    elif support_ratio >= effective_policy.high_confidence_ratio:
        level = DiagnosticConfidenceLevel.HIGH
        rationale = "explicit_evidence_meets_high_confidence_policy"
    else:
        level = DiagnosticConfidenceLevel.MEDIUM
        rationale = "explicit_evidence_meets_supported_confidence_policy"

    evidence_codes = tuple(
        code
        for observation in report.observations
        if observation.observation_id in referenced_ids
        for code in observation.evidence_codes
    )
    return DiagnosticHypothesisAssessment(
        hypothesis=hypothesis,
        confidence_level=level,
        confidence_score=round(support_ratio, 6),
        supporting_evidence_count=supporting_count,
        contradicting_evidence_count=contradicting_count,
        evidence_codes=evidence_codes,
        policy=effective_policy,
        rationale=(
            rationale,
            "confidence_derived_from_explicit_evidence_only",
            "hypothesis_is_candidate_not_causal_certainty",
            "prediction_is_not_certainty",
            "no_corrective_action_performed",
        ),
    )
