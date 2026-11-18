"""Pure, conservative cross-domain conversational reference resolution.

This module does not read history, authorize access, or execute capabilities.
Callers must supply already-authorized, session-scoped antecedents.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class ContextDecision(str, Enum):
    CONTINUE = "CONTINUE"
    RESUME = "RESUME"
    TOPIC_CHANGE = "TOPIC_CHANGE"
    CLARIFY = "CLARIFY"
    UNRESOLVED = "UNRESOLVED"


class ContextDomain(str, Enum):
    LIBRARY = "library"
    DOCUMENTS = "documents"
    MUSIC = "music"
    DEVELOPMENT = "development"


@dataclass(frozen=True)
class ContextAntecedent:
    turn_id: str
    owner: str
    session_id: str
    domain: ContextDomain
    sequence: int
    provenance: str
    authorized: bool = True


@dataclass(frozen=True)
class ContextResolution:
    decision: ContextDecision
    domain: ContextDomain | None = None
    antecedent_turn_id: str | None = None
    reason: str = ""


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def _mentions(text: str, words: tuple[str, ...]) -> bool:
    return any(
        re.search(r"(?<!\w)" + re.escape(word) + r"(?!\w)", text)
        for word in words
    )


_DOMAIN_WORDS = {
    ContextDomain.LIBRARY: (
        "libro", "libros", "biblioteca", "novela", "novelas"
    ),
    ContextDomain.DOCUMENTS: (
        "documento", "documentos", "estudio", "estudios",
        "informe", "informes"
    ),
    ContextDomain.MUSIC: (
        "musica", "obra musical", "obras musicales",
        "pinacoteca", "compositor", "compositores"
    ),
    ContextDomain.DEVELOPMENT: (
        "codigo", "programacion", "modulo", "modulos",
        "repositorio", "proyecto roby"
    ),
}

_RESUME = re.compile(
    r"\b(?:volvamos|volveme|retomemos|regresemos|"
    r"sigamos con|continuemos con|regresemos a)\b"
)
_CHANGE = re.compile(
    r"\b(?:cambiemos de tema|hablemos de otra cosa|"
    r"pasemos a otro tema)\b"
)
_FOLLOW = re.compile(
    r"\b(?:y los|y las|y cuales|y que|otros|otras|"
    r"mas recientes|mas nuevas|el primero|la primera|"
    r"el segundo|la segunda|ese|esa|esos|esas|"
    r"del mismo|de la misma|que dice|seguimos con aquella|"
    r"como lo mejorarias|y ahora)\b"
)


def resolve_cross_domain_reference(
    text: str,
    authorized_turns: Iterable[ContextAntecedent],
    *,
    owner: str,
    session_id: str,
) -> ContextResolution:
    """Select a safe antecedent; never infer permission or execute an action.

    Input ordering is irrelevant; sequence identifies recency.
    Conflicting identities for the same sequence are ambiguous.
    """
    if not isinstance(text, str) or not text.strip() or not owner or not session_id:
        return ContextResolution(
            ContextDecision.UNRESOLVED, reason="missing_input"
        )

    folded = _fold(text)
    if _CHANGE.search(folded):
        return ContextResolution(
            ContextDecision.TOPIC_CHANGE,
            reason="explicit_topic_change",
        )

    turns = [
        turn for turn in authorized_turns
        if isinstance(turn, ContextAntecedent)
        and turn.authorized is True
        and isinstance(turn.owner, str)
        and isinstance(turn.turn_id, str)
        and isinstance(turn.provenance, str)
        and turn.owner.casefold() == owner.casefold()
        and turn.session_id == session_id
        and isinstance(turn.domain, ContextDomain)
        and isinstance(turn.sequence, int)
        and not isinstance(turn.sequence, bool)
        and turn.sequence > 0
        and bool(turn.turn_id.strip())
        and bool(turn.provenance.strip())
    ]

    domains = [
        domain for domain, words in _DOMAIN_WORDS.items()
        if _mentions(folded, words)
    ]
    resume = bool(_RESUME.search(folded))

    if len(domains) > 1:
        return ContextResolution(
            ContextDecision.CLARIFY, reason="multiple_domains"
        )

    if not turns:
        return ContextResolution(
            ContextDecision.UNRESOLVED,
            reason="no_authorized_antecedent",
        )

    if resume and not domains:
        return ContextResolution(
            ContextDecision.CLARIFY,
            reason="resume_domain_unspecified",
        )

    if domains:
        if not resume and not _FOLLOW.search(folded):
            return ContextResolution(
                ContextDecision.UNRESOLVED,
                reason="new_domain_request",
            )

        domain = domains[0]
        matching = [turn for turn in turns if turn.domain == domain]

        if not matching:
            return ContextResolution(
                ContextDecision.UNRESOLVED,
                reason="domain_not_in_history",
            )

        decision = (
            ContextDecision.RESUME
            if resume else ContextDecision.CONTINUE
        )
    else:
        if not _FOLLOW.search(folded):
            return ContextResolution(
                ContextDecision.UNRESOLVED,
                reason="not_a_contextual_reference",
            )

        latest_sequence = max(turn.sequence for turn in turns)
        latest = [
            turn for turn in turns
            if turn.sequence == latest_sequence
        ]

        if len({turn.domain for turn in latest}) != 1:
            return ContextResolution(
                ContextDecision.CLARIFY,
                reason="ambiguous_latest_domain",
            )

        domain = latest[0].domain
        matching = latest
        decision = ContextDecision.CONTINUE

    max_sequence = max(turn.sequence for turn in matching)
    candidates = [
        turn for turn in matching
        if turn.sequence == max_sequence
    ]

    if len({turn.turn_id for turn in candidates}) != 1:
        return ContextResolution(
            ContextDecision.CLARIFY,
            reason="ambiguous_antecedent",
        )

    return ContextResolution(
        decision, domain, candidates[0].turn_id,
        "authorized_antecedent",
    )
