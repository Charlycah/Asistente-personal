from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.knowledge_source_policy import (
    KnowledgeSourceDecision,
    KnowledgeSourceKind,
)


class KnowledgeRetrievalStatus(str, Enum):
    INTERNAL_PLANNED = "internal_planned"
    LOCAL_PLANNED = "local_planned"
    EXTERNAL_PLANNED = "external_planned"
    VERIFICATION_PLANNED = "verification_planned"
    WITHHELD = "withheld"
    NOT_APPLICABLE = "not_applicable"


class KnowledgeRetrievalAction(str, Enum):
    PREPARE_INTERNAL = "prepare_internal"
    PREPARE_LOCAL = "prepare_local"
    PREPARE_EXTERNAL = "prepare_external"
    PREPARE_VERIFICATION = "prepare_verification"
    WITHHOLD = "withhold"
    NONE = "none"


class RetrievalStrategy(str, Enum):
    DIRECT = "direct"
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


@dataclass(frozen=True)
class KnowledgeRetrievalStep:
    source: KnowledgeSourceKind | str
    priority: int
    required: bool = True
    query: str = ""
    step_id: str = ""

    def __post_init__(self) -> None:
        source = KnowledgeSourceKind(self.source)
        query = self.query.strip()
        if self.priority < 1:
            raise ValueError("retrieval step priority must be positive")
        if not query:
            raise ValueError("retrieval step query must not be blank")
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "query", query)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.step_id and self.step_id != expected:
            raise ValueError("retrieval step id is inconsistent")
        object.__setattr__(self, "step_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.source.value,
                str(self.priority),
                str(self.required),
                self.query.casefold(),
            )
        )


@dataclass(frozen=True)
class KnowledgeRetrievalConfig:
    max_sources: int = 3
    parallel_verification: bool = True

    def __post_init__(self) -> None:
        if self.max_sources < 1:
            raise ValueError("maximum retrieval sources must be positive")


@dataclass(frozen=True)
class KnowledgeRetrievalRequest:
    owner: str
    source_decision: KnowledgeSourceDecision
    orchestration_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("knowledge retrieval owner must not be blank")
        source_owner = self.source_decision.request.owner
        if owner.casefold() != source_owner.casefold():
            raise ValueError("knowledge retrieval owner must match source owner")
        object.__setattr__(self, "owner", owner)


@dataclass(frozen=True)
class KnowledgeRetrievalPlan:
    request: KnowledgeRetrievalRequest
    status: KnowledgeRetrievalStatus | str
    action: KnowledgeRetrievalAction | str
    strategy: RetrievalStrategy | str
    steps: tuple[KnowledgeRetrievalStep, ...]
    verification_required: bool
    retrieval_allowed: bool
    network_access_allowed: bool
    provider_call_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        status = KnowledgeRetrievalStatus(self.status)
        action = KnowledgeRetrievalAction(self.action)
        strategy = RetrievalStrategy(self.strategy)
        steps = tuple(self.steps)
        rationale = tuple(item.strip() for item in self.rationale)
        if self.created_at.tzinfo is None:
            raise ValueError("knowledge retrieval timestamp must be timezone-aware")
        if not rationale or any(not item for item in rationale):
            raise ValueError("knowledge retrieval rationale must not be empty")
        if len({item.step_id for item in steps}) != len(steps):
            raise ValueError("knowledge retrieval steps must be unique")
        priorities = tuple(item.priority for item in steps)
        if priorities != tuple(range(1, len(steps) + 1)):
            raise ValueError("knowledge retrieval priorities must be contiguous")
        if any(
            (
                self.retrieval_allowed,
                self.network_access_allowed,
                self.provider_call_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M170 cannot authorize retrieval or execution")
        inactive = {
            KnowledgeRetrievalStatus.WITHHELD,
            KnowledgeRetrievalStatus.NOT_APPLICABLE,
        }
        if status in inactive and steps:
            raise ValueError("inactive retrieval plan cannot contain steps")
        if status not in inactive and not steps:
            raise ValueError("active retrieval plan requires steps")
        if self.verification_required != (
            status is KnowledgeRetrievalStatus.VERIFICATION_PLANNED
        ):
            raise ValueError("verification flag must match retrieval status")
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "strategy", strategy)
        object.__setattr__(self, "steps", steps)
        object.__setattr__(self, "rationale", rationale)
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("knowledge retrieval plan id is inconsistent")
        object.__setattr__(self, "plan_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.source_decision.decision_id,
                self.status.value,
                self.action.value,
                self.strategy.value,
                ",".join(item.step_id for item in self.steps),
                str(self.verification_required),
                self.created_at.isoformat(),
                *self.rationale,
            )
        )


@runtime_checkable
class KnowledgeRetrievalRepository(Protocol):
    def add(self, plan: KnowledgeRetrievalPlan) -> None: ...

    def get(self, plan_id: str) -> KnowledgeRetrievalPlan | None: ...

    def list_all(self) -> tuple[KnowledgeRetrievalPlan, ...]: ...


class InMemoryKnowledgeRetrievalRepository:
    def __init__(self) -> None:
        self._items: dict[str, KnowledgeRetrievalPlan] = {}

    def add(self, plan: KnowledgeRetrievalPlan) -> None:
        if plan.plan_id in self._items:
            raise ValueError("knowledge retrieval plan already exists")
        self._items[plan.plan_id] = plan

    def get(self, plan_id: str) -> KnowledgeRetrievalPlan | None:
        return self._items.get(plan_id)

    def list_all(self) -> tuple[KnowledgeRetrievalPlan, ...]:
        return tuple(self._items.values())
