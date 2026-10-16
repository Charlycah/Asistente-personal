from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnalysisSnapshot,
    CognitiveTraceAnomalyDetector,
    CognitiveTraceAnomalyPolicy,
)


def _snapshot(**overrides):
    values = {
        "schema_version": "rp22.10",
        "retained_correlations": 4,
        "analyzed_traces": 4,
        "fallback_count": 0,
        "policy_counts": (("respond", 4),),
        "risk_counts": (("low", 4),),
        "calibration_counts": (("aligned", 4),),
        "stage_counts": (("decision", 4),),
        "divergence_counts": (),
    }
    values.update(overrides)
    return CognitiveTraceAnalysisSnapshot(**values)


def test_detector_reports_no_anomaly_for_stable_aggregates():
    result = CognitiveTraceAnomalyDetector().detect(_snapshot())

    assert result.schema_version == "rp22.11"
    assert result.eligible is True
    assert result.anomaly_detected is False
    assert result.findings == ()


def test_detector_flags_deterministic_rate_anomalies():
    analysis = _snapshot(
        fallback_count=3,
        risk_counts=(("high", 3), ("low", 1)),
        calibration_counts=(("diverged", 2), ("incomplete", 1), ("aligned", 1)),
        divergence_counts=(("policy_execution_mismatch", 3),),
    )

    result = CognitiveTraceAnomalyDetector().detect(analysis)

    assert result.anomaly_detected is True
    assert result.finding_codes == (
        "calibration_degradation_elevated",
        "divergence_rate_elevated",
        "fallback_rate_elevated",
        "high_risk_rate_elevated",
    )
    assert all(finding.severity == "warning" for finding in result.findings)


def test_detector_requires_minimum_sample_size():
    detector = CognitiveTraceAnomalyDetector(
        CognitiveTraceAnomalyPolicy(minimum_sample_size=5)
    )

    result = detector.detect(_snapshot(analyzed_traces=4))

    assert result.eligible is False
    assert result.anomaly_detected is False
    assert result.finding_codes == ()


def test_snapshot_is_serializable_immutable_and_contains_no_free_text():
    result = CognitiveTraceAnomalyDetector().detect(
        _snapshot(fallback_count=3)
    )
    payload = result.as_dict()

    assert payload["schema_version"] == "rp22.11"
    assert "prompt" not in str(payload).lower()
    assert "narrative" not in str(payload).lower()
    with pytest.raises(FrozenInstanceError):
        result.sample_size = 99


def test_detector_failure_does_not_affect_decision_consolidation():
    class BrokenDetector:
        def detect(self, analysis):
            raise RuntimeError("detector unavailable")

    kernel = CognitiveDecisionKernel(trace_anomaly_detector=BrokenDetector())
    from core.cognitive_planning import CognitivePlanner

    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    with pytest.raises(RuntimeError, match="detector unavailable"):
        kernel.detect_trace_anomalies()
