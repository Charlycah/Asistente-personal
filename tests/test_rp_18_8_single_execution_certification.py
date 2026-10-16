from __future__ import annotations

from pathlib import Path

from app.official_runtime_composition import build_official_runtime_from_environment
from app.runtime_execution_certification import certify_runtime_execution


def _runtime(tmp_path, monkeypatch):
    monkeypatch.setenv("ROBY_RUNTIME_STATE_PATH", str(tmp_path / "runtime.json"))
    monkeypatch.setenv(
        "ROBY_RUNTIME_ROOT_FACTORY",
        "app.runtime_root_factory:build_runtime_root",
    )
    return build_official_runtime_from_environment()


def test_inventory_certifies_one_process_and_lifecycle_authority() -> None:
    report = certify_runtime_execution()

    assert report.certified
    assert report.process_entrypoints == ("main:main",)
    assert report.lifecycle_authorities == (
        "app.official_runtime_composition:OfficialROBYRuntime",
    )


def test_runtime_graph_preserves_canonical_object_identity(
    tmp_path, monkeypatch
) -> None:
    runtime = _runtime(tmp_path, monkeypatch)

    report = certify_runtime_execution(runtime)

    assert report.certified
    assert runtime.conversation.bootstrap is runtime.bootstrap
    assert runtime.bootstrap.root is runtime.root


def test_compatibility_surfaces_are_non_executable() -> None:
    report = certify_runtime_execution()

    assert report.non_executable_compatibility_paths
    assert not report.findings


def test_retired_console_composition_is_outside_the_process_entrypoint() -> None:
    main_source = Path("main.py").read_text(encoding="utf-8")
    legacy_path = Path("app/legacy_console_compatibility.py")

    assert "--console" not in main_source
    assert "build_official_runtime_from_environment(" not in main_source
    assert not legacy_path.exists()


def test_retired_console_is_absent_and_runtime_owns_lifecycle() -> None:
    console_path = Path("app/local_conversation_entrypoint.py")
    source = Path("app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert not console_path.exists()
    assert "self.lifecycle.start()" in source
    assert "self.lifecycle.heartbeat()" in source
    assert "self.lifecycle.stop()" in source
