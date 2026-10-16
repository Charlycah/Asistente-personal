from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.living_conversation_presence_policy import (
    LivingConversationPresencePolicyResult,
)


class LivingConversationPresenceOpportunityStatus(str, Enum):
    AVAILABLE = "available"
    AVAILABLE_PARTIAL = "available_partial"
    INHIBITED = "inhibited"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationPresenceOpportunityAction(str, Enum):
    DECLARE_AVAILABLE = "declare_available"
    DECLARE_PARTIAL = "declare_partial"
    INHIBIT = "inhibit"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class LivingConversationPresenceOpportunityKind(str, Enum):
    AVAILABLE = "available"
    AVAILABLE_PARTIAL = "available_partial"
    INHIBITED_BY_POLICY = "inhibited_by_policy"


@dataclass(frozen=True)
class LivingConversationPresenceOpportunityConfig:
    maximum_policy_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_context: bool = True

    def __post_init__(self) -> None:
        if self.maximum_policy_results <= 0:
            raise ValueError("presence opportunity result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence opportunity result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence opportunity confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationPresenceOpportunityRequest:
    owner: str
    policy_results: tuple[LivingConversationPresencePolicyResult, ...]
    opportunity_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence opportunity owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "policy_results", tuple(self.policy_results))


@dataclass(frozen=True)
class LivingConversationPresenceOpportunityResult:
    request: LivingConversationPresenceOpportunityRequest
    status: LivingConversationPresenceOpportunityStatus | str
    action: LivingConversationPresenceOpportunityAction | str
    kind: LivingConversationPresenceOpportunityKind | str | None
    source_policy: LivingConversationPresencePolicyResult | None
    confidence: float
    opportunity_available: bool
    opportunity_inhibited: bool
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
    opportunity_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationPresenceOpportunityStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationPresenceOpportunityAction(self.action)
        )
        if self.kind is not None:
            object.__setattr__(
                self, "kind", LivingConversationPresenceOpportunityKind(self.kind)
            )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence opportunity timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence opportunity confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence opportunity rationale must not be empty")
        forbidden = (
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
        if any(forbidden):
            raise ValueError("M150 cannot authorize downstream capabilities")
        active = self.status in {
            self.status.AVAILABLE,
            self.status.AVAILABLE_PARTIAL,
            self.status.INHIBITED,
        }
        if active:
            if (
                self.source_policy is None
                or self.kind is None
                or self.confidence <= 0
                or self.confirmation_required
            ):
                raise ValueError(
                    "active opportunity requires source, kind and confidence"
                )
            expected_available = self.status in {
                self.status.AVAILABLE,
                self.status.AVAILABLE_PARTIAL,
            }
            if (
                self.opportunity_available != expected_available
                or self.opportunity_inhibited == expected_available
            ):
                raise ValueError("presence opportunity flags are inconsistent")
            if self.partial_context != (self.status is self.status.AVAILABLE_PARTIAL):
                raise ValueError(
                    "presence opportunity partial metadata is inconsistent"
                )
        else:
            if (
                self.source_policy is not None
                or self.kind is not None
                or self.confidence != 0
                or self.opportunity_available
                or self.opportunity_inhibited
                or self.partial_context
            ):
                raise ValueError("inactive opportunity cannot expose active values")
        if self.confirmation_required != (self.status is self.status.REVIEW_REQUIRED):
            raise ValueError("presence opportunity confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.opportunity_id and self.opportunity_id != expected:
            raise ValueError("presence opportunity id is inconsistent")
        object.__setattr__(self, "opportunity_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(item.policy_id for item in self.request.policy_results)
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.opportunity_declared),
                self.status.value,
                self.action.value,
                self.kind.value if self.kind else "none",
                self.source_policy.policy_id if self.source_policy else "none",
                str(self.confidence),
                str(self.opportunity_available),
                str(self.opportunity_inhibited),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationPresenceOpportunityRepository(Protocol):
    def add(self, result: LivingConversationPresenceOpportunityResult) -> None: ...
    def get(
        self, opportunity_id: str
    ) -> LivingConversationPresenceOpportunityResult | None: ...
    def list_all(self) -> tuple[LivingConversationPresenceOpportunityResult, ...]: ...


class InMemoryLivingConversationPresenceOpportunityRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationPresenceOpportunityResult] = {}

    def add(self, result: LivingConversationPresenceOpportunityResult) -> None:
        if result.opportunity_id in self._items:
            raise ValueError("presence opportunity result already exists")
        self._items[result.opportunity_id] = result

    def get(
        self, opportunity_id: str
    ) -> LivingConversationPresenceOpportunityResult | None:
        return self._items.get(opportunity_id)

    def list_all(self) -> tuple[LivingConversationPresenceOpportunityResult, ...]:
        return tuple(self._items.values())
