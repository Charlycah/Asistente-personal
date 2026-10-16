from __future__ import annotations

import hashlib
import json
from dataclasses import asdict
from enum import Enum

from .hypothesis import _assess_diagnostic_hypothesis
from .models import (
    DiagnosticConfidenceLevel,
    DiagnosticHypothesisAssessment,
    DiagnosticProofResult,
    DiagnosticProofSpecification,
    DiagnosticProofStatus,
    SelfDiagnosticReport,
)


def _prepare_reproducible_proof(
    report: SelfDiagnosticReport,
    assessment: DiagnosticHypothesisAssessment,
    *,
    proof_id: str,
) -> DiagnosticProofSpecification:
    """Freeze explicit diagnostic inputs for deterministic read-only replay."""

    proof_id = proof_id.strip()
    if not proof_id:
        raise ValueError("diagnostic proof requires proof_id")
    reproduced = _assess_diagnostic_hypothesis(
        report,
        assessment.hypothesis,
        policy=assessment.policy,
    )
    if reproduced != assessment:
        raise ValueError(
            "diagnostic assessment must match reproducible source evidence"
        )
    if assessment.confidence_level is DiagnosticConfidenceLevel.INSUFFICIENT_EVIDENCE:
        raise ValueError("diagnostic proof requires sufficient explicit evidence")
    return DiagnosticProofSpecification(
        proof_id=proof_id,
        hypothesis=assessment.hypothesis,
        policy=assessment.policy,
        source_authority=report.source_authority,
        metric=report.metric,
        expected_confidence_level=assessment.confidence_level,
        expected_confidence_score=assessment.confidence_score,
        evidence_digest=_diagnostic_evidence_digest(report),
        rationale=(
            "proof_replays_explicit_diagnostic_inputs_only",
            "proof_reproduces_assessment_not_causal_truth",
            "prediction_is_not_certainty",
            "read_only_no_corrective_action_performed",
        ),
    )


def _run_reproducible_proof(
    report: SelfDiagnosticReport,
    proof: DiagnosticProofSpecification,
) -> DiagnosticProofResult:
    """Replay a frozen proof without changing runtime or operational code."""

    reasons: list[str] = []
    if report.source_authority != proof.source_authority:
        reasons.append("source_authority_mismatch")
    if report.metric != proof.metric:
        reasons.append("metric_mismatch")

    digest = _diagnostic_evidence_digest(report)
    if digest != proof.evidence_digest:
        reasons.append("evidence_digest_mismatch")

    if reasons:
        return DiagnosticProofResult(
            proof_id=proof.proof_id,
            hypothesis_id=proof.hypothesis.hypothesis_id,
            status=DiagnosticProofStatus.NOT_REPRODUCED,
            reproduced_confidence_level=None,
            reproduced_confidence_score=None,
            evidence_digest=digest,
            rationale=tuple(reasons)
            + (
                "proof_did_not_modify_environment",
                "proof_result_is_not_causal_certainty",
            ),
        )

    try:
        assessment = _assess_diagnostic_hypothesis(
            report,
            proof.hypothesis,
            policy=proof.policy,
        )
    except ValueError as exc:
        return DiagnosticProofResult(
            proof_id=proof.proof_id,
            hypothesis_id=proof.hypothesis.hypothesis_id,
            status=DiagnosticProofStatus.INCONCLUSIVE,
            reproduced_confidence_level=None,
            reproduced_confidence_score=None,
            evidence_digest=digest,
            rationale=(
                "diagnostic_replay_inconclusive",
                str(exc),
                "proof_did_not_modify_environment",
                "proof_result_is_not_causal_certainty",
            ),
        )

    reproduced = (
        assessment.confidence_level is proof.expected_confidence_level
        and assessment.confidence_score == proof.expected_confidence_score
    )
    return DiagnosticProofResult(
        proof_id=proof.proof_id,
        hypothesis_id=proof.hypothesis.hypothesis_id,
        status=(
            DiagnosticProofStatus.REPRODUCED
            if reproduced
            else DiagnosticProofStatus.NOT_REPRODUCED
        ),
        reproduced_confidence_level=assessment.confidence_level,
        reproduced_confidence_score=assessment.confidence_score,
        evidence_digest=digest,
        rationale=(
            "diagnostic_assessment_reproduced"
            if reproduced
            else "diagnostic_assessment_changed",
            "proof_reproduces_assessment_not_causal_truth",
            "prediction_is_not_certainty",
            "proof_did_not_modify_environment",
        ),
    )


def _diagnostic_evidence_digest(report: SelfDiagnosticReport) -> str:
    payload = _json_safe(asdict(report))
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _json_safe(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()  # type: ignore[union-attr]
    return value
