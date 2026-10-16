from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveTraceAnomalyLifecycleQuery,
)
from tests.test_rp_22_14_trace_anomaly_lifecycle import consolidation


def populated_kernel() -> CognitiveDecisionKernel:
    kernel = CognitiveDecisionKernel()
    kernel.update_trace_anomaly_lifecycle(consolidation("a", "b", "c"))
    kernel.update_trace_anomaly_lifecycle(consolidation("a", "b", "c"))
    kernel.acknowledge_trace_anomaly("b")
    kernel.resolve_trace_anomaly("c")
    return kernel


def test_query_filters_exact_allow_listed_fields() -> None:
    view = populated_kernel().query_trace_anomaly_lifecycle(
        CognitiveTraceAnomalyLifecycleQuery(
            states=("active",),
            codes=("a", "missing"),
            classifications=("high",),
            minimum_priority_score=80,
            minimum_occurrence_count=2,
        )
    )
    assert [record.code for record in view.records] == ["a"]
    assert view.matched_count == 1


def test_view_aggregates_states_and_supports_transition_projection() -> None:
    view = populated_kernel().query_trace_anomaly_lifecycle(
        CognitiveTraceAnomalyLifecycleQuery(include_transitions=True)
    )
    assert dict(view.state_counts) == {
        "acknowledged": 1,
        "active": 1,
        "resolved": 1,
    }
    assert view.active_count == 2
    assert view.resolved_count == 1
    assert view.transitions


def test_query_limit_only_truncates_presentation() -> None:
    view = populated_kernel().query_trace_anomaly_lifecycle(
        CognitiveTraceAnomalyLifecycleQuery(limit=1)
    )
    assert view.matched_count == 3
    assert view.returned_count == 1
    assert view.truncated_count == 2
    assert sum(dict(view.state_counts).values()) == 3


def test_view_is_deterministic_immutable_serializable_and_redacted() -> None:
    kernel = populated_kernel()
    query = CognitiveTraceAnomalyLifecycleQuery(include_transitions=True)
    first = kernel.query_trace_anomaly_lifecycle(query)
    second = kernel.query_trace_anomaly_lifecycle(query)
    assert first.as_dict() == second.as_dict()
    with pytest.raises(FrozenInstanceError):
        first.returned_count = 99  # type: ignore[misc]
    payload = first.as_dict()
    assert payload["schema_version"] == "rp22.15"
    assert "prompt" not in str(payload).lower()


def test_invalid_query_bounds_are_rejected() -> None:
    with pytest.raises(ValueError):
        CognitiveTraceAnomalyLifecycleQuery(limit=0)
    with pytest.raises(ValueError):
        CognitiveTraceAnomalyLifecycleQuery(minimum_priority_score=101)
