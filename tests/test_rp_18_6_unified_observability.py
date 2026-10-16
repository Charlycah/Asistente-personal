from datetime import datetime, timezone

from app.official_runtime_composition import build_official_runtime_from_environment
from app.unified_runtime_observability import UnifiedRuntimeObservability


def test_official_runtime_exposes_one_observability_surface(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    runtime = build_official_runtime_from_environment()
    now = datetime(2026, 7, 17, 22, 0, tzinfo=timezone.utc)

    snapshot = runtime.observability(now=now)

    assert snapshot.generated_at == now
    assert snapshot.operational == runtime.snapshot(now=now)
    assert snapshot.conversation == runtime.conversation.snapshot
    assert snapshot.registered_capabilities
    assert snapshot.capabilities is not None


def test_observability_reads_gateway_state_without_copying_it(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    runtime = build_official_runtime_from_environment()
    service = UnifiedRuntimeObservability()

    before = service.snapshot(runtime)
    runtime.conversation._submitted_turns = 2
    after = service.snapshot(runtime)

    assert before.conversation.submitted_turns == 0
    assert after.conversation.submitted_turns == 2


def test_observability_reports_absent_cognitive_core_without_failure(
    tmp_path, monkeypatch
):
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    runtime = build_official_runtime_from_environment()

    snapshot = runtime.observability()

    assert snapshot.cognitive_core.present is False
    assert snapshot.cognitive_core.snapshot is None


def test_observability_serializes_to_plain_data(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    runtime = build_official_runtime_from_environment()

    payload = runtime.observability().as_dict()

    assert isinstance(payload["generated_at"], str)
    assert isinstance(payload["registered_capabilities"], list)
    assert "operational" in payload
    assert "readiness" in payload
