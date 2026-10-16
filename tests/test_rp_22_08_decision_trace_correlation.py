from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitivePlanner,
    CognitiveTraceCorrelator,
)


def test_decision_has_opaque_correlation_without_user_content():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Mi clave es 1234"))

    correlation = decision.correlation
    assert correlation is not None
    assert correlation.schema_version == "rp22.08"
    assert len(correlation.trace_id) == 24
    assert correlation.stage_codes == ("planning", "decision")
    assert "clave" not in str(correlation.as_dict()).lower()
    assert "1234" not in str(correlation.as_dict())


def test_activation_and_outcome_are_linked_as_optional_spans():
    kernel = CognitiveDecisionKernel()
    plan = CognitivePlanner().plan("Hola")
    base = kernel.consolidate(plan)

    assert base.correlation is not None
    assert base.correlation.activation_span_id is None
    assert base.correlation.outcome_span_id is None


def test_trace_snapshot_is_bounded_immutable_and_serializable():
    correlator = CognitiveTraceCorrelator(capacity=2)
    for _ in range(3):
        correlator.correlate(activation_present=False, outcome_present=False)

    snapshot = correlator.snapshot
    assert snapshot.total_correlations == 3
    assert snapshot.dropped_correlations == 1
    assert len(snapshot.correlations) == 2
    assert snapshot.as_dict()["schema_version"] == "rp22.08"
    with pytest.raises(FrozenInstanceError):
        snapshot.total_correlations = 99


def test_decision_log_links_to_same_trace_identifiers():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))
    event = kernel.decision_log_snapshot.events[-1]

    assert decision.correlation is not None
    assert event.trace_id == decision.correlation.trace_id
    assert event.decision_span_id == decision.correlation.decision_span_id


def test_trace_failure_is_fail_open_and_can_be_cleared():
    class BrokenCorrelator:
        @property
        def snapshot(self):
            raise RuntimeError("unavailable")

        def correlate(self, **kwargs):
            raise RuntimeError("broken")

        def clear(self):
            raise RuntimeError("broken")

    kernel = CognitiveDecisionKernel(trace_correlator=BrokenCorrelator())
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    assert decision.correlation is None
