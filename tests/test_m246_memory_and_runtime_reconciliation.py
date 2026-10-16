from __future__ import annotations

from pathlib import Path

from app.desktop_bootstrap import build_desktop_app, build_unified_desktop_app


def _memory_environment(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_RECALL_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_LEARNING_ENABLED", "true")


def test_legacy_scheduler_module_is_retired():
    assert not Path("core/scheduler.py").exists()


def test_historical_desktop_builder_is_an_official_alias(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(
        "app.desktop_bootstrap.build_unified_desktop_app", lambda: sentinel
    )
    assert build_desktop_app() is sentinel
    assert build_unified_desktop_app is not None
