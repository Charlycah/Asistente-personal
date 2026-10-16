from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from app.long_lived_runtime_entrypoint import (
    build_long_lived_lifecycle_from_environment,
)
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
    LocalRuntimeStatus,
)
from core.long_lived_runtime_lifecycle import (
    JsonLongLivedRuntimeStateStore,
    LongLivedRuntimeConfig,
    LongLivedRuntimeLifecycle,
    LongLivedRuntimeStatus,
    RuntimeLeaseError,
)
from core.platform_runtime_compatibility import private_file_is_protected
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import dependencies

START = datetime(2026, 7, 12, 20, 0, tzinfo=timezone.utc)
HEARTBEAT = datetime(2026, 7, 12, 20, 0, 30, tzinfo=timezone.utc)
STOP = datetime(2026, 7, 12, 21, 0, tzinfo=timezone.utc)


def lifecycle(tmp_path, *, process_id=101):
    bootstrap = LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(dependencies()),
        config=LocalRuntimeBootstrapConfig(
            owner="Carlos",
            session_id="desktop-main",
            state_path=tmp_path / "runtime.json",
        ),
    )
    return LongLivedRuntimeLifecycle(
        bootstrap=bootstrap,
        config=LongLivedRuntimeConfig(
            lease_path=tmp_path / "runtime.lease",
            heartbeat_path=tmp_path / "heartbeat.json",
            heartbeat_interval=timedelta(seconds=30),
            stale_after=timedelta(minutes=2),
        ),
        process_id=process_id,
    )


def test_start_owns_single_runtime_lease(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    assert (tmp_path / "runtime.lease").exists()
    assert runtime.state.status is LongLivedRuntimeStatus.RUNNING


def test_start_delegates_to_m179_bootstrap(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    assert runtime.bootstrap.is_running
    assert runtime.bootstrap.state.status is LocalRuntimeStatus.RUNNING


def test_start_is_idempotent(tmp_path):
    runtime = lifecycle(tmp_path)
    first = runtime.start(now=START)
    second = runtime.start(now=HEARTBEAT)
    assert first is second
    assert second.started_at == START


def test_second_process_is_rejected_while_lease_exists(tmp_path):
    first = lifecycle(tmp_path, process_id=101)
    second = lifecycle(tmp_path, process_id=202)
    first.start(now=START)
    with pytest.raises(RuntimeLeaseError, match="another ROBY"):
        second.start(now=HEARTBEAT)


def test_heartbeat_updates_persistent_liveness(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    state = runtime.heartbeat(now=HEARTBEAT)
    loaded = JsonLongLivedRuntimeStateStore(tmp_path / "heartbeat.json").load()
    assert state.heartbeat_at == HEARTBEAT
    assert loaded == state


def test_heartbeat_requires_running_runtime(tmp_path):
    with pytest.raises(RuntimeError, match="running"):
        lifecycle(tmp_path).heartbeat(now=HEARTBEAT)


def test_stale_detection_uses_configured_threshold(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    assert not runtime.is_stale(now=START + timedelta(minutes=2))
    assert runtime.is_stale(now=START + timedelta(minutes=2, seconds=1))


def test_mark_degraded_contains_exception_type_only(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    state = runtime.mark_degraded(ValueError("private detail"), now=HEARTBEAT)
    assert state.status is LongLivedRuntimeStatus.DEGRADED
    assert state.failure == "ValueError"
    assert "private detail" not in (tmp_path / "heartbeat.json").read_text()


def test_degraded_runtime_can_heartbeat_back_to_running(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    runtime.mark_degraded(ValueError("x"), now=HEARTBEAT)
    state = runtime.heartbeat(now=STOP)
    assert state.status is LongLivedRuntimeStatus.RUNNING
    assert state.failure is None


def test_stop_closes_bootstrap_and_releases_lease(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    state = runtime.stop(now=STOP)
    assert state.status is LongLivedRuntimeStatus.STOPPED
    assert runtime.bootstrap.state.status is LocalRuntimeStatus.STOPPED
    assert not (tmp_path / "runtime.lease").exists()


def test_stop_is_idempotent(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    first = runtime.stop(now=STOP)
    second = runtime.stop(now=STOP + timedelta(hours=1))
    assert first is second


def test_context_manager_releases_lease(tmp_path):
    runtime = lifecycle(tmp_path)
    with runtime:
        assert runtime.is_running
    assert runtime.state.status is LongLivedRuntimeStatus.STOPPED
    assert not (tmp_path / "runtime.lease").exists()


def test_context_manager_marks_failure_without_leaking_message(tmp_path):
    runtime = lifecycle(tmp_path)
    with pytest.raises(ValueError, match="secret"):
        with runtime:
            raise ValueError("secret")
    payload = json.loads((tmp_path / "heartbeat.json").read_text())
    assert payload["status"] == "stopped"
    assert "secret" not in json.dumps(payload)


def test_generation_increases_across_process_restarts(tmp_path):
    first = lifecycle(tmp_path, process_id=101)
    first.start(now=START)
    first.stop(now=HEARTBEAT)
    second = lifecycle(tmp_path, process_id=202)
    second.start(now=STOP)
    assert second.state.generation == first.state.generation + 1


def test_state_file_contains_only_operational_metadata(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    payload = json.loads((tmp_path / "heartbeat.json").read_text())
    assert set(payload) == {
        "failure",
        "generation",
        "heartbeat_at",
        "owner",
        "process_id",
        "session_id",
        "started_at",
        "status",
        "stopped_at",
        "updated_at",
    }


def test_state_and_lease_files_are_private(tmp_path):
    runtime = lifecycle(tmp_path)
    runtime.start(now=START)
    assert private_file_is_protected(tmp_path / "heartbeat.json")
    assert private_file_is_protected(tmp_path / "runtime.lease")


def test_invalid_heartbeat_interval_is_rejected():
    with pytest.raises(ValueError, match="positive"):
        LongLivedRuntimeConfig(heartbeat_interval=timedelta(0))


def test_stale_threshold_must_cover_interval():
    with pytest.raises(ValueError, match="cover"):
        LongLivedRuntimeConfig(
            heartbeat_interval=timedelta(minutes=2),
            stale_after=timedelta(seconds=30),
        )


def test_naive_lifecycle_time_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="timezone-aware"):
        lifecycle(tmp_path).start(now=datetime(2026, 7, 12, 20, 0))


def test_environment_builder_reads_lifecycle_paths(monkeypatch, tmp_path):
    runtime = type("Runtime", (), {"bootstrap": lifecycle(tmp_path).bootstrap})()
    monkeypatch.setenv("ROBY_RUNTIME_LEASE_PATH", str(tmp_path / "custom.lease"))
    monkeypatch.setenv("ROBY_RUNTIME_HEARTBEAT_PATH", str(tmp_path / "custom.json"))
    monkeypatch.setenv("ROBY_RUNTIME_HEARTBEAT_SECONDS", "10")
    monkeypatch.setenv("ROBY_RUNTIME_STALE_SECONDS", "60")
    built = build_long_lived_lifecycle_from_environment(runtime)
    assert built.config.lease_path == tmp_path / "custom.lease"
    assert built.config.heartbeat_path == tmp_path / "custom.json"
    assert built.config.heartbeat_interval == timedelta(seconds=10)
