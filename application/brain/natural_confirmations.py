from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class NaturalConfirmationKind(str, Enum):
    """Shape of an affirmative conversational turn."""

    NONE = "none"
    STANDALONE = "standalone"
    PREFIXED_REQUEST = "prefixed_request"


@dataclass(frozen=True)
class NaturalConfirmationDecision:
    kind: NaturalConfirmationKind
    cue: str | None = None
    substantive_text: str = ""
    has_context: bool = False

    @property
    def is_confirmation(self) -> bool:
        return self.kind is not NaturalConfirmationKind.NONE


class NaturalConfirmationAnalyzer:
    """Recognize natural affirmations without inferring an action."""

    _CONFIRMATION_RE = re.compile(
        r"^\s*(?P<cue>s[ií]|claro|dale|ok(?:ay)?|exacto|correcto|"
        r"perfecto|de acuerdo|tal cual|esa misma)\b[,.…:;!\s-]*",
        re.IGNORECASE,
    )

    def evaluate(
        self,
        request_text: str,
        *,
        previous_turn: str | None = None,
    ) -> NaturalConfirmationDecision:
        text = request_text.strip()
        match = self._CONFIRMATION_RE.match(text)
        if match is None:
            return NaturalConfirmationDecision(
                kind=NaturalConfirmationKind.NONE,
                substantive_text=text,
                has_context=bool(previous_turn),
            )

        cue = " ".join(match.group("cue").casefold().split())
        remainder = text[match.end() :].strip()
        if remainder:
            return NaturalConfirmationDecision(
                kind=NaturalConfirmationKind.PREFIXED_REQUEST,
                cue=cue,
                substantive_text=remainder,
                has_context=bool(previous_turn),
            )
        return NaturalConfirmationDecision(
            kind=NaturalConfirmationKind.STANDALONE,
            cue=cue,
            has_context=bool(previous_turn),
        )
