from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from app.desktop_ui import ROBYDesktopApp
from core.application_lifecycle import (
    ApplicationLifecycleManager,
    LifecycleEventKind,
    LifecycleExitReason,
)

NOW = datetime(2026, 7, 20, 15, 0, tzinfo=timezone.utc)


class _Adapter:
    def submit_text(self, text: str, session_id: str | None = None):
        raise AssertionError(
            "los comandos de ciclo de vida no deben llegar al adaptador"
        )


def test_start_persists_an_open_session(tmp_path):
    path = tmp_path / "lifecycle.json"
    manager = ApplicationLifecycleManager(state_path=path)

    snapshot = manager.start(now=NOW)

    assert snapshot.current_session is not None
    assert not snapshot.current_session.clean_shutdown
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "rp25.1-v1"


def test_clean_shutdown_records_reason_and_duration(tmp_path):
    manager = ApplicationLifecycleManager(state_path=tmp_path / "state.json")
    manager.start(now=NOW)

    snapshot = manager.shutdown(
        reason=LifecycleExitReason.MENU_EXIT,
        now=datetime(2026, 7, 20, 15, 1, tzinfo=timezone.utc),
    )

    session = snapshot.current_session
    assert session is not None
    assert session.clean_shutdown
    assert session.exit_reason is LifecycleExitReason.MENU_EXIT
    assert session.duration_seconds == 60.0


def test_restart_is_persisted_and_exposed(tmp_path):
    manager = ApplicationLifecycleManager(state_path=tmp_path / "state.json")
    manager.start(now=NOW)

    snapshot = manager.shutdown(reason=LifecycleExitReason.RESTART, now=NOW)

    assert snapshot.restart_requested
    assert snapshot.events[-1].kind is LifecycleEventKind.APPLICATION_RESTART_REQUESTED


def test_previous_unclean_session_is_detected_and_recovered(tmp_path):
    path = tmp_path / "state.json"
    first = ApplicationLifecycleManager(state_path=path)
    first.start(now=NOW)

    second = ApplicationLifecycleManager(state_path=path)
    snapshot = second.start(
        now=datetime(2026, 7, 20, 15, 5, tzinfo=timezone.utc)
    )

    assert snapshot.unexpected_previous_shutdown
    kinds = {event.kind for event in snapshot.events}
    assert LifecycleEventKind.UNEXPECTED_TERMINATION in kinds
    assert LifecycleEventKind.RECOVERY_COMPLETED in kinds
    assert "recuperé" in second.recovery_message()


def test_clean_previous_session_is_not_reported_as_unexpected(tmp_path):
    path = tmp_path / "state.json"
    first = ApplicationLifecycleManager(state_path=path)
    first.start(now=NOW)
    first.shutdown(reason=LifecycleExitReason.WINDOW_CLOSE, now=NOW)

    second = ApplicationLifecycleManager(state_path=path)
    snapshot = second.start(now=NOW)

    assert not snapshot.unexpected_previous_shutdown
    assert second.recovery_message() == ""


def test_shutdown_runs_all_steps_even_when_one_fails(tmp_path):
    manager = ApplicationLifecycleManager(state_path=tmp_path / "state.json")
    manager.start(now=NOW)
    calls: list[str] = []

    def fail() -> None:
        calls.append("fail")
        raise RuntimeError("boom")

    snapshot = manager.shutdown(
        reason=LifecycleExitReason.WINDOW_CLOSE,
        steps=(("first", fail), ("second", lambda: calls.append("second"))),
        now=NOW,
    )

    assert calls == ["fail", "second"]
    assert snapshot.current_session is not None
    assert snapshot.current_session.clean_shutdown
    assert any(
        event.kind is LifecycleEventKind.SHUTDOWN_STEP_FAILED
        for event in snapshot.events
    )


def test_shutdown_timeout_does_not_block_application_exit(tmp_path):
    manager = ApplicationLifecycleManager(
        state_path=tmp_path / "state.json",
        shutdown_timeout_seconds=0.01,
    )
    manager.start(now=NOW)

    started = time.monotonic()
    snapshot = manager.shutdown(
        reason=LifecycleExitReason.WINDOW_CLOSE,
        steps=(("slow", lambda: time.sleep(0.2)),),
        now=NOW,
    )

    assert time.monotonic() - started < 0.15
    assert any(
        event.kind is LifecycleEventKind.SHUTDOWN_STEP_TIMED_OUT
        for event in snapshot.events
    )


def test_shutdown_is_idempotent(tmp_path):
    manager = ApplicationLifecycleManager(state_path=tmp_path / "state.json")
    manager.start(now=NOW)
    first = manager.shutdown(reason=LifecycleExitReason.MENU_EXIT, now=NOW)
    second = manager.shutdown(reason=LifecycleExitReason.RESTART, now=NOW)

    assert first == second
    assert not second.restart_requested


def test_natural_shutdown_commands_are_local():
    for text in (
        "Roby apagate",
        "Roby, apagáte.",
        "Roby cerrate",
        "Roby terminamos por hoy",
        "Roby hasta mañana",
        "Roby podés descansar",
    ):
        assert (
            ROBYDesktopApp.lifecycle_command(text)
            is LifecycleExitReason.VOICE_SHUTDOWN
        )


def test_natural_restart_commands_are_local():
    for text in (
        "Roby reiniciate",
        "Roby, reiniciáte.",
        "Roby reiniciá la aplicación",
    ):
        assert ROBYDesktopApp.lifecycle_command(text) is LifecycleExitReason.RESTART


def test_normal_conversation_is_not_intercepted():
    assert ROBYDesktopApp.lifecycle_command("Roby, qué hacemos hoy") is None
