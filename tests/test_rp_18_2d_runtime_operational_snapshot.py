from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

import pytest

from app.official_runtime_composition import (
    OfficialROBYRuntime,
    OfficialRuntimeComposition,
)
from app.resident_component_registry import (
    ResidentComponentRegistry,
    ResidentCriticality,
    ResidentHealth,
    ResidentRegistration,
    ResidentState,
)
from app.runtime_operational_snapshot import (
    RuntimeOperationalHealth,
    RuntimeOperationalSnapshotBuilder,
    RuntimeOperationalStatus,
)


class LifecycleStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    DEGRADED = "degraded"
    STOPPED = "stopped"
    FAILED = "failed"


@dataclass
class LifecycleState:
    status: LifecycleStatus
    owner: str = "carlos"
    session_id: str = "local-session"
    process_id: int = 42
    generation: int = 3
    started_at: datetime | None = None
    heartbeat_at: datetime | None = None
    updated_at: datetime | None = None
    stopped_at: datetime | None = None
    failure: str | None = None


@dataclass
class StubLifecycle:
    state: LifecycleState

    @property
    def is_running(self) -> bool:
        return self.state.status in {LifecycleStatus.RUNNING, LifecycleStatus.DEGRADED}

    def start(self) -> None:
        self.state.status = LifecycleStatus.RUNNING

    def stop(self) -> None:
        self.state.status = LifecycleStatus.STOPPED

    def heartbeat(self) -> str:
        return "heartbeat"

    def mark_degraded(self, exc: BaseException) -> None:
        self.state.status = LifecycleStatus.DEGRADED
        self.state.failure = type(exc).__name__


@dataclass
class StubSupervisor:
    is_running: bool = False

    def start(self) -> None:
        self.is_running = True

    def stop(self) -> None:
        self.is_running = False


@dataclass
class StubResident:
    def start(self) -> None: ...
    def stop(self) -> None: ...


def _runtime(
    *,
    status: LifecycleStatus = LifecycleStatus.CREATED,
    registry: ResidentComponentRegistry | None = None,
    supervisor_running: bool = False,
) -> OfficialROBYRuntime:
    lifecycle = StubLifecycle(LifecycleState(status=status))
    composition = OfficialRuntimeComposition(
        conversation=object(),
        bootstrap=object(),
        root=object(),
        lifecycle=lifecycle,
        supervisor=StubSupervisor(supervisor_running),
    )
    return OfficialROBYRuntime(
        composition,
        resident_registry=registry or ResidentComponentRegistry(),
    )


def test_snapshot_exposes_lifecycle_identity_and_timestamp() -> None:
    now = datetime(2026, 7, 17, 21, 0, tzinfo=timezone.utc)
    snapshot = _runtime().snapshot(now=now)
    assert snapshot.generated_at == now
    assert snapshot.owner == "carlos"
    assert snapshot.session_id == "local-session"
    assert snapshot.process_id == 42
    assert snapshot.generation == 3


def test_created_runtime_has_unknown_health_and_is_not_available() -> None:
    snapshot = _runtime().snapshot()
    assert snapshot.status is RuntimeOperationalStatus.CREATED
    assert snapshot.health is RuntimeOperationalHealth.UNKNOWN
    assert not snapshot.available


def test_running_runtime_without_failures_is_healthy_and_available() -> None:
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "required",
                StubResident(),
                ResidentCriticality.REQUIRED,
                state=ResidentState.RUNNING,
                health=ResidentHealth.HEALTHY,
            ),
        )
    )
    snapshot = _runtime(
        status=LifecycleStatus.RUNNING,
        registry=registry,
        supervisor_running=True,
    ).snapshot()
    assert snapshot.status is RuntimeOperationalStatus.RUNNING
    assert snapshot.health is RuntimeOperationalHealth.HEALTHY
    assert snapshot.available
    assert snapshot.running_residents == 1
    assert snapshot.unavailable_required_residents == 0


def test_missing_supervisor_degrades_active_runtime() -> None:
    snapshot = _runtime(status=LifecycleStatus.RUNNING).snapshot()
    assert snapshot.health is RuntimeOperationalHealth.DEGRADED
    assert not snapshot.available
    assert "supervisor:not_running" in snapshot.issues


def test_optional_failure_degrades_without_making_runtime_unavailable() -> None:
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "optional",
                StubResident(),
                ResidentCriticality.OPTIONAL,
                state=ResidentState.FAILED,
                health=ResidentHealth.UNAVAILABLE,
                last_error="sensor ausente",
            ),
        )
    )
    snapshot = _runtime(
        status=LifecycleStatus.RUNNING,
        registry=registry,
        supervisor_running=True,
    ).snapshot()
    assert snapshot.health is RuntimeOperationalHealth.DEGRADED
    assert not snapshot.available
    assert snapshot.failed_residents == 1
    assert snapshot.unavailable_required_residents == 0
    assert "resident:optional:sensor ausente" in snapshot.issues


def test_required_failure_makes_runtime_unavailable() -> None:
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "required",
                StubResident(),
                ResidentCriticality.REQUIRED,
                state=ResidentState.FAILED,
                health=ResidentHealth.UNAVAILABLE,
                last_error="inicio fallido",
            ),
        )
    )
    snapshot = _runtime(
        status=LifecycleStatus.RUNNING,
        registry=registry,
        supervisor_running=True,
    ).snapshot()
    assert snapshot.health is RuntimeOperationalHealth.UNAVAILABLE
    assert not snapshot.available
    assert snapshot.unavailable_required_residents == 1


def test_lifecycle_degradation_is_preserved_as_issue() -> None:
    runtime = _runtime(
        status=LifecycleStatus.DEGRADED,
        supervisor_running=True,
    )
    runtime.lifecycle.state.failure = "RuntimeError"
    snapshot = runtime.snapshot()
    assert snapshot.status is RuntimeOperationalStatus.DEGRADED
    assert snapshot.health is RuntimeOperationalHealth.DEGRADED
    assert "lifecycle:RuntimeError" in snapshot.issues


def test_failed_lifecycle_is_unavailable() -> None:
    snapshot = _runtime(status=LifecycleStatus.FAILED).snapshot()
    assert snapshot.health is RuntimeOperationalHealth.UNAVAILABLE
    assert not snapshot.available


def test_snapshot_is_immutable_and_does_not_expose_component_instances() -> None:
    registry = ResidentComponentRegistry(
        (ResidentRegistration("resident", StubResident()),)
    )
    snapshot = _runtime(registry=registry).snapshot()
    assert not hasattr(snapshot.residents[0], "component")
    with pytest.raises(AttributeError):
        snapshot.total_residents = 99


def test_snapshot_serializes_enums_datetimes_and_tuples() -> None:
    now = datetime(2026, 7, 17, 21, 0, tzinfo=timezone.utc)
    payload = _runtime().snapshot(now=now).to_dict()
    assert payload["generated_at"] == now.isoformat()
    assert payload["status"] == "created"
    assert payload["health"] == "unknown"
    assert payload["residents"] == []
    assert payload["issues"] == []


def test_snapshot_rejects_naive_time() -> None:
    builder = RuntimeOperationalSnapshotBuilder()
    runtime = _runtime()
    with pytest.raises(ValueError, match="timezone-aware"):
        builder.build(
            lifecycle=runtime.lifecycle,
            supervisor=runtime.supervisor,
            registrations=(),
            now=datetime(2026, 7, 17, 21, 0),
        )
