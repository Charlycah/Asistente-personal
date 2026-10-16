from datetime import datetime, timezone

import pytest

from core.executive_recovery_health import (
    CircuitState,
    ComponentHealthPolicy,
    ComponentHealthState,
    RecoveryHealthCoordinator,
    RecoveryStatus,
)


def _utc(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 25, hour, minute, tzinfo=timezone.utc)


def test_m325_5_registers_unknown_component() -> None:
    coordinator = RecoveryHealthCoordinator()

    health = coordinator.register("voice", registered_at=_utc(18))

    assert health.component_id == "voice"
    assert health.state is ComponentHealthState.UNKNOWN
    assert health.circuit is CircuitState.CLOSED
    assert coordinator.snapshot.registered_count == 1


def test_m325_5_success_marks_component_healthy() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register("weather", registered_at=_utc(18))

    health = coordinator.record_success("weather", observed_at=_utc(19))

    assert health.state is ComponentHealthState.HEALTHY
    assert health.total_successes == 1
    assert health.consecutive_failures == 0


def test_m325_5_failures_degrade_then_open_circuit() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "gmail",
        policy=ComponentHealthPolicy(failure_threshold=2),
        registered_at=_utc(18),
    )

    degraded = coordinator.record_failure(
        "gmail", RuntimeError("timeout"), observed_at=_utc(19)
    )
    unhealthy = coordinator.record_failure(
        "gmail", "still unavailable", observed_at=_utc(20)
    )

    assert degraded.state is ComponentHealthState.DEGRADED
    assert degraded.circuit is CircuitState.CLOSED
    assert unhealthy.state is ComponentHealthState.UNHEALTHY
    assert unhealthy.circuit is CircuitState.OPEN
    assert unhealthy.total_failures == 2


def test_m325_5_success_resets_failure_streak_and_circuit() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "news",
        policy=ComponentHealthPolicy(failure_threshold=1),
        registered_at=_utc(18),
    )
    coordinator.record_failure("news", "offline", observed_at=_utc(19))

    health = coordinator.record_success("news", observed_at=_utc(20))

    assert health.state is ComponentHealthState.HEALTHY
    assert health.circuit is CircuitState.CLOSED
    assert health.consecutive_failures == 0
    assert health.last_error is None


def test_m325_5_open_circuit_blocks_until_cooldown() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "camera",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=3600,
        ),
        registered_at=_utc(18),
    )
    coordinator.record_failure("camera", "busy", observed_at=_utc(19))

    assert coordinator.can_execute("camera", now=_utc(19, 30)) is False
    assert coordinator.can_execute("camera", now=_utc(20)) is True
    assert coordinator.get("camera").circuit is CircuitState.HALF_OPEN


def test_m325_5_successful_recovery_closes_circuit() -> None:
    calls: list[str] = []

    def recover() -> bool:
        calls.append("recover")
        return True

    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "audio",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=0,
        ),
        recovery_handler=recover,
        registered_at=_utc(18),
    )
    coordinator.record_failure("audio", "device lost", observed_at=_utc(19))

    result = coordinator.attempt_recovery("audio", now=_utc(19))

    assert result.status is RecoveryStatus.SUCCEEDED
    assert result.component.state is ComponentHealthState.HEALTHY
    assert result.component.circuit is CircuitState.CLOSED
    assert result.component.recovery_attempts == 1
    assert calls == ["recover"]


def test_m325_5_failed_recovery_keeps_circuit_open() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "calendar",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=0,
        ),
        recovery_handler=lambda: False,
        registered_at=_utc(18),
    )
    coordinator.record_failure("calendar", "unauthorized", observed_at=_utc(19))

    result = coordinator.attempt_recovery("calendar", now=_utc(19))

    assert result.status is RecoveryStatus.FAILED
    assert result.component.state is ComponentHealthState.UNHEALTHY
    assert result.component.circuit is CircuitState.OPEN


