from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnomalyLifecycleComparator,
    CognitiveTraceAnomalyLifecycleComparisonPolicy,
)
from tests.test_rp_22_14_trace_anomaly_lifecycle import consolidation


def snapshots():
    kernel = CognitiveDecisionKernel()
    previous = kernel.update_trace_anomaly_lifecycle(consolidation("a", "b"))
    kernel.update_trace_anomaly_lifecycle(consolidation("a", "b"))
    kernel.resolve_trace_anomaly("b")
    current = kernel.update_trace_anomaly_lifecycle(consolidation("a", "c"))
    return kernel, previous, current


def test_comparison_detects_added_and_state_changes() -> None:
    kernel, previous, current = snapshots()
    comparison = kernel.compare_trace_anomaly_lifecycle(previous, current)
    by_code = {change.code: change for change in comparison.changes}
    assert by_code["c"].change_type == "added"
    assert by_code["c"].trend == "degrading"
    assert by_code["b"].current_state == "resolved"
    assert by_code["b"].trend == "improving"


def test_comparison_counts_and_orders_changes_deterministically() -> None:
    kernel, previous, current = snapshots()
    first = kernel.compare_trace_anomaly_lifecycle(previous, current)
    second = kernel.compare_trace_anomaly_lifecycle(previous, current)
    assert first.as_dict() == second.as_dict()
    assert first.changed_count == 3
    assert first.degrading_count >= 1
    assert first.improving_count >= 1


def test_comparison_uses_current_kernel_snapshot_by_default() -> None:
    kernel, previous, current = snapshots()
    assert kernel.compare_trace_anomaly_lifecycle(previous).as_dict() == (
        kernel.compare_trace_anomaly_lifecycle(previous, current).as_dict()
    )


def test_comparison_limit_only_truncates_change_presentation() -> None:
    _, previous, current = snapshots()
    comparator = CognitiveTraceAnomalyLifecycleComparator(
        CognitiveTraceAnomalyLifecycleComparisonPolicy(maximum_changes=1)
    )
    comparison = comparator.compare(previous, current)
    assert comparison.changed_count == 3
    assert comparison.returned_count == 1
    assert comparison.truncated_count == 2


def test_comparison_is_immutable_serializable_and_redacted() -> None:
    kernel, previous, current = snapshots()
    comparison = kernel.compare_trace_anomaly_lifecycle(previous, current)
    assert comparison.schema_version == "rp22.16"
    assert "prompt" not in str(comparison.as_dict()).lower()
    with pytest.raises(FrozenInstanceError):
        comparison.changed_count = 99  # type: ignore[misc]


def test_removed_record_is_improving_and_invalid_policy_is_rejected() -> None:
    kernel, previous, current = snapshots()
    without_c = replace(
        current,
        record_count=current.record_count - 1,
        records=tuple(record for record in current.records if record.code != "c"),
    )
    comparison = kernel.compare_trace_anomaly_lifecycle(current, without_c)
    change = next(item for item in comparison.changes if item.code == "c")
    assert change.change_type == "removed"
    assert change.trend == "improving"
    with pytest.raises(ValueError):
        CognitiveTraceAnomalyLifecycleComparisonPolicy(maximum_changes=0)
