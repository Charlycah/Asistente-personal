from datetime import datetime, timedelta, timezone
from pathlib import Path

from core.controlled_autonomy import RuntimeObservation
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 26, 23, 0, tzinfo=timezone.utc)


def _observation(at: datetime, error: str = "same failure") -> RuntimeObservation:
    return RuntimeObservation(
        kind="component_health.degraded",
        source="component_health.executive.coordinator",
        observed_at=at,
        facts=(
            "component_id=executive.coordinator",
            "health_state=degraded",
            "consecutive_failures=1",
            f"last_error={error}",
        ),
        severity="warning",
        attributes={"component_id": "executive.coordinator"},
    )


def test_m327_6_repeated_observation_is_suppressed(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start(now=NOW)

    first = runtime._run_autonomous_cycle(_observation(NOW))
    second = runtime._run_autonomous_cycle(
        _observation(NOW + timedelta(seconds=10))
    )

    assert first is not None
    assert second is None
    assert runtime.snapshot.autonomous_cycle_count == 1
    assert runtime.snapshot.autonomy_suppressed_count == 1
    assert len(runtime.drain_notifications()) == 1


def test_m327_6_same_condition_can_retry_after_window(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        autonomy_deduplication_window=timedelta(seconds=30),
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start(now=NOW)

    runtime._run_autonomous_cycle(_observation(NOW))
    retried = runtime._run_autonomous_cycle(
        _observation(NOW + timedelta(seconds=31))
    )

    assert retried is not None
    assert runtime.snapshot.autonomous_cycle_count == 2
    assert runtime.snapshot.autonomy_suppressed_count == 0


def test_m327_6_changed_condition_is_not_suppressed(tmp_path: Path) -> None:
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "journal.jsonl",
    )
    runtime.start(now=NOW)

    runtime._run_autonomous_cycle(_observation(NOW, "microphone unavailable"))
    changed = runtime._run_autonomous_cycle(
        _observation(NOW + timedelta(seconds=5), "stream disconnected")
    )

    assert changed is not None
    assert runtime.snapshot.autonomous_cycle_count == 2
    assert runtime.snapshot.autonomy_suppressed_count == 0
