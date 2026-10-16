from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitivePlanner,
    CognitiveTraceQuery,
    CognitiveTraceRetentionPolicy,
)


def test_retention_policy_bounds_trace_storage_and_query_output():
    policy = CognitiveTraceRetentionPolicy(capacity=2, maximum_query_results=1)
    kernel = CognitiveDecisionKernel(trace_retention_policy=policy)
    planner = CognitivePlanner()
    for prompt in ("uno", "dos", "tres"):
        kernel.consolidate(planner.plan(prompt))

    assert kernel.trace_snapshot.capacity == 2
    assert kernel.trace_snapshot.dropped_correlations == 1
    result = kernel.query_traces(CognitiveTraceQuery(limit=99))
    assert result.applied_limit == 1
    assert result.matched_count == 2
    assert result.returned_count == 1


def test_safe_query_filters_only_allow_listed_structured_metadata():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Mi secreto es alfa"))

    result = kernel.query_traces(
        CognitiveTraceQuery(policy=decision.policy.value, risk=decision.risk.value)
    )
    payload = result.as_dict()
    assert result.schema_version == "rp22.09"
    assert result.returned_count == 1
    assert "secreto" not in str(payload).lower()
    assert "alfa" not in str(payload).lower()
    assert "narrative" not in str(payload).lower()


def test_query_by_opaque_trace_id_and_stage_is_deterministic():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))
    assert decision.correlation is not None

    result = kernel.query_traces(
        CognitiveTraceQuery(
            trace_id=decision.correlation.trace_id,
            stage_code="decision",
        )
    )
    assert result.returned_count == 1
    assert result.records[0].trace_id == decision.correlation.trace_id
    assert result.records[0].decision_span_id == decision.correlation.decision_span_id


def test_query_results_and_retention_policy_are_immutable_serializable():
    policy = CognitiveTraceRetentionPolicy(capacity=4, maximum_query_results=2)
    kernel = CognitiveDecisionKernel(trace_retention_policy=policy)
    kernel.consolidate(CognitivePlanner().plan("Hola"))
    result = kernel.query_traces()

    assert policy.as_dict()["schema_version"] == "rp22.09"
    assert result.as_dict()["schema_version"] == "rp22.09"
    with pytest.raises(FrozenInstanceError):
        result.returned_count = 9


def test_invalid_limits_are_rejected_without_affecting_kernel_decisions():
    with pytest.raises(ValueError):
        CognitiveTraceRetentionPolicy(capacity=0)
    with pytest.raises(ValueError):
        CognitiveTraceQuery(limit=0)

    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))
    assert decision.policy.value == "respond"
