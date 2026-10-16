from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnalysisSnapshot,
    CognitiveTraceAnomalyDetector,
    CognitiveTraceAnomalyPrioritizer,
    CognitiveTraceAnomalyPriorityPolicy,
)


def _analysis(**overrides):
    values = {
        "schema_version": "rp22.10",
        "retained_correlations": 4,
        "analyzed_traces": 4,
        "fallback_count": 3,
        "policy_counts": (("fallback", 3), ("respond", 1)),
        "risk_counts": (("high", 3), ("low", 1)),
        "calibration_counts": (("diverged", 3), ("aligned", 1)),
        "stage_counts": (("decision", 4),),
        "divergence_counts": (("policy_execution_mismatch", 3),),
    }
    values.update(overrides)
    return CognitiveTraceAnalysisSnapshot(**values)


def _anomaly(**overrides):
    return CognitiveTraceAnomalyDetector().detect(_analysis(**overrides))


def test_prioritizer_orders_records_deterministically():
    result = CognitiveTraceAnomalyPrioritizer().prioritize(_anomaly())

    assert result.schema_version == "rp22.12"
    assert result.prioritized_count == 4
    assert tuple(record.priority_score for record in result.records) == tuple(
        sorted((record.priority_score for record in result.records), reverse=True)
    )
    assert result.highest_classification == "medium"


def test_recurrence_increases_priority_without_free_text():
    current = _anomaly()
    history = (current, current, current)
    prioritizer = CognitiveTraceAnomalyPrioritizer()

    first = prioritizer.prioritize(current)
    recurring = prioritizer.prioritize(current, history)

    assert recurring.records[0].recurrence_count == 4
    assert recurring.records[0].priority_score > first.records[0].priority_score
    assert "prompt" not in str(recurring.as_dict()).lower()


def test_empty_anomaly_produces_empty_priority_snapshot():
    stable = _anomaly(
        fallback_count=0,
        risk_counts=(("low", 4),),
        calibration_counts=(("aligned", 4),),
        divergence_counts=(),
    )

    result = CognitiveTraceAnomalyPrioritizer().prioritize(stable)

    assert result.anomaly_count == 0
    assert result.records == ()
    assert result.highest_classification is None


def test_policy_validation_and_snapshot_immutability():
    with pytest.raises(ValueError, match="sum to 100"):
        CognitiveTraceAnomalyPriorityPolicy(severity_weight=20)

    result = CognitiveTraceAnomalyPrioritizer().prioritize(_anomaly())
    with pytest.raises(FrozenInstanceError):
        result.prioritized_count = 99


def test_prioritizer_failure_does_not_affect_consolidation():
    class BrokenPrioritizer:
        def prioritize(self, anomaly, history=()):
            raise RuntimeError("prioritizer unavailable")

    from core.cognitive_planning import CognitivePlanner

    kernel = CognitiveDecisionKernel(trace_anomaly_prioritizer=BrokenPrioritizer())
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    with pytest.raises(RuntimeError, match="prioritizer unavailable"):
        kernel.prioritize_trace_anomalies()
