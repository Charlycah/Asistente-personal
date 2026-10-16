from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ConversationalMarkerKind(str, Enum):
    """Shape of the conversational opening detected in a user turn."""

    NONE = "none"
    PREFIX_SEQUENCE = "prefix_sequence"
    STANDALONE = "standalone"


@dataclass(frozen=True)
class ConversationalMarkerDecision:
    kind: ConversationalMarkerKind
    markers: tuple[str, ...] = ()
    substantive_text: str = ""

    @property
    def has_substantive_text(self) -> bool:
        return bool(self.substantive_text)


class ConversationalMarkerAnalyzer:
    """Separate harmless opening markers from the substantive request."""

    _MARKER_RE = re.compile(
        r"^\s*(?P<marker>bueno|a\s+ver|mir[aá]|veamos|entonces|"
        r"mmm+|eh+|ok(?:ay)?|dale|perfecto)\b[,.…:;\s-]*",
        re.IGNORECASE,
    )

    def evaluate(self, request_text: str) -> ConversationalMarkerDecision:
        remainder = request_text.strip()
        markers: list[str] = []

        while remainder:
            match = self._MARKER_RE.match(remainder)
            if match is None:
                break
            markers.append(self._normalize_marker(match.group("marker")))
            new_remainder = remainder[match.end() :].strip()
            if new_remainder == remainder:
                break
            remainder = new_remainder

        if not markers:
            return ConversationalMarkerDecision(
                kind=ConversationalMarkerKind.NONE,
                substantive_text=request_text.strip(),
            )
        if not remainder:
            return ConversationalMarkerDecision(
                kind=ConversationalMarkerKind.STANDALONE,
                markers=tuple(markers),
            )
        return ConversationalMarkerDecision(
            kind=ConversationalMarkerKind.PREFIX_SEQUENCE,
            markers=tuple(markers),
            substantive_text=remainder,
        )

    @staticmethod
    def _normalize_marker(marker: str) -> str:
        return " ".join(marker.casefold().split())
