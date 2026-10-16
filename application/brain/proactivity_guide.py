from __future__ import annotations

from .proactivity import ProactivityDecision


class ProactivityGuide:
    """Append one optional next step while preserving the completed answer."""

    def apply(self, text: str, decision: ProactivityDecision) -> str:
        if not decision.available or decision.suggestion is None:
            return text
        return f"{text.rstrip()}\n\n{decision.suggestion}"
