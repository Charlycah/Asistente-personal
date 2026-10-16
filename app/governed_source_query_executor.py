from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
from time import perf_counter
from types import MappingProxyType
from typing import Mapping, Protocol

from .governed_source_query import (
    GovernedSourceQuery,
    GovernedSourceQueryContract,
    GovernedSourceQueryError,
    GovernedSourceQueryResponse,
    GovernedSourceQueryResult,
    GovernedSourceQueryStatus,
)


class GovernedSourceExecutionErrorKind(StrEnum):
    ADAPTER_UNAVAILABLE = "adapter_unavailable"
    TIMEOUT = "timeout"
    ADAPTER_FAILURE = "adapter_failure"
    INVALID_ADAPTER_RESPONSE = "invalid_adapter_response"


class GovernedSourceQueryAdapter(Protocol):
    """Synchronous source boundary used only by the canonical executor."""

    def execute(
        self, query: GovernedSourceQuery
    ) -> tuple[Mapping[str, object], ...]: ...


@dataclass(frozen=True)
class GovernedSourceQueryObservation:
    sequence_id: int
    execution_id: str
    source_id: str
    started_at: datetime
    finished_at: datetime
    duration_ms: float
    status: GovernedSourceQueryStatus
    item_count: int
    dropped_items: int
    error_kind: str | None
    retryable: bool


@dataclass(frozen=True)
class GovernedSourceQueryObservabilitySnapshot:
    schema_version: str
    authority: str
    total_queries: int
    succeeded_queries: int
    empty_queries: int
    failed_queries: int
    rejected_queries: int
    timeout_queries: int
    unavailable_queries: int
    invalid_response_queries: int
    returned_items: int
    dropped_items: int
    observations_retained: int
    max_observations: int
    last_observation: GovernedSourceQueryObservation | None


@dataclass(frozen=True)
class GovernedSourceQueryExecutorSnapshot:
    schema_version: str
    authority: str
    execution_enabled: bool
    network_enabled: bool
    resilience_enabled: bool
    observability_enabled: bool
    registered_sources: tuple[str, ...]


