from __future__ import annotations

from dataclasses import dataclass, field

from core.cognitive_memory_recall import CognitiveMemoryRecallResult
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.conversation_strategy import ConversationStrategy


@dataclass(frozen=True)
class MemoryPromptContextConfig:
    """Configuración mínima para transformar recuerdos en contexto de prompt."""

    max_items: int = 5
    max_item_length: int = 240
    include_metadata: bool = False
    header: str = "Contexto de memoria relevante de ROBY"


@dataclass(frozen=True)
class MemoryPromptContext:
    """Contexto seguro que puede adjuntarse a un prompt posterior."""

    should_include: bool
    context: str
    memories: tuple[CognitiveMemoryRecord, ...] = field(default_factory=tuple)
    reason: str = ""

    @property
    def is_empty(self) -> bool:
        return not self.should_include or not self.context.strip()


class MemoryPromptContextBuilder:
    """
    Convierte recuerdos recuperados en un bloque de contexto para el LLM.

    M39 no llama al modelo, no consulta SQLite directamente y no hace recall.
    Solo toma el resultado de M37/M38 y construye un bloque textual compacto,
    ordenado y seguro para enriquecer el prompt en milestones posteriores.
    """

    def __init__(
        self,
        config: MemoryPromptContextConfig | None = None,
    ) -> None:
        self.config = config or MemoryPromptContextConfig()

    def build(
        self,
        recall_result: CognitiveMemoryRecallResult,
        *,
        strategy: ConversationStrategy | None = None,
    ) -> MemoryPromptContext:
        if not recall_result.should_use_memory or not recall_result.items:
            return MemoryPromptContext(
                should_include=False,
                context="",
                memories=(),
                reason=recall_result.reason or "no_memory_available",
            )

        max_items = max(1, min(self.config.max_items, 20))
        selected = tuple(recall_result.items[:max_items])
        lines = [self.config.header]

        if strategy is not None:
            lines.append(
                "Estrategia: "
                f"tono={strategy.tone.value}; "
                f"profundidad={strategy.depth.value}; "
                f"formato={strategy.response_format.value}"
            )

        for index, item in enumerate(selected, start=1):
            lines.append(self._format_memory(index, item.memory))

        return MemoryPromptContext(
            should_include=True,
            context="\n".join(lines),
            memories=tuple(item.memory for item in selected),
            reason="memory_context_built",
        )

    def _format_memory(
        self,
        index: int,
        memory: CognitiveMemoryRecord,
    ) -> str:
        content = self._compact(memory.content)
        base = (
            f"{index}. [{memory.category.value}; "
            f"confianza={memory.confidence:.2f}] {content}"
        )
        if not self.config.include_metadata or not memory.tags:
            return base

        tags = ", ".join(memory.tags[:5])
        return f"{base} (tags: {tags})"

    def wrap_prompt(
        self,
        user_prompt: str,
        prompt_context: MemoryPromptContext,
    ) -> str:
        prompt = user_prompt.strip()
        if not prompt_context.should_include:
            return prompt

        return "\n\n".join(
            (
                prompt_context.context,
                "Mensaje actual del usuario",
                prompt,
            )
        )

    def _compact(self, text: str) -> str:
        normalized = " ".join(text.strip().split())
        max_length = max(40, self.config.max_item_length)
        if len(normalized) <= max_length:
            return normalized
        return f"{normalized[: max_length - 1].rstrip()}…"
