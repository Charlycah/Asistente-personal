from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
)
from core.llm_provider import LLMRequest
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
    MemoryRuntimeScope,
)
from core.platform_runtime_compatibility import private_file_is_protected
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import RecordingProvider, dependencies

NOW = datetime(2026, 7, 13, 3, 0, tzinfo=timezone.utc)


def memory(tmp_path, **overrides):
    values = {"root_path": tmp_path / "memory"}
    values.update(overrides)
    return MemoryRuntimeIntegration(MemoryRuntimeConfig(**values))


def runtime(tmp_path, *, owner="Carlos", memory_runtime=None, provider=None):
    deps = replace(
        dependencies(provider=provider),
        memory_runtime=memory_runtime or memory(tmp_path),
    )
    bootstrap = LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(deps),
        config=LocalRuntimeBootstrapConfig(
            owner=owner,
            session_id="desktop-main",
            state_path=tmp_path / f"{owner}-runtime.json",
        ),
    )
    return EndToEndLocalConversation(
        bootstrap=bootstrap,
        config=EndToEndLocalConversationConfig(
            journal_path=tmp_path / f"{owner}-turns.jsonl",
            trace_path=tmp_path / f"{owner}-traces.jsonl",
        ),
    )


def request(prompt="Recordemos Ruff en ROBY"):
    return LLMRequest(prompt=prompt, metadata={"source": "test"})


def test_config_normalizes_root_path(tmp_path):
    config = MemoryRuntimeConfig(root_path=str(tmp_path / "memory"))
    assert config.root_path == tmp_path / "memory"


def test_config_rejects_invalid_recall_limit(tmp_path):
    with pytest.raises(ValueError, match="between 1 and 20"):
        MemoryRuntimeConfig(root_path=tmp_path, recall_limit=0)


def test_blank_owner_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="owner"):
        memory(tmp_path).enrich(owner=" ", text="hola", request=request())


def test_no_memory_keeps_request_unchanged(tmp_path):
    result = memory(tmp_path).enrich(
        owner="Carlos", text="Recordemos Ruff", request=request()
    )
    assert result.request == request()
    assert not result.context_included


def test_learning_stores_approved_private_memory(tmp_path):
    item = memory(tmp_path)
    result = item.record(
        owner="Carlos",
        text="En ROBY usamos Ruff y pytest antes de cerrar milestones",
    )
    assert result.stored_count == 1
    assert item.private_store("Carlos").count() == 1


def test_noise_is_not_stored(tmp_path):
    item = memory(tmp_path)
    assert item.record(owner="Carlos", text="ok").stored_count == 0


def test_recall_enriches_llm_prompt(tmp_path):
    item = memory(tmp_path)
    item.record(owner="Carlos", text="En ROBY usamos Ruff para validar milestones")
    result = item.enrich(
        owner="Carlos", text="Recordemos Ruff en milestones", request=request()
    )
    assert result.context_included
    assert "Contexto de memoria relevante de ROBY" in result.request.prompt
    assert result.request.metadata["memory_context"] == "included"


def test_original_request_fields_are_preserved(tmp_path):
    item = memory(tmp_path)
    item.record(owner="Carlos", text="En ROBY usamos Ruff para validar milestones")
    original = LLMRequest(
        prompt="Ruff en ROBY",
        system_prompt="system",
        model="local",
        max_tokens=10,
        temperature=0.2,
        metadata={"x": "y"},
    )
    enriched = item.enrich(
        owner="Carlos", text="Ruff en ROBY", request=original
    ).request
    assert (enriched.system_prompt, enriched.model, enriched.max_tokens) == (
        "system",
        "local",
        10,
    )
    assert enriched.metadata["x"] == "y"


def test_private_memories_are_isolated_by_owner(tmp_path):
    item = memory(tmp_path)
    item.record(owner="Carlos", text="En ROBY usamos Ruff para validar milestones")
    result = item.enrich(owner="Esposa", text="Ruff en milestones", request=request())
    assert not result.context_included
    assert item.private_store("Esposa").count() == 0


def test_owner_database_names_do_not_expose_identity(tmp_path):
    item = memory(tmp_path)
    item.private_store("Carlos")
    names = [path.name for path in (tmp_path / "memory").iterdir()]
    assert all("Carlos" not in name for name in names)


def test_memory_database_is_private(tmp_path):
    item = memory(tmp_path)
    item.private_store("Carlos")
    database = next((tmp_path / "memory").glob("owner-*.sqlite3"))
    assert private_file_is_protected(database)


def test_shared_memory_is_opt_in(tmp_path):
    item = memory(tmp_path, include_shared=False)
    assert item.enrich(owner="Carlos", text="hola", request=request()).scopes == (
        MemoryRuntimeScope.PRIVATE,
    )


def test_shared_scope_is_included_when_enabled(tmp_path):
    item = memory(tmp_path, include_shared=True)
    assert item.enrich(owner="Carlos", text="hola", request=request()).scopes == (
        MemoryRuntimeScope.PRIVATE,
        MemoryRuntimeScope.SHARED,
    )


def test_disabled_recall_never_changes_prompt(tmp_path):
    item = memory(tmp_path, enable_recall=False)
    result = item.enrich(owner="Carlos", text="Ruff", request=request())
    assert result.request == request()
    assert result.rationale == ("memory_recall_disabled",)


def test_disabled_learning_never_writes(tmp_path):
    item = memory(tmp_path, enable_learning=False)
    result = item.record(owner="Carlos", text="En ROBY usamos Ruff y pytest")
    assert not result.learning_enabled
    assert result.stored_count == 0
    assert not (tmp_path / "memory").exists()


def test_composition_does_not_access_memory(tmp_path):
    class RecordingMemory:
        def __init__(self):
            self.calls = []

        def enrich(self, **kwargs):
            self.calls.append(kwargs)

    port = RecordingMemory()
    RuntimeCompositionRoot(replace(dependencies(), memory_runtime=port)).compose()
    assert port.calls == []


def test_end_to_end_turn_learns_after_pipeline(tmp_path):
    item = memory(tmp_path)
    conversation = runtime(tmp_path, memory_runtime=item)
    conversation.bootstrap.start(now=NOW)
    conversation.converse(
        "En ROBY usamos Ruff y pytest antes de cerrar milestones", now=NOW
    )
    assert item.private_store("Carlos").count() == 1


def test_second_turn_receives_recalled_context(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    item.converse("En ROBY usamos Ruff para validar milestones", now=NOW)
    item.converse("Recordemos Ruff en milestones", now=NOW)
    assert "Contexto de memoria relevante de ROBY" in provider.calls[1].prompt


def test_memory_survives_runtime_recreation(tmp_path):
    first_memory = memory(tmp_path)
    first = runtime(tmp_path, memory_runtime=first_memory)
    first.bootstrap.start(now=NOW)
    first.converse("En ROBY usamos Ruff para validar milestones", now=NOW)
    second_memory = memory(tmp_path)
    result = second_memory.enrich(
        owner="Carlos", text="Ruff en milestones", request=request()
    )
    assert result.context_included


def test_models_are_immutable(tmp_path):
    result = memory(tmp_path).record(owner="Carlos", text="ok")
    with pytest.raises(FrozenInstanceError):
        result.stored_count = 3