class GovernedSourceQueryExecutor:
    """Single governed execution authority with bounded local observability."""

    SCHEMA_VERSION = "m344.1"
    OBSERVABILITY_SCHEMA_VERSION = "m344.3"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    MAX_OBSERVATIONS = 100

    def __init__(self, contract: GovernedSourceQueryContract) -> None:
        self._contract = contract
        self._adapters: dict[str, GovernedSourceQueryAdapter] = {}
        self._observations: list[GovernedSourceQueryObservation] = []
        self._sequence_id = 0
        self._total_queries = 0
        self._succeeded_queries = 0
        self._empty_queries = 0
        self._failed_queries = 0
        self._rejected_queries = 0
        self._timeout_queries = 0
        self._unavailable_queries = 0
        self._invalid_response_queries = 0
        self._returned_items = 0
        self._dropped_items = 0

    @property
    def snapshot(self) -> GovernedSourceQueryExecutorSnapshot:
        return GovernedSourceQueryExecutorSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            execution_enabled=True,
            network_enabled=any(
                bool(getattr(adapter, "network_enabled", False))
                for adapter in self._adapters.values()
            ),
            resilience_enabled=True,
            observability_enabled=True,
            registered_sources=tuple(sorted(self._adapters)),
        )

    @property
    def observability(self) -> GovernedSourceQueryObservabilitySnapshot:
        return GovernedSourceQueryObservabilitySnapshot(
            schema_version=self.OBSERVABILITY_SCHEMA_VERSION,
            authority=self.AUTHORITY,
            total_queries=self._total_queries,
            succeeded_queries=self._succeeded_queries,
            empty_queries=self._empty_queries,
            failed_queries=self._failed_queries,
            rejected_queries=self._rejected_queries,
            timeout_queries=self._timeout_queries,
            unavailable_queries=self._unavailable_queries,
            invalid_response_queries=self._invalid_response_queries,
            returned_items=self._returned_items,
            dropped_items=self._dropped_items,
            observations_retained=len(self._observations),
            max_observations=self.MAX_OBSERVATIONS,
            last_observation=(self._observations[-1] if self._observations else None),
        )

    @property
    def observations(self) -> tuple[GovernedSourceQueryObservation, ...]:
        return tuple(self._observations)

    def register(self, source_id: str, adapter: GovernedSourceQueryAdapter) -> None:
        normalized_source_id = source_id.strip().casefold()
        if not normalized_source_id:
            raise ValueError("governed query adapter source id cannot be empty")

        declaration = getattr(adapter, "source_declaration", None)
        if declaration is not None:
            declared_source_id = declaration.source_id.strip().casefold()
            if declared_source_id != normalized_source_id:
                raise ValueError(
                    "governed source declaration and adapter identity must match"
                )
            self._contract.admit_non_default_source(declaration)
        else:
            self._contract.source_for(normalized_source_id)

        self._adapters[normalized_source_id] = adapter

    def execute(self, query: GovernedSourceQuery) -> GovernedSourceQueryResult:
        started_at = datetime.now(timezone.utc)
        started_clock = perf_counter()
        self._total_queries += 1
        try:
            prepared = self._contract.prepare(query)
        except ValueError:
            self._rejected_queries += 1
            self._record(
                query=query,
                started_at=started_at,
                started_clock=started_clock,
                status=GovernedSourceQueryStatus.REJECTED,
            )
            raise

        adapter = self._adapters.get(query.source_id)
        if adapter is None:
            self._unavailable_queries += 1
            response = self._failed_response(
                query,
                kind=GovernedSourceExecutionErrorKind.ADAPTER_UNAVAILABLE,
                message="no governed query adapter is registered for the source",
                retryable=False,
            )
            return self._finish(
                query=query,
                prepared=prepared,
                response=response,
                started_at=started_at,
                started_clock=started_clock,
            )

        try:
            raw_items = adapter.execute(query)
            items, dropped_items = self._bounded_items(raw_items, query.limit)
        except TimeoutError:
            self._timeout_queries += 1
            response = self._failed_response(
                query,
                kind=GovernedSourceExecutionErrorKind.TIMEOUT,
                message="governed source query exceeded its timeout",
                retryable=True,
            )
            dropped_items = 0
        except TypeError:
            self._invalid_response_queries += 1
            response = self._failed_response(
                query,
                kind=GovernedSourceExecutionErrorKind.INVALID_ADAPTER_RESPONSE,
                message="governed source adapter returned an invalid response",
                retryable=False,
            )
            dropped_items = 0
        except Exception as exc:
            response = self._failed_response(
                query,
                kind=GovernedSourceExecutionErrorKind.ADAPTER_FAILURE,
                message=f"governed source adapter failed: {type(exc).__name__}",
                retryable=True,
            )
            dropped_items = 0
        else:
            status = (
                GovernedSourceQueryStatus.SUCCEEDED
                if items
                else GovernedSourceQueryStatus.EMPTY
            )
            response = GovernedSourceQueryResponse(
                source_id=query.source_id,
                status=status,
                raw_items=items,
                received_at=datetime.now(timezone.utc),
            )

        return self._finish(
            query=query,
            prepared=prepared,
            response=response,
            started_at=started_at,
            started_clock=started_clock,
            dropped_items=dropped_items,
        )

    def _finish(
        self,
        *,
        query: GovernedSourceQuery,
        prepared: GovernedSourceQueryResult,
        response: GovernedSourceQueryResponse,
        started_at: datetime,
        started_clock: float,
        dropped_items: int = 0,
    ) -> GovernedSourceQueryResult:
        item_count = len(response.raw_items)
        self._returned_items += item_count
        self._dropped_items += dropped_items
        if response.status is GovernedSourceQueryStatus.SUCCEEDED:
            self._succeeded_queries += 1
        elif response.status is GovernedSourceQueryStatus.EMPTY:
            self._empty_queries += 1
        elif response.status is GovernedSourceQueryStatus.FAILED:
            self._failed_queries += 1
        execution_id = self._execution_id(
            query=query,
            response=response,
            started_at=started_at,
        )
        self._record(
            query=query,
            started_at=started_at,
            started_clock=started_clock,
            status=response.status,
            item_count=item_count,
            dropped_items=dropped_items,
            error=response.error,
            execution_id=execution_id,
        )
        return GovernedSourceQueryResult(
            query=query,
            source=prepared.source,
            status=response.status,
            response=response,
            execution_id=execution_id,
        )

    def _record(
        self,
        *,
        query: GovernedSourceQuery,
        started_at: datetime,
        started_clock: float,
        status: GovernedSourceQueryStatus,
        item_count: int = 0,
        dropped_items: int = 0,
        error: GovernedSourceQueryError | None = None,
        execution_id: str = "",
    ) -> None:
        self._sequence_id += 1
        finished_at = datetime.now(timezone.utc)
        observation = GovernedSourceQueryObservation(
            sequence_id=self._sequence_id,
            execution_id=execution_id,
            source_id=query.source_id,
            started_at=started_at,
            finished_at=finished_at,
            duration_ms=max(0.0, (perf_counter() - started_clock) * 1000),
            status=status,
            item_count=item_count,
            dropped_items=dropped_items,
            error_kind=(str(error.kind) if error is not None else None),
            retryable=bool(error.retryable) if error is not None else False,
        )
        self._observations.append(observation)
        del self._observations[: -self.MAX_OBSERVATIONS]

    @staticmethod
    def _execution_id(
        *,
        query: GovernedSourceQuery,
        response: GovernedSourceQueryResponse,
        started_at: datetime,
    ) -> str:
        items = json.dumps(
            [dict(item) for item in response.raw_items],
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        error_kind = str(response.error.kind) if response.error is not None else ""
        error_retryable = (
            str(response.error.retryable)
            if response.error is not None
            else ""
        )
        parameters = json.dumps(
            dict(query.parameters or {}),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        payload = "|".join(
            (
                query.source_id,
                ",".join(sorted(topic.value for topic in query.topics)),
                query.query_text or "",
                str(query.limit),
                query.region.value if query.region is not None else "",
                query.published_after.isoformat()
                if query.published_after is not None
                else "",
                query.published_before.isoformat()
                if query.published_before is not None
                else "",
                str(query.timeout_seconds),
                parameters,
                query.order.value if query.order is not None else "",
                started_at.isoformat(),
                response.received_at.isoformat()
                if response.received_at is not None
                else "",
                response.status.value,
                items,
                error_kind,
                error_retryable,
            )
        )
        return sha256(payload.encode()).hexdigest()

    @staticmethod
    def _bounded_items(
        raw_items: object,
        limit: int,
    ) -> tuple[tuple[Mapping[str, object], ...], int]:
        if not isinstance(raw_items, (tuple, list)):
            raise TypeError("governed adapter response must be a sequence")
        bounded = raw_items[:limit]
        if any(not isinstance(item, Mapping) for item in bounded):
            raise TypeError("governed adapter items must be mappings")
        items = tuple(MappingProxyType(dict(item)) for item in bounded)
        return items, max(0, len(raw_items) - len(items))

    @staticmethod
    def _failed_response(
        query: GovernedSourceQuery,
        *,
        kind: GovernedSourceExecutionErrorKind,
        message: str,
        retryable: bool,
    ) -> GovernedSourceQueryResponse:
        return GovernedSourceQueryResponse(
            source_id=query.source_id,
            status=GovernedSourceQueryStatus.FAILED,
            received_at=datetime.now(timezone.utc),
            error=GovernedSourceQueryError(
                kind=kind,
                message=message,
                retryable=retryable,
            ),
        )
