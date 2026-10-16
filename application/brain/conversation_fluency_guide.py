from __future__ import annotations

import re

from .conversation_fluency import ConversationFluencyDecision


class ConversationFluencyGuide:
    """Remove one redundant transition while preserving response semantics."""

    _BRIDGE_RE = re.compile(
        r"^\s*(?:entonces|en ese caso|bien,? entonces)[.!,:;\s-]+",
        re.IGNORECASE,
    )

    def apply(self, text: str, decision: ConversationFluencyDecision) -> str:
        if not decision.remove_redundant_bridge:
            return text
        fluent = self._BRIDGE_RE.sub("", text, count=1).strip()
        if not fluent or fluent == text.strip():
            return text
        return fluent[:1].upper() + fluent[1:]
