from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_situation_assessment import PresenceSituationAssessmentResult


class PresenceContextIntegrationStatus(str, Enum):
    INTEGRATED = "integrated"
    PARTIAL = "partial"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContextIntegrationAction(str, Enum):
    EXPOSE = "expose"
    EXPOSE_PARTIAL = "expose_partial"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceContextDimension(str, Enum):
    DEVICE = "device"
    CONVERSATION = "conversation"
    SPATIAL = "spatial"
    TEMPORAL = "temporal"


@dataclass(frozen=True)
class PresenceContextIntegrationPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7
    minimum_dimensions_for_integrated: int = 2

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence context result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence context result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("presence context confidence must be between zero and one")
        if not 1 <= self.minimum_dimensions_for_integrated <= 4:
            raise ValueError(
                "presence context dimension threshold must be between one and four"
            )


@dataclass(frozen=True)
class PresenceContextIntegrationRequest:
    owner: str
    assessment_results: tuple[PresenceSituationAssessmentResult, ...]
    device_context: str | None = None
    conversation_context: str | None = None
    spatial_context: str | None = None
    temporal_context: str | None = None
    integration_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence context owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "assessment_results", tuple(self.assessment_results))
        for name in (
            "device_context",
            "conversation_context",
            "spatial_context",
            "temporal_context",
        ):
            value = getattr(self, name)
            if value is not None:
                value = value.strip()
                if not value:
                    raise ValueError(f"{name} must not be blank")
                object.__setattr__(self, name, value)


@dataclass(frozen=True)
class PresenceContextIntegrationResult:
    request: PresenceContextIntegrationRequest
    status: PresenceContextIntegrationStatus | str
    action: PresenceContextIntegrationAction | str
    source_assessment: PresenceSituationAssessmentResult | None
    integrated_dimensions: tuple[PresenceContextDimension | str, ...]
    device_context: str | None
    conversation_context: str | None
    spatial_context: str | None
    temporal_context: str | None
    confidence: float
    context_integrated: bool
    context_exposed: bool
    confirmation_required: bool
    identity_inference_allowed: bool
    biometric_analysis_allowed: bool
    precise_person_counting_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    individual_tracking_allowed: bool
    movement_tracking_allowed: bool
    response_decision_allowed: bool
    behavior_adaptation_allowed: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    integration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceContextIntegrationStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceContextIntegrationAction(self.action)
        )
        object.__setattr__(
            self,
            "integrated_dimensions",
            tuple(
                PresenceContextDimension(item) for item in self.integrated_dimensions
            ),
        )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence context timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("presence context confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence context rationale must not be empty")
        if any(
            (
                self.identity_inference_allowed,
                self.biometric_analysis_allowed,
                self.precise_person_counting_allowed,
                self.activity_inference_allowed,
                self.intent_inference_allowed,
                self.individual_tracking_allowed,
                self.movement_tracking_allowed,
                self.response_decision_allowed,
                self.behavior_adaptation_allowed,
                self.sensor_access_allowed,
                self.automation_allowed,
            )
        ):
            raise ValueError("M141 cannot authorize downstream presence capabilities")
        active = self.status in {
            PresenceContextIntegrationStatus.INTEGRATED,
            PresenceContextIntegrationStatus.PARTIAL,
        }
        if active:
            if self.source_assessment is None or not self.context_integrated:
                raise ValueError("active integration requires source assessment")
            if not self.integrated_dimensions:
                raise ValueError("active integration requires declared dimensions")
            if not self.context_exposed or self.confidence <= 0:
                raise ValueError("active integration flags are inconsistent")
            if self.confirmation_required:
                raise ValueError("active integration cannot require confirmation")
        else:
            if self.source_assessment is not None or self.integrated_dimensions:
                raise ValueError("inactive integration cannot expose source context")
            if any(
                (
                    self.device_context,
                    self.conversation_context,
                    self.spatial_context,
                    self.temporal_context,
                )
            ):
                raise ValueError("inactive integration cannot expose context values")
            if self.confidence != 0 or self.context_integrated or self.context_exposed:
                raise ValueError("inactive integration cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceContextIntegrationStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence context confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.integration_id and self.integration_id != expected:
            raise ValueError("presence context integration id is inconsistent")
        object.__setattr__(self, "integration_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.assessment_id for item in self.request.assessment_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.integration_declared),
                self.status.value,
                self.action.value,
                self.source_assessment.assessment_id
                if self.source_assessment
                else "none",
                ";".join(item.value for item in self.integrated_dimensions),
                self.device_context or "none",
                self.conversation_context or "none",
                self.spatial_context or "none",
                self.temporal_context or "none",
                str(self.confidence),
                str(self.context_integrated),
                str(self.context_exposed),
                str(self.confirmation_required),
                str(self.identity_inference_allowed),
                str(self.biometric_analysis_allowed),
                str(self.precise_person_counting_allowed),
                str(self.activity_inference_allowed),
                str(self.intent_inference_allowed),
                str(self.individual_tracking_allowed),
                str(self.movement_tracking_allowed),
                str(self.response_decision_allowed),
                str(self.behavior_adaptation_allowed),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceContextIntegrationRepository(Protocol):
    def add(self, result: PresenceContextIntegrationResult) -> None: ...
    def get(self, integration_id: str) -> PresenceContextIntegrationResult | None: ...
    def list_all(self) -> tuple[PresenceContextIntegrationResult, ...]: ...


class InMemoryPresenceContextIntegrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContextIntegrationResult] = {}

    def add(self, result: PresenceContextIntegrationResult) -> None:
        if result.integration_id in self._items:
            raise ValueError("presence context integration result already exists")
        self._items[result.integration_id] = result

    def get(self, integration_id: str) -> PresenceContextIntegrationResult | None:
        return self._items.get(integration_id)

    def list_all(self) -> tuple[PresenceContextIntegrationResult, ...]:
        return tuple(self._items.values())
