from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import CapabilityRunStatus, OutcomeStatus
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 26, 22, 0, tzinfo=timezone.utc)


class FailingAutonomyRunner:
    def run(self, observation, policy):
        raise RuntimeError("autonomy unavailable")


def test_real_runtime_failure_triggers_first_autonomous_cycle(monkeypatch) -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)

    def fail_publish(event):
        raise RuntimeError("coordinator unavailable")

    monkeypatch.setattr(runtime.coordinator, "publish", fail_publish)

    with pytest.raises(RuntimeError, match="coordinator unavailable"):
        runtime.publish_text("activar fallo real")

    result = runtime.last_autonomy_result
    assert result is not None
    assert result.status is CapabilityRunStatus.EXECUTED
    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.DEGRADED
    assert result.candidate is not None
    assert result.candidate.action == "verify_component_health"
    assert "component_id=executive.coordinator" in result.outcome.evidence

    snapshot = runtime.snapshot
    assert snapshot.autonomous_cycle_count == 1
    assert snapshot.last_autonomy_status == "executed"
    assert snapshot.last_autonomy_error is None


def test_successful_runtime_path_does_not_trigger_autonomy() -> None:
    runtime = RuntimeExecutiveIntegration()
    runtime.start(now=NOW)

    runtime.publish_text("camino normal")
    assert runtime.drain_notifications() == ("camino normal",)

    assert runtime.last_autonomy_result is None
    assert runtime.snapshot.autonomous_cycle_count == 0


def test_autonomy_failure_never_masks_original_runtime_error(monkeypatch) -> None:
    runtime = RuntimeExecutiveIntegration(autonomy_runner=FailingAutonomyRunner())
    runtime.start(now=NOW)

    def fail_publish(event):
        raise LookupError("original runtime failure")

    monkeypatch.setattr(runtime.coordinator, "publish", fail_publish)

    with pytest.raises(LookupError, match="original runtime failure"):
        runtime.publish_text("preservar error")

    snapshot = runtime.snapshot
    assert snapshot.autonomous_cycle_count == 1
    assert snapshot.last_autonomy_status is None
    assert snapshot.last_autonomy_error == "RuntimeError: autonomy unavailable"
