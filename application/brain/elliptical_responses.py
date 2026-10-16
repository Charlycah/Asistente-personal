from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class EllipticalResponseKind(str, Enum):
    """Conversational reference expressed without repeating the full request."""

    NONE = "none"
    ORDINAL = "ordinal"
    NAMED_REFERENCE = "named_reference"
    DEMONSTRATIVE = "demonstrative"
    COLLECTIVE = "collective"
    NEGATIVE = "negative"


@dataclass(frozen=True)
class EllipticalResponseDecision:
    kind: EllipticalResponseKind
    cue: str | None = None
    reference_text: str = ""
    has_context: bool = False

    @property
    def is_elliptical(self) -> bool:
        return self.kind is not EllipticalResponseKind.NONE


class EllipticalResponseAnalyzer:
    """Recognize short contextual replies without resolving their reference."""

    _ORDINAL_RE = re.compile(
        r"^\s*(?P<cue>(?:la|el)\s+(?:primera|primero|segunda|segundo|"
        r"tercera|tercero))\s*[.!…]*\s*$",
        re.IGNORECASE,
    )
    _NAMED_REFERENCE_RE = re.compile(
        r"^\s*(?P<cue>(?:la|el)\s+de\s+(?P<reference>[^.!?]+?))"
        r"\s*[.!…]*\s*$",
        re.IGNORECASE,
    )
    _SIMPLE_CUES = {
        "esa": EllipticalResponseKind.DEMONSTRATIVE,
        "ese": EllipticalResponseKind.DEMONSTRATIVE,
        "esa misma": EllipticalResponseKind.DEMONSTRATIVE,
        "ese mismo": EllipticalResponseKind.DEMONSTRATIVE,
        "ambas": EllipticalResponseKind.COLLECTIVE,
        "ambos": EllipticalResponseKind.COLLECTIVE,
        "ninguna": EllipticalResponseKind.NEGATIVE,
        "ninguno": EllipticalResponseKind.NEGATIVE,
    }

    def evaluate(
        self,
        request_text: str,
        *,
        previous_turn: str | None = None,
    ) -> EllipticalResponseDecision:
        text = request_text.strip()
        has_context = bool(previous_turn)

        if match := self._ORDINAL_RE.fullmatch(text):
            cue = self._normalize(match.group("cue"))
            return EllipticalResponseDecision(
                kind=EllipticalResponseKind.ORDINAL,
                cue=cue,
                has_context=has_context,
            )

        if match := self._NAMED_REFERENCE_RE.fullmatch(text):
            cue = self._normalize(match.group("cue"))
            reference = match.group("reference").strip()
            return EllipticalResponseDecision(
                kind=EllipticalResponseKind.NAMED_REFERENCE,
                cue=cue,
                reference_text=reference,
                has_context=has_context,
            )

        normalized = self._normalize(text.strip(".!… "))
        kind = self._SIMPLE_CUES.get(normalized)
        if kind is not None:
            return EllipticalResponseDecision(
                kind=kind,
                cue=normalized,
                has_context=has_context,
            )

        return EllipticalResponseDecision(
            kind=EllipticalResponseKind.NONE,
            reference_text=text,
            has_context=has_context,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.casefold().split())
