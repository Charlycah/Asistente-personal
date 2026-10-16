from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_conversation_readiness import (
    LivingConversationConversationReadinessResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationConversationEligibilityDecisionStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_PARTIAL = "eligible_partial"
    NOT_ELIGIBLE = "not_eligible"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationConversationEligibilityDecisionAction(str, Enum):
    DECLARE_ELIGIBLE = "declare_eligible"
    DECLARE_ELIGIBLE_PARTIAL = "declare_eligible_partial"
    DECLARE_NOT_ELIGIBLE = "declare_not_eligible"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationConversationEligibilityDecisionConfig:
    maximum_readiness_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_readiness_results <= 0:
            raise ValueError("eligibility decision result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("eligibility decision result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "eligibility decision confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationConversationEligibilityDecisionRequest:
    owner: str
    readiness_results: tuple[LivingConversationConversationReadinessResult, ...]
    decision_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("eligibility decision owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "readiness_results", tuple(self.readiness_results))


@dataclass(frozen=True)
class LivingConversationConversationEligibilityDecisionResult:
    request: LivingConversationConversationEligibilityDecisionRequest
    status: LivingConversationConversationEligibilityDecisionStatus | str
    action: LivingConversationConversationEligibilityDecisionAction | str
    selected_readiness: LivingConversationConversationReadinessResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    confidence: float
    eligible: bool
    partial_context: bool
    not_eligible: bool
    confirmation_required: bool
    conversation_start_allowed: bool
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
    decision_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "status",
            LivingConversationConversationEligibilityDecisionStatus(self.status),
        )
        object.__setattr__(
            self,
            "action",
            LivingConversationConversationEligibilityDecisionAction(self.action),
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("eligibility decision timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "eligibility decision confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("eligibility decision rationale must not be empty")
        if any(
            (
                self.conversation_start_allowed,
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
            raise ValueError("M154 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.ELIGIBLE,
            self.status.ELIGIBLE_PARTIAL,
            self.status.NOT_ELIGIBLE,
        }
        if active:
            if (
                self.selected_readiness is None
                or self.selected_opportunity is None
                or self.confidence <= 0
            ):
                raise ValueError("active decision requires source and confidence")
            if (
                self.selected_readiness.selected_opportunity
                is not self.selected_opportunity
            ):
                raise ValueError(
                    "decision opportunity must come from selected readiness"
                )
            if self.eligible != (
                self.status in {self.status.ELIGIBLE, self.status.ELIGIBLE_PARTIAL}
            ):
                raise ValueError("decision eligible flag is inconsistent")
            if self.partial_context != (self.status is self.status.ELIGIBLE_PARTIAL):
                raise ValueError("decision partial flag is inconsistent")
            if self.not_eligible != (self.status is self.status.NOT_ELIGIBLE):
                raise ValueError("decision not-eligible flag is inconsistent")
        elif (
            self.selected_readiness is not None
            or self.selected_opportunity is not None
            or self.confidence != 0
            or self.eligible
            or self.partial_context
            or self.not_eligible
        ):
            raise ValueError("inactive decision cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("decision confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("eligibility decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.readiness_id for item in self.request.readiness_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.decision_requested),
                self.status.value,
                self.action.value,
                self.selected_readiness.readiness_id
                if self.selected_readiness
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.eligible),
                str(self.partial_context),
                str(self.not_eligible),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationConversationEligibilityDecisionRepository(Protocol):
    def add(
        self, result: LivingConversationConversationEligibilityDecisionResult
    ) -> None: ...
    def get(
        self, decision_id: str
    ) -> LivingConversationConversationEligibilityDecisionResult | None: ...
    def list_all(
        self,
    ) -> tuple[LivingConversationConversationEligibilityDecisionResult, ...]: ...


class InMemoryLivingConversationConversationEligibilityDecisionRepository:
    def __init__(self) -> None:
        self._items: dict[
            str, LivingConversationConversationEligibilityDecisionResult
        ] = {}

    def add(
        self, result: LivingConversationConversationEligibilityDecisionResult
    ) -> None:
        if result.decision_id in self._items:
            raise ValueError("eligibility decision result already exists")
        self._items[result.decision_id] = result

    def get(
        self, decision_id: str
    ) -> LivingConversationConversationEligibilityDecisionResult | None:
        return self._items.get(decision_id)

    def list_all(
        self,
    ) -> tuple[LivingConversationConversationEligibilityDecisionResult, ...]:
        return tuple(self._items.values())
