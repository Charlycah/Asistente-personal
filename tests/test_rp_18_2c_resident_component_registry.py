from __future__ import annotations

from dataclasses import dataclass

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
    registration_from_component,
)


@dataclass
class StubLifecycle:
    events: list[str]
    is_running: bool = False

    def start(self) -> None:
        self.events.append("lifecycle.start")
        self.is_running = True

    def stop(self) -> None:
        self.events.append("lifecycle.stop")
        self.is_running = False

    def heartbeat(self):
        return "heartbeat"

    def mark_degraded(self, exc: BaseException) -> None:
        self.events.append(f"degraded:{exc}")


@dataclass
class StubSupervisor:
    events: list[str]

    def start(self) -> None:
        self.events.append("supervisor.start")

    def stop(self) -> None:
        self.events.append("supervisor.stop")


@dataclass
class StubResident:
    name: str
    events: list[str]
    fail_start: bool = False
    fail_stop: bool = False

    def start(self) -> None:
        self.events.append(f"{self.name}.start")
        if self.fail_start:
            raise RuntimeError(f"{self.name} no inició")

    def stop(self) -> None:
        self.events.append(f"{self.name}.stop")
        if self.fail_stop:
            raise RuntimeError(f"{self.name} no se detuvo")


def _runtime(
    registry: ResidentComponentRegistry, events: list[str]
) -> OfficialROBYRuntime:
    lifecycle = StubLifecycle(events)
    composition = OfficialRuntimeComposition(
        conversation=object(),
        bootstrap=object(),
        root=object(),
        lifecycle=lifecycle,
        supervisor=StubSupervisor(events),
    )
    return OfficialROBYRuntime(
        composition,
        resident_registry=registry,
    )


def test_registry_rejects_empty_and_duplicate_component_ids() -> None:
    resident = StubResident("uno", [])
    registry = ResidentComponentRegistry()
    with pytest.raises(ValueError, match="vacío"):
        registry.register(ResidentRegistration(" ", resident))
    registry.register(ResidentRegistration("uno", resident))
    with pytest.raises(ValueError, match="duplicado"):
        registry.register(ResidentRegistration("uno", resident))


def test_registry_orders_by_startup_order_then_identity() -> None:
    events: list[str] = []
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration("zeta", StubResident("z", events), startup_order=20),
            ResidentRegistration("beta", StubResident("b", events), startup_order=10),
            ResidentRegistration("alfa", StubResident("a", events), startup_order=10),
        )
    )
    assert tuple(item.component_id for item in registry.ordered()) == (
        "alfa",
        "beta",
        "zeta",
    )


def test_compatibility_residents_view_uses_registry_order() -> None:
    events: list[str] = []
    second = StubResident("second", events)
    first = StubResident("first", events)
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration("second", second, startup_order=20),
            ResidentRegistration("first", first, startup_order=10),
        )
    )
    runtime = _runtime(registry, events)
    assert runtime.residents == (first, second)
    assert runtime.resident_registry is registry


def test_required_residents_start_and_stop_in_registry_order() -> None:
    events: list[str] = []
    first = StubResident("first", events)
    second = StubResident("second", events)
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "second", second, ResidentCriticality.REQUIRED, startup_order=20
            ),
            ResidentRegistration(
                "first", first, ResidentCriticality.REQUIRED, startup_order=10
            ),
        )
    )
    runtime = _runtime(registry, events)
    runtime.start()
    runtime.stop()
    assert events == [
        "lifecycle.start",
        "supervisor.start",
        "first.start",
        "second.start",
        "second.stop",
        "first.stop",
        "supervisor.stop",
        "lifecycle.stop",
    ]


def test_resident_state_and_health_are_recorded() -> None:
    events: list[str] = []
    registry = ResidentComponentRegistry(
        (ResidentRegistration("resident", StubResident("resident", events)),)
    )
    runtime = _runtime(registry, events)
    assert runtime.resident_snapshot[0].state is ResidentState.REGISTERED
    runtime.start()
    running = runtime.resident_snapshot[0]
    assert running.state is ResidentState.RUNNING
    assert running.health is ResidentHealth.HEALTHY
    runtime.stop()
    stopped = runtime.resident_snapshot[0]
    assert stopped.state is ResidentState.STOPPED
    assert stopped.health is ResidentHealth.UNKNOWN


def test_optional_start_failure_is_visible_without_aborting_runtime() -> None:
    events: list[str] = []
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "optional",
                StubResident("optional", events, fail_start=True),
                ResidentCriticality.OPTIONAL,
            ),
        )
    )
    runtime = _runtime(registry, events)
    runtime.start()
    failed = runtime.resident_snapshot[0]
    assert runtime.is_running
    assert failed.state is ResidentState.FAILED
    assert failed.health is ResidentHealth.UNAVAILABLE
    assert "no inició" in (failed.last_error or "")
    runtime.stop()


def test_required_start_failure_rolls_back_and_is_recorded() -> None:
    events: list[str] = []
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "required",
                StubResident("required", events, fail_start=True),
                ResidentCriticality.REQUIRED,
            ),
        )
    )
    runtime = _runtime(registry, events)
    with pytest.raises(RuntimeError, match="no inició"):
        runtime.start()
    failed = runtime.resident_snapshot[0]
    assert failed.state is ResidentState.FAILED
    assert failed.health is ResidentHealth.UNAVAILABLE
    assert events[-2:] == ["supervisor.stop", "lifecycle.stop"]


def test_stop_failure_is_recorded_and_propagated_after_full_shutdown() -> None:
    events: list[str] = []
    registry = ResidentComponentRegistry(
        (
            ResidentRegistration(
                "resident", StubResident("resident", events, fail_stop=True)
            ),
        )
    )
    runtime = _runtime(registry, events)
    runtime.start()
    with pytest.raises(RuntimeError, match="no se detuvo"):
        runtime.stop()
    failed = runtime.resident_snapshot[0]
    assert failed.state is ResidentState.FAILED
    assert failed.health is ResidentHealth.DEGRADED
    assert events[-2:] == ["supervisor.stop", "lifecycle.stop"]


def test_registration_factory_generates_stable_snake_case_identity() -> None:
    class ContinuousCognitiveLoop:
        def start(self) -> None: ...
        def stop(self) -> None: ...

    registration = registration_from_component(ContinuousCognitiveLoop())
    assert registration.component_id == "continuous_cognitive_loop"


def test_registry_snapshot_is_immutable_external_view() -> None:
    resident = StubResident("resident", [])
    registry = ResidentComponentRegistry((ResidentRegistration("resident", resident),))
    snapshot = registry.snapshot()
    assert isinstance(snapshot, tuple)
    assert snapshot[0].component is resident
