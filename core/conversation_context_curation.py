from __future__ import annotations

import re
import unicodedata

from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
)


def normalize_conversational_text(text: str) -> str:
    """Normalize conversational text for safe duplicate detection."""
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_marks = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return " ".join(re.findall(r"[a-z0-9]+", without_marks))


def curate_recent_conversation_context(
    *,
    current_text: str,
    recent_context: tuple[ConversationalContextTurn, ...],
) -> tuple[ConversationalContextTurn, ...]:
    """Remove repeated-question anchors and duplicate historical statements.

    The journal remains immutable and complete. Curation only affects the bounded
    short-term context supplied to inference for the current turn.
    """
    normalized_current = normalize_conversational_text(current_text)
    selected_reversed: list[ConversationalContextTurn] = []
    seen_user_messages: set[str] = set()

    for turn in reversed(recent_context):
        normalized_user = normalize_conversational_text(turn.user_text)
        if not normalized_user:
            continue
        if normalized_user == normalized_current:
            continue
        if normalized_user in seen_user_messages:
            continue
        selected_reversed.append(turn)
        seen_user_messages.add(normalized_user)

    return tuple(reversed(selected_reversed))
