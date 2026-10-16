from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnomalyConsolidatedRecord,
    CognitiveTraceAnomalyConsolidationSnapshot,
    CognitiveTraceAnomalyLifecycle,
    CognitiveTraceAnomalyLifecyclePolicy,
)


def consolidation(*codes: str) -> CognitiveTraceAnomalyConsolidationSnapshot:
    records = tuple(
        CognitiveTraceAnomalyConsolidatedRecord(
            code=code,
            classification="high",
            severity="warning",
            operational_impact="high",
            priority_score=80,
            occurrence_count=1,
            duplicate_count=0,
            maximum_recurrence_count=1,
            maximum_observed_rate=0.8,
            minimum_threshold=0.5,
            maximum_excess_rate=0.3,
        )
        for code in codes
    )
    return CognitiveTraceAnomalyConsolidationSnapshot(
        schema_version="rp22.13",
        input_snapshot_count=1,
        input_record_count=len(records),
        consolidated_count=len(records),
        duplicate_count=0,
        truncated_group_count=0,
        records=records,
    )


def test_lifecycle_moves_new_active_acknowledged_resolved_reopened() -> None:
    lifecycle = CognitiveTraceAnomalyLifecycle()
    snapshot = lifecycle.ingest(consolidation("fallback_rate_elevated"))
    assert snapshot.records[0].state == "new"
    snapshot = lifecycle.ingest(consolidation("fallback_rate_elevated"))
    assert snapshot.records[0].state == "active"
    snapshot = lifecycle.acknowledge("fallback_rate_elevated")
    assert snapshot.records[0].state == "acknowledged"
    assert lifecycle.resolve("fallback_rate_elevated").records[0].state == "resolved"
    snapshot = lifecycle.ingest(consolidation("fallback_rate_elevated"))
    assert snapshot.records[0].state == "reopened"
    assert snapshot.records[0].reopen_count == 1


def test_absent_anomaly_is_resolved_deterministically() -> None:
    lifecycle = CognitiveTraceAnomalyLifecycle()
    lifecycle.ingest(consolidation("divergence_rate_elevated"))
    snapshot = lifecycle.ingest(consolidation())
    assert snapshot.records[0].state == "resolved"
    assert snapshot.transitions[-1].reason_code == "absent_from_snapshot"


def test_history_and_records_are_bounded() -> None:
    lifecycle = CognitiveTraceAnomalyLifecycle(
        CognitiveTraceAnomalyLifecyclePolicy(maximum_records=1, maximum_transitions=2)
    )
    lifecycle.ingest(consolidation("a", "b"))
    snapshot = lifecycle.ingest(consolidation("b"))
    assert snapshot.record_count == 1
    assert snapshot.transition_count == 2


def test_snapshot_is_immutable_serializable_and_redacted() -> None:
    lifecycle = CognitiveTraceAnomalyLifecycle()
    snapshot = lifecycle.ingest(consolidation("high_risk_rate_elevated"))
    with pytest.raises(FrozenInstanceError):
        snapshot.record_count = 99  # type: ignore[misc]
    payload = snapshot.as_dict()
    assert payload["schema_version"] == "rp22.14"
    assert "prompt" not in str(payload).lower()


def test_kernel_exposes_lifecycle_without_affecting_decisions() -> None:
    kernel = CognitiveDecisionKernel()
    snapshot = kernel.update_trace_anomaly_lifecycle(consolidation("x"))
    assert snapshot.records[0].state == "new"
    kernel.clear_trace_anomaly_lifecycle()
    assert kernel.trace_anomaly_lifecycle_snapshot.record_count == 0
