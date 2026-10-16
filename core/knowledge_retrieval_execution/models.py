from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Mapping, Protocol, runtime_checkable

from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalPlan,
    KnowledgeRetrievalStep,
)
from core.knowledge_source_policy import KnowledgeSourceKind


class KnowledgeExecutionStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class KnowledgeStepExecutionStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    SKIPPED = "skipped"
    WITHHELD = "withheld"


@dataclass(frozen=True)
class KnowledgeRetrievalArtifact:
    source: KnowledgeSourceKind | str
    query: str
    content: str
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        source = KnowledgeSourceKind(self.source)
        query = self.query.strip()
        content = self.content.strip()
        references = tuple(item.strip() for item in self.references)
        if not query:
            raise ValueError("retrieval artifact query must not be blank")
        if not content:
            raise ValueError("retrieval artifact content must not be blank")
        if any(not item for item in references):
            raise ValueError("retrieval artifact references must not be blank")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "references", references)


@runtime_checkable
class KnowledgeRetriever(Protocol):
    def retrieve(self, step: KnowledgeRetrievalStep) -> KnowledgeRetrievalArtifact: ...


@dataclass(frozen=True)
class KnowledgeRetrievalExecutionConfig:
    execution_enabled: bool = True
    allow_internal: bool = True
    allow_local_documents: bool = True
    allow_network: bool = False
    continue_after_optional_failure: bool = True
    max_content_characters: int = 100_000

    def __post_init__(self) -> None:
        if self.max_content_characters < 1:
            raise ValueError("maximum content characters must be positive")


@dataclass(frozen=True)
class KnowledgeRetrievalExecutionRequest:
    owner: str
    plan: KnowledgeRetrievalPlan
    execution_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("knowledge retrieval execution owner must not be blank")
        if owner.casefold() != self.plan.request.owner.casefold():
            raise ValueError("execution owner must match retrieval plan owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class KnowledgeStepExecution:
    step: KnowledgeRetrievalStep
    status: KnowledgeStepExecutionStatus | str
    artifact: KnowledgeRetrievalArtifact | None
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        status = KnowledgeStepExecutionStatus(self.status)
        rationale = tuple(item.strip() for item in self.rationale)
        if not rationale or any(not item for item in rationale):
            raise ValueError("step execution rationale must not be empty")
        if status is KnowledgeStepExecutionStatus.SUCCEEDED:
            if self.artifact is None:
                raise ValueError("successful step execution requires an artifact")
            if self.artifact.source is not self.step.source:
                raise ValueError("artifact source must match retrieval step source")
            if self.artifact.query != self.step.query:
                raise ValueError("artifact query must match retrieval step query")
        elif self.artifact is not None:
            raise ValueError("inactive step execution cannot contain an artifact")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class KnowledgeRetrievalExecution:
    request: KnowledgeRetrievalExecutionRequest
    status: KnowledgeExecutionStatus | str
    steps: tuple[KnowledgeStepExecution, ...]
    retrieval_performed: bool
    network_access_performed: bool
    provider_call_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    execution_id: str = ""

    def __post_init__(self) -> None:
        status = KnowledgeExecutionStatus(self.status)
        steps = tuple(self.steps)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge execution timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("knowledge execution rationale must not be empty")
        if len(steps) != len(self.request.plan.steps):
            raise ValueError("execution must account for every retrieval step")
        if tuple(item.step for item in steps) != self.request.plan.steps:
            raise ValueError("execution steps must preserve retrieval plan order")
        succeeded = any(
            item.status is KnowledgeStepExecutionStatus.SUCCEEDED for item in steps
        )
        if self.retrieval_performed != succeeded:
            raise ValueError("retrieval performed flag must match successful steps")
        network_succeeded = any(
            item.status is KnowledgeStepExecutionStatus.SUCCEEDED
            and item.step.source
            in {
                KnowledgeSourceKind.OFFICIAL_DOCUMENTATION,
                KnowledgeSourceKind.WEB,
                KnowledgeSourceKind.NEWS,
                KnowledgeSourceKind.API,
            }
            for item in steps
        )
        if self.network_access_performed != network_succeeded:
            raise ValueError("network flag must match successful external steps")
        if self.provider_call_performed or self.platform_mutation_performed:
            raise ValueError("M171 cannot call providers or mutate the platform")
        if (
            status
            in {
                KnowledgeExecutionStatus.WITHHELD,
                KnowledgeExecutionStatus.NOT_APPLICABLE,
            }
            and succeeded
        ):
            raise ValueError("inactive execution cannot contain successful steps")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "steps", steps)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.execution_id and self.execution_id != expected:
            raise ValueError("knowledge execution id is inconsistent")
        object.__setattr__(self, "execution_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.plan.plan_id,
                self.status.value,
                ",".join(item.status.value for item in self.steps),
                str(self.retrieval_performed),
                str(self.network_access_performed),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class KnowledgeRetrievalExecutionRepository(Protocol):
    def add(self, execution: KnowledgeRetrievalExecution) -> None: ...

    def get(self, execution_id: str) -> KnowledgeRetrievalExecution | None: ...

    def list_all(self) -> tuple[KnowledgeRetrievalExecution, ...]: ...


class InMemoryKnowledgeRetrievalExecutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, KnowledgeRetrievalExecution] = {}

    def add(self, execution: KnowledgeRetrievalExecution) -> None:
        if execution.execution_id in self._items:
            raise ValueError("knowledge retrieval execution already exists")
        self._items[execution.execution_id] = execution

    def get(self, execution_id: str) -> KnowledgeRetrievalExecution | None:
        return self._items.get(execution_id)

    def list_all(self) -> tuple[KnowledgeRetrievalExecution, ...]:
        return tuple(self._items.values())


RetrieverRegistry = Mapping[KnowledgeSourceKind, KnowledgeRetriever]
