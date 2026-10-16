from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_publication import PresenceContextPublicationResult
from core.presence_context_subscription import PresenceContextSubscriptionResult


class PresenceContextDispatchStatus(str, Enum):
    PLANNED = "planned"
    PLANNED_PARTIAL = "planned_partial"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextDispatchAction(str, Enum):
    PLAN = "plan"
    PLAN_PARTIAL = "plan_partial"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class PresenceContextDispatchPolicy:
    maximum_publication_results: int = 64
    maximum_subscription_results: int = 256
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_publication_results <= 0:
            raise ValueError("presence dispatch publication limit must be positive")
        if self.maximum_subscription_results <= 0:
            raise ValueError("presence dispatch subscription limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence dispatch result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence dispatch confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContextDispatchRequest:
    owner: str
    publication_results: tuple[PresenceContextPublicationResult, ...]
    subscription_results: tuple[PresenceContextSubscriptionResult, ...]
    dispatch_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence dispatch owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "publication_results", tuple(self.publication_results))
        object.__setattr__(
            self, "subscription_results", tuple(self.subscription_results)
        )


@dataclass(frozen=True)
class PresenceContextDispatchDestination:
    subscription: PresenceContextSubscriptionResult
    subscriber_id: str
    publication_topic: str
    schema_version: str
    partial_context: bool

    def __post_init__(self) -> None:
        if not self.subscriber_id.strip():
            raise ValueError("presence dispatch subscriber id must not be blank")
        if not self.publication_topic.strip():
            raise ValueError("presence dispatch topic must not be blank")
        if not self.schema_version.strip():
            raise ValueError("presence dispatch schema version must not be blank")


@dataclass(frozen=True)
class PresenceContextDispatchResult:
    request: PresenceContextDispatchRequest
    status: PresenceContextDispatchStatus | str
    action: PresenceContextDispatchAction | str
    source_publication: PresenceContextPublicationResult | None
    destinations: tuple[PresenceContextDispatchDestination, ...]
    confidence: float
    dispatch_planned: bool
    partial_context: bool
    confirmation_required: bool
    delivery_allowed: bool
    callback_invocation_allowed: bool
    consumer_processing_allowed: bool
    routing_execution_allowed: bool
    identity_inference_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    response_decision_allowed: bool
    behavior_adaptation_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    dispatch_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PresenceContextDispatchStatus(self.status))
        object.__setattr__(self, "action", PresenceContextDispatchAction(self.action))
        object.__setattr__(self, "destinations", tuple(self.destinations))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence dispatch timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence dispatch confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence dispatch rationale must not be empty")
        if any(
            (
                self.delivery_allowed,
                self.callback_invocation_allowed,
                self.consumer_processing_allowed,
                self.routing_execution_allowed,
                self.identity_inference_allowed,
                self.activity_inference_allowed,
                self.intent_inference_allowed,
                self.response_decision_allowed,
                self.behavior_adaptation_allowed,
                self.provider_call_allowed,
                self.automation_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M144 cannot authorize downstream capabilities")
        planned = self.status in {
            PresenceContextDispatchStatus.PLANNED,
            PresenceContextDispatchStatus.PLANNED_PARTIAL,
        }
        if planned:
            if self.source_publication is None or not self.destinations:
                raise ValueError(
                    "planned dispatch requires publication and destinations"
                )
            if not self.dispatch_planned or self.confidence <= 0:
                raise ValueError("planned dispatch metadata is incomplete")
            expected_partial = (
                self.status is PresenceContextDispatchStatus.PLANNED_PARTIAL
            )
            if self.partial_context != expected_partial:
                raise ValueError("presence dispatch partial flag is inconsistent")
            if self.confirmation_required:
                raise ValueError("planned dispatch cannot require confirmation")
        else:
            if self.source_publication is not None or self.destinations:
                raise ValueError("inactive dispatch cannot expose plan data")
            if self.confidence != 0 or self.dispatch_planned or self.partial_context:
                raise ValueError("inactive dispatch cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextDispatchStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence dispatch confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.dispatch_id and self.dispatch_id != expected:
            raise ValueError("presence context dispatch id is inconsistent")
        object.__setattr__(self, "dispatch_id", expected)

    def _identity_payload(self) -> str:
        publication_ids = ";".join(
            item.publication_id for item in self.request.publication_results
        )
        subscription_ids = ";".join(
            item.subscription_id for item in self.request.subscription_results
        )
        destination_ids = ";".join(
            item.subscription.subscription_id for item in self.destinations
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                publication_ids,
                subscription_ids,
                str(self.request.dispatch_declared),
                self.status.value,
                self.action.value,
                self.source_publication.publication_id
                if self.source_publication
                else "none",
                destination_ids or "none",
                str(self.confidence),
                str(self.dispatch_planned),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextDispatchRepository(Protocol):
    def add(self, result: PresenceContextDispatchResult) -> None: ...
    def get(self, dispatch_id: str) -> PresenceContextDispatchResult | None: ...
    def list_all(self) -> tuple[PresenceContextDispatchResult, ...]: ...


class InMemoryPresenceContextDispatchRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextDispatchResult] = {}

    def add(self, result: PresenceContextDispatchResult) -> None:
        if result.dispatch_id in self._items:
            raise ValueError("presence context dispatch result already exists")
        self._items[result.dispatch_id] = result

    def get(self, dispatch_id: str) -> PresenceContextDispatchResult | None:
        return self._items.get(dispatch_id)

    def list_all(self) -> tuple[PresenceContextDispatchResult, ...]:
        return tuple(self._items.values())
