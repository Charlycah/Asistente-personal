from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_conversation_candidate import (
    LivingConversationConversationCandidateResult,
)
from core.living_conversation_conversation_timing_evaluation import (
    LivingConversationConversationTimingEvaluationResult,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityResult,
)


class CrossContextKind(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    DRIVING = "driving"
    HOME = "home"
    WORK = "work"
    WALKING = "walking"
    TRAVEL = "travel"
    AMBIENT = "ambient"
    PHYSICAL_WORLD = "physical_world"
    UNKNOWN = "unknown"


class CrossContextContinuityStatus(str, Enum):
    CONTINUOUS = "continuous"
    CONTINUOUS_PARTIAL = "continuous_partial"
    INTERRUPTED = "interrupted"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class CrossContextContinuityAction(str, Enum):
    DECLARE_CONTINUITY = "declare_continuity"
    DECLARE_PARTIAL_CONTINUITY = "declare_partial_continuity"
    DECLARE_INTERRUPTION = "declare_interruption"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class CrossContextReference:
    context_id: str
    owner: str
    kind: CrossContextKind | str
    observed_at: datetime
    device_id: str | None = None
    session_reference_id: str | None = None
    continuity_thread_id: str | None = None
    available: bool = True
    authenticated: bool = True

    def __post_init__(self) -> None:
        context_id = self.context_id.strip()
        owner = self.owner.strip()
        if not context_id or not owner:
            raise ValueError("cross-context reference fields must not be blank")
        object.__setattr__(self, "context_id", context_id)
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "kind", CrossContextKind(self.kind))
        if self.observed_at.tzinfo is None:
            raise ValueError(
                "cross-context observation timestamp must be timezone-aware"
            )
        for name in ("device_id", "session_reference_id", "continuity_thread_id"):
            value = getattr(self, name)
            if value is not None:
                normalized = value.strip()
                if not normalized:
                    raise ValueError(f"cross-context {name} must not be blank")
                object.__setattr__(self, name, normalized)


@dataclass(frozen=True)
class CrossContextContinuityConfig:
    maximum_timing_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    maximum_context_gap: timedelta = timedelta(minutes=30)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True
    require_authenticated_contexts: bool = True
    require_shared_session_reference: bool = False
    require_shared_continuity_thread: bool = False

    def __post_init__(self) -> None:
        if self.maximum_timing_results <= 0:
            raise ValueError("cross-context timing result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("cross-context timing result age must be positive")
        if self.maximum_context_gap <= timedelta(0):
            raise ValueError("cross-context gap must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("cross-context confidence must be between zero and one")


@dataclass(frozen=True)
class CrossContextContinuityRequest:
    owner: str
    timing_results: tuple[LivingConversationConversationTimingEvaluationResult, ...]
    source_context: CrossContextReference
    target_context: CrossContextReference
    continuity_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("cross-context continuity owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "timing_results", tuple(self.timing_results))


@dataclass(frozen=True)
class CrossContextContinuityResult:
    request: CrossContextContinuityRequest
    status: CrossContextContinuityStatus | str
    action: CrossContextContinuityAction | str
    selected_timing_evaluation: (
        LivingConversationConversationTimingEvaluationResult | None
    )
    selected_candidate: LivingConversationConversationCandidateResult | None
    selected_opportunity: LivingConversationPresenceOpportunityResult | None
    source_context: CrossContextReference | None
    target_context: CrossContextReference | None
    confidence: float
    continuity_established: bool
    partial_context: bool
    continuity_interrupted: bool
    confirmation_required: bool
    device_handoff_allowed: bool
    context_transfer_allowed: bool
    conversation_start_allowed: bool
    conversational_activation_allowed: bool
    channel_selection_allowed: bool
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
    continuity_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CrossContextContinuityStatus(self.status))
        object.__setattr__(self, "action", CrossContextContinuityAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("cross-context result timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("cross-context confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("cross-context rationale must not be empty")
        if any(
            (
                self.device_handoff_allowed,
                self.context_transfer_allowed,
                self.conversation_start_allowed,
                self.conversational_activation_allowed,
                self.channel_selection_allowed,
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
            raise ValueError("M157 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.CONTINUOUS,
            self.status.CONTINUOUS_PARTIAL,
            self.status.INTERRUPTED,
        }
        if active:
            if (
                any(
                    item is None
                    for item in (
                        self.selected_timing_evaluation,
                        self.selected_candidate,
                        self.selected_opportunity,
                        self.source_context,
                        self.target_context,
                    )
                )
                or self.confidence <= 0
            ):
                raise ValueError("active cross-context result requires full lineage")
            timing = self.selected_timing_evaluation
            candidate = self.selected_candidate
            opportunity = self.selected_opportunity
            assert (
                timing is not None and candidate is not None and opportunity is not None
            )
            if timing.selected_candidate is not candidate:
                raise ValueError("cross-context candidate must come from timing result")
            if timing.selected_opportunity is not opportunity:
                raise ValueError(
                    "cross-context opportunity must come from timing result"
                )
            if self.continuity_established != (
                self.status in {self.status.CONTINUOUS, self.status.CONTINUOUS_PARTIAL}
            ):
                raise ValueError("cross-context continuity flag is inconsistent")
            if self.partial_context != (self.status is self.status.CONTINUOUS_PARTIAL):
                raise ValueError("cross-context partial flag is inconsistent")
            if self.continuity_interrupted != (self.status is self.status.INTERRUPTED):
                raise ValueError("cross-context interruption flag is inconsistent")
        elif any(
            item is not None
            for item in (
                self.selected_timing_evaluation,
                self.selected_candidate,
                self.selected_opportunity,
                self.source_context,
                self.target_context,
            )
        ) or any(
            (
                self.confidence != 0,
                self.continuity_established,
                self.partial_context,
                self.continuity_interrupted,
            )
        ):
            raise ValueError(
                "inactive cross-context result cannot expose active values"
            )
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("cross-context confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.continuity_id and self.continuity_id != expected:
            raise ValueError("cross-context continuity id is inconsistent")
        object.__setattr__(self, "continuity_id", expected)

    def _identity_payload(self) -> str:
        timing_ids = ";".join(
            item.timing_evaluation_id for item in self.request.timing_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                timing_ids,
                self.request.source_context.context_id,
                self.request.target_context.context_id,
                str(self.request.continuity_requested),
                self.status.value,
                self.action.value,
                self.selected_timing_evaluation.timing_evaluation_id
                if self.selected_timing_evaluation
                else "none",
                self.selected_candidate.candidate_id
                if self.selected_candidate
                else "none",
                self.selected_opportunity.opportunity_id
                if self.selected_opportunity
                else "none",
                str(self.confidence),
                str(self.continuity_established),
                str(self.partial_context),
                str(self.continuity_interrupted),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class CrossContextContinuityRepository(Protocol):
    def add(self, result: CrossContextContinuityResult) -> None: ...
    def get(self, continuity_id: str) -> CrossContextContinuityResult | None: ...
    def list_all(self) -> tuple[CrossContextContinuityResult, ...]: ...


class InMemoryCrossContextContinuityRepository:
    def __init__(self) -> None:
        self._items: dict[str, CrossContextContinuityResult] = {}

    def add(self, result: CrossContextContinuityResult) -> None:
        if result.continuity_id in self._items:
            raise ValueError("cross-context continuity result already exists")
        self._items[result.continuity_id] = result

    def get(self, continuity_id: str) -> CrossContextContinuityResult | None:
        return self._items.get(continuity_id)

    def list_all(self) -> tuple[CrossContextContinuityResult, ...]:
        return tuple(self._items.values())
