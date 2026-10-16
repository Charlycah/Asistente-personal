from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.governed_provider_execution_adapter import LocalProviderExecutionResult
from core.knowledge_retrieval_execution import KnowledgeRetrievalExecution


class OperationalResponseStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class OperationalResponseAction(str, Enum):
    DELIVER_RESPONSE = "deliver_response"
    DELIVER_WITH_LIMITATIONS = "deliver_with_limitations"
    REPORT_FAILURE = "report_failure"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class OperationalResponseAssemblyConfig:
    assembly_enabled: bool = True
    maximum_response_characters: int = 64_000
    maximum_evidence_items: int = 16
    maximum_evidence_characters: int = 100_000
    require_provider_response: bool = True

    def __post_init__(self) -> None:
        if self.maximum_response_characters < 1:
            raise ValueError("maximum response characters must be positive")
        if self.maximum_evidence_items < 0:
            raise ValueError("maximum evidence items cannot be negative")
        if self.maximum_evidence_characters < 0:
            raise ValueError("maximum evidence characters cannot be negative")


@dataclass(frozen=True)
class OperationalEvidence:
    source: str
    query: str
    content: str
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        source = self.source.strip()
        query = self.query.strip()
        content = self.content.strip()
        references = tuple(item.strip() for item in self.references)
        if not source or not query or not content:
            raise ValueError("operational evidence fields must not be blank")
        if any(not item for item in references):
            raise ValueError("operational evidence references must not be blank")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "query", query)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "references", references)


@dataclass(frozen=True)
class OperationalResponseAssemblyRequest:
    owner: str
    provider_execution: LocalProviderExecutionResult | None = None
    retrieval_execution: KnowledgeRetrievalExecution | None = None
    assembly_requested: bool = True
    external_network_access_performed: bool = False

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("operational response owner must not be blank")
        if (
            self.provider_execution
            and owner.casefold() != self.provider_execution.request.owner.casefold()
        ):
            raise ValueError("provider execution owner must match assembly owner")
        if (
            self.retrieval_execution
            and owner.casefold() != self.retrieval_execution.request.owner.casefold()
        ):
            raise ValueError("retrieval execution owner must match assembly owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class OperationalResponse:
    request: OperationalResponseAssemblyRequest
    status: OperationalResponseStatus | str
    action: OperationalResponseAction | str
    response_text: str
    evidence: tuple[OperationalEvidence, ...]
    limitations: tuple[str, ...]
    provider_execution_id: str
    retrieval_execution_id: str
    provider_call_performed: bool
    retrieval_performed: bool
    network_access_performed: bool
    platform_mutation_performed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_id: str = ""

    def __post_init__(self) -> None:
        status = OperationalResponseStatus(self.status)
        action = OperationalResponseAction(self.action)
        response_text = self.response_text.strip()
        evidence = tuple(self.evidence)
        limitations = tuple(item.strip() for item in self.limitations)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("operational response timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("operational response rationale must not be empty")
        if any(not item for item in limitations):
            raise ValueError("operational response limitations must not be blank")
        deliverable = status in {
            OperationalResponseStatus.COMPLETED,
            OperationalResponseStatus.PARTIAL,
        }
        if deliverable != bool(response_text):
            raise ValueError("deliverable operational response must contain text")
        if deliverable and action not in {
            OperationalResponseAction.DELIVER_RESPONSE,
            OperationalResponseAction.DELIVER_WITH_LIMITATIONS,
        }:
            raise ValueError("deliverable response action is inconsistent")
        if not deliverable and action in {
            OperationalResponseAction.DELIVER_RESPONSE,
            OperationalResponseAction.DELIVER_WITH_LIMITATIONS,
        }:
            raise ValueError("inactive response cannot use a delivery action")
        if self.platform_mutation_performed:
            raise ValueError("M175 cannot mutate the platform")
        provider = self.request.provider_execution
        retrieval = self.request.retrieval_execution
        if self.provider_call_performed != bool(
            provider and provider.provider_call_performed
        ):
            raise ValueError("provider call lineage flag is inconsistent")
        if self.retrieval_performed != bool(
            retrieval and retrieval.retrieval_performed
        ):
            raise ValueError("retrieval lineage flag is inconsistent")
        if self.network_access_performed != bool(
            (provider and provider.network_access_allowed)
            or (retrieval and retrieval.network_access_performed)
            or self.request.external_network_access_performed
        ):
            raise ValueError("network lineage flag is inconsistent")
        expected_provider_id = provider.execution_id if provider else ""
        expected_retrieval_id = retrieval.execution_id if retrieval else ""
        if (
            self.provider_execution_id != expected_provider_id
            or self.retrieval_execution_id != expected_retrieval_id
        ):
            raise ValueError("operational response lineage ids are inconsistent")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "response_text", response_text)
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(self, "limitations", limitations)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.response_id and self.response_id != expected:
            raise ValueError("operational response id is inconsistent")
        object.__setattr__(self, "response_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.status.value,
                self.action.value,
                self.response_text,
                self.provider_execution_id,
                self.retrieval_execution_id,
                ";".join(
                    f"{item.source}:{item.query}:{item.content}"
                    for item in self.evidence
                ),
                ";".join(self.limitations),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class OperationalResponseRepository(Protocol):
    def add(self, response: OperationalResponse) -> None: ...
    def get(self, response_id: str) -> OperationalResponse | None: ...
    def list_all(self) -> tuple[OperationalResponse, ...]: ...


class InMemoryOperationalResponseRepository:
    def __init__(self) -> None:
        self._items: dict[str, OperationalResponse] = {}

    def add(self, response: OperationalResponse) -> None:
        if response.response_id in self._items:
            raise ValueError("operational response already exists")
        self._items[response.response_id] = response

    def get(self, response_id: str) -> OperationalResponse | None:
        return self._items.get(response_id)

    def list_all(self) -> tuple[OperationalResponse, ...]:
        return tuple(self._items.values())
