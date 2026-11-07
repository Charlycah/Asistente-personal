"""Interpret contextual follow-ups without accessing conversation history."""

import re
import unicodedata
from dataclasses import dataclass
from enum import Enum


class FollowUpIntent(str, Enum):
    CONTINUE = "continue"
    REORDER = "reorder"
    RESTRICT = "restrict"
    TOPIC_CHANGE = "topic_change"
    UNDETERMINED = "undetermined"


@dataclass(frozen=True)
class FollowUpInterpretation:
    intent: FollowUpIntent
    newest_first: bool = False
    exclusion: str | None = None
    inclusion: str | None = None


def _normalize(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(
        character
        for character in folded
        if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


def interpret_contextual_follow_up(text: str) -> FollowUpInterpretation:
    normalized = _normalize(text)

    if not normalized:
        return FollowUpInterpretation(FollowUpIntent.UNDETERMINED)

    if re.search(
        r"\b(cambiemos de tema|hablemos de otra cosa|"
        r"ahora hablemos de|pasemos a otro tema)\b",
        normalized,
    ):
        return FollowUpInterpretation(FollowUpIntent.TOPIC_CHANGE)

    freshness = bool(
        re.search(
            r"\b(?:mas recientes|mas nuevas|ultimas|"
            r"mas actuales|recientes)\b",
            normalized,
        )
    )

    exclusion = re.search(
        r"\bsin (?:los |las |el |la )?"
        r"([a-z0-9][a-z0-9 ]{1,60}?)"
        r"(?=\s*(?:,|\.|\?|!|$|\by las mas\b|\by los mas\b))",
        normalized,
    )

    inclusion = re.search(
        r"\b(?:solo|solamente|unicamente) "
        r"([a-z0-9][a-z0-9 ]{1,60}?)"
        r"(?=\s*(?:,|\.|\?|!|$))",
        normalized,
    )

    if exclusion or inclusion:
        return FollowUpInterpretation(
            FollowUpIntent.RESTRICT,
            newest_first=freshness,
            exclusion=(
                exclusion.group(1).strip() if exclusion else None
            ),
            inclusion=(
                inclusion.group(1).strip() if inclusion else None
            ),
        )

    if freshness:
        return FollowUpInterpretation(
            FollowUpIntent.REORDER,
            newest_first=True,
        )

    continuation = re.search(
        r"\b(?:tenes mas|tienes mas|mostrame mas|"
        r"muestrame mas|mostrar mas|"
        r"algunas mas|algunos mas)\b",
        normalized,
    )

    standalone_reference = re.search(
        r"\b(?:otras|otros)\b"
        r"(?=\s*(?:\?|!|\.|,|$|\bpero\b|\by\b))",
        normalized,
    )

    if continuation or standalone_reference:
        return FollowUpInterpretation(FollowUpIntent.CONTINUE)

    return FollowUpInterpretation(FollowUpIntent.UNDETERMINED)
