from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_dispatch import (
    PresenceContextDispatchDestination,
    PresenceContextDispatchResult,
)


class PresenceContextDeliveryStatus(str, Enum):
    DELIVERED = "delivered"
    DELIVERED_PARTIAL = "delivered_partial"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextDeliveryAction(str, Enum):
    MATERIALIZE = "materialize"
    MATERIALIZE_PARTIAL = "materialize_partial"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceContextDeliveryItemStatus(str, Enum):
    DELIVERED = "delivered"
    DELIVERED_PARTIAL = "delivered_partial"


@dataclass(frozen=True)
class PresenceContextDeliveryPolicy:
    maximum_dispatch_results: int = 64
    maximum_destinations: int = 256
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_dispatch_results <= 0:
            raise ValueError("presence delivery dispatch limit must be positive")
        if self.maximum_destinations <= 0:
            raise ValueError("presence delivery destination limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence delivery result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence delivery confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContextDeliveryRequest:
    owner: str
    dispatch_results: tuple[PresenceContextDispatchResult, ...]
    delivery_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence delivery owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "dispatch_results", tuple(self.dispatch_results))


@dataclass(frozen=True)
class PresenceContextDeliveryItem:
    destination: PresenceContextDispatchDestination
    status: PresenceContextDeliveryItemStatus | str
    subscriber_id: str
    publication_id: str
    publication_topic: str
    schema_version: str
    partial_context: bool
    delivered_at: datetime
    delivery_item_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceContextDeliveryItemStatus(self.status)
        )
        if not self.subscriber_id.strip() or not self.publication_id.strip():
            raise ValueError("presence delivery item identity must not be blank")
        if not self.publication_topic.strip() or not self.schema_version.strip():
            raise ValueError("presence delivery item contract must not be blank")
        if self.delivered_at.tzinfo is None:
            raise ValueError("presence delivery item timestamp must be timezone-aware")
        expected_partial = (
            self.status is PresenceContextDeliveryItemStatus.DELIVERED_PARTIAL
        )
        if self.partial_context != expected_partial:
            raise ValueError("presence delivery item partial flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.delivery_item_id and self.delivery_item_id != expected:
            raise ValueError("presence delivery item id is inconsistent")
        object.__setattr__(self, "delivery_item_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.destination.subscription.subscription_id,
                self.subscriber_id,
                self.publication_id,
                self.publication_topic,
                self.schema_version,
                self.status.value,
                str(self.partial_context),
                self.delivered_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class PresenceContextDeliveryResult:
    request: PresenceContextDeliveryRequest
    status: PresenceContextDeliveryStatus | str
    action: PresenceContextDeliveryAction | str
    source_dispatch: PresenceContextDispatchResult | None
    deliveries: tuple[PresenceContextDeliveryItem, ...]
    confidence: float
    delivery_materialized: bool
    partial_context: bool
    confirmation_required: bool
    transport_delivery_allowed: bool
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
    delivery_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PresenceContextDeliveryStatus(self.status))
        object.__setattr__(self, "action", PresenceContextDeliveryAction(self.action))
        object.__setattr__(self, "deliveries", tuple(self.deliveries))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence delivery timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence delivery confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence delivery rationale must not be empty")
        if any(
            (
                self.transport_delivery_allowed,
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
            raise ValueError("M145 cannot authorize downstream capabilities")
        active = self.status in {
            PresenceContextDeliveryStatus.DELIVERED,
            PresenceContextDeliveryStatus.DELIVERED_PARTIAL,
        }
        if active:
            if self.source_dispatch is None or not self.deliveries:
                raise ValueError("materialized delivery requires dispatch and items")
            if not self.delivery_materialized or self.confidence <= 0:
                raise ValueError("materialized delivery metadata is incomplete")
            expected_partial = (
                self.status is PresenceContextDeliveryStatus.DELIVERED_PARTIAL
            )
            if self.partial_context != expected_partial:
                raise ValueError("presence delivery partial flag is inconsistent")
            if self.confirmation_required:
                raise ValueError("materialized delivery cannot require confirmation")
        else:
            if self.source_dispatch is not None or self.deliveries:
                raise ValueError("inactive delivery cannot expose delivery data")
            if (
                self.confidence != 0
                or self.delivery_materialized
                or self.partial_context
            ):
                raise ValueError("inactive delivery cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextDeliveryStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence delivery confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.delivery_id and self.delivery_id != expected:
            raise ValueError("presence context delivery id is inconsistent")
        object.__setattr__(self, "delivery_id", expected)

    def _identity_payload(self) -> str:
        dispatch_ids = ";".join(
            item.dispatch_id for item in self.request.dispatch_results
        )
        item_ids = ";".join(item.delivery_item_id for item in self.deliveries)
        return "|".join(
            (
                self.request.owner.casefold(),
                dispatch_ids,
                str(self.request.delivery_declared),
                self.status.value,
                self.action.value,
                self.source_dispatch.dispatch_id if self.source_dispatch else "none",
                item_ids or "none",
                str(self.confidence),
                str(self.delivery_materialized),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextDeliveryRepository(Protocol):
    def add(self, result: PresenceContextDeliveryResult) -> None: ...
    def get(self, delivery_id: str) -> PresenceContextDeliveryResult | None: ...
    def list_all(self) -> tuple[PresenceContextDeliveryResult, ...]: ...


class InMemoryPresenceContextDeliveryRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextDeliveryResult] = {}

    def add(self, result: PresenceContextDeliveryResult) -> None:
        if result.delivery_id in self._items:
            raise ValueError("presence context delivery result already exists")
        self._items[result.delivery_id] = result

    def get(self, delivery_id: str) -> PresenceContextDeliveryResult | None:
        return self._items.get(delivery_id)

    def list_all(self) -> tuple[PresenceContextDeliveryResult, ...]:
        return tuple(self._items.values())
