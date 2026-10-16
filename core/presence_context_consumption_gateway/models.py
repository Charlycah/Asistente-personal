from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_delivery import (
    PresenceContextDeliveryItem,
    PresenceContextDeliveryResult,
)


class PresenceContextConsumptionGatewayStatus(str, Enum):
    AVAILABLE = "available"
    AVAILABLE_PARTIAL = "available_partial"
    EMPTY = "empty"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextConsumptionGatewayAction(str, Enum):
    EXPOSE = "expose"
    EXPOSE_PARTIAL = "expose_partial"
    HOLD = "hold"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class PresenceContextConsumptionGatewayPolicy:
    maximum_delivery_results: int = 64
    maximum_access_items: int = 256
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_delivery_results <= 0:
            raise ValueError(
                "presence consumption gateway delivery limit must be positive"
            )
        if self.maximum_access_items <= 0:
            raise ValueError(
                "presence consumption gateway access limit must be positive"
            )
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence consumption gateway result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence consumption gateway confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContextConsumptionGatewayRequest:
    owner: str
    delivery_results: tuple[PresenceContextDeliveryResult, ...]
    consumer_id: str
    expected_topic: str = "roby.ambient.presence.context"
    accepted_schema_versions: tuple[str, ...] = ("1.0",)
    gateway_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        consumer_id = self.consumer_id.strip()
        topic = self.expected_topic.strip()
        versions = tuple(
            dict.fromkeys(
                item.strip() for item in self.accepted_schema_versions if item.strip()
            )
        )
        if not owner:
            raise ValueError("presence consumption gateway owner must not be blank")
        if not consumer_id:
            raise ValueError("presence consumption gateway consumer must not be blank")
        if not topic:
            raise ValueError("presence consumption gateway topic must not be blank")
        if not versions:
            raise ValueError(
                "presence consumption gateway schema versions must not be empty"
            )
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "consumer_id", consumer_id)
        object.__setattr__(self, "expected_topic", topic)
        object.__setattr__(self, "accepted_schema_versions", versions)
        object.__setattr__(self, "delivery_results", tuple(self.delivery_results))


@dataclass(frozen=True)
class PresenceContextConsumptionAccess:
    delivery_item: PresenceContextDeliveryItem
    consumer_id: str
    publication_id: str
    topic: str
    schema_version: str
    partial_context: bool
    exposed_at: datetime
    access_id: str = ""

    def __post_init__(self) -> None:
        if not self.consumer_id.strip() or not self.publication_id.strip():
            raise ValueError("presence consumption access identity must not be blank")
        if not self.topic.strip() or not self.schema_version.strip():
            raise ValueError("presence consumption access contract must not be blank")
        if self.exposed_at.tzinfo is None:
            raise ValueError(
                "presence consumption access timestamp must be timezone-aware"
            )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.access_id and self.access_id != expected:
            raise ValueError("presence consumption access id is inconsistent")
        object.__setattr__(self, "access_id", expected)

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.delivery_item.delivery_item_id,
                self.consumer_id,
                self.publication_id,
                self.topic,
                self.schema_version,
                str(self.partial_context),
                self.exposed_at.isoformat(),
            )
        )


@dataclass(frozen=True)
class PresenceContextConsumptionGatewayResult:
    request: PresenceContextConsumptionGatewayRequest
    status: PresenceContextConsumptionGatewayStatus | str
    action: PresenceContextConsumptionGatewayAction | str
    source_delivery: PresenceContextDeliveryResult | None
    accesses: tuple[PresenceContextConsumptionAccess, ...]
    confidence: float
    context_exposed: bool
    partial_context: bool
    confirmation_required: bool
    consumer_execution_allowed: bool
    context_transformation_allowed: bool
    consumption_confirmation_allowed: bool
    callback_invocation_allowed: bool
    transport_delivery_allowed: bool
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
    gateway_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceContextConsumptionGatewayStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceContextConsumptionGatewayAction(self.action)
        )
        object.__setattr__(self, "accesses", tuple(self.accesses))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError(
                "presence consumption gateway timestamp must be timezone-aware"
            )
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence consumption gateway confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence consumption gateway rationale must not be empty")
        if any(
            (
                self.consumer_execution_allowed,
                self.context_transformation_allowed,
                self.consumption_confirmation_allowed,
                self.callback_invocation_allowed,
                self.transport_delivery_allowed,
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
            raise ValueError("M146 cannot authorize downstream capabilities")
        active = self.status in {
            PresenceContextConsumptionGatewayStatus.AVAILABLE,
            PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL,
        }
        if active:
            if (
                self.source_delivery is None
                or not self.accesses
                or not self.context_exposed
                or self.confidence <= 0
            ):
                raise ValueError(
                    "available gateway result requires delivery and accesses"
                )
            expected_partial = (
                self.status is PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL
            )
            if self.partial_context != expected_partial or self.confirmation_required:
                raise ValueError(
                    "presence consumption gateway active metadata is inconsistent"
                )
        else:
            if (
                self.source_delivery is not None
                or self.accesses
                or self.confidence != 0
                or self.context_exposed
                or self.partial_context
            ):
                raise ValueError("inactive gateway result cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED
        ):
            raise ValueError(
                "presence consumption gateway confirmation flag is inconsistent"
            )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.gateway_id and self.gateway_id != expected:
            raise ValueError("presence consumption gateway id is inconsistent")
        object.__setattr__(self, "gateway_id", expected)

    def _identity_payload(self) -> str:
        delivery_ids = ";".join(
            item.delivery_id for item in self.request.delivery_results
        )
        access_ids = ";".join(item.access_id for item in self.accesses)
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.consumer_id.casefold(),
                delivery_ids,
                self.request.expected_topic,
                ";".join(self.request.accepted_schema_versions),
                str(self.request.gateway_declared),
                self.status.value,
                self.action.value,
                self.source_delivery.delivery_id if self.source_delivery else "none",
                access_ids or "none",
                str(self.confidence),
                str(self.context_exposed),
                str(self.partial_context),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextConsumptionGatewayRepository(Protocol):
    def add(self, result: PresenceContextConsumptionGatewayResult) -> None: ...
    def get(
        self, gateway_id: str
    ) -> PresenceContextConsumptionGatewayResult | None: ...
    def list_all(self) -> tuple[PresenceContextConsumptionGatewayResult, ...]: ...


class InMemoryPresenceContextConsumptionGatewayRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextConsumptionGatewayResult] = {}

    def add(self, result: PresenceContextConsumptionGatewayResult) -> None:
        if result.gateway_id in self._items:
            raise ValueError("presence consumption gateway result already exists")
        self._items[result.gateway_id] = result

    def get(self, gateway_id: str) -> PresenceContextConsumptionGatewayResult | None:
        return self._items.get(gateway_id)

    def list_all(self) -> tuple[PresenceContextConsumptionGatewayResult, ...]:
        return tuple(self._items.values())
