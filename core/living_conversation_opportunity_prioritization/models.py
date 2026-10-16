from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationOpportunityPrioritizationStatus(str, Enum):
    PRIORITIZED = "prioritized"
    PRIORITIZED_PARTIAL = "prioritized_partial"
    DEFERRED = "deferred"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationOpportunityPrioritizationAction(str, Enum):
    RANK = "rank"
    RANK_PARTIAL = "rank_partial"
    DEFER = "defer"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class LivingConversationOpportunityPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    DEFERRED = "deferred"


@dataclass(frozen=True)
class LivingConversationOpportunityPrioritizationConfig:
    maximum_opportunity_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_opportunity_results <= 0:
            raise ValueError("opportunity prioritization result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("opportunity prioritization result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "opportunity prioritization confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationOpportunityPrioritizationRequest:
    owner: str
    opportunity_results: tuple[LivingConversationPresenceOpportunityResult, ...]
    prioritization_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("opportunity prioritization owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "opportunity_results", tuple(self.opportunity_results))


@dataclass(frozen=True)
class LivingConversationOpportunityPrioritizationResult:
    request: LivingConversationOpportunityPrioritizationRequest
    status: LivingConversationOpportunityPrioritizationStatus | str
    action: LivingConversationOpportunityPrioritizationAction | str
    priority: LivingConversationOpportunityPriority | str | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    ranked_opportunities: tuple[LivingConversationPresenceOpportunityResult, ...]
    confidence: float
    partial_context: bool
    deferred: bool
    confirmation_required: bool
    conversation_decision_allowed: bool
    conversational_activation_allowed: bool
    timing_selection_allowed: bool
    prompt_generation_allowed: bool
    response_realization_allowed: bool
    identity_inference_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    behavior_adaptation_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prioritization_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "status",
            LivingConversationOpportunityPrioritizationStatus(self.status),
        )
        object.__setattr__(
            self,
            "action",
            LivingConversationOpportunityPrioritizationAction(self.action),
        )
        if self.priority is not None:
            object.__setattr__(
                self, "priority", LivingConversationOpportunityPriority(self.priority)
            )
        object.__setattr__(
            self, "ranked_opportunities", tuple(self.ranked_opportunities)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "opportunity prioritization timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "opportunity prioritization confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("opportunity prioritization rationale must not be empty")
        if any(
            (
                self.conversation_decision_allowed,
                self.conversational_activation_allowed,
                self.timing_selection_allowed,
                self.prompt_generation_allowed,
                self.response_realization_allowed,
                self.identity_inference_allowed,
                self.activity_inference_allowed,
                self.intent_inference_allowed,
                self.behavior_adaptation_allowed,
                self.provider_call_allowed,
                self.automation_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M151 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.PRIORITIZED,
            self.status.PRIORITIZED_PARTIAL,
            self.status.DEFERRED,
        }
        if active:
            if (
                self.selected_opportunity is None
                or self.priority is None
                or not self.ranked_opportunities
                or self.confidence <= 0
            ):
                raise ValueError(
                    "active prioritization requires source, rank and confidence"
                )
            if self.ranked_opportunities[0] is not self.selected_opportunity:
                raise ValueError("selected opportunity must lead ranked opportunities")
            if self.partial_context != (self.status is self.status.PRIORITIZED_PARTIAL):
                raise ValueError("partial prioritization metadata is inconsistent")
            if self.deferred != (self.status is self.status.DEFERRED):
                raise ValueError("deferred prioritization metadata is inconsistent")
        elif (
            self.selected_opportunity is not None
            or self.priority is not None
            or self.ranked_opportunities
            or self.confidence != 0
            or self.partial_context
            or self.deferred
        ):
            raise ValueError("inactive prioritization cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("prioritization confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.prioritization_id and self.prioritization_id != expected:
            raise ValueError("opportunity prioritization id is inconsistent")
        object.__setattr__(self, "prioritization_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.opportunity_id for item in self.request.opportunity_results
        )
        ranked_ids = ";".join(item.opportunity_id for item in self.ranked_opportunities)
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.prioritization_requested),
                self.status.value,
                self.action.value,
                self.priority.value if self.priority else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                ranked_ids,
                str(self.confidence),
                str(self.partial_context),
                str(self.deferred),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationOpportunityPrioritizationRepository(Protocol):
    def add(
        self, result: LivingConversationOpportunityPrioritizationResult
    ) -> None: ...
    def get(
        self, prioritization_id: str
    ) -> LivingConversationOpportunityPrioritizationResult | None: ...
    def list_all(
        self,
    ) -> tuple[LivingConversationOpportunityPrioritizationResult, ...]: ...


class InMemoryLivingConversationOpportunityPrioritizationRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationOpportunityPrioritizationResult] = {}

    def add(self, result: LivingConversationOpportunityPrioritizationResult) -> None:
        if result.prioritization_id in self._items:
            raise ValueError("opportunity prioritization result already exists")
        self._items[result.prioritization_id] = result

    def get(
        self, prioritization_id: str
    ) -> LivingConversationOpportunityPrioritizationResult | None:
        return self._items.get(prioritization_id)

    def list_all(self) -> tuple[LivingConversationOpportunityPrioritizationResult, ...]:
        return tuple(self._items.values())
