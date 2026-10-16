from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class ConversationalTurnKind(str, Enum):
    """Stable, presentation-agnostic conversational categories."""

    GREETING = "greeting"
    CLOSURE = "closure"
    CONTINUATION = "continuation"
    DIRECT_REQUEST = "direct_request"
    SOCIAL = "social"


@dataclass(frozen=True)
class ConversationalCriterionDecision:
    kind: ConversationalTurnKind
    preserve_response_greeting: bool = False
    closure_response: str | None = None


class ConversationalCriterion:
    """Classifies a turn without routing capabilities or mutating context.

    M320.1 keeps the criterion deliberately small: it supplies the Brain's
    conversational judgment to presentation while engines retain ownership of
    capability routing and response semantics.
    """

    _GREETING_RE = re.compile(
        r"^\s*(?:hola(?:\s+roby)?|buen(?:os|as)\s+"
        r"(?:d[ií]as|tardes|noches))(?:[, ]+[¿¡]?c[oó]mo\s+"
        r"(?:te\s+va|est[aá]s|andas))?[.!?¿¡ ]*$",
        re.IGNORECASE,
    )
    _THANKS_RE = re.compile(
        r"^\s*(?:no[, ]+)?(?:roby[, ]+)?gracias"
        r"(?:[, ]+(?:roby|era eso|eso era todo|por ahora nada m[aá]s))*"
        r"[.!?]*\s*$",
        re.IGNORECASE,
    )
    _GOODBYE_RE = re.compile(
        r"^\s*(?:(?:bueno|listo)[, ]+)?(?:chau|adi[oó]s|hasta luego|"
        r"nos vemos|hasta ma[nñ]ana)(?:[, ]+roby)?[.!?]*\s*$",
        re.IGNORECASE,
    )
    _CONTINUATION_RE = re.compile(
        r"^\s*(?:(?:y\s+)?(?:s[ií]|dale|bueno)(?:\b|[, ])|"
        r"(?:segu[ií]|continu[aá]|ampli[aá]|explicame|expl[ií]came)\b)",
        re.IGNORECASE,
    )
    _GREETING_PREFIX_RE = re.compile(
        r"^\s*(?:hola(?:\s+roby)?|buen(?:os|as)\s+"
        r"(?:d[ií]as|tardes|noches))(?:[,;:]+|\s+-\s+)\s*"
        r"(?P<remainder>.+)$",
        re.IGNORECASE,
    )
    _DEFERRAL_TERMS = (
        "después seguimos",
        "despues seguimos",
        "luego seguimos",
        "hablamos después",
        "hablamos despues",
        "seguimos más tarde",
        "seguimos mas tarde",
    )
    _COURTESY_REQUEST_RE = re.compile(
        r"^\s*(?:gracias|por favor|dale|bueno)(?:[, ]+roby)?[,;:]?\s+"
        r"(?P<request>.+)$",
        re.IGNORECASE,
    )
    _PRIORITY_PREFIX_RE = re.compile(
        r"^(?:(?:hola(?:\s+roby)?|buen(?:os|as)\s+"
        r"(?:d[ií]as|tardes|noches))|(?:gracias|por favor|dale|bueno)"
        r"(?:\s+roby)?|(?:y\s+)?(?:ahora|entonces|adem[aá]s)|pero)"
        r"(?:[,;:]+|\s+-\s+|\s+)+",
        re.IGNORECASE,
    )
    _DIRECT_MARKERS = (
        "qué",
        "que",
        "cómo",
        "como",
        "cuándo",
        "cuando",
        "dónde",
        "donde",
        "por qué",
        "porque",
        "decime",
        "dame",
        "mostrame",
        "buscá",
        "busca",
        "hacé",
        "hace",
    )

    def evaluate(self, text: str) -> ConversationalCriterionDecision:
        normalized = re.sub(r"\s+", " ", text.strip()).casefold()
        if not normalized:
            return ConversationalCriterionDecision(ConversationalTurnKind.SOCIAL)
        if self._GREETING_RE.match(text):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.GREETING,
                preserve_response_greeting=True,
            )
        greeting_request = self._GREETING_PREFIX_RE.match(text)
        if greeting_request and self._looks_like_direct_request(
            greeting_request.group("remainder")
        ):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.DIRECT_REQUEST
            )
        courtesy_request = self._COURTESY_REQUEST_RE.match(text)
        if courtesy_request and self._looks_like_direct_request(
            courtesy_request.group("request")
        ):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.DIRECT_REQUEST
            )
        if self._THANKS_RE.match(text):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.CLOSURE,
                closure_response="De nada.",
            )
        if self._GOODBYE_RE.match(text):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.CLOSURE,
                closure_response="Hasta luego.",
            )
        if any(term in normalized for term in self._DEFERRAL_TERMS):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.CLOSURE,
                closure_response="Perfecto. Hablamos después.",
            )
        if self._CONTINUATION_RE.match(text):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.CONTINUATION
            )
        if self._looks_like_direct_request(text):
            return ConversationalCriterionDecision(
                ConversationalTurnKind.DIRECT_REQUEST
            )
        return ConversationalCriterionDecision(ConversationalTurnKind.SOCIAL)

    def _looks_like_direct_request(self, text: str) -> bool:
        normalized = re.sub(r"\s+", " ", text.strip()).casefold()
        candidates = [normalized]
        candidates.extend(
            segment.strip()
            for segment in re.split(r"[,;:]|\bpero\b", normalized)
            if segment.strip()
        )

        for candidate in candidates:
            prioritized = candidate
            while True:
                stripped = self._PRIORITY_PREFIX_RE.sub("", prioritized, count=1)
                if stripped == prioritized:
                    break
                prioritized = stripped.strip()
            prioritized = prioritized.lstrip("¿¡ ")
            if "?" in prioritized or any(
                prioritized.startswith(marker) for marker in self._DIRECT_MARKERS
            ):
                return True
        return False
