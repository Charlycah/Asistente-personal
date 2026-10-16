from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_presence_awareness import (
    LivingConversationPresenceAwarenessResult,
    LivingConversationPresenceAwarenessState,
)


class LivingConversationPresencePolicyStatus(str, Enum):
    ELIGIBLE = "eligible"
    ELIGIBLE_PARTIAL = "eligible_partial"
    INHIBITED = "inhibited"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationPresencePolicyAction(str, Enum):
    MARK_ELIGIBLE = "mark_eligible"
    MARK_PARTIALLY_ELIGIBLE = "mark_partially_eligible"
    INHIBIT = "inhibit"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class LivingConversationPresenceEligibility(str, Enum):
    ELIGIBLE = "eligible"
    INHIBITED_TRANSITION = "inhibited_transition"
    INHIBITED_UNCERTAINTY = "inhibited_uncertainty"
    INHIBITED_INTERRUPTION = "inhibited_interruption"


@dataclass(frozen=True)
class LivingConversationPresencePolicyConfig:
    maximum_awareness_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_awareness_results <= 0:
            raise ValueError(
                "living conversation presence policy result limit must be positive"
            )
        if self.maximum_result_age <= timedelta(0):
            raise ValueError(
                "living conversation presence policy result age must be positive"
            )
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("presence policy confidence must be between zero and one")


@dataclass(frozen=True)
class LivingConversationPresencePolicyRequest:
    owner: str
    awareness_results: tuple[LivingConversationPresenceAwarenessResult, ...]
    policy_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError(
                "living conversation presence policy owner must not be blank"
            )
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "awareness_results", tuple(self.awareness_results))


@dataclass(frozen=True)
class LivingConversationPresencePolicyEvaluation:
    source_state: LivingConversationPresenceAwarenessState
    eligibility: LivingConversationPresenceEligibility | str
    eligible: bool
    inhibited: bool
    partial_context: bool
    confidence: float
    evaluated_at: datetime
    evaluation_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "eligibility", LivingConversationPresenceEligibility(self.eligibility)
        )
        if self.evaluated_at.tzinfo is None:
            raise ValueError(
                "living conversation presence policy timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError("presence policy confidence must be between zero and one")
        expected_eligible = (
            self.eligibility is LivingConversationPresenceEligibility.ELIGIBLE
        )
        if self.eligible != expected_eligible or self.inhibited == expected_eligible:
            raise ValueError(
                "living conversation presence policy flags are inconsistent"
            )
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.evaluation_id and self.evaluation_id != expected:
            raise ValueError(
                "living conversation presence policy evaluation id is inconsistent"
            )
        object.__setattr__(self, "evaluation_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.source_state.state_id,
                self.eligibility.value,
                str(self.eligible),
                str(self.inhibited),
                str(self.partial_context),
                str(self.confidence),
                self.evaluated_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class LivingConversationPresencePolicyResult:
    request: LivingConversationPresencePolicyRequest
    status: LivingConversationPresencePolicyStatus | str
    action: LivingConversationPresencePolicyAction | str
    source_awareness: LivingConversationPresenceAwarenessResult | None
    evaluations: tuple[LivingConversationPresencePolicyEvaluation, ...]
    confidence: float
    presence_context_eligible: bool
    presence_context_inhibited: bool
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
    policy_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationPresencePolicyStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationPresencePolicyAction(self.action)
        )
        object.__setattr__(self, "evaluations", tuple(self.evaluations))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "living conversation presence policy timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError("presence policy confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError(
                "living conversation presence policy rationale must not be empty"
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
            raise ValueError("M149 cannot authorize downstream capabilities")
        active = self.status in {
            LivingConversationPresencePolicyStatus.ELIGIBLE,
            LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL,
            LivingConversationPresencePolicyStatus.INHIBITED,
        }
        if active:
            if (
                self.source_awareness is None
                or not self.evaluations
                or self.confidence <= 0
                or self.confirmation_required
            ):
                raise ValueError(
                    "active presence policy result requires source and evaluations"
                )
            expected_eligible = self.status in {
                LivingConversationPresencePolicyStatus.ELIGIBLE,
                LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL,
            }
            if (
                self.presence_context_eligible != expected_eligible
                or self.presence_context_inhibited == expected_eligible
            ):
                raise ValueError("presence policy outcome flags are inconsistent")
            expected_partial = (
                self.status is LivingConversationPresencePolicyStatus.ELIGIBLE_PARTIAL
            )
            if self.partial_context != expected_partial:
                raise ValueError("presence policy partial metadata is inconsistent")
        else:
            if (
                self.source_awareness is not None
                or self.evaluations
                or self.confidence != 0
                or self.presence_context_eligible
                or self.presence_context_inhibited
                or self.partial_context
            ):
                raise ValueError(
                    "inactive presence policy result cannot expose active values"
                )
        if self.confirmation_required != (
            self.status is LivingConversationPresencePolicyStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence policy confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.policy_id and self.policy_id != expected:
            raise ValueError("living conversation presence policy id is inconsistent")
        object.__setattr__(self, "policy_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.awareness_id for item in self.request.awareness_results
        )
        evaluation_ids = ";".join(item.evaluation_id for item in self.evaluations)
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.policy_declared),
                self.status.value,
                self.action.value,
                self.source_awareness.awareness_id if self.source_awareness else "none",
                evaluation_ids or "none",
                str(self.confidence),
                str(self.presence_context_eligible),
                str(self.presence_context_inhibited),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationPresencePolicyRepository(Protocol):
    def add(self, result: LivingConversationPresencePolicyResult) -> None: ...
    def get(self, policy_id: str) -> LivingConversationPresencePolicyResult | None: ...
    def list_all(self) -> tuple[LivingConversationPresencePolicyResult, ...]: ...


class InMemoryLivingConversationPresencePolicyRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationPresencePolicyResult] = {}

    def add(self, result: LivingConversationPresencePolicyResult) -> None:
        if result.policy_id in self._items:
            raise ValueError(
                "living conversation presence policy result already exists"
            )
        self._items[result.policy_id] = result

    def get(self, policy_id: str) -> LivingConversationPresencePolicyResult | None:
        return self._items.get(policy_id)

    def list_all(self) -> tuple[LivingConversationPresencePolicyResult, ...]:
        return tuple(self._items.values())
