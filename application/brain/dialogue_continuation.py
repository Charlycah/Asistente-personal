from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class DialogueContinuationKind(str, Enum):
    """Bounded dialogue-continuation outcomes owned by the Brain."""

    NEW_TOPIC = "new_topic"
    CONTINUE_TOPIC = "continue_topic"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class DialogueContinuationDecision:
    kind: DialogueContinuationKind
    previous_turn_available: bool
    cue: str | None = None


class DialogueContinuationAnalyzer:
    """Detect whether a turn depends on a previous conversational topic.

    M321.1 deliberately detects only explicit, low-risk continuation cues. It
    does not resolve references, mutate memory, or route requests to engines.
    """

    _CONTINUATION_RE = re.compile(
        r"^\s*(?P<cue>"
        r"(?:y\s+)?(?:ma[nñ]ana|despu[eé]s|antes|ahora|el\s+otro|la\s+otra|"
        r"los\s+otros|las\s+otras|el\s+anterior|la\s+anterior|"
        r"en\s+deportes|sobre\s+eso)|"
        r"(?:y\s+)(?:qu[eé]|c[oó]mo|cu[aá]ndo|d[oó]nde|qui[eé]n)\b|"
        r"(?:segu[ií]|continu[aá]|ampli[aá]|contame\s+m[aá]s|decime\s+m[aá]s)\b"
        r")",
        re.IGNORECASE,
    )

    def evaluate(
        self,
        text: str,
        *,
        previous_turn: str | None = None,
    ) -> DialogueContinuationDecision:
        previous_available = bool(previous_turn and previous_turn.strip())
        candidate = text.lstrip("¿¡ ")
        match = self._CONTINUATION_RE.match(candidate)
        if match is None:
            return DialogueContinuationDecision(
                DialogueContinuationKind.NEW_TOPIC,
                previous_turn_available=previous_available,
            )
        cue = re.sub(r"\s+", " ", match.group("cue").strip()).casefold()
        if previous_available:
            return DialogueContinuationDecision(
                DialogueContinuationKind.CONTINUE_TOPIC,
                previous_turn_available=True,
                cue=cue,
            )
        return DialogueContinuationDecision(
            DialogueContinuationKind.UNRESOLVED,
            previous_turn_available=False,
            cue=cue,
        )
