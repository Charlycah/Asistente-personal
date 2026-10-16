from __future__ import annotations

from dataclasses import dataclass

from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
)

RESERVED_CONVERSATION_PREFIXES = (
    "obs>",
    "roby>",
    "sys>",
    "trace>",
    "system:",
    "assistant:",
    "user:",
)


@dataclass(frozen=True)
class ConversationHistorySanitization:
    context: tuple[ConversationalContextTurn, ...]
    removed_turns: int


def has_reserved_conversation_prefix(text: str) -> bool:
    """Return whether text begins with a runtime-reserved prefix."""
    return text.strip().casefold().startswith(RESERVED_CONVERSATION_PREFIXES)


def sanitize_conversation_history(
    recent_context: tuple[ConversationalContextTurn, ...],
) -> ConversationHistorySanitization:
    """Exclude contaminated turns from the inference-only history view.

    The persisted journal is intentionally left untouched for auditability. A
    whole turn is removed if either side contains a reserved runtime prefix.
    """
    selected = tuple(
        turn
        for turn in recent_context
        if not has_reserved_conversation_prefix(turn.user_text)
        and not has_reserved_conversation_prefix(turn.assistant_text)
    )
    return ConversationHistorySanitization(
        context=selected,
        removed_turns=len(recent_context) - len(selected),
    )
