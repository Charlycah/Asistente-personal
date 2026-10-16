from __future__ import annotations

import re

from application.brain.response_style import (
    ResponseStyleDecision,
    ResponseStyleKind,
)


class ResponseStyleGuide:
    """Apply bounded presentation changes while preserving answer content."""

    _TRAILING_OFFER_RE = re.compile(
        r"(?:\n\n|\s+)(?:si quer[eé]s|si te sirve|puedo tambi[eé]n)"
        r"[^.!?]*(?:[.!?]+)?\s*$",
        re.IGNORECASE,
    )

    def apply(self, text: str, decision: ResponseStyleDecision) -> str:
        if decision.kind is not ResponseStyleKind.CONCISE:
            return text
        concise = self._TRAILING_OFFER_RE.sub("", text).strip()
        return concise or text
