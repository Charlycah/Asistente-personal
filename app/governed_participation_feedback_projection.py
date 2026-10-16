from __future__ import annotations

import re
import unicodedata

from core.living_conversation import (
    ConversationalFeedbackOrigin,
    ConversationalFeedbackSignal,
    ConversationalFeedbackSignalKind,
)


class GovernedParticipationFeedbackProjection:
    """Project bounded participation feedback into the existing M101 contract."""

    _MINIMUM_CONFIDENCE = 0.55
    _PARTICIPATION = frozenset(
        {
            "habla",
            "hablar",
            "interveni",
            "intervenir",
            "opina",
            "opinar",
            "participa",
            "participar",
            "participes",
        }
    )
    _REDUCE = frozenset(
        {
            "callado",
            "callate",
            "menos",
            "para",
            "silencio",
        }
    )
    _ENCOURAGE = frozenset(
        {
            "dale",
            "mas",
        }
    )
    _MAINTAIN = frozenset(
        {
            "asi",
            "bien",
            "segui",
            "seguir",
        }
    )

    def project(
        self,
        *,
        text: str,
        confidence: float,
    ) -> ConversationalFeedbackSignal:
        """Return only an existing M101 signal; ambiguous evidence fails closed."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("feedback confidence must be between 0 and 1")
        normalized = self._normalize(text)
        if confidence < self._MINIMUM_CONFIDENCE or not normalized:
            return self._no_signal(confidence)

        tokens = frozenset(normalized.split())
        if not tokens.intersection(self._PARTICIPATION):
            return self._no_signal(confidence)

        reduce = bool(tokens.intersection(self._REDUCE))
        encourage = bool(tokens.intersection(self._ENCOURAGE))
        maintain = bool(tokens.intersection(self._MAINTAIN))

        # Direction must be unambiguous. Participation words alone are evidence
        # of topic, not evidence of the requested conversational adjustment.
        if reduce and not encourage:
            kind = ConversationalFeedbackSignalKind.DISENGAGEMENT
        elif encourage and not reduce:
            kind = ConversationalFeedbackSignalKind.DEEPENING
        elif maintain and not reduce and not encourage:
            kind = ConversationalFeedbackSignalKind.ACCEPTANCE
        else:
            return self._no_signal(confidence)

        return ConversationalFeedbackSignal(
            kind=kind,
            origin=ConversationalFeedbackOrigin.EXPLICIT,
            confidence=confidence,
            evidence=text.strip(),
        )

    @staticmethod
    def _normalize(text: str) -> str:
        decomposed = unicodedata.normalize("NFKD", text.casefold())
        ascii_text = "".join(
            char for char in decomposed if not unicodedata.combining(char)
        )
        return " ".join(re.findall(r"[a-z0-9]+", ascii_text))

    @staticmethod
    def _no_signal(confidence: float) -> ConversationalFeedbackSignal:
        return ConversationalFeedbackSignal(
            kind=ConversationalFeedbackSignalKind.NO_SIGNAL,
            origin=ConversationalFeedbackOrigin.EXPLICIT,
            confidence=confidence,
            evidence="",
        )
