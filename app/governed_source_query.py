from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from .governed_conversational_request_mode import GovernedConversationalRequestMode
from .governed_information_sources import (
    GovernedInformationSource,
    GovernedInformationSources,
    InformationRegion,
    InformationSourceCapability,
)
from .personal_interest_center import InterestTopic


class GovernedSourceQueryOrder(StrEnum):
    NEWEST_FIRST = "newest_first"


class GovernedSourceQueryStatus(StrEnum):
    PREPARED = "prepared"
    SUCCEEDED = "succeeded"
    EMPTY = "empty"
    REJECTED = "rejected"
    FAILED = "failed"


class GovernedSourceQueryErrorKind(StrEnum):
    UNKNOWN_SOURCE = "unknown_source"
    SOURCE_DISABLED = "source_disabled"
    UNDECLARED_TOPIC = "undeclared_topic"
    INVALID_LIMIT = "invalid_limit"
    INVALID_TIMEOUT = "invalid_timeout"
    INVALID_TIME_WINDOW = "invalid_time_window"
    EXECUTION_UNAVAILABLE = "execution_unavailable"


@dataclass(frozen=True)
class GovernedSourceQuery:
    source_id: str
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
        source_id = self.source_id.strip()
        query_text = self.query_text.strip() if self.query_text else None
        if not source_id:
            raise ValueError("governed source query source id cannot be empty")
        if (
            self.mode is GovernedConversationalRequestMode.TOPIC_CONSTRAINED
            and not self.topics
        ):
            raise ValueError("governed source query needs at least one topic")
        if (
            self.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
            and query_text is None
        ):
            raise ValueError("open visual subject query needs query text")
        if self.order is not None and not isinstance(
            self.order, GovernedSourceQueryOrder
        ):
            raise ValueError("governed source query order is invalid")
        if not 1 <= self.limit <= 100:
            raise ValueError("governed source query limit must be between 1 and 100")
        if not 0 < self.timeout_seconds <= 60:
            raise ValueError(
                "governed source query timeout must be greater than 0 and at most 60"
            )
        published_after = _as_utc(self.published_after)
        published_before = _as_utc(self.published_before)
        if (
            published_after is not None
            and published_before is not None
            and published_after > published_before
        ):
            raise ValueError("governed source query time window is invalid")
        parameters = MappingProxyType(
            {
                str(key).strip(): str(value).strip()
                for key, value in (self.parameters or {}).items()
                if str(key).strip()
            }
        )
        object.__setattr__(self, "source_id", source_id.casefold())
        object.__setattr__(self, "query_text", query_text)
        object.__setattr__(self, "published_after", published_after)
        object.__setattr__(self, "published_before", published_before)
        object.__setattr__(self, "parameters", parameters)


@dataclass(frozen=True)
class GovernedSourceQueryError:
    kind: GovernedSourceQueryErrorKind
    message: str
    retryable: bool = False


@dataclass(frozen=True)
class GovernedSourceQueryResponse:
    source_id: str
    status: GovernedSourceQueryStatus
    raw_items: tuple[Mapping[str, object], ...] = ()
    received_at: datetime | None = None
    error: GovernedSourceQueryError | None = None

    def __post_init__(self) -> None:
        if not self.source_id.strip():
            raise ValueError("governed source response source id cannot be empty")
        if self.status is GovernedSourceQueryStatus.FAILED and self.error is None:
            raise ValueError("failed governed source response needs an error")
        if (
            self.status is not GovernedSourceQueryStatus.FAILED
            and self.error is not None
        ):
            raise ValueError(
                "only failed governed source responses may include an error"
            )
        object.__setattr__(self, "source_id", self.source_id.strip().casefold())
        object.__setattr__(self, "received_at", _as_utc(self.received_at))
        object.__setattr__(
            self,
            "raw_items",
            tuple(MappingProxyType(dict(item)) for item in self.raw_items),
        )


@dataclass(frozen=True)
class GovernedSourceQueryResult:
    query: GovernedSourceQuery
    source: GovernedInformationSource
    status: GovernedSourceQueryStatus = GovernedSourceQueryStatus.PREPARED
    response: GovernedSourceQueryResponse | None = None
    execution_id: str = ""

    def __post_init__(self) -> None:
        execution_id = self.execution_id.strip()
        if self.response is None and execution_id:
            raise ValueError("prepared governed source query cannot have execution id")
        if execution_id and len(execution_id) != 64:
            raise ValueError("governed source execution id must be sha256")
        object.__setattr__(self, "execution_id", execution_id)

    @property
    def execution_enabled(self) -> bool:
        return self.response is not None


@dataclass(frozen=True)
class GovernedSourceQueryContractSnapshot:
    schema_version: str
    authority: str
    execution_enabled: bool
    network_enabled: bool
    max_limit: int
    max_timeout_seconds: float


class GovernedSourceQueryContract:
    """Canonical query contract; validates intent but never executes I/O."""

    SCHEMA_VERSION = "m344.0"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"

    def __init__(self, sources: GovernedInformationSources) -> None:
        self._sources = sources

    def admit_non_default_source(self, source: GovernedInformationSource) -> None:
        """Extend the owned runtime registry without changing module defaults."""
        self._sources.admit_non_default(source)

    def source_for(self, source_id: str) -> GovernedInformationSource:
        """Resolve a source through the contract-owned canonical registry."""
        return self._sources.source_for(source_id)

    @property
    def snapshot(self) -> GovernedSourceQueryContractSnapshot:
        return GovernedSourceQueryContractSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            execution_enabled=False,
            network_enabled=False,
            max_limit=100,
            max_timeout_seconds=60.0,
        )

    def prepare(self, query: GovernedSourceQuery) -> GovernedSourceQueryResult:
        source = self._sources.source_for(query.source_id)
        if source.status.value != "declared":
            raise ValueError("governed information source is disabled")
        if query.mode is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT:
            if (
                InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY
                not in source.capabilities
            ):
                raise ValueError(
                    "governed source lacks open visual subject capability"
                )
        elif not query.topics.issubset(source.topics):
            raise ValueError("governed source query contains undeclared source topics")
        if (
            query.order is GovernedSourceQueryOrder.NEWEST_FIRST
            and InformationSourceCapability.EXTERNAL_IMAGE_NEWEST_FIRST_QUERY
            not in source.capabilities
        ):
            raise ValueError(
                "governed source lacks newest-first query capability"
            )
        if (
            query.region is not None
            and query.region not in source.classification.regions
        ):
            if InformationRegion.GLOBAL not in source.classification.regions:
                raise ValueError(
                    "governed source query region is outside source coverage"
                )
        return GovernedSourceQueryResult(query=query, source=source)

    def unavailable_response(
        self, query: GovernedSourceQuery
    ) -> GovernedSourceQueryResponse:
        self.prepare(query)
        return GovernedSourceQueryResponse(
            source_id=query.source_id,
            status=GovernedSourceQueryStatus.FAILED,
            error=GovernedSourceQueryError(
                kind=GovernedSourceQueryErrorKind.EXECUTION_UNAVAILABLE,
                message="M344.0 defines the governed query contract without execution",
                retryable=False,
            ),
        )


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
