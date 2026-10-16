from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.local_runtime_entrypoint import (
    LocalRuntimeFactoryError,
    _load_root_factory,
)
from core.local_runtime_bootstrap import (
    JsonLocalRuntimeStateStore,
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
    LocalRuntimeState,
    LocalRuntimeStatus,
)
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import dependencies

START = datetime(2026, 7, 12, 20, 0, tzinfo=timezone.utc)
STOP = datetime(2026, 7, 12, 21, 0, tzinfo=timezone.utc)


def bootstrap(tmp_path):
    return LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(dependencies()),
        config=LocalRuntimeBootstrapConfig(
            owner="Carlos",
            session_id="desktop-main",
            state_path=tmp_path / "runtime.json",
        ),
    )


def test_start_composes_m178_runtime(tmp_path):
    runtime = bootstrap(tmp_path)
    composition = runtime.start(now=START)
    assert composition is runtime.root.compose()
    assert runtime.composition is composition


def test_start_marks_runtime_running(tmp_path):
    runtime = bootstrap(tmp_path)
    runtime.start(now=START)
    assert runtime.is_running
    assert runtime.state.status is LocalRuntimeStatus.RUNNING
    assert runtime.state.started_at == START


def test_start_persists_lifecycle_state(tmp_path):
    runtime = bootstrap(tmp_path)
    runtime.start(now=START)
    loaded = JsonLocalRuntimeStateStore(tmp_path / "runtime.json").load()
    assert loaded == runtime.state


def test_start_is_idempotent(tmp_path):
    runtime = bootstrap(tmp_path)
    first = runtime.start(now=START)
    second = runtime.start(now=STOP)
    assert first is second
    assert runtime.state.started_at == START


def test_start_does_not_process_conversation(tmp_path):
    runtime = bootstrap(tmp_path)
    composition = runtime.start(now=START)
    assert composition.conversation_pipeline.last_result is None


def test_stop_marks_runtime_stopped(tmp_path):
    runtime = bootstrap(tmp_path)
    runtime.start(now=START)
    state = runtime.stop(now=STOP)
    assert state.status is LocalRuntimeStatus.STOPPED
    assert state.started_at == START
    assert state.stopped_at == STOP
    assert not runtime.is_running


def test_stop_is_idempotent(tmp_path):
    runtime = bootstrap(tmp_path)
    runtime.start(now=START)
    first = runtime.stop(now=STOP)
    second = runtime.stop(now=datetime(2026, 7, 12, 22, tzinfo=timezone.utc))
    assert first is second


def test_stop_before_start_is_valid(tmp_path):
    runtime = bootstrap(tmp_path)
    state = runtime.stop(now=STOP)
    assert state.status is LocalRuntimeStatus.STOPPED
    assert state.started_at is None


def test_context_manager_starts_and_stops(tmp_path):
    runtime = bootstrap(tmp_path)
    with runtime:
        assert runtime.is_running
    assert runtime.state.status is LocalRuntimeStatus.STOPPED


def test_state_survives_bootstrap_recreation(tmp_path):
    first = bootstrap(tmp_path)
    first.start(now=START)
    second = bootstrap(tmp_path)
    assert second.state.status is LocalRuntimeStatus.RUNNING
    assert second.state.started_at == START


def test_recreated_running_bootstrap_rehydrates_composition(tmp_path):
    first = bootstrap(tmp_path)
    first.start(now=START)
    second = bootstrap(tmp_path)
    assert second.composition is None
    assert second.start(now=STOP) is second.root.compose()
    assert second.state.started_at == START


def test_persisted_owner_is_accepted_for_household_compatibility(tmp_path):
    store = JsonLocalRuntimeStateStore(tmp_path / "runtime.json")
    store.save(LocalRuntimeState("Ana", "desktop-main", LocalRuntimeStatus.CREATED))

    runtime = bootstrap(tmp_path)

    assert runtime.state.owner == "Ana"


def test_persisted_session_is_accepted_for_household_compatibility(tmp_path):
    store = JsonLocalRuntimeStateStore(tmp_path / "runtime.json")
    store.save(LocalRuntimeState("Carlos", "other", LocalRuntimeStatus.CREATED))

    runtime = bootstrap(tmp_path)

    assert runtime.state.session_id == "other"


def test_json_store_writes_no_conversation_content(tmp_path):
    runtime = bootstrap(tmp_path)
    runtime.start(now=START)
    payload = json.loads((tmp_path / "runtime.json").read_text(encoding="utf-8"))
    assert set(payload) == {
        "failure",
        "owner",
        "session_id",
        "started_at",
        "status",
        "stopped_at",
        "updated_at",
    }


def test_json_store_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "runtime.json"
    JsonLocalRuntimeStateStore(path).save(
        LocalRuntimeState("Carlos", "desktop-main", LocalRuntimeStatus.CREATED)
    )
    assert path.exists()


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError, match="owner"):
        LocalRuntimeBootstrapConfig(owner=" ")


def test_blank_session_is_rejected():
    with pytest.raises(ValueError, match="session"):
        LocalRuntimeBootstrapConfig(owner="Carlos", session_id=" ")


def test_naive_lifecycle_time_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="timezone-aware"):
        bootstrap(tmp_path).start(now=datetime(2026, 7, 12, 20, 0))


def test_factory_path_is_required():
    with pytest.raises(LocalRuntimeFactoryError, match="ROBY_RUNTIME_ROOT_FACTORY"):
        _load_root_factory("")


def test_factory_must_exist():
    with pytest.raises(LocalRuntimeFactoryError, match="Cannot load"):
        _load_root_factory("missing.module:factory")
