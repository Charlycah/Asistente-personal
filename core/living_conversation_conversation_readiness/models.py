from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_opportunity_selection import (
    LivingConversationOpportunitySelectionResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationConversationReadinessStatus(str, Enum):
    READY = "ready"
    READY_PARTIAL = "ready_partial"
    NOT_READY = "not_ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationConversationReadinessAction(str, Enum):
    DECLARE_READY = "declare_ready"
    DECLARE_READY_PARTIAL = "declare_ready_partial"
    DECLARE_NOT_READY = "declare_not_ready"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationConversationReadinessConfig:
    maximum_selection_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_selection_results <= 0:
            raise ValueError("conversation readiness result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("conversation readiness result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "conversation readiness confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationConversationReadinessRequest:
    owner: str
    selection_results: tuple[LivingConversationOpportunitySelectionResult, ...]
    readiness_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("conversation readiness owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "selection_results", tuple(self.selection_results))


@dataclass(frozen=True)
class LivingConversationConversationReadinessResult:
    request: LivingConversationConversationReadinessRequest
    status: LivingConversationConversationReadinessStatus | str
    action: LivingConversationConversationReadinessAction | str
    selected_selection: LivingConversationOpportunitySelectionResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    confidence: float
    ready: bool
    partial_context: bool
    not_ready: bool
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
    readiness_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationConversationReadinessStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationConversationReadinessAction(self.action)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("conversation readiness timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "conversation readiness confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("conversation readiness rationale must not be empty")
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
            raise ValueError("M153 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.READY,
            self.status.READY_PARTIAL,
            self.status.NOT_READY,
        }
        if active:
            if (
                self.selected_selection is None
                or self.selected_opportunity is None
                or self.confidence <= 0
            ):
                raise ValueError("active readiness requires source and confidence")
            if (
                self.selected_selection.selected_opportunity
                is not self.selected_opportunity
            ):
                raise ValueError(
                    "readiness opportunity must come from selected selection"
                )
            if self.ready != (
                self.status in {self.status.READY, self.status.READY_PARTIAL}
            ):
                raise ValueError("readiness ready flag is inconsistent")
            if self.partial_context != (self.status is self.status.READY_PARTIAL):
                raise ValueError("readiness partial flag is inconsistent")
            if self.not_ready != (self.status is self.status.NOT_READY):
                raise ValueError("readiness not-ready flag is inconsistent")
        elif (
            self.selected_selection is not None
            or self.selected_opportunity is not None
            or self.confidence != 0
            or self.ready
            or self.partial_context
            or self.not_ready
        ):
            raise ValueError("inactive readiness cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("readiness confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.readiness_id and self.readiness_id != expected:
            raise ValueError("conversation readiness id is inconsistent")
        object.__setattr__(self, "readiness_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.selection_id for item in self.request.selection_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.readiness_requested),
                self.status.value,
                self.action.value,
                self.selected_selection.selection_id
                if self.selected_selection
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.ready),
                str(self.partial_context),
                str(self.not_ready),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationConversationReadinessRepository(Protocol):
    def add(self, result: LivingConversationConversationReadinessResult) -> None: ...
    def get(
        self, readiness_id: str
    ) -> LivingConversationConversationReadinessResult | None: ...
    def list_all(self) -> tuple[LivingConversationConversationReadinessResult, ...]: ...


class InMemoryLivingConversationConversationReadinessRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationConversationReadinessResult] = {}

    def add(self, result: LivingConversationConversationReadinessResult) -> None:
        if result.readiness_id in self._items:
            raise ValueError("conversation readiness result already exists")
        self._items[result.readiness_id] = result

    def get(
        self, readiness_id: str
    ) -> LivingConversationConversationReadinessResult | None:
        return self._items.get(readiness_id)

    def list_all(self) -> tuple[LivingConversationConversationReadinessResult, ...]:
        return tuple(self._items.values())
