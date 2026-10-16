from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from app.console_input import ConsoleInputBoundary, ConsoleInputKind
from app.runtime_supervisor import RuntimeHeartbeatSupervisor
from core.long_lived_runtime_lifecycle import RuntimeLeaseError
from core.platform_runtime_compatibility import private_file_is_protected
from tests.test_m185_long_lived_runtime_lifecycle import lifecycle

NOW = datetime(2026, 7, 12, 18, 0, tzinfo=timezone.utc)


def test_tool_command_crosses_independent_input_boundary():
    boundary = ConsoleInputBoundary()
    parsed = boundary.classify('/tool echo {"x":1}')
    calls: list[str] = []

    result = boundary.forward(parsed, lambda text: calls.append(text) or text)

    assert parsed.kind is ConsoleInputKind.CONVERSATION
    assert result == '/tool echo {"x":1}'
    assert calls == ['/tool echo {"x":1}']


def test_other_slash_commands_cannot_cross_independent_input_boundary():
    boundary = ConsoleInputBoundary()
    parsed = boundary.classify("/status")
    calls: list[str] = []

    result = boundary.forward(parsed, lambda text: calls.append(text))

    assert parsed.kind is ConsoleInputKind.COMMAND
    assert result is None
    assert calls == []


def test_supervisor_is_idempotent(tmp_path):
    item = lifecycle(tmp_path)
    supervisor = RuntimeHeartbeatSupervisor(item, wait=lambda _: True)
    supervisor.start()
    supervisor.start()
    supervisor.stop()
    supervisor.stop()
    assert not supervisor.is_running


def test_supervisor_uses_configured_interval(tmp_path):
    item = lifecycle(tmp_path)
    item.config = type(item.config)(
        lease_path=item.config.lease_path,
        heartbeat_path=item.config.heartbeat_path,
        heartbeat_interval=timedelta(seconds=7),
        stale_after=timedelta(seconds=30),
    )
    seen = []
    supervisor = RuntimeHeartbeatSupervisor(
        item, wait=lambda seconds: seen.append(seconds) or True
    )
    supervisor._run()
    assert seen == [7.0]


def test_stale_dead_lease_is_recovered(tmp_path, monkeypatch):
    first = lifecycle(tmp_path, process_id=111)
    first.start(now=NOW)
    first.state_store.save(first.state)
    monkeypatch.setattr(first, "_process_exists", lambda _: False)
    first.state_store.save(
        first.state.__class__(
            owner=first.state.owner,
            session_id=first.state.session_id,
            process_id=111,
            status=first.state.status,
            generation=first.state.generation,
            started_at=NOW - timedelta(minutes=10),
            heartbeat_at=NOW - timedelta(minutes=10),
            updated_at=NOW - timedelta(minutes=10),
        )
    )
    second = lifecycle(tmp_path, process_id=222)
    monkeypatch.setattr(second, "_process_exists", lambda _: False)
    state = second.start(now=NOW)
    assert state.process_id == 222
    second.stop(now=NOW)


def test_live_lease_is_never_recovered(tmp_path, monkeypatch):
    first = lifecycle(tmp_path, process_id=111)
    first.start(now=NOW)
    second = lifecycle(tmp_path, process_id=222)
    monkeypatch.setattr(second, "_process_exists", lambda _: True)
    try:
        second.start(now=NOW + timedelta(minutes=10))
    except RuntimeLeaseError:
        pass
    else:
        raise AssertionError("live lease must remain exclusive")
    first.stop(now=NOW)


def test_malformed_lease_is_not_deleted(tmp_path):
    item = lifecycle(tmp_path)
    item.config.lease_path.parent.mkdir(parents=True, exist_ok=True)
    item.config.lease_path.write_text("not-json", encoding="utf-8")
    try:
        item.start(now=NOW)
    except RuntimeLeaseError:
        pass
    else:
        raise AssertionError("malformed lease must fail closed")
    assert item.config.lease_path.exists()


def test_lease_file_remains_private_after_recovery(tmp_path, monkeypatch):
    item = lifecycle(tmp_path, process_id=111)
    path = item.config.lease_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"process_id": 999}), encoding="utf-8")
    item.state_store.save(
        item._state.__class__(
            owner=item._state.owner,
            session_id=item._state.session_id,
            process_id=999,
            status="running",
            generation=1,
            started_at=NOW - timedelta(minutes=10),
            heartbeat_at=NOW - timedelta(minutes=10),
            updated_at=NOW - timedelta(minutes=10),
        )
    )
    monkeypatch.setattr(item, "_process_exists", lambda _: False)
    item.start(now=NOW)
    assert private_file_is_protected(path)
    item.stop(now=NOW)


def test_runtime_dependency_ports_are_protocols():
    from core.runtime_composition_root.models import MemoryRuntimePort, ToolRuntimePort

    assert getattr(MemoryRuntimePort, "_is_runtime_protocol", False)
    assert getattr(ToolRuntimePort, "_is_runtime_protocol", False)
