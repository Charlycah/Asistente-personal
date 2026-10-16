from __future__ import annotations

import pytest

from app.official_runtime_composition import (
    OfficialROBYRuntime,
    OfficialRuntimeComposition,
)


class Component:
    def __init__(self, name, events, *, fail_start=False, fail_stop=False):
        self.name = name
        self.events = events
        self.fail_start = fail_start
        self.fail_stop = fail_stop

    def start(self):
        self.events.append(f"start:{self.name}")
        if self.fail_start:
            raise RuntimeError(f"start {self.name}")

    def stop(self):
        self.events.append(f"stop:{self.name}")
        if self.fail_stop:
            raise RuntimeError(f"stop {self.name}")


class Lifecycle(Component):
    def __init__(self, events):
        super().__init__("lifecycle", events)
        self.is_running = False
        self.bootstrap = type("Bootstrap", (), {"root": object()})()

    def start(self):
        super().start()
        self.is_running = True

    def stop(self):
        super().stop()
        self.is_running = False

    def heartbeat(self):
        self.events.append("heartbeat")
        return "beat"

    def mark_degraded(self, exc):
        self.events.append(f"degraded:{type(exc).__name__}")


def runtime(*residents):
    events = []
    lifecycle = Lifecycle(events)
    supervisor = Component("supervisor", events)
    bootstrap = lifecycle.bootstrap
    conversation = type("Conversation", (), {"bootstrap": bootstrap})()
    composition = OfficialRuntimeComposition(
        conversation=conversation,
        bootstrap=bootstrap,
        root=bootstrap.root,
        lifecycle=lifecycle,
        supervisor=supervisor,
    )
    return OfficialROBYRuntime(composition, residents=residents), events


def test_composition_exposes_one_shared_graph():
    unified, _ = runtime()
    assert unified.conversation.bootstrap is unified.bootstrap
    assert unified.bootstrap.root is unified.root


def test_start_order_is_lifecycle_supervisor_then_residents():
    events = []
    first = Component("first", events)
    second = Component("second", events)
    unified, internal = runtime(first, second)
    first.events = internal
    second.events = internal
    unified.start()
    assert internal == [
        "start:lifecycle",
        "start:supervisor",
        "start:first",
        "start:second",
    ]


def test_stop_order_is_reverse_then_supervisor_and_lifecycle():
    unified, events = runtime(
        Component("first", []),
        Component("second", []),
    )
    for item in unified.residents:
        item.events = events
    unified.start()
    unified.stop()
    assert events[-4:] == [
        "stop:second",
        "stop:first",
        "stop:supervisor",
        "stop:lifecycle",
    ]


def test_start_and_stop_are_idempotent():
    unified, events = runtime()
    unified.start()
    unified.start()
    unified.stop()
    unified.stop()
    assert events.count("start:lifecycle") == 1
    assert events.count("stop:lifecycle") == 1


def test_start_failure_rolls_back_started_components():
    unified, events = runtime(
        Component("ready", []),
        Component("broken", [], fail_start=True),
    )
    for item in unified.residents:
        item.events = events
    with pytest.raises(RuntimeError, match="start broken"):
        unified.start()
    assert "stop:ready" in events
    assert events[-2:] == ["stop:supervisor", "stop:lifecycle"]


def test_context_manager_degrades_and_stops():
    unified, events = runtime()
    with pytest.raises(ValueError):
        with unified:
            raise ValueError("failure")
    assert "degraded:ValueError" in events
    assert events[-1] == "stop:lifecycle"


def test_heartbeat_delegates_to_lifecycle():
    unified, events = runtime()
    unified.start()
    assert unified.heartbeat() == "beat"
    assert "heartbeat" in events


def test_residents_cannot_change_while_running():
    unified, _ = runtime()
    unified.start()
    with pytest.raises(RuntimeError, match="residentes"):
        unified.with_residents(Component("late", []))


def test_with_residents_returns_new_authority_before_start():
    unified, _ = runtime()
    resident = Component("resident", [])
    updated = unified.with_residents(resident, None)
    assert updated is not unified
    assert updated.composition is unified.composition
    assert updated.residents == (resident,)
