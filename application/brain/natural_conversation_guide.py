from __future__ import annotations

import re

from .natural_conversation import (
    NaturalConversationDecision,
    NaturalConversationKind,
)


class NaturalConversationGuide:
    """Remove only redundant acknowledgements from visible responses."""

    _ACKNOWLEDGEMENT_RE = re.compile(
        r"^\s*(?:perfecto|claro|bien|de acuerdo|dale)[.!,:;\s-]+",
        re.IGNORECASE,
    )

    def apply(self, text: str, decision: NaturalConversationDecision) -> str:
        if decision.kind not in {
            NaturalConversationKind.DISCOURSE_MARKER,
            NaturalConversationKind.CONFIRMATION,
        }:
            return text
        natural = self._ACKNOWLEDGEMENT_RE.sub("", text, count=1).strip()
        return natural or text
