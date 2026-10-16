from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_context_integration import PresenceContextIntegrationResult


class PresenceContextPublicationStatus(str, Enum):
    PUBLISHED = "published"
    PUBLISHED_PARTIAL = "published_partial"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextPublicationAction(str, Enum):
    PUBLISH = "publish"
    PUBLISH_PARTIAL = "publish_partial"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class PresenceContextPublicationPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    allow_partial_publication: bool = True

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence publication result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence publication result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence publication confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContextPublicationRequest:
    owner: str
    integration_results: tuple[PresenceContextIntegrationResult, ...]
    publication_topic: str = "roby.ambient.presence.context"
    schema_version: str = "1.0"
    publication_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        topic = self.publication_topic.strip()
        version = self.schema_version.strip()
        if not owner:
            raise ValueError("presence publication owner must not be blank")
        if not topic:
            raise ValueError("presence publication topic must not be blank")
        if not version:
            raise ValueError("presence publication schema version must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "publication_topic", topic)
        object.__setattr__(self, "schema_version", version)
        object.__setattr__(self, "integration_results", tuple(self.integration_results))


@dataclass(frozen=True)
class PresenceContextPublicationResult:
    request: PresenceContextPublicationRequest
    status: PresenceContextPublicationStatus | str
    action: PresenceContextPublicationAction | str
    source_integration: PresenceContextIntegrationResult | None
    publication_topic: str | None
    schema_version: str | None
    payload_digest: str | None
    confidence: float
    context_published: bool
    partial_context_published: bool
    confirmation_required: bool
    consumer_invocation_allowed: bool
    identity_inference_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    individual_tracking_allowed: bool
    response_decision_allowed: bool
    behavior_adaptation_allowed: bool
    sensor_access_allowed: bool
    provider_call_allowed: bool
    automation_allowed: bool
    platform_mutation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    publication_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceContextPublicationStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceContextPublicationAction(self.action)
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence publication timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence publication confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence publication rationale must not be empty")
        if any(
            (
                self.consumer_invocation_allowed,
                self.identity_inference_allowed,
                self.activity_inference_allowed,
                self.intent_inference_allowed,
                self.individual_tracking_allowed,
                self.response_decision_allowed,
                self.behavior_adaptation_allowed,
                self.sensor_access_allowed,
                self.provider_call_allowed,
                self.automation_allowed,
                self.platform_mutation_allowed,
            )
        ):
            raise ValueError("M142 cannot authorize downstream capabilities")
        active = self.status in {
            PresenceContextPublicationStatus.PUBLISHED,
            PresenceContextPublicationStatus.PUBLISHED_PARTIAL,
        }
        if active:
            if self.source_integration is None or not self.context_published:
                raise ValueError("active publication requires source integration")
            if (
                not self.publication_topic
                or not self.schema_version
                or not self.payload_digest
            ):
                raise ValueError("active publication requires canonical metadata")
            if self.confidence <= 0 or self.confirmation_required:
                raise ValueError("active publication flags are inconsistent")
            expected_partial = (
                self.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
            )
            if self.partial_context_published != expected_partial:
                raise ValueError("partial publication flag is inconsistent")
        else:
            if self.source_integration is not None:
                raise ValueError(
                    "inactive publication cannot expose source integration"
                )
            if any((self.publication_topic, self.schema_version, self.payload_digest)):
                raise ValueError(
                    "inactive publication cannot expose canonical metadata"
                )
            if (
                self.confidence != 0
                or self.context_published
                or self.partial_context_published
            ):
                raise ValueError("inactive publication cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextPublicationStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence publication confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.publication_id and self.publication_id != expected:
            raise ValueError("presence context publication id is inconsistent")
        object.__setattr__(self, "publication_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.integration_id for item in self.request.integration_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                self.request.publication_topic,
                self.request.schema_version,
                str(self.request.publication_declared),
                self.status.value,
                self.action.value,
                self.source_integration.integration_id
                if self.source_integration
                else "none",
                self.publication_topic or "none",
                self.schema_version or "none",
                self.payload_digest or "none",
                str(self.confidence),
                str(self.context_published),
                str(self.partial_context_published),
                str(self.confirmation_required),
                str(self.consumer_invocation_allowed),
                str(self.identity_inference_allowed),
                str(self.activity_inference_allowed),
                str(self.intent_inference_allowed),
                str(self.individual_tracking_allowed),
                str(self.response_decision_allowed),
                str(self.behavior_adaptation_allowed),
                str(self.sensor_access_allowed),
                str(self.provider_call_allowed),
                str(self.automation_allowed),
                str(self.platform_mutation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextPublicationRepository(Protocol):
    def add(self, result: PresenceContextPublicationResult) -> None: ...
    def get(self, publication_id: str) -> PresenceContextPublicationResult | None: ...
    def list_all(self) -> tuple[PresenceContextPublicationResult, ...]: ...


class InMemoryPresenceContextPublicationRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextPublicationResult] = {}

    def add(self, result: PresenceContextPublicationResult) -> None:
        if result.publication_id in self._items:
            raise ValueError("presence context publication result already exists")
        self._items[result.publication_id] = result

    def get(self, publication_id: str) -> PresenceContextPublicationResult | None:
        return self._items.get(publication_id)

    def list_all(self) -> tuple[PresenceContextPublicationResult, ...]:
        return tuple(self._items.values())
