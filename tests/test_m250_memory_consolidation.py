from datetime import datetime, timezone
from pathlib import Path

from app.memory_consolidation import OfficialMemoryGateway
from app.runtime_root_factory import (
    build_memory_runtime_from_environment,
    build_runtime_root,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.memory import MemoryItem, MemoryQuery


def _configure(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_RECALL_ENABLED", "true")
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_LEARNING_ENABLED", "true")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    monkeypatch.setenv("ROBY_RUNTIME_OWNER", "Carlos")


def test_gateway_implements_legacy_memory_store_over_official_runtime(
    monkeypatch, tmp_path
):
    _configure(monkeypatch, tmp_path)
    runtime = build_memory_runtime_from_environment()
    assert runtime is not None
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    gateway.remember(MemoryItem("ROBY usa una memoria oficial persistente"))
    recalled = gateway.recall(MemoryQuery("memoria oficial"))
    assert recalled
    assert "memoria oficial" in recalled[0].content


def test_explicit_memory_command_persists_without_learning_heuristics(
    monkeypatch, tmp_path
):
    _configure(monkeypatch, tmp_path)
    root = build_runtime_root()
    registry = root.dependencies.official_capability_registry
    result = registry.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos",
            session_id="m250",
            text="Recordá que mi color favorito es azul",
        ),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert result.rationale == "official_memory_explicit_store_completed"
    runtime = root.dependencies.memory_runtime
    assert runtime.count(owner="Carlos") == 1


def test_memory_inspection_uses_same_persistent_store(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    root = build_runtime_root()
    runtime = root.dependencies.memory_runtime
    runtime.store_explicit(owner="Carlos", text="Prefiero respuestas directas")
    result = root.dependencies.official_capability_registry.intercept(
        GovernedConversationPipelineRequest(
            owner="Carlos", session_id="m250", text="¿Qué recordás de mí?"
        ),
        now=datetime.now(timezone.utc),
    )
    assert result is not None
    assert "prefiero respuestas directas" in result.response_text.casefold()


def test_official_registry_exposes_unified_memory_capability(monkeypatch, tmp_path):
    _configure(monkeypatch, tmp_path)
    registry = build_runtime_root().dependencies.official_capability_registry
    assert "memory.personal" in registry.capability_names


def test_disabled_memory_does_not_register_capability(monkeypatch):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_ENABLED", "false")
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_ENABLED", "false")
    registry = build_runtime_root().dependencies.official_capability_registry
    assert "memory.personal" not in registry.capability_names
