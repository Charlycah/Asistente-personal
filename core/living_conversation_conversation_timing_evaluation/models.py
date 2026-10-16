from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_conversation_candidate import (
    LivingConversationConversationCandidateResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class LivingConversationConversationTimingEvaluationStatus(str, Enum):
    TIMELY = "timely"
    TIMELY_PARTIAL = "timely_partial"
    DEFERRED = "deferred"
    NOT_TIMELY = "not_timely"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationConversationTimingEvaluationAction(str, Enum):
    DECLARE_TIMELY = "declare_timely"
    DECLARE_TIMELY_PARTIAL = "declare_timely_partial"
    DEFER = "defer"
    DECLARE_NOT_TIMELY = "declare_not_timely"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationConversationTimingEvaluationConfig:
    maximum_candidate_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_candidate_results <= 0:
            raise ValueError(
                "timing evaluation candidate result limit must be positive"
            )
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("timing evaluation candidate result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "timing evaluation confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationConversationTimingEvaluationRequest:
    owner: str
    candidate_results: tuple[LivingConversationConversationCandidateResult, ...]
    not_before: datetime | None = None
    expires_at: datetime | None = None
    evaluation_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("timing evaluation owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "candidate_results", tuple(self.candidate_results))
        for value in (self.not_before, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("timing window timestamps must be timezone-aware")
        if (
            self.not_before is not None
            and self.expires_at is not None
            and self.not_before > self.expires_at
        ):
            raise ValueError("timing window start must not follow its expiration")


@dataclass(frozen=True)
class LivingConversationConversationTimingEvaluationResult:
    request: LivingConversationConversationTimingEvaluationRequest
    status: LivingConversationConversationTimingEvaluationStatus | str
    action: LivingConversationConversationTimingEvaluationAction | str
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    confidence: float
    timely_now: bool
    partial_context: bool
    deferred: bool
    not_timely: bool
    confirmation_required: bool
    conversation_start_allowed: bool
    conversational_activation_allowed: bool
    timing_selection_allowed: bool
    scheduling_allowed: bool
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
    timing_evaluation_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "status",
            LivingConversationConversationTimingEvaluationStatus(self.status),
        )
        object.__setattr__(
            self,
            "action",
            LivingConversationConversationTimingEvaluationAction(self.action),
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("timing evaluation timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "timing evaluation confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("timing evaluation rationale must not be empty")
        if any(
            (
                self.conversation_start_allowed,
                self.conversational_activation_allowed,
                self.timing_selection_allowed,
                self.scheduling_allowed,
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
            raise ValueError("M156 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.TIMELY,
            self.status.TIMELY_PARTIAL,
            self.status.DEFERRED,
            self.status.NOT_TIMELY,
        }
        if active:
            if (
                self.selected_candidate is None
                or self.selected_opportunity is None
                or self.confidence <= 0
            ):
                raise ValueError(
                    "active timing evaluation requires source and confidence"
                )
            if (
                self.selected_candidate.selected_opportunity
                is not self.selected_opportunity
            ):
                raise ValueError("timing opportunity must come from selected candidate")
            if self.timely_now != (
                self.status in {self.status.TIMELY, self.status.TIMELY_PARTIAL}
            ):
                raise ValueError("timely-now flag is inconsistent")
            if self.partial_context != (self.status is self.status.TIMELY_PARTIAL):
                raise ValueError("timing partial flag is inconsistent")
            if self.deferred != (self.status is self.status.DEFERRED):
                raise ValueError("timing deferred flag is inconsistent")
            if self.not_timely != (self.status is self.status.NOT_TIMELY):
                raise ValueError("not-timely flag is inconsistent")
        elif (
            self.selected_candidate is not None
            or self.selected_opportunity is not None
            or self.confidence != 0
            or self.timely_now
            or self.partial_context
            or self.deferred
            or self.not_timely
        ):
            raise ValueError("inactive timing evaluation cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("timing evaluation confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.timing_evaluation_id and self.timing_evaluation_id != expected:
            raise ValueError("timing evaluation id is inconsistent")
        object.__setattr__(self, "timing_evaluation_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.candidate_id for item in self.request.candidate_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                self.request.not_before.isoformat()
                if self.request.not_before
                else "none",
                self.request.expires_at.isoformat()
                if self.request.expires_at
                else "none",
                str(self.request.evaluation_requested),
                self.status.value,
                self.action.value,
                self.selected_candidate.candidate_id
                if self.selected_candidate
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.timely_now),
                str(self.partial_context),
                str(self.deferred),
                str(self.not_timely),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationConversationTimingEvaluationRepository(Protocol):
    def add(
        self, result: LivingConversationConversationTimingEvaluationResult
    ) -> None: ...
    def get(
        self, timing_evaluation_id: str
    ) -> LivingConversationConversationTimingEvaluationResult | None: ...
    def list_all(
        self,
    ) -> tuple[LivingConversationConversationTimingEvaluationResult, ...]: ...


class InMemoryLivingConversationConversationTimingEvaluationRepository:
    def __init__(self) -> None:
        self._items: dict[
            str, LivingConversationConversationTimingEvaluationResult
        ] = {}

    def add(self, result: LivingConversationConversationTimingEvaluationResult) -> None:
        if result.timing_evaluation_id in self._items:
            raise ValueError("timing evaluation result already exists")
        self._items[result.timing_evaluation_id] = result

    def get(
        self, timing_evaluation_id: str
    ) -> LivingConversationConversationTimingEvaluationResult | None:
        return self._items.get(timing_evaluation_id)

    def list_all(
        self,
    ) -> tuple[LivingConversationConversationTimingEvaluationResult, ...]:
        return tuple(self._items.values())
