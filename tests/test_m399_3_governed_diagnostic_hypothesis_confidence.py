from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from core.self_diagnostics import (
    DiagnosticConfidenceLevel,
    DiagnosticConfidencePolicy,
    DiagnosticHypothesis,
    DiagnosticObservation,
    DiagnosticThreshold,
    GovernedSelfDiagnostics,
)

NOW = datetime(2026, 8, 10, 14, 0, tzinfo=timezone.utc)


def _observation(index: int, value: float) -> DiagnosticObservation:
    return DiagnosticObservation(
        observation_id=f"obs-{index}",
        source_authority="runtime_health_readiness",
        metric="failed_residents",
        value=value,
        observed_at=NOW + timedelta(minutes=index),
        evidence_codes=(f"runtime_snapshot:{index}",),
    )


def _anomalous_report():
    observations = (_observation(1, 1.0), _observation(2, 1.0), _observation(3, 1.0))
    threshold = DiagnosticThreshold(
        metric="failed_residents",
        limit=0.0,
        direction="above",
        minimum_consecutive_samples=2,
    )
    return GovernedSelfDiagnostics().diagnose(observations, threshold=threshold)


def test_m399_3_requires_explicit_hypothesis_identity_and_statement() -> None:
    with pytest.raises(ValueError, match="hypothesis_id"):
        DiagnosticHypothesis(" ", "candidate", ("obs-1",))
    with pytest.raises(ValueError, match="statement"):
        DiagnosticHypothesis("hyp-1", " ", ("obs-1",))


def test_m399_3_rejects_empty_or_duplicate_evidence_ids() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        DiagnosticHypothesis("hyp-1", "candidate", (" ",))
    with pytest.raises(ValueError, match="must be unique"):
        DiagnosticHypothesis("hyp-1", "candidate", ("obs-1", "obs-1"))


def test_m399_3_same_evidence_cannot_support_and_contradict() -> None:
    with pytest.raises(ValueError, match="both support and contradict"):
        DiagnosticHypothesis(
            "hyp-1",
            "candidate",
            ("obs-1",),
            ("obs-1",),
        )


def test_m399_3_requires_observed_anomaly_before_hypothesis_assessment() -> None:
    report = GovernedSelfDiagnostics().diagnose((_observation(1, 0.0),))
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1",))
    with pytest.raises(ValueError, match="observed anomaly"):
        GovernedSelfDiagnostics().assess_hypothesis(report, hypothesis)


def test_m399_3_rejects_evidence_outside_report() -> None:
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-404",))
    with pytest.raises(ValueError, match="unknown evidence"):
        GovernedSelfDiagnostics().assess_hypothesis(_anomalous_report(), hypothesis)


def test_m399_3_one_supporting_sample_is_insufficient_by_default() -> None:
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1",))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis
    )
    assert (
        assessment.confidence_level
        is DiagnosticConfidenceLevel.INSUFFICIENT_EVIDENCE
    )
    assert assessment.confidence_score == 1.0


def test_m399_3_two_supporting_samples_can_reach_high_confidence() -> None:
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1", "obs-2"))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis
    )
    assert assessment.confidence_level is DiagnosticConfidenceLevel.HIGH
    assert assessment.confidence_score == 1.0


def test_m399_3_contradiction_degrades_confidence_transparently() -> None:
    hypothesis = DiagnosticHypothesis(
        "hyp-1",
        "candidate",
        ("obs-1", "obs-2"),
        ("obs-3",),
    )
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis
    )
    assert assessment.confidence_level is DiagnosticConfidenceLevel.MEDIUM
    assert assessment.confidence_score == pytest.approx(2 / 3, abs=1e-6)


def test_m399_3_explicit_policy_can_classify_low_confidence() -> None:
    hypothesis = DiagnosticHypothesis(
        "hyp-1",
        "candidate",
        ("obs-1", "obs-2"),
        ("obs-3",),
    )
    policy = DiagnosticConfidencePolicy(
        minimum_supporting_evidence=2,
        minimum_supported_ratio=0.8,
        high_confidence_ratio=0.95,
    )
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis, policy=policy
    )
    assert assessment.confidence_level is DiagnosticConfidenceLevel.LOW
    assert assessment.policy == policy


def test_m399_3_confidence_policy_is_explicit_and_validated() -> None:
    with pytest.raises(ValueError, match="positive"):
        DiagnosticConfidencePolicy(minimum_supporting_evidence=0)
    with pytest.raises(ValueError, match="between 0 and 1"):
        DiagnosticConfidencePolicy(minimum_supported_ratio=1.1)
    with pytest.raises(ValueError, match="cannot be below"):
        DiagnosticConfidencePolicy(
            minimum_supported_ratio=0.9,
            high_confidence_ratio=0.8,
        )


def test_m399_3_preserves_source_evidence_codes() -> None:
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1", "obs-3"))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis
    )
    assert assessment.evidence_codes == ("runtime_snapshot:1", "runtime_snapshot:3")


def test_m399_3_confidence_rationale_preserves_epistemic_boundary() -> None:
    hypothesis = DiagnosticHypothesis("hyp-1", "candidate", ("obs-1", "obs-2"))
    assessment = GovernedSelfDiagnostics().assess_hypothesis(
        _anomalous_report(), hypothesis
    )
    assert "confidence_derived_from_explicit_evidence_only" in assessment.rationale
    assert "hypothesis_is_candidate_not_causal_certainty" in assessment.rationale
    assert "prediction_is_not_certainty" in assessment.rationale
    assert "no_corrective_action_performed" in assessment.rationale


def test_m399_3_does_not_generate_hypothesis_from_anomaly() -> None:
    report = _anomalous_report()
    assert not hasattr(report, "hypothesis")
    assert not hasattr(GovernedSelfDiagnostics(), "generate_hypothesis")
    assert not hasattr(GovernedSelfDiagnostics(), "infer_cause")


def test_m399_3_still_exposes_no_repair_proposal_or_background_methods() -> None:
    diagnostic = GovernedSelfDiagnostics()
    for name in (
        "repair",
        "fix",
        "patch",
        "apply",
        "propose",
        "sandbox",
        "start",
        "poll",
        "monitor",
        "run_forever",
    ):
        assert not hasattr(diagnostic, name)


def test_m399_3_keeps_single_self_diagnostics_authority() -> None:
    diagnostic = GovernedSelfDiagnostics()
    assert diagnostic.authority_id == "self_diagnostics"
    source = Path("core/self_diagnostics/hypothesis.py").read_text(encoding="utf-8")
    assert "AUTHORITY_ID" not in source
    assert "class Governed" not in source


def test_m399_3_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document_path = (
        root / "docs/M399_3_GOVERNED_DIAGNOSTIC_HYPOTHESIS_CONFIDENCE.md"
    )
    document = document_path.read_text(encoding="utf-8")
    chain = (
        "Observación → tendencia → anomalía → hipótesis → "
        "confianza → evidencia"
    )
    assert chain in document
    assert "predicción ≠ certeza" in document
    assert "hipótesis candidata explícita" in document
    assert "sin proposals" in document
    assert "Milestone M399.3 — Governed Diagnostic Hypothesis & Confidence" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M399.3 — Governed Diagnostic Hypothesis & Confidence" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M399.3 — Regla de hipótesis diagnóstica gobernada" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
