from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from app.console_input import ConsoleInputBoundary, ConsoleInputKind
from app.desktop_bootstrap import DesktopPersonalRuntime
from core.long_lived_runtime_lifecycle import (
    LongLivedRuntimeConfig,
    LongLivedRuntimeLifecycle,
    LongLivedRuntimeStatus,
)
from tests.test_m180_end_to_end_local_conversation import runtime


@pytest.mark.parametrize(
    "command",
    ["exit", "quit", "salir", "/exit", "/quit", "/salir"],
)
def test_exit_commands_are_classified_before_conversation_submission(command):
    boundary = ConsoleInputBoundary()
    parsed = boundary.classify(command)
    calls: list[str] = []

    result = boundary.forward(parsed, lambda text: calls.append(text))

    assert parsed.kind is ConsoleInputKind.EXIT
    assert result is None
    assert calls == []


def test_lifecycle_stop_releases_lease_without_console_adapter(tmp_path):
    item = runtime(tmp_path)
    managed = LongLivedRuntimeLifecycle(
        bootstrap=item.bootstrap,
        config=LongLivedRuntimeConfig(
            lease_path=tmp_path / "runtime.lease",
            heartbeat_path=tmp_path / "heartbeat.json",
            heartbeat_interval=timedelta(seconds=30),
            stale_after=timedelta(minutes=2),
        ),
    )
    lease_path = Path(managed.config.lease_path)

    managed.start()
    assert lease_path.exists()
    managed.stop()

    assert managed.state.status is LongLivedRuntimeStatus.STOPPED
    assert not lease_path.exists()


def test_desktop_runtime_starts_and_stops_services_without_console_adapter():
    events: list[str] = []

    class Service:
        def __init__(self, name: str) -> None:
            self.name = name

        def start(self) -> None:
            events.append(f"start:{self.name}")

        def stop(self) -> None:
            events.append(f"stop:{self.name}")

    desktop = DesktopPersonalRuntime(
        lifecycle=Service("lifecycle"),
        supervisor=Service("supervisor"),
        battery_awareness=Service("battery"),
        reminder_awareness=Service("reminders"),
    )

    desktop.start()
    desktop.stop()

    assert events == [
        "start:lifecycle",
        "start:supervisor",
        "start:battery",
        "start:reminders",
        "stop:reminders",
        "stop:battery",
        "stop:supervisor",
        "stop:lifecycle",
    ]
    assert not desktop.is_running
