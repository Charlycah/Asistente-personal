from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Mapping, Protocol, runtime_checkable

from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.knowledge_source_policy import KnowledgeSourceKind

EXTERNAL_SOURCES = frozenset(
    {
        KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
        KnowledgeSourceKind.WEB,
        KnowledgeSourceKind.NEWS,
        KnowledgeSourceKind.API,
    }
)


class ExternalRetrievalStatus(str, Enum):
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class ExternalRetrievalAction(str, Enum):
    EXECUTE_EXTERNAL_RETRIEVAL = "execute_external_retrieval"
    REJECT_RESULT = "reject_result"
    REPORT_FAILURE = "report_failure"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class ExternalRetrievalClientRequest:
    source: KnowledgeSourceKind | str
    query: str
    maximum_content_characters: int
    maximum_references: int

    def __post_init__(self) -> None:
        source = KnowledgeSourceKind(self.source)
        query = self.query.strip()
        if source not in EXTERNAL_SOURCES:
            raise ValueError("external client request requires an external source")
        if not query:
            raise ValueError("external client request query must not be blank")
        if self.maximum_content_characters < 1:
            raise ValueError("maximum content characters must be positive")
        if self.maximum_references < 1:
            raise ValueError("maximum references must be positive")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "query", query)


@dataclass(frozen=True)
class ExternalRetrievalClientResult:
    source: KnowledgeSourceKind | str
    query: str
    content: str
    references: tuple[str, ...]

    def __post_init__(self) -> None:
        source = KnowledgeSourceKind(self.source)
        query = self.query.strip()
        content = self.content.strip()
        references = tuple(item.strip() for item in self.references)
        if source not in EXTERNAL_SOURCES:
            raise ValueError("external client result requires an external source")
        if not query:
            raise ValueError("external client result query must not be blank")
        if not content:
            raise ValueError("external client result content must not be blank")
        if not references or any(not item for item in references):
            raise ValueError("external client result requires non-blank references")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "references", references)


@runtime_checkable
class ExternalRetrievalClient(Protocol):
    def retrieve(
        self, request: ExternalRetrievalClientRequest
    ) -> ExternalRetrievalClientResult: ...


@dataclass(frozen=True)
class ExternalRetrievalExecutionConfig:
    execution_enabled: bool = True
    require_https_references: bool = True
    maximum_query_characters: int = 4_000
    maximum_content_characters: int = 100_000
    maximum_references: int = 32
    allowed_sources: tuple[KnowledgeSourceKind | str, ...] = tuple(EXTERNAL_SOURCES)

    def __post_init__(self) -> None:
        sources = tuple(KnowledgeSourceKind(item) for item in self.allowed_sources)
        if any(item not in EXTERNAL_SOURCES for item in sources):
            raise ValueError("allowed sources must be external")
        if len(sources) != len(set(sources)):
            raise ValueError("allowed external sources must be unique")
        if self.maximum_query_characters < 1:
            raise ValueError("maximum query characters must be positive")
        if self.maximum_content_characters < 1:
            raise ValueError("maximum content characters must be positive")
        if self.maximum_references < 1:
            raise ValueError("maximum references must be positive")
        object.__setattr__(self, "allowed_sources", sources)


@dataclass(frozen=True)
class ExternalRetrievalExecutionRequest:
    owner: str
    step: KnowledgeRetrievalStep
    execution_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("external retrieval owner must not be blank")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class ExternalRetrievalExecutionResult:
    request: ExternalRetrievalExecutionRequest
    status: ExternalRetrievalStatus | str
    action: ExternalRetrievalAction | str
    client_result: ExternalRetrievalClientResult | None
    network_access_performed: bool
    provider_call_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_id: str = ""

    def __post_init__(self) -> None:
        status = ExternalRetrievalStatus(self.status)
        action = ExternalRetrievalAction(self.action)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("external retrieval timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("external retrieval rationale must not be empty")
        attempted = status in {
            ExternalRetrievalStatus.COMPLETED,
            ExternalRetrievalStatus.REJECTED,
            ExternalRetrievalStatus.FAILED,
        }
        if self.network_access_performed != attempted:
            raise ValueError("network access flag must match retrieval attempt")
        if self.provider_call_performed or self.platform_mutation_performed:
            raise ValueError("M174 cannot call inference providers or mutate platform")
        if status is ExternalRetrievalStatus.COMPLETED:
            if self.client_result is None:
                raise ValueError("completed external retrieval requires a result")
        elif self.client_result is not None:
            raise ValueError("inactive external retrieval cannot expose a result")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.execution_id and self.execution_id != expected:
            raise ValueError("external retrieval execution id is inconsistent")
        object.__setattr__(self, "execution_id", expected)

    def _identity_payload(self) -> str:
        result = self.client_result
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.step.step_id,
                self.status.value,
                self.action.value,
                result.content if result else "",
                ",".join(result.references) if result else "",
                str(self.network_access_performed),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class ExternalRetrievalExecutionRepository(Protocol):
    def add(self, result: ExternalRetrievalExecutionResult) -> None: ...
    def get(self, execution_id: str) -> ExternalRetrievalExecutionResult | None: ...
    def list_all(self) -> tuple[ExternalRetrievalExecutionResult, ...]: ...


class InMemoryExternalRetrievalExecutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, ExternalRetrievalExecutionResult] = {}

    def add(self, result: ExternalRetrievalExecutionResult) -> None:
        if result.execution_id in self._items:
            raise ValueError("external retrieval execution already exists")
        self._items[result.execution_id] = result

    def get(self, execution_id: str) -> ExternalRetrievalExecutionResult | None:
        return self._items.get(execution_id)

    def list_all(self) -> tuple[ExternalRetrievalExecutionResult, ...]:
        return tuple(self._items.values())


ExternalClientRegistry = Mapping[KnowledgeSourceKind, ExternalRetrievalClient]
