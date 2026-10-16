from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticConfidenceLevel,
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticProofStatus,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 10, 15, 0, tzinfo=timezone.utc)


def _observation(index: int, value: float) -> DiagnosticObservation:
    return DiagnosticObservation(
        observation_id=f"obs-{index}",
        source_authority="runtime_health_readiness",
        metric="failed_residents",
        value=value,
        observed_at=NOW + timedelta(minutes=index),
        evidence_codes=(f"runtime_snapshot:{index}",),
    )


def _report():
    threshold = DiagnosticThreshold(
        metric="failed_residents",
        limit=0.0,
        direction="above",
        minimum_consecutive_samples=2,
    )
    observations = (
        _observation(1, 1.0),
        _observation(2, 1.0),
        _observation(3, 1.0),
    )
    return GovernedSelfDiagnostics().diagnose(observations, threshold=threshold)


def _assessment():
    report = _report()
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1", "obs-2"))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(report, hypothesis)
    return report, assessment


def test_m399_4_requires_explicit_proof_id() -> None:
    report, assessment = _assessment()
    with pytest.raises(ValueError, match="proof_id"):
        GovernedSelfDiagnostics().prepare_reproducible_proof(
            report,
            assessment,
            proof_id=" ",
        )


def test_m399_4_requires_assessment_reproducible_from_same_evidence() -> None:
    report, assessment = _assessment()
    altered = replace(assessment, confidence_score=0.5)
    with pytest.raises(ValueError, match="must match reproducible"):
        GovernedSelfDiagnostics().prepare_reproducible_proof(
            report,
            altered,
            proof_id="proof-1",
        )


def test_m399_4_rejects_insufficient_evidence_as_proof_input() -> None:
    report = _report()
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1",))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(report, hypothesis)
    assert (
        assessment.confidence_level
        is DiagnosticConfidenceLevel.INSUFFICIENT_EVIDENCE
    )
    with pytest.raises(ValueError, match="sufficient explicit evidence"):
        GovernedSelfDiagnostics().prepare_reproducible_proof(
            report,
            assessment,
            proof_id="proof-1",
        )


def test_m399_4_proof_freezes_sha256_evidence_digest() -> None:
    report, assessment = _assessment()
    proof = GovernedSelfDiagnostics().prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    assert len(proof.evidence_digest) == 64
    int(proof.evidence_digest, 16)


def test_m399_4_exact_replay_reproduces_diagnostic_assessment() -> None:
    report, assessment = _assessment()
    diagnostic = GovernedSelfDiagnostics()
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    result = diagnostic.run_reproducible_proof(report, proof)
    assert result.status is DiagnosticProofStatus.REPRODUCED
    assert result.reproduced_confidence_level is DiagnosticConfidenceLevel.HIGH
    assert result.reproduced_confidence_score == 1.0


def test_m399_4_changed_evidence_is_not_reproduced() -> None:
    report, assessment = _assessment()
    diagnostic = GovernedSelfDiagnostics()
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    changed = replace(
        report,
        observations=report.observations[:-1]
        + (replace(report.observations[-1], value=2.0),),
    )
    result = diagnostic.run_reproducible_proof(changed, proof)
    assert result.status is DiagnosticProofStatus.NOT_REPRODUCED
    assert "evidence_digest_mismatch" in result.rationale


def test_m399_4_source_authority_mismatch_fails_closed() -> None:
    report, assessment = _assessment()
    diagnostic = GovernedSelfDiagnostics()
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    changed = replace(report, source_authority="provider_health")
    result = diagnostic.run_reproducible_proof(changed, proof)
    assert result.status is DiagnosticProofStatus.NOT_REPRODUCED
    assert "source_authority_mismatch" in result.rationale


def test_m399_4_metric_mismatch_fails_closed() -> None:
    report, assessment = _assessment()
    diagnostic = GovernedSelfDiagnostics()
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    changed = replace(report, metric="latency_ms")
    result = diagnostic.run_reproducible_proof(changed, proof)
    assert result.status is DiagnosticProofStatus.NOT_REPRODUCED
    assert "metric_mismatch" in result.rationale


def test_m399_4_proof_does_not_claim_causal_truth() -> None:
    report, assessment = _assessment()
    diagnostic = GovernedSelfDiagnostics()
    proof = diagnostic.prepare_reproducible_proof(
        report,
        assessment,
        proof_id="proof-1",
    )
    result = diagnostic.run_reproducible_proof(report, proof)
    assert "proof_reproduces_assessment_not_causal_truth" in proof.rationale
    assert "prediction_is_not_certainty" in proof.rationale
    assert "proof_reproduces_assessment_not_causal_truth" in result.rationale


def test_m399_4_proof_is_read_only_and_has_no_action_methods() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in (
        "repair",
        "fix",
        "patch",
        "apply",
        "propose",
        "sandbox",
        "write",
        "mutate",
        "run_forever",
    ):
        assert not hasattr(diagnostic, name)


def test_m399_4_keeps_single_self_diagnostics_authority() -> None:
    diagnostic = GovernedSelfDiagnostics()
    assert diagnostic.authority_id == "self_diagnostics"
    source = Path("core/self_diagnostics/proof.py").read_text(encoding="utf-8")
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source


def test_m399_4_proof_contains_no_operational_code_path() -> None:
    source = Path("core/self_diagnostics/proof.py").read_text(encoding="utf-8")
    for forbidden in ("subprocess", "os.system", ".write_text(", ".unlink(", "shutil"):
        assert forbidden not in source


def test_m399_4_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M399_4_GOVERNED_REPRODUCIBLE_DIAGNOSTIC_PROOF.md"
    ).read_text(encoding="utf-8")
    assert "evidencia → prueba reproducible" in document
    assert "predicción ≠ certeza" in document
    assert "no prueba causalidad" in document
    assert "sin proposals" in document
    assert "Milestone M399.4 — Governed Reproducible Diagnostic Proof" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.4 — Governed Reproducible Diagnostic Proof" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.4 — Regla de prueba diagnóstica reproducible" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
