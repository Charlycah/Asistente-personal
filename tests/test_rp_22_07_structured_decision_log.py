from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveDecisionLog,
    CognitivePlanner,
)


def test_kernel_records_redacted_structured_decision_event():
    kernel = CognitiveDecisionKernel()
    plan = CognitivePlanner().plan("Mi secreto es 1234; ¿qué hora es?")

    decision = kernel.consolidate(plan)
    event = kernel.decision_log_snapshot.events[-1]

    assert event.schema_version == "rp22.07"
    assert event.policy == decision.policy.value
    assert event.intent == plan.intent.value
    assert "secreto" not in str(event.as_dict()).lower()
    assert "1234" not in str(event.as_dict())
    assert "narrative" not in event.as_dict()


def test_decision_log_is_bounded_and_counts_dropped_events():
    log = CognitiveDecisionLog(capacity=2)
    kernel = CognitiveDecisionKernel(decision_log=log)
    planner = CognitivePlanner()

    for message in ("Hola", "¿Qué hora es?", "Gracias"):
        kernel.consolidate(planner.plan(message))

    snapshot = kernel.decision_log_snapshot
    assert snapshot.total_recorded == 3
    assert snapshot.dropped_events == 1
    assert [event.sequence for event in snapshot.events] == [2, 3]


def test_decision_log_snapshot_is_immutable_and_serializable():
    kernel = CognitiveDecisionKernel()
    kernel.consolidate(CognitivePlanner().plan("Hola"))
    snapshot = kernel.decision_log_snapshot

    assert snapshot.as_dict()["schema_version"] == "rp22.07"
    assert isinstance(snapshot.events, tuple)
    with pytest.raises(FrozenInstanceError):
        snapshot.total_recorded = 99


def test_decision_log_can_be_cleared_explicitly():
    kernel = CognitiveDecisionKernel()
    kernel.consolidate(CognitivePlanner().plan("Hola"))

    kernel.clear_decision_log()

    snapshot = kernel.decision_log_snapshot
    assert snapshot.total_recorded == 0
    assert snapshot.dropped_events == 0
    assert snapshot.events == ()


def test_decision_logging_failure_is_fail_open():
    class BrokenLog:
        @property
        def snapshot(self):
            raise RuntimeError("unavailable")

        def record(self, *args, **kwargs):
            raise RuntimeError("broken")

        def clear(self):
            raise RuntimeError("broken")

    kernel = CognitiveDecisionKernel(decision_log=BrokenLog())

    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
