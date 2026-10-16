from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Iterable, Mapping

from .governed_conversational_request_mode import GovernedConversationalRequestMode
from .governed_information_sources import (
    GovernedInformationSource,
    GovernedInformationSources,
    InformationRegion,
    InformationSourceCapability,
    InformationSourceStatus,
)
from .governed_source_query import GovernedSourceQuery, GovernedSourceQueryOrder
from .personal_interest_center import InterestTopic


class GovernedConversationalSourceSelectionStatus(StrEnum):
    SELECTED = "selected"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class GovernedConversationalSourceSelectionRequest:
    text: str
    topics: frozenset[InterestTopic]
    query_text: str | None = None
    limit: int = 10
    region: InformationRegion | None = None
    published_after: datetime | None = None
    published_before: datetime | None = None
    timeout_seconds: float = 10.0
    parameters: Mapping[str, str] | None = None
    order: GovernedSourceQueryOrder | None = None
    mode: GovernedConversationalRequestMode = (
        GovernedConversationalRequestMode.TOPIC_CONSTRAINED
    )

    def __post_init__(self) -> None:
        text = " ".join(self.text.split())
        query_text = self.query_text.strip() if self.query_text else None
        if not text:
            raise ValueError("governed source selection text cannot be empty")
        if self.order is not None and not isinstance(
            self.order, GovernedSourceQueryOrder
        ):
            raise ValueError("governed source selection order is invalid")
        if (
            self.mode is GovernedConversationalRequestMode.TOPIC_CONSTRAINED
            and not self.topics
        ):
            raise ValueError("governed source selection needs at least one topic")
        if (
            self.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
            and query_text is None
        ):
            raise ValueError("open visual subject needs query text")
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "query_text", query_text)


@dataclass(frozen=True)
class GovernedConversationalSourceSelection:
    request: GovernedConversationalSourceSelectionRequest
    status: GovernedConversationalSourceSelectionStatus
    source: GovernedInformationSource | None
    query: GovernedSourceQuery | None
    eligible_sources: tuple[str, ...]


@dataclass(frozen=True)
class GovernedConversationalSourceSelectionSnapshot:
    schema_version: str
    authority: str
    registered_sources_only: bool
    deterministic_selection: bool
    automatic_fetch_enabled: bool
    changes_cognitive_flow: bool


class GovernedConversationalSourceSelector:
    """Pure source selection owned by the official conversation gateway."""

    SCHEMA_VERSION = "m344.5"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(self, sources: GovernedInformationSources) -> None:
        self._sources = sources

    @property
    def snapshot(self) -> GovernedConversationalSourceSelectionSnapshot:
        return GovernedConversationalSourceSelectionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            registered_sources_only=True,
            deterministic_selection=True,
            automatic_fetch_enabled=False,
            changes_cognitive_flow=False,
        )

    def select(
        self,
        request: GovernedConversationalSourceSelectionRequest,
        *,
        registered_sources: Iterable[str],
    ) -> GovernedConversationalSourceSelection:
        registered = {
            source_id.strip().casefold()
            for source_id in registered_sources
            if source_id.strip()
        }
        eligible = tuple(
            source
            for source in self._sources.sources.values()
            if self._is_eligible(source, request, registered)
        )
        ranked = tuple(sorted(eligible, key=self._ranking_key))
        eligible_ids = tuple(source.source_id for source in ranked)
        if not ranked:
            return GovernedConversationalSourceSelection(
                request=request,
                status=GovernedConversationalSourceSelectionStatus.UNAVAILABLE,
                source=None,
                query=None,
                eligible_sources=(),
            )

        source = ranked[0]
        query = GovernedSourceQuery(
            source_id=source.source_id,
            topics=request.topics,
            query_text=request.query_text,
            limit=request.limit,
            region=request.region,
            published_after=request.published_after,
            published_before=request.published_before,
            timeout_seconds=request.timeout_seconds,
            parameters=request.parameters,
            order=request.order,
            mode=request.mode,
        )
        return GovernedConversationalSourceSelection(
            request=request,
            status=GovernedConversationalSourceSelectionStatus.SELECTED,
            source=source,
            query=query,
            eligible_sources=eligible_ids,
        )

    @staticmethod
    def _is_eligible(
        source: GovernedInformationSource,
        request: GovernedConversationalSourceSelectionRequest,
        registered: set[str],
    ) -> bool:
        if source.source_id not in registered:
            return False
        if source.status is not InformationSourceStatus.DECLARED:
            return False
        if (
            request.order is GovernedSourceQueryOrder.NEWEST_FIRST
            and InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY
            not in source.capabilities
        ):
            return False
        if request.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT:
            return (
                InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY
                in source.capabilities
            )
        if not request.topics.issubset(source.topics):
            return False
        if request.region is None:
            return True
        regions = source.classification.regions
        return request.region in regions or InformationRegion.GLOBAL in regions

    @staticmethod
    def _ranking_key(source: GovernedInformationSource) -> tuple[int, int, str]:
        return (
            -source.classification.confidence,
            len(source.topics),
            source.source_id,
        )
