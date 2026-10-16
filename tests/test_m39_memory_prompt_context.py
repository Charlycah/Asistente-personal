from pathlib import Path

from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_recall import CognitiveMemoryRecallResult
from core.cognitive_memory_store import (
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.memory_prompt_context import (
    MemoryPromptContextBuilder,
    MemoryPromptContextConfig,
)


def _integration(tmp_path: Path) -> CognitiveMemoryIntegration:
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )
    return CognitiveMemoryIntegration(store)


def test_memory_prompt_context_returns_empty_context_without_recall():
    builder = MemoryPromptContextBuilder()
    recall_result = CognitiveMemoryRecallResult(
        should_use_memory=False,
        items=(),
        reason="no_relevant_memory_found",
    )

    context = builder.build(recall_result)

    assert context.should_include is False
    assert context.is_empty is True
    assert context.context == ""
    assert context.reason == "no_relevant_memory_found"


def test_memory_prompt_context_builds_block_from_recalled_memories(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos Ruff y pytest antes del commit")
    result = integration.process_turn("Recordemos Ruff y pytest para M39")

    context = MemoryPromptContextBuilder().build(result.recall_result)

    assert context.should_include is True
    assert "Contexto de memoria relevante de ROBY" in context.context
    assert "ruff y pytest" in context.context
    assert context.memories == tuple(item.memory for item in result.recall_result.items)


def test_memory_prompt_context_can_include_strategy(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos milestones con cierre verificable")
    result = integration.process_turn("Sigamos el milestone verificable")

    context = MemoryPromptContextBuilder().build(
        result.recall_result,
        strategy=result.strategy,
    )

    assert "Estrategia:" in context.context
    assert "tono=" in context.context
    assert "profundidad=" in context.context
    assert "formato=" in context.context


def test_memory_prompt_context_respects_max_items(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos Ruff para validar milestones")
    integration.process_turn("En ROBY usamos pytest para validar milestones")
    integration.process_turn("En ROBY usamos commits para cerrar milestones")
    result = integration.process_turn("validar milestones en ROBY")

    builder = MemoryPromptContextBuilder(MemoryPromptContextConfig(max_items=1))
    context = builder.build(result.recall_result)

    assert len(context.memories) == 1
    assert context.context.count("1. [") == 1
    assert "2. [" not in context.context


def test_memory_prompt_context_compacts_long_memory_items(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn(
        "En ROBY la metodología incremental exige documentación, tests, "
        "Ruff, pytest, commit limpio y cierre explícito por milestone"
    )
    result = integration.process_turn("metodología incremental ROBY")

    builder = MemoryPromptContextBuilder(MemoryPromptContextConfig(max_item_length=60))
    context = builder.build(result.recall_result)

    assert "…" in context.context


def test_memory_prompt_context_can_include_tags_when_requested(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos metodología por milestone")
    result = integration.process_turn("metodología milestone")

    builder = MemoryPromptContextBuilder(
        MemoryPromptContextConfig(include_metadata=True)
    )
    context = builder.build(result.recall_result)

    assert "tags:" in context.context


def test_memory_prompt_context_wraps_user_prompt_with_context(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("Prefiero respuestas breves para commits")
    result = integration.process_turn("preparar mensaje de commit breve")
    builder = MemoryPromptContextBuilder()
    context = builder.build(result.recall_result)

    prompt = builder.wrap_prompt("Escribí el commit", context)

    assert prompt.startswith("Contexto de memoria relevante de ROBY")
    assert "Mensaje actual del usuario" in prompt
    assert prompt.endswith("Escribí el commit")


def test_memory_prompt_context_wraps_plain_prompt_without_memory():
    builder = MemoryPromptContextBuilder()
    recall_result = CognitiveMemoryRecallResult(
        should_use_memory=False,
        items=(),
        reason="recall_disabled",
    )
    context = builder.build(recall_result)

    prompt = builder.wrap_prompt("Hola ROBY", context)

    assert prompt == "Hola ROBY"


def test_memory_prompt_context_keeps_custom_header(tmp_path):
    integration = _integration(tmp_path)
    integration.process_turn("En ROBY usamos una DB cerebral local")
    result = integration.process_turn("DB cerebral local")

    builder = MemoryPromptContextBuilder(
        MemoryPromptContextConfig(header="Memoria recuperada")
    )
    context = builder.build(result.recall_result)

    assert context.context.startswith("Memoria recuperada")
