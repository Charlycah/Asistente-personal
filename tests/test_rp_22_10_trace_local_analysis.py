from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitivePlanner,
    CognitiveTraceQuery,
)


def test_local_analysis_aggregates_only_retained_redacted_traces():
    kernel = CognitiveDecisionKernel()
    planner = CognitivePlanner()
    for prompt in ("Hola", "Resume esto", "Mi secreto es alfa"):
        kernel.consolidate(planner.plan(prompt))

    snapshot = kernel.analyze_traces()
    payload = snapshot.as_dict()
    assert snapshot.schema_version == "rp22.10"
    assert snapshot.analyzed_traces == 3
    assert sum(payload["policy_counts"].values()) == 3
    assert "secreto" not in str(payload).lower()
    assert "alfa" not in str(payload).lower()


def test_local_analysis_supports_same_exact_allow_listed_filters():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    snapshot = kernel.analyze_traces(
        CognitiveTraceQuery(policy=decision.policy.value, stage_code="decision")
    )
    assert snapshot.analyzed_traces == 1
    assert dict(snapshot.policy_counts) == {decision.policy.value: 1}
    assert dict(snapshot.stage_counts)["decision"] == 1


def test_analysis_is_independent_from_query_result_limit():
    kernel = CognitiveDecisionKernel()
    planner = CognitivePlanner()
    for prompt in ("uno", "dos", "tres"):
        kernel.consolidate(planner.plan(prompt))

    query = CognitiveTraceQuery(limit=1)
    assert kernel.query_traces(query).returned_count == 1
    assert kernel.analyze_traces(query).analyzed_traces == 3


def test_analysis_snapshot_is_deterministic_serializable_and_immutable():
    kernel = CognitiveDecisionKernel()
    kernel.consolidate(CognitivePlanner().plan("Hola"))

    first = kernel.analyze_traces()
    second = kernel.analyze_traces()
    assert first == second
    assert first.as_dict()["schema_version"] == "rp22.10"
    with pytest.raises(FrozenInstanceError):
        first.analyzed_traces = 99


def test_analysis_failure_does_not_affect_decision_consolidation():
    class BrokenAnalysisEngine:
        def analyze(self, correlations, events, query=None):
            raise RuntimeError("analysis unavailable")

    kernel = CognitiveDecisionKernel(trace_analysis_engine=BrokenAnalysisEngine())
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    with pytest.raises(RuntimeError, match="analysis unavailable"):
        kernel.analyze_traces()
