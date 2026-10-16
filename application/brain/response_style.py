from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ResponseStyleKind(str, Enum):
    """Stable response-style preferences recognized by the Brain."""

    BALANCED = "balanced"
    CONCISE = "concise"
    DETAILED = "detailed"


@dataclass(frozen=True)
class ResponseStyleDecision:
    kind: ResponseStyleKind
    cue: str | None = None


class ResponseStyleAnalyzer:
    """Detect explicit response-style requests without changing semantics."""

    _CONCISE_RE = re.compile(
        r"\b(?:breve|corto|corta|resumido|resumida|resumime|"
        r"sin detalles|en pocas palabras)\b",
        re.IGNORECASE,
    )
    _DETAILED_RE = re.compile(
        r"\b(?:detallado|detallada|en detalle|explicame|expl[ií]came|"
        r"paso a paso|profundiz[áa]|con detalles)\b",
        re.IGNORECASE,
    )

    def evaluate(self, request_text: str) -> ResponseStyleDecision:
        text = request_text.strip()
        concise = self._CONCISE_RE.search(text)
        detailed = self._DETAILED_RE.search(text)

        if concise and not detailed:
            return ResponseStyleDecision(
                kind=ResponseStyleKind.CONCISE,
                cue=concise.group(0).casefold(),
            )
        if detailed:
            return ResponseStyleDecision(
                kind=ResponseStyleKind.DETAILED,
                cue=detailed.group(0).casefold(),
            )
        return ResponseStyleDecision(kind=ResponseStyleKind.BALANCED)
