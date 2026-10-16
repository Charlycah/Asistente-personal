from __future__ import annotations

import os

from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
)
from core.local_runtime_bootstrap import LocalRuntimeBootstrap

from .local_runtime_entrypoint import build_local_runtime_from_environment


def build_local_conversation_from_environment(
    *,
    bootstrap: LocalRuntimeBootstrap | None = None,
) -> EndToEndLocalConversation:
    """Build the local conversation runtime without any user-interface adapter."""

    local_bootstrap = bootstrap or build_local_runtime_from_environment()
    journal_path = os.getenv(
        "ROBY_CONVERSATION_JOURNAL_PATH",
        ".roby/conversation_turns.jsonl",
    )
    persist = os.getenv("ROBY_CONVERSATION_PERSIST", "1").strip().casefold()
    return EndToEndLocalConversation(
        bootstrap=local_bootstrap,
        config=EndToEndLocalConversationConfig(
            journal_path=journal_path,
            persist_turns=persist not in {"0", "false", "no"},
        ),
    )
