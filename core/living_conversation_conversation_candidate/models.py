from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_conversation_eligibility_decision import (
    LivingConversationConversationEligibilityDecisionResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationConversationCandidateStatus(str, Enum):
    CANDIDATE = "candidate"
    CANDIDATE_PARTIAL = "candidate_partial"
    WITHHELD = "withheld"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationConversationCandidateAction(str, Enum):
    BUILD_CANDIDATE = "build_candidate"
    BUILD_PARTIAL_CANDIDATE = "build_partial_candidate"
    WITHHOLD_CANDIDATE = "withhold_candidate"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationConversationCandidateConfig:
    maximum_decision_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_decision_results <= 0:
            raise ValueError("candidate decision result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("candidate decision result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("candidate confidence must be between zero and one")


@dataclass(frozen=True)
class LivingConversationConversationCandidateRequest:
    owner: str
    decision_results: tuple[
        LivingConversationConversationEligibilityDecisionResult, ...
    ]
    candidate_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("candidate owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "decision_results", tuple(self.decision_results))


@dataclass(frozen=True)
class LivingConversationConversationCandidateResult:
    request: LivingConversationConversationCandidateRequest
    status: LivingConversationConversationCandidateStatus | str
    action: LivingConversationConversationCandidateAction | str
    selected_decision: LivingConversationConversationEligibilityDecisionResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    confidence: float
    candidate_available: bool
    partial_context: bool
    withheld: bool
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
    candidate_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationConversationCandidateStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationConversationCandidateAction(self.action)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("candidate timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("candidate confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("candidate rationale must not be empty")
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
            raise ValueError("M155 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.CANDIDATE,
            self.status.CANDIDATE_PARTIAL,
            self.status.WITHHELD,
        }
        if active:
            if (
                self.selected_decision is None
                or self.selected_opportunity is None
                or self.confidence <= 0
            ):
                raise ValueError("active candidate requires source and confidence")
            if (
                self.selected_decision.selected_opportunity
                is not self.selected_opportunity
            ):
                raise ValueError(
                    "candidate opportunity must come from selected decision"
                )
            if self.candidate_available != (
                self.status in {self.status.CANDIDATE, self.status.CANDIDATE_PARTIAL}
            ):
                raise ValueError("candidate availability flag is inconsistent")
            if self.partial_context != (self.status is self.status.CANDIDATE_PARTIAL):
                raise ValueError("candidate partial flag is inconsistent")
            if self.withheld != (self.status is self.status.WITHHELD):
                raise ValueError("candidate withheld flag is inconsistent")
        elif (
            self.selected_decision is not None
            or self.selected_opportunity is not None
            or self.confidence != 0
            or self.candidate_available
            or self.partial_context
            or self.withheld
        ):
            raise ValueError("inactive candidate cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("candidate confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.candidate_id and self.candidate_id != expected:
            raise ValueError("candidate id is inconsistent")
        object.__setattr__(self, "candidate_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.decision_id for item in self.request.decision_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.candidate_requested),
                self.status.value,
                self.action.value,
                self.selected_decision.decision_id
                if self.selected_decision
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.candidate_available),
                str(self.partial_context),
                str(self.withheld),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationConversationCandidateRepository(Protocol):
    def add(self, result: LivingConversationConversationCandidateResult) -> None: ...
    def get(
        self, candidate_id: str
    ) -> LivingConversationConversationCandidateResult | None: ...
    def list_all(self) -> tuple[LivingConversationConversationCandidateResult, ...]: ...


class InMemoryLivingConversationConversationCandidateRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationConversationCandidateResult] = {}

    def add(self, result: LivingConversationConversationCandidateResult) -> None:
        if result.candidate_id in self._items:
            raise ValueError("candidate result already exists")
        self._items[result.candidate_id] = result

    def get(
        self, candidate_id: str
    ) -> LivingConversationConversationCandidateResult | None:
        return self._items.get(candidate_id)

    def list_all(self) -> tuple[LivingConversationConversationCandidateResult, ...]:
        return tuple(self._items.values())
