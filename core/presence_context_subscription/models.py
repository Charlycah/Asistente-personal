from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_publication import PresenceContextPublicationResult


class PresenceContextSubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextSubscriptionAction(str, Enum):
    REGISTER = "register"
    PAUSE = "pause"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceContextSubscriptionFilter(str, Enum):
    COMPLETE_ONLY = "complete_only"
    INCLUDE_PARTIAL = "include_partial"


class PresenceContextSubscriptionLifecycle(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"


@dataclass(frozen=True)
class PresenceContextSubscriptionPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence subscription result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence subscription result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence subscription confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContextSubscriptionRequest:
    owner: str
    publication_results: tuple[PresenceContextPublicationResult, ...]
    subscriber_id: str
    accepted_topic: str = "roby.ambient.presence.context"
    accepted_schema_versions: tuple[str, ...] = ("1.0",)
    filter_mode: PresenceContextSubscriptionFilter | str = (
        PresenceContextSubscriptionFilter.INCLUDE_PARTIAL
    )
    lifecycle: PresenceContextSubscriptionLifecycle | str = (
        PresenceContextSubscriptionLifecycle.ACTIVE
    )
    subscription_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        subscriber = self.subscriber_id.strip()
        topic = self.accepted_topic.strip()
        versions = tuple(item.strip() for item in self.accepted_schema_versions)
        if not owner:
            raise ValueError("presence subscription owner must not be blank")
        if not subscriber:
            raise ValueError("presence subscription subscriber id must not be blank")
        if not topic:
            raise ValueError("presence subscription topic must not be blank")
        if not versions or any(not item for item in versions):
            raise ValueError("presence subscription schema versions must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "subscriber_id", subscriber)
        object.__setattr__(self, "accepted_topic", topic)
        object.__setattr__(self, "accepted_schema_versions", versions)
        object.__setattr__(self, "publication_results", tuple(self.publication_results))
        object.__setattr__(
            self, "filter_mode", PresenceContextSubscriptionFilter(self.filter_mode)
        )
        object.__setattr__(
            self, "lifecycle", PresenceContextSubscriptionLifecycle(self.lifecycle)
        )


@dataclass(frozen=True)
class PresenceContextSubscriptionResult:
    request: PresenceContextSubscriptionRequest
    status: PresenceContextSubscriptionStatus | str
    action: PresenceContextSubscriptionAction | str
    source_publication: PresenceContextPublicationResult | None
    subscriber_id: str | None
    accepted_topic: str | None
    accepted_schema_versions: tuple[str, ...]
    filter_mode: PresenceContextSubscriptionFilter | str | None
    lifecycle: PresenceContextSubscriptionLifecycle | str | None
    confidence: float
    subscription_registered: bool
    context_eligible: bool
    confirmation_required: bool
    delivery_allowed: bool
    callback_invocation_allowed: bool
    consumer_processing_allowed: bool
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
    subscription_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceContextSubscriptionStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceContextSubscriptionAction(self.action)
        )
        object.__setattr__(
            self, "accepted_schema_versions", tuple(self.accepted_schema_versions)
        )
        if self.filter_mode is not None:
            object.__setattr__(
                self, "filter_mode", PresenceContextSubscriptionFilter(self.filter_mode)
            )
        if self.lifecycle is not None:
            object.__setattr__(
                self, "lifecycle", PresenceContextSubscriptionLifecycle(self.lifecycle)
            )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence subscription timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence subscription confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence subscription rationale must not be empty")
        if any(
            (
                self.delivery_allowed,
                self.callback_invocation_allowed,
                self.consumer_processing_allowed,
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
            raise ValueError("M143 cannot authorize downstream capabilities")
        registered = self.status in {
            PresenceContextSubscriptionStatus.ACTIVE,
            PresenceContextSubscriptionStatus.PAUSED,
        }
        if registered:
            if self.source_publication is None or not self.subscription_registered:
                raise ValueError("registered subscription requires source publication")
            if (
                not self.subscriber_id
                or not self.accepted_topic
                or not self.accepted_schema_versions
            ):
                raise ValueError("registered subscription requires canonical metadata")
            if (
                self.filter_mode is None
                or self.lifecycle is None
                or self.confidence <= 0
            ):
                raise ValueError("registered subscription metadata is incomplete")
            if self.confirmation_required:
                raise ValueError("registered subscription cannot require confirmation")
            expected_eligible = self.status is PresenceContextSubscriptionStatus.ACTIVE
            if self.context_eligible != expected_eligible:
                raise ValueError("subscription eligibility flag is inconsistent")
        else:
            if self.source_publication is not None:
                raise ValueError(
                    "inactive subscription cannot expose source publication"
                )
            if any(
                (self.subscriber_id, self.accepted_topic, self.accepted_schema_versions)
            ):
                raise ValueError(
                    "inactive subscription cannot expose canonical metadata"
                )
            if self.filter_mode is not None or self.lifecycle is not None:
                raise ValueError(
                    "inactive subscription cannot expose lifecycle metadata"
                )
            if (
                self.confidence != 0
                or self.subscription_registered
                or self.context_eligible
            ):
                raise ValueError("inactive subscription cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextSubscriptionStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence subscription confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.subscription_id and self.subscription_id != expected:
            raise ValueError("presence context subscription id is inconsistent")
        object.__setattr__(self, "subscription_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.publication_id for item in self.request.publication_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                self.request.subscriber_id,
                self.request.accepted_topic,
                ";".join(self.request.accepted_schema_versions),
                self.request.filter_mode.value,
                self.request.lifecycle.value,
                str(self.request.subscription_declared),
                self.status.value,
                self.action.value,
                self.source_publication.publication_id
                if self.source_publication
                else "none",
                self.subscriber_id or "none",
                self.accepted_topic or "none",
                ";".join(self.accepted_schema_versions) or "none",
                self.filter_mode.value if self.filter_mode else "none",
                self.lifecycle.value if self.lifecycle else "none",
                str(self.confidence),
                str(self.subscription_registered),
                str(self.context_eligible),
                str(self.confirmation_required),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextSubscriptionRepository(Protocol):
    def add(self, result: PresenceContextSubscriptionResult) -> None: ...
    def get(self, subscription_id: str) -> PresenceContextSubscriptionResult | None: ...
    def list_all(self) -> tuple[PresenceContextSubscriptionResult, ...]: ...


class InMemoryPresenceContextSubscriptionRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextSubscriptionResult] = {}

    def add(self, result: PresenceContextSubscriptionResult) -> None:
        if result.subscription_id in self._items:
            raise ValueError("presence context subscription result already exists")
        self._items[result.subscription_id] = result

    def get(self, subscription_id: str) -> PresenceContextSubscriptionResult | None:
        return self._items.get(subscription_id)

    def list_all(self) -> tuple[PresenceContextSubscriptionResult, ...]:
        return tuple(self._items.values())
