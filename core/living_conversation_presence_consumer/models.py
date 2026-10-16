from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_consumption_gateway import (
    PresenceContextConsumptionGatewayResult,
)
from core.presence_situation_assessment import (
    PresenceSituationKind,
    PresenceSituationSignal,
)


class LivingConversationPresenceConsumerStatus(str, Enum):
    ADAPTED = "adapted"
    ADAPTED_PARTIAL = "adapted_partial"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LivingConversationPresenceConsumerAction(str, Enum):
    EXPOSE_CUE = "expose_cue"
    EXPOSE_PARTIAL_CUE = "expose_partial_cue"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LivingConversationPresenceConsumerPolicy:
    maximum_gateway_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_gateway_results <= 0:
            raise ValueError(
                "living conversation presence gateway limit must be positive"
            )
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("living conversation presence result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "living conversation presence confidence must be between zero and one"
            )


@dataclass(frozen=True)
class LivingConversationPresenceConsumerRequest:
    owner: str
    gateway_results: tuple[PresenceContextConsumptionGatewayResult, ...]
    consumer_id: str = "living-conversation"
    consumption_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        consumer_id = self.consumer_id.strip()
        if not owner:
            raise ValueError("living conversation presence owner must not be blank")
        if not consumer_id:
            raise ValueError("living conversation presence consumer must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "consumer_id", consumer_id)
        object.__setattr__(self, "gateway_results", tuple(self.gateway_results))


@dataclass(frozen=True)
class LivingConversationPresenceCue:
    access_id: str
    situation_kind: PresenceSituationKind | str
    situation_signal: PresenceSituationSignal | str
    conversation_context: str | None
    partial_context: bool
    confidence: float
    adapted_at: datetime
    cue_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "situation_kind", PresenceSituationKind(self.situation_kind)
        )
        object.__setattr__(
            self, "situation_signal", PresenceSituationSignal(self.situation_signal)
        )
        if not self.access_id.strip():
            raise ValueError("living conversation presence access id must not be blank")
        if self.adapted_at.tzinfo is None:
            raise ValueError(
                "living conversation presence cue timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "living conversation presence cue confidence must be between "
                "zero and one"
            )
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.cue_id and self.cue_id != expected:
            raise ValueError("living conversation presence cue id is inconsistent")
        object.__setattr__(self, "cue_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.access_id,
                self.situation_kind.value,
                self.situation_signal.value,
                self.conversation_context or "none",
                str(self.partial_context),
                str(self.confidence),
                self.adapted_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class LivingConversationPresenceConsumerResult:
    request: LivingConversationPresenceConsumerRequest
    status: LivingConversationPresenceConsumerStatus | str
    action: LivingConversationPresenceConsumerAction | str
    source_gateway: PresenceContextConsumptionGatewayResult | None
    cues: tuple[LivingConversationPresenceCue, ...]
    confidence: float
    context_adapted: bool
    partial_context: bool
    confirmation_required: bool
    conversation_decision_allowed: bool
    conversational_activation_allowed: bool
    prompt_generation_allowed: bool
    response_realization_allowed: bool
    consumer_execution_allowed: bool
    identity_inference_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    behavior_adaptation_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    consumption_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", LivingConversationPresenceConsumerStatus(self.status)
        )
        object.__setattr__(
            self, "action", LivingConversationPresenceConsumerAction(self.action)
        )
        object.__setattr__(self, "cues", tuple(self.cues))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "living conversation presence timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "living conversation presence confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("living conversation presence rationale must not be empty")
        if any(
            (
                self.conversation_decision_allowed,
                self.conversational_activation_allowed,
                self.prompt_generation_allowed,
                self.response_realization_allowed,
                self.consumer_execution_allowed,
                self.identity_inference_allowed,
                self.activity_inference_allowed,
                self.intent_inference_allowed,
                self.behavior_adaptation_allowed,
                self.provider_call_allowed,
                self.automation_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M147 cannot authorize downstream capabilities")
        active = self.status in {
            LivingConversationPresenceConsumerStatus.ADAPTED,
            LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL,
        }
        if active:
            if (
                self.source_gateway is None
                or not self.cues
                or not self.context_adapted
                or self.confidence <= 0
            ):
                raise ValueError(
                    "active living conversation presence result requires source "
                    "and cues"
                )
            expected_partial = (
                self.status is LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL
            )
            if self.partial_context != expected_partial or self.confirmation_required:
                raise ValueError(
                    "living conversation presence active metadata is inconsistent"
                )
        else:
            if (
                self.source_gateway is not None
                or self.cues
                or self.confidence != 0
                or self.context_adapted
                or self.partial_context
            ):
                raise ValueError(
                    "inactive living conversation presence result cannot expose "
                    "active values"
                )
        if self.confirmation_required != (
            self.status is LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED
        ):
            raise ValueError(
                "living conversation presence confirmation flag is inconsistent"
            )
        expected = sha256(self._identity_payload().encode()).hexdigest()
        if self.consumption_id and self.consumption_id != expected:
            raise ValueError(
                "living conversation presence consumption id is inconsistent"
            )
        object.__setattr__(self, "consumption_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(item.gateway_id for item in self.request.gateway_results)
        cue_ids = ";".join(item.cue_id for item in self.cues)
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.consumer_id.casefold(),
                source_ids,
                str(self.request.consumption_declared),
                self.status.value,
                self.action.value,
                self.source_gateway.gateway_id if self.source_gateway else "none",
                cue_ids or "none",
                str(self.confidence),
                str(self.context_adapted),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class LivingConversationPresenceConsumerRepository(Protocol):
    def add(self, result: LivingConversationPresenceConsumerResult) -> None: ...
    def get(
        self, consumption_id: str
    ) -> LivingConversationPresenceConsumerResult | None: ...
    def list_all(self) -> tuple[LivingConversationPresenceConsumerResult, ...]: ...


class InMemoryLivingConversationPresenceConsumerRepository:
    def __init__(self) -> None:
        self._items: dict[str, LivingConversationPresenceConsumerResult] = {}

    def add(self, result: LivingConversationPresenceConsumerResult) -> None:
        if result.consumption_id in self._items:
            raise ValueError(
                "living conversation presence consumer result already exists"
            )
        self._items[result.consumption_id] = result

    def get(
        self, consumption_id: str
    ) -> LivingConversationPresenceConsumerResult | None:
        return self._items.get(consumption_id)

    def list_all(self) -> tuple[LivingConversationPresenceConsumerResult, ...]:
        return tuple(self._items.values())
