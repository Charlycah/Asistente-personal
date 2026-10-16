from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class DialogueAmbiguityKind(str, Enum):
    """Bounded ambiguity outcomes owned by the Brain."""

    CLEAR = "clear"
    AMBIGUOUS_REFERENCE = "ambiguous_reference"


@dataclass(frozen=True)
class DialogueAmbiguityDecision:
    kind: DialogueAmbiguityKind
    previous_turn_available: bool
    cue: str | None = None


class DialogueAmbiguityAnalyzer:
    """Detect explicit references that lack enough information to resolve safely.

    M321.2 only exposes a conservative ambiguity signal. It does not ask a
    clarification question, rewrite the request, mutate context, or alter
    engine routing.
    """

    _AMBIGUOUS_REFERENCE_RE = re.compile(
        r"^\s*(?P<cue>"
        r"(?:y\s+)?(?:el\s+otro|la\s+otra|los\s+otros|las\s+otras|"
        r"el\s+anterior|la\s+anterior|ese|esa|esos|esas|eso|aquello)|"
        r"(?:cu[aá]l|cu[aá]les)\s+(?:de\s+)?(?:esos|esas|ellos|ellas)|"
        r"(?:a\s+)?(?:cu[aá]l|qui[eé]n)\s+te\s+refer[ií]s"
        r")\s*[.!?¿¡]*\s*$",
        re.IGNORECASE,
    )

    def evaluate(
        self,
        text: str,
        *,
        previous_turn: str | None = None,
    ) -> DialogueAmbiguityDecision:
        previous_available = bool(previous_turn and previous_turn.strip())
        candidate = text.lstrip("¿¡ ")
        match = self._AMBIGUOUS_REFERENCE_RE.match(candidate)
        if match is None:
            return DialogueAmbiguityDecision(
                DialogueAmbiguityKind.CLEAR,
                previous_turn_available=previous_available,
            )
        cue = re.sub(r"\s+", " ", match.group("cue").strip()).casefold()
        return DialogueAmbiguityDecision(
            DialogueAmbiguityKind.AMBIGUOUS_REFERENCE,
            previous_turn_available=previous_available,
            cue=cue,
        )