def test_m325_5_recovery_exception_is_contained() -> None:
    def recover() -> bool:
        raise RuntimeError("restart failed")

    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "heartbeat",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=0,
        ),
        recovery_handler=recover,
        registered_at=_utc(18),
    )
    coordinator.record_failure("heartbeat", "stalled", observed_at=_utc(19))

    result = coordinator.attempt_recovery("heartbeat", now=_utc(19))

    assert result.status is RecoveryStatus.FAILED
    assert result.error == "restart failed"
    assert result.component.last_error == "restart failed"


def test_m325_5_recovery_respects_cooldown() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "lease",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=120,
        ),
        recovery_handler=lambda: True,
        registered_at=_utc(18),
    )
    coordinator.record_failure("lease", "lost", observed_at=_utc(19))

    result = coordinator.attempt_recovery("lease", now=_utc(19, 1))

    assert result.status is RecoveryStatus.DEFERRED
    assert result.component.recovery_attempts == 0


def test_m325_5_recovery_attempts_are_bounded() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register(
        "provider",
        policy=ComponentHealthPolicy(
            failure_threshold=1,
            recovery_cooldown_seconds=0,
            max_recovery_attempts=1,
        ),
        recovery_handler=lambda: False,
        registered_at=_utc(18),
    )
    coordinator.record_failure("provider", "offline", observed_at=_utc(19))

    first = coordinator.attempt_recovery("provider", now=_utc(19))
    second = coordinator.attempt_recovery("provider", now=_utc(20))

    assert first.status is RecoveryStatus.FAILED
    assert second.status is RecoveryStatus.EXHAUSTED
    assert second.component.recovery_attempts == 1


def test_m325_5_disabled_component_rejects_execution_and_updates() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register("ambient", registered_at=_utc(18))

    disabled = coordinator.disable("ambient", observed_at=_utc(19))
    ignored = coordinator.record_failure(
        "ambient", "should be ignored", observed_at=_utc(20)
    )

    assert disabled.state is ComponentHealthState.DISABLED
    assert ignored.total_failures == 0
    assert coordinator.can_execute("ambient", now=_utc(20)) is False

    enabled = coordinator.enable("ambient", observed_at=_utc(21))
    assert enabled.state is ComponentHealthState.UNKNOWN
    assert coordinator.can_execute("ambient", now=_utc(21)) is True


def test_m325_5_snapshot_aggregates_component_health() -> None:
    coordinator = RecoveryHealthCoordinator()
    coordinator.register("healthy", registered_at=_utc(18))
    coordinator.register(
        "unhealthy",
        policy=ComponentHealthPolicy(failure_threshold=1),
        registered_at=_utc(18),
    )
    coordinator.register("disabled", registered_at=_utc(18))
    coordinator.record_success("healthy", observed_at=_utc(19))
    coordinator.record_failure("unhealthy", "failure", observed_at=_utc(19))
    coordinator.disable("disabled", observed_at=_utc(19))

    snapshot = coordinator.snapshot

    assert snapshot.registered_count == 3
    assert snapshot.healthy_count == 1
    assert snapshot.unhealthy_count == 1
    assert snapshot.disabled_count == 1
    assert snapshot.open_circuit_count == 1
    assert snapshot.total_failures == 1
    assert snapshot.total_successes == 1


def test_m325_5_validates_registration_and_timestamps() -> None:
    coordinator = RecoveryHealthCoordinator()

    with pytest.raises(ValueError, match="blank"):
        coordinator.register(" ")
    with pytest.raises(ValueError, match="timezone-aware"):
        coordinator.register("voice", registered_at=datetime(2026, 7, 25))

    coordinator.register("voice", registered_at=_utc(18))
    with pytest.raises(ValueError, match="already registered"):
        coordinator.register("voice", registered_at=_utc(18))
    with pytest.raises(KeyError, match="unknown component"):
        coordinator.get("missing")
