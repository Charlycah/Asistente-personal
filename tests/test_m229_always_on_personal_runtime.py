from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.always_on_personal_runtime_wiring import (
    build_battery_awareness_from_environment,
)
from core.always_on_personal_runtime import (
    BatteryAwarenessPolicy,
    BatteryAwarenessService,
    BatterySnapshot,
)
from infrastructure.system.battery_sensor import NativeBatterySensor

NOW = datetime(2026, 7, 14, 20, 0, tzinfo=timezone.utc)


class Sensor:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = 0

    def read(self):
        self.calls += 1
        if not self.values:
            return None
        if len(self.values) == 1:
            return self.values[0]
        return self.values.pop(0)


def service(sensor, messages, **policy):
    return BatteryAwarenessService(
        sensor,
        notify=messages.append,
        owner="Carlos",
        policy=BatteryAwarenessPolicy(**policy),
        clock=lambda: NOW,
    )


def test_low_battery_emits_spontaneous_intervention():
    messages = []
    runtime = service(Sensor(BatterySnapshot(15, False)), messages)

    result = runtime.check_once()

    assert result == "Carlos, la batería está en 15 %. Conviene conectar el cargador."
    assert messages == [result]


def test_low_battery_does_not_repeat_inside_cooldown():
    messages = []
    runtime = service(Sensor(BatterySnapshot(10, False)), messages)

    runtime.check_once(now=NOW)
    assert runtime.check_once(now=NOW + timedelta(minutes=29)) is None
    assert len(messages) == 1


def test_low_battery_repeats_after_cooldown():
    messages = []
    runtime = service(
        Sensor(BatterySnapshot(10, False)),
        messages,
        repeat_after=timedelta(minutes=30),
    )

    runtime.check_once(now=NOW)
    runtime.check_once(now=NOW + timedelta(minutes=30))

    assert len(messages) == 2


def test_charging_suppresses_notification():
    messages = []
    runtime = service(Sensor(BatterySnapshot(5, True)), messages)

    assert runtime.check_once() is None
    assert messages == []


def test_recovery_starts_a_new_low_battery_episode():
    messages = []
    sensor = Sensor(
        BatterySnapshot(10, False),
        BatterySnapshot(20, False),
        BatterySnapshot(10, False),
    )
    runtime = service(sensor, messages)

    runtime.check_once(now=NOW)
    runtime.check_once(now=NOW + timedelta(minutes=1))
    runtime.check_once(now=NOW + timedelta(minutes=2))

    assert len(messages) == 2


def test_sensor_unavailable_is_silent():
    messages = []
    runtime = service(Sensor(None), messages)

    assert runtime.check_once() is None
    assert messages == []


def test_sensor_failure_does_not_break_roby():
    class BrokenSensor:
        def read(self):
            raise OSError("private device failure")

    messages = []
    runtime = service(BrokenSensor(), messages)

    assert runtime.check_once() is None
    assert messages == []


def test_naive_time_is_rejected():
    runtime = service(Sensor(BatterySnapshot(10, False)), [])

    with pytest.raises(ValueError, match="timezone-aware"):
        runtime.check_once(now=datetime(2026, 7, 14, 20, 0))


@pytest.mark.parametrize("percent", [-1, 101])
def test_battery_snapshot_validates_percentage(percent):
    with pytest.raises(ValueError, match="battery percent"):
        BatterySnapshot(percent, False)


def test_wiring_is_enabled_by_default(monkeypatch):
    monkeypatch.delenv("ROBY_PERSONAL_RUNTIME_ENABLED", raising=False)
    monkeypatch.delenv("ROBY_BATTERY_AWARENESS_ENABLED", raising=False)

    runtime = build_battery_awareness_from_environment(
        notify=lambda message: None,
        owner="Carlos",
    )

    assert runtime is not None
    assert runtime.policy.low_threshold == 15


def test_wiring_can_disable_entire_personal_runtime(monkeypatch):
    monkeypatch.setenv("ROBY_PERSONAL_RUNTIME_ENABLED", "false")

    assert (
        build_battery_awareness_from_environment(
            notify=lambda message: None,
            owner="Carlos",
        )
        is None
    )


def test_wiring_can_disable_only_battery_awareness(monkeypatch):
    monkeypatch.setenv("ROBY_PERSONAL_RUNTIME_ENABLED", "true")
    monkeypatch.setenv("ROBY_BATTERY_AWARENESS_ENABLED", "false")

    assert (
        build_battery_awareness_from_environment(
            notify=lambda message: None,
            owner="Carlos",
        )
        is None
    )


def test_wiring_reads_governed_policy(monkeypatch):
    monkeypatch.setenv("ROBY_BATTERY_LOW_PERCENT", "12")
    monkeypatch.setenv("ROBY_BATTERY_RECOVERY_MARGIN", "7")
    monkeypatch.setenv("ROBY_BATTERY_POLL_SECONDS", "5")
    monkeypatch.setenv("ROBY_BATTERY_REPEAT_SECONDS", "600")

    runtime = build_battery_awareness_from_environment(
        notify=lambda message: None,
        owner="Carlos",
    )

    assert runtime is not None
    assert runtime.policy == BatteryAwarenessPolicy(
        low_threshold=12,
        recovery_margin=7,
        poll_interval=timedelta(seconds=5),
        repeat_after=timedelta(seconds=600),
    )


def test_linux_sensor_returns_none_when_no_battery(monkeypatch):
    monkeypatch.setattr("infrastructure.system.battery_sensor.sys.platform", "linux")
    monkeypatch.setattr(
        "infrastructure.system.battery_sensor.Path.glob",
        lambda self, pattern: iter(()),
    )

    assert NativeBatterySensor().read() is None
