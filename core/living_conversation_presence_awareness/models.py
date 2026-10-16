from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_presence_consumer import (
    LivingConversationPresenceConsumerResult,
    LivingConversationPresenceCue,
)


class LivingConversationPresenceAwarenessStatus(str, Enum):
    AWARE = "aware"
    AWARE_PARTIAL = "aware_partial"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationPresenceAwarenessAction(str, Enum):
    EXPOSE_AWARENESS = "expose_awareness"
    EXPOSE_PARTIAL_AWARENESS = "expose_partial_awareness"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class LivingConversationPresenceAwarenessKind(str, Enum):
    STABLE = "stable"
    TRANSITIONAL = "transitional"
    UNCERTAIN = "uncertain"
    INTERRUPTED = "interrupted"


@dataclass(frozen=True)
class LivingConversationPresenceAwarenessPolicy:
    maximum_consumer_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_consumer_results <= 0:
            raise ValueError(
                "living conversation awareness result limit must be positive"
            )
        if self.maximum_result_age <= timedelta(0):
            raise ValueError(
                "living conversation awareness result age must be positive"
            )
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "living conversation awareness confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationPresenceAwarenessRequest:
    owner: str
    consumer_results: tuple[LivingConversationPresenceConsumerResult, ...]
    awareness_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("living conversation awareness owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "consumer_results", tuple(self.consumer_results))


@dataclass(frozen=True)
class LivingConversationPresenceAwarenessState:
    source_cue: LivingConversationPresenceCue
    awareness_kind: LivingConversationPresenceAwarenessKind | str
    presence_available: bool
    stable_presence: bool
    transition_present: bool
    uncertainty_present: bool
    continuity_interrupted: bool
    partial_context: bool
    confidence: float
    assessed_at: datetime
    state_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "awareness_kind",
            LivingConversationPresenceAwarenessKind(self.awareness_kind),
        )
        if self.assessed_at.tzinfo is None:
            raise ValueError(
                "living conversation awareness timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "living conversation awareness confidence must be between zero and one"
            )
        expected_flags = {
            LivingConversationPresenceAwarenessKind.STABLE: (True, False, False, False),
            LivingConversationPresenceAwarenessKind.TRANSITIONAL: (
                False,
                True,
                False,
                False,
            ),
            LivingConversationPresenceAwarenessKind.UNCERTAIN: (
                False,
                False,
                True,
                False,
            ),
            LivingConversationPresenceAwarenessKind.INTERRUPTED: (
                False,
                False,
                False,
                True,
            ),
        }[self.awareness_kind]
        if (
            self.stable_presence,
            self.transition_present,
            self.uncertainty_present,
            self.continuity_interrupted,
        ) != expected_flags:
            raise ValueError("living conversation awareness flags are inconsistent")
        if not self.presence_available:
            raise ValueError("living conversation awareness state requires presence")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.state_id and self.state_id != expected:
            raise ValueError("living conversation awareness state id is inconsistent")
        object.__setattr__(self, "state_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.source_cue.cue_id,
                self.awareness_kind.value,
                str(self.presence_available),
                str(self.stable_presence),
                str(self.transition_present),
                str(self.uncertainty_present),
                str(self.continuity_interrupted),
                str(self.partial_context),
                str(self.confidence),
                self.assessed_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class LivingConversationPresenceAwarenessResult:
    request: LivingConversationPresenceAwarenessRequest
    status: LivingConversationPresenceAwarenessStatus | str
    action: LivingConversationPresenceAwarenessAction | str
    source_consumer: LivingConversationPresenceConsumerResult | None
    states: tuple[LivingConversationPresenceAwarenessState, ...]
    confidence: float
    presence_awareness_available: bool
    partial_context: bool
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
    awareness_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationPresenceAwarenessStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationPresenceAwarenessAction(self.action)
        )
        object.__setattr__(self, "states", tuple(self.states))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "living conversation awareness timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "living conversation awareness confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError(
                "living conversation awareness rationale must not be empty"
            )
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
            raise ValueError("M148 cannot authorize downstream capabilities")
        active = self.status in {
            LivingConversationPresenceAwarenessStatus.AWARE,
            LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL,
        }
        if active:
            if (
                self.source_consumer is None
                or not self.states
                or not self.presence_awareness_available
                or self.confidence <= 0
                or self.confirmation_required
            ):
                raise ValueError("active awareness result requires source and states")
            expected_partial = (
                self.status is LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL
            )
            if self.partial_context != expected_partial:
                raise ValueError("active awareness metadata is inconsistent")
        else:
            if (
                self.source_consumer is not None
                or self.states
                or self.confidence != 0
                or self.presence_awareness_available
                or self.partial_context
            ):
                raise ValueError(
                    "inactive awareness result cannot expose active values"
                )
        if self.confirmation_required != (
            self.status is LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED
        ):
            raise ValueError("awareness confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.awareness_id and self.awareness_id != expected:
            raise ValueError("living conversation awareness id is inconsistent")
        object.__setattr__(self, "awareness_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.consumption_id for item in self.request.consumer_results
        )
        state_ids = ";".join(item.state_id for item in self.states)
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.awareness_declared),
                self.status.value,
                self.action.value,
                self.source_consumer.consumption_id if self.source_consumer else "none",
                state_ids or "none",
                str(self.confidence),
                str(self.presence_awareness_available),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationPresenceAwarenessRepository(Protocol):
    def add(self, result: LivingConversationPresenceAwarenessResult) -> None: ...
    def get(
        self, awareness_id: str
    ) -> LivingConversationPresenceAwarenessResult | None: ...
    def list_all(self) -> tuple[LivingConversationPresenceAwarenessResult, ...]: ...


class InMemoryLivingConversationPresenceAwarenessRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationPresenceAwarenessResult] = {}

    def add(self, result: LivingConversationPresenceAwarenessResult) -> None:
        if result.awareness_id in self._items:
            raise ValueError(
                "living conversation presence awareness result already exists"
            )
        self._items[result.awareness_id] = result

    def get(
        self, awareness_id: str
    ) -> LivingConversationPresenceAwarenessResult | None:
        return self._items.get(awareness_id)

    def list_all(self) -> tuple[LivingConversationPresenceAwarenessResult, ...]:
        return tuple(self._items.values())
