from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from .governed_information_normalizer import (
    InformationVerificationStatus,
    NormalizedGovernedInformation,
    NormalizedInformationKind,
    RawGovernedInformation,
)
from .governed_information_sources import InformationRegion
from .governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryError,
    GovernedSourceQueryResult,
)
from .personal_interest_center import InterestTopic
from .relevance_evaluator import RelevanceDecision


class GovernedConversationalQueryStatus(StrEnum):
    SUCCEEDED = "succeeded"
    EMPTY = "empty"
    FAILED = "failed"


@dataclass(frozen=True)
class GovernedConversationalQuery:
    text: str
    query: GovernedSourceQuery

    def __post_init__(self) -> None:
        text = " ".join(self.text.split())
        if not text:
            raise ValueError("governed conversational query text cannot be empty")
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class GovernedConversationalInformation:
    raw: Mapping[str, object]
    normalized: NormalizedGovernedInformation
    relevance: RelevanceDecision


@dataclass(frozen=True)
class GovernedConversationalQueryResult:
    request: GovernedConversationalQuery
    status: GovernedConversationalQueryStatus
    source_result: GovernedSourceQueryResult
    items: tuple[GovernedConversationalInformation, ...]
    answer_text: str
    discarded_items: int = 0
    error: GovernedSourceQueryError | None = None


@dataclass(frozen=True)
class GovernedConversationalQuerySnapshot:
    schema_version: str
    authority: str
    explicit_queries_only: bool
    automatic_fetch_enabled: bool
    changes_cognitive_flow: bool


SCHEMA_VERSION = "m344.4"
AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"


def snapshot() -> GovernedConversationalQuerySnapshot:
    return GovernedConversationalQuerySnapshot(
        schema_version=SCHEMA_VERSION,
        authority=AUTHORITY,
        explicit_queries_only=True,
        automatic_fetch_enabled=False,
        changes_cognitive_flow=False,
    )


def raw_information_from_item(
    item: Mapping[str, object],
    query: GovernedSourceQuery,
) -> RawGovernedInformation:
    external_id = _required_text(item, "external_id")
    title = _required_text(item, "title")
    topics = _topics(item.get("topics"), query.topics)
    return RawGovernedInformation(
        source_id=query.source_id,
        external_id=external_id,
        title=title,
        topics=topics,
        kind=_enum_value(
            NormalizedInformationKind,
            item.get("information_kind"),
            NormalizedInformationKind.NEWS,
        ),
        verification=_enum_value(
            InformationVerificationStatus,
            item.get("verification"),
            InformationVerificationStatus.REPORTED,
        ),
        published_at=_datetime_or_none(item.get("published_at")),
        event_at=_datetime_or_none(item.get("event_at")),
        region=_enum_value(InformationRegion, item.get("region"), None),
        location=_optional_text(item.get("location")),
        is_free=_boolean(item.get("is_free"), default=True),
        time_sensitive=_boolean(item.get("time_sensitive"), default=False),
        importance=_importance(item.get("importance")),
        tags=_strings(item.get("tags")),
    )


def immutable_item(item: Mapping[str, object]) -> Mapping[str, object]:
    return MappingProxyType(dict(item))


def _required_text(item: Mapping[str, object], key: str) -> str:
    text = _optional_text(item.get(key))
    if text is None:
        raise ValueError(f"governed information item needs {key}")
    return text


def _optional_text(value: object) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).split())
    return text or None


def _datetime_or_none(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None


def _strings(value: object) -> tuple[str, ...]:
    if not isinstance(value, (tuple, list, frozenset, set)):
        return ()
    return tuple(
        text
        for element in value
        if (text := _optional_text(element)) is not None
    )


def _topics(
    value: object,
    fallback: frozenset[InterestTopic],
) -> frozenset[InterestTopic]:
    if not isinstance(value, (tuple, list, frozenset, set)):
        return fallback
    topics: set[InterestTopic] = set()
    for element in value:
        try:
            topics.add(InterestTopic(str(element)))
        except ValueError:
            continue
    return frozenset(topics) or fallback


def _enum_value(enum_type, value: object, default):
    if value is None:
        return default
    try:
        return enum_type(str(value))
    except ValueError:
        return default


def _boolean(value: object, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _importance(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        return 0
    return min(20, max(0, value))
