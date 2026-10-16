from __future__ import annotations

from pathlib import Path

from app.runtime_root_factory import (
    build_memory_runtime_from_environment,
    build_runtime_root,
)
from core.llm_provider import LLMRequest


def _configure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_RECALL_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_LEARNING_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_RECALL_LIMIT", "5")


def test_memory_runtime_can_be_disabled(monkeypatch):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_ENABLED", "false")
    assert build_memory_runtime_from_environment() is None


def test_memory_runtime_uses_environment_path(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    runtime = build_memory_runtime_from_environment()
    assert runtime is not None
    runtime.record(
        owner="Carlos y Cristina",
        text="En casa preferimos validar ROBY con Ruff y pytest",
    )
    assert (tmp_path / "memory" / "coowners.sqlite3").exists()


def test_household_memory_survives_runtime_recreation(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    first = build_memory_runtime_from_environment()
    assert first is not None
    stored = first.record(
        owner="Carlos y Cristina",
        text="En casa preferimos validar ROBY con Ruff y pytest",
    )
    assert stored.stored_count == 1

    second = build_memory_runtime_from_environment()
    assert second is not None
    recalled = second.enrich(
        owner="Carlos y Cristina",
        text="¿Cómo preferimos validar ROBY?",
        request=LLMRequest(prompt="¿Cómo preferimos validar ROBY?"),
    )
    assert recalled.context_included
    assert "ruff" in recalled.request.prompt.casefold()


def test_official_runtime_root_wires_personal_memory(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "false")
    root = build_runtime_root()
    assert root.dependencies.memory_runtime is not None


def test_recall_limit_is_read_from_environment(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_RECALL_LIMIT", "3")
    runtime = build_memory_runtime_from_environment()
    assert runtime is not None
    assert runtime.config.recall_limit == 3
