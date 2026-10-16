from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnomalyConsolidationPolicy,
    CognitiveTraceAnomalyConsolidator,
    CognitiveTraceAnomalyPriorityRecord,
    CognitiveTraceAnomalyPrioritySnapshot,
)


def _record(code: str, score: int, *, rate: float = 0.8):
    return CognitiveTraceAnomalyPriorityRecord(
        code=code,
        classification="high" if score >= 60 else "medium",
        severity="warning",
        operational_impact="high",
        recurrence_count=2,
        observed_rate=rate,
        threshold=0.5,
        excess_rate=rate - 0.5,
        priority_score=score,
    )


def _snapshot(*records):
    return CognitiveTraceAnomalyPrioritySnapshot(
        schema_version="rp22.12",
        anomaly_count=len(records),
        prioritized_count=len(records),
        highest_classification="high" if records else None,
        records=tuple(records),
    )


def test_consolidator_deduplicates_equivalent_codes_deterministically():
    snapshots = (
        _snapshot(_record("fallback_rate_elevated", 62)),
        _snapshot(_record("fallback_rate_elevated", 71, rate=0.9)),
    )

    result = CognitiveTraceAnomalyConsolidator().consolidate(snapshots)

    assert result.schema_version == "rp22.13"
    assert result.input_record_count == 2
    assert result.consolidated_count == 1
    assert result.duplicate_count == 1
    assert result.records[0].priority_score == 71
    assert result.records[0].occurrence_count == 2
    assert result.records[0].maximum_observed_rate == 0.9


def test_distinct_codes_remain_separate_and_sorted_by_priority():
    result = CognitiveTraceAnomalyConsolidator().consolidate(
        (
            _snapshot(
                _record("divergence_rate_elevated", 55),
                _record("high_risk_rate_elevated", 88),
            ),
        )
    )

    assert tuple(record.code for record in result.records) == (
        "high_risk_rate_elevated",
        "divergence_rate_elevated",
    )
    assert result.duplicate_count == 0


def test_policy_bounds_snapshots_and_output_groups():
    consolidator = CognitiveTraceAnomalyConsolidator(
        CognitiveTraceAnomalyConsolidationPolicy(
            maximum_snapshots=1,
            maximum_groups=1,
        )
    )
    result = consolidator.consolidate(
        (
            _snapshot(_record("old_code", 99)),
            _snapshot(_record("code_a", 40), _record("code_b", 80)),
        )
    )

    assert result.input_snapshot_count == 1
    assert result.input_record_count == 2
    assert result.consolidated_count == 1
    assert result.truncated_group_count == 1
    assert result.records[0].code == "code_b"


def test_policy_validation_and_snapshot_immutability():
    with pytest.raises(ValueError, match="maximum_snapshots"):
        CognitiveTraceAnomalyConsolidationPolicy(maximum_snapshots=0)

    result = CognitiveTraceAnomalyConsolidator().consolidate(())
    with pytest.raises(FrozenInstanceError):
        result.consolidated_count = 99


def test_consolidator_failure_does_not_affect_decision_consolidation():
    class BrokenConsolidator:
        def consolidate(self, snapshots):
            raise RuntimeError("consolidator unavailable")

    from core.cognitive_planning import CognitivePlanner

    kernel = CognitiveDecisionKernel(trace_anomaly_consolidator=BrokenConsolidator())
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    with pytest.raises(RuntimeError, match="consolidator unavailable"):
        kernel.consolidate_trace_anomalies(())
