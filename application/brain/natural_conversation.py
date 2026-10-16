from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class NaturalConversationKind(str, Enum):
    """Natural turn shapes recognized without changing user intent."""

    DIRECT = "direct"
    DISCOURSE_MARKER = "discourse_marker"
    CONFIRMATION = "confirmation"
    ELLIPTICAL = "elliptical"


@dataclass(frozen=True)
class NaturalConversationDecision:
    kind: NaturalConversationKind
    cue: str | None = None


class NaturalConversationAnalyzer:
    """Recognize common conversational forms while preserving semantics."""

    _MARKER_RE = re.compile(
        r"^\s*(?:bueno|a ver|mmm+|eh+|ok(?:ay)?|dale|perfecto)\b[,.…\s-]*",
        re.IGNORECASE,
    )
    _CONFIRMATION_RE = re.compile(
        r"^\s*(?:s[ií]|dale|ok(?:ay)?|exacto|correcto|esa misma)\s*[.!…]*\s*$",
        re.IGNORECASE,
    )
    _ELLIPTICAL_RE = re.compile(
        r"^\s*(?:la|el)\s+(?:primera|primero|segunda|segundo|tercera|tercero|"
        r"de\s+[^.!?]+)|^\s*(?:esa|ese|ninguna|ninguno|ambas|ambos)\s*[.!…]*\s*$",
        re.IGNORECASE,
    )

    def evaluate(self, request_text: str) -> NaturalConversationDecision:
        text = request_text.strip()
        if confirmation := self._CONFIRMATION_RE.match(text):
            return NaturalConversationDecision(
                kind=NaturalConversationKind.CONFIRMATION,
                cue=confirmation.group(0).strip().casefold(),
            )
        if elliptical := self._ELLIPTICAL_RE.match(text):
            return NaturalConversationDecision(
                kind=NaturalConversationKind.ELLIPTICAL,
                cue=elliptical.group(0).strip().casefold(),
            )
        if marker := self._MARKER_RE.match(text):
            return NaturalConversationDecision(
                kind=NaturalConversationKind.DISCOURSE_MARKER,
                cue=marker.group(0).strip(" ,.……-").casefold(),
            )
        return NaturalConversationDecision(kind=NaturalConversationKind.DIRECT)
