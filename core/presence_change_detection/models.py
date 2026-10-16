from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_continuity import (
    PresenceContinuityResult,
)
from core.presence_understanding import PresenceState


class PresenceChangeDetectionStatus(str, Enum):
    DETECTED = "detected"
    NO_CHANGE = "no_change"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceChangeDetectionAction(str, Enum):
    PUBLISH = "publish"
    SUPPRESS = "suppress"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceChangeKind(str, Enum):
    NONE = "none"
    APPEARANCE = "appearance"
    DISAPPEARANCE = "disappearance"
    OCCUPANCY_VARIATION = "occupancy_variation"
    TRANSIENT_VARIATION = "transient_variation"
    UNCERTAIN_VARIATION = "uncertain_variation"
    CONTINUITY_BREAK = "continuity_break"


@dataclass(frozen=True)
class PresenceChangeDetectionPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence change result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence change result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("presence change confidence must be between zero and one")


@dataclass(frozen=True)
class PresenceChangeDetectionRequest:
    owner: str
    continuity_results: tuple[PresenceContinuityResult, ...]
    detection_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence change owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "continuity_results", tuple(self.continuity_results))


@dataclass(frozen=True)
class PresenceChangeDetectionResult:
    request: PresenceChangeDetectionRequest
    status: PresenceChangeDetectionStatus | str
    action: PresenceChangeDetectionAction | str
    change_kind: PresenceChangeKind | str
    source_continuity: PresenceContinuityResult | None
    previous_presence: PresenceState | str | None
    current_presence: PresenceState | str | None
    confidence: float
    change_detected: bool
    change_published: bool
    continuity_break_detected: bool
    confirmation_required: bool
    identity_inference_allowed: bool
    biometric_analysis_allowed: bool
    precise_person_counting_allowed: bool
    activity_inference_allowed: bool
    individual_tracking_allowed: bool
    movement_tracking_allowed: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    detection_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PresenceChangeDetectionStatus(self.status))
        object.__setattr__(self, "action", PresenceChangeDetectionAction(self.action))
        object.__setattr__(self, "change_kind", PresenceChangeKind(self.change_kind))
        if self.previous_presence is not None:
            object.__setattr__(
                self, "previous_presence", PresenceState(self.previous_presence)
            )
        if self.current_presence is not None:
            object.__setattr__(
                self, "current_presence", PresenceState(self.current_presence)
            )
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence change timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("presence change confidence must be between zero and one")
        if not self.rationale or any(not reason.strip() for reason in self.rationale):
            raise ValueError("presence change rationale must not be empty")
        forbidden = (
            self.identity_inference_allowed,
            self.biometric_analysis_allowed,
            self.precise_person_counting_allowed,
            self.activity_inference_allowed,
            self.individual_tracking_allowed,
            self.movement_tracking_allowed,
            self.sensor_access_allowed,
            self.automation_allowed,
        )
        if any(forbidden):
            raise ValueError("M138 cannot authorize downstream presence capabilities")
        if self.status is PresenceChangeDetectionStatus.DETECTED:
            if self.source_continuity is None:
                raise ValueError("detected change requires source continuity")
            if self.previous_presence is None or self.current_presence is None:
                raise ValueError("detected change requires presence states")
            if self.change_kind is PresenceChangeKind.NONE:
                raise ValueError("detected change requires a change kind")
            if not self.change_detected or not self.change_published:
                raise ValueError("detected change flags are inconsistent")
            if self.confidence <= 0 or self.confirmation_required:
                raise ValueError("detected change confidence is inconsistent")
        elif self.status is PresenceChangeDetectionStatus.NO_CHANGE:
            if self.source_continuity is None:
                raise ValueError("no-change result requires source continuity")
            if self.previous_presence is None or self.current_presence is None:
                raise ValueError("no-change result requires presence states")
            if self.change_kind is not PresenceChangeKind.NONE:
                raise ValueError("no-change result cannot expose a change kind")
            if self.change_detected or self.change_published:
                raise ValueError("no-change flags are inconsistent")
            if self.confidence <= 0 or self.confirmation_required:
                raise ValueError("no-change confidence is inconsistent")
        else:
            if self.source_continuity is not None:
                raise ValueError("inactive detection cannot expose source continuity")
            if self.previous_presence is not None or self.current_presence is not None:
                raise ValueError("inactive detection cannot expose presence states")
            if self.change_kind is not PresenceChangeKind.NONE:
                raise ValueError("inactive detection cannot expose a change kind")
            if self.confidence != 0 or self.change_detected or self.change_published:
                raise ValueError("inactive detection cannot expose active values")
        if self.continuity_break_detected != (
            self.status is PresenceChangeDetectionStatus.DETECTED
            and self.change_kind is PresenceChangeKind.CONTINUITY_BREAK
        ):
            raise ValueError("continuity-break flag is inconsistent")
        if self.confirmation_required != (
            self.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence change confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.detection_id and self.detection_id != expected:
            raise ValueError("presence change detection id is inconsistent")
        object.__setattr__(self, "detection_id", expected)

    def _identity_payload(self) -> str:
        result_ids = ";".join(
            item.continuity_id for item in self.request.continuity_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                result_ids,
                str(self.request.detection_declared),
                self.status.value,
                self.action.value,
                self.change_kind.value,
                self.source_continuity.continuity_id
                if self.source_continuity
                else "none",
                self.previous_presence.value if self.previous_presence else "none",
                self.current_presence.value if self.current_presence else "none",
                str(self.confidence),
                str(self.change_detected),
                str(self.change_published),
                str(self.continuity_break_detected),
                str(self.confirmation_required),
                str(self.identity_inference_allowed),
                str(self.biometric_analysis_allowed),
                str(self.precise_person_counting_allowed),
                str(self.activity_inference_allowed),
                str(self.individual_tracking_allowed),
                str(self.movement_tracking_allowed),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceChangeDetectionRepository(Protocol):
    def add(self, result: PresenceChangeDetectionResult) -> None: ...
    def get(self, detection_id: str) -> PresenceChangeDetectionResult | None: ...
    def list_all(self) -> tuple[PresenceChangeDetectionResult, ...]: ...


class InMemoryPresenceChangeDetectionRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceChangeDetectionResult] = {}

    def add(self, result: PresenceChangeDetectionResult) -> None:
        if result.detection_id in self._items:
            raise ValueError("presence change detection result already exists")
        self._items[result.detection_id] = result

    def get(self, detection_id: str) -> PresenceChangeDetectionResult | None:
        return self._items.get(detection_id)

    def list_all(self) -> tuple[PresenceChangeDetectionResult, ...]:
        return tuple(self._items.values())
