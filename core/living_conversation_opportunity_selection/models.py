from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_opportunity_prioritization import (
    LivingConversationOpportunityPrioritizationResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationOpportunitySelectionStatus(str, Enum):
    SELECTED = "selected"
    SELECTED_PARTIAL = "selected_partial"
    DEFERRED = "deferred"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationOpportunitySelectionAction(str, Enum):
    SELECT = "select"
    SELECT_PARTIAL = "select_partial"
    DEFER = "defer"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationOpportunitySelectionConfig:
    maximum_prioritization_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_prioritization_results <= 0:
            raise ValueError("opportunity selection result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("opportunity selection result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "opportunity selection confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationOpportunitySelectionRequest:
    owner: str
    prioritization_results: tuple[
        LivingConversationOpportunityPrioritizationResult, ...
    ]
    selection_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("opportunity selection owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(
            self, "prioritization_results", tuple(self.prioritization_results)
        )


@dataclass(frozen=True)
class LivingConversationOpportunitySelectionResult:
    request: LivingConversationOpportunitySelectionRequest
    status: LivingConversationOpportunitySelectionStatus | str
    action: LivingConversationOpportunitySelectionAction | str
    selected_prioritization: LivingConversationOpportunityPrioritizationResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
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
    selection_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationOpportunitySelectionStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationOpportunitySelectionAction(self.action)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("opportunity selection timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "opportunity selection confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("opportunity selection rationale must not be empty")
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
            raise ValueError("M152 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.SELECTED,
            self.status.SELECTED_PARTIAL,
            self.status.DEFERRED,
        }
        if active:
            if (
                self.selected_prioritization is None
                or self.selected_opportunity is None
                or self.confidence <= 0
            ):
                raise ValueError("active selection requires source and confidence")
            if (
                self.selected_prioritization.selected_opportunity
                is not self.selected_opportunity
            ):
                raise ValueError(
                    "selected opportunity must come from selected prioritization"
                )
            if self.partial_context != (self.status is self.status.SELECTED_PARTIAL):
                raise ValueError("partial selection metadata is inconsistent")
            if self.deferred != (self.status is self.status.DEFERRED):
                raise ValueError("deferred selection metadata is inconsistent")
        elif (
            self.selected_prioritization is not None
            or self.selected_opportunity is not None
            or self.confidence != 0
            or self.partial_context
            or self.deferred
        ):
            raise ValueError("inactive selection cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("selection confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.selection_id and self.selection_id != expected:
            raise ValueError("opportunity selection id is inconsistent")
        object.__setattr__(self, "selection_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.prioritization_id for item in self.request.prioritization_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.selection_requested),
                self.status.value,
                self.action.value,
                self.selected_prioritization.prioritization_id
                if self.selected_prioritization
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.partial_context),
                str(self.deferred),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationOpportunitySelectionRepository(Protocol):
    def add(self, result: LivingConversationOpportunitySelectionResult) -> None: ...
    def get(
        self, selection_id: str
    ) -> LivingConversationOpportunitySelectionResult | None: ...
    def list_all(self) -> tuple[LivingConversationOpportunitySelectionResult, ...]: ...


class InMemoryLivingConversationOpportunitySelectionRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationOpportunitySelectionResult] = {}

    def add(self, result: LivingConversationOpportunitySelectionResult) -> None:
        if result.selection_id in self._items:
            raise ValueError("opportunity selection result already exists")
        self._items[result.selection_id] = result

    def get(
        self, selection_id: str
    ) -> LivingConversationOpportunitySelectionResult | None:
        return self._items.get(selection_id)

    def list_all(self) -> tuple[LivingConversationOpportunitySelectionResult, ...]:
        return tuple(self._items.values())
