from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_change_detection import (
    PresenceChangeDetectionResult,
    PresenceChangeKind,
)
from core.presence_understanding import PresenceState


class PresenceEventInterpretationStatus(str, Enum):
    INTERPRETED = "interpreted"
    NO_EVENT = "no_event"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceEventInterpretationAction(str, Enum):
    EXPOSE = "expose"
    SUPPRESS = "suppress"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceEventMeaning(str, Enum):
    NONE = "none"
    PRESENCE_BECAME_OBSERVED = "presence_became_observed"
    PRESENCE_BECAME_UNOBSERVED = "presence_became_unobserved"
    AMBIENT_OCCUPANCY_SHIFTED = "ambient_occupancy_shifted"
    TRANSIENT_PRESENCE_SIGNAL = "transient_presence_signal"
    PRESENCE_CERTAINTY_CHANGED = "presence_certainty_changed"
    PRESENCE_CONTINUITY_LOST = "presence_continuity_lost"


@dataclass(frozen=True)
class PresenceEventInterpretationPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence event result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence event result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("presence event confidence must be between zero and one")


@dataclass(frozen=True)
class PresenceEventInterpretationRequest:
    owner: str
    detection_results: tuple[PresenceChangeDetectionResult, ...]
    interpretation_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence event owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "detection_results", tuple(self.detection_results))


@dataclass(frozen=True)
class PresenceEventInterpretationResult:
    request: PresenceEventInterpretationRequest
    status: PresenceEventInterpretationStatus | str
    action: PresenceEventInterpretationAction | str
    meaning: PresenceEventMeaning | str
    source_detection: PresenceChangeDetectionResult | None
    source_change_kind: PresenceChangeKind | str
    previous_presence: PresenceState | str | None
    current_presence: PresenceState | str | None
    confidence: float
    event_interpreted: bool
    event_exposed: bool
    confirmation_required: bool
    identity_inference_allowed: bool
    biometric_analysis_allowed: bool
    precise_person_counting_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    individual_tracking_allowed: bool
    movement_tracking_allowed: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    interpretation_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceEventInterpretationStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceEventInterpretationAction(self.action)
        )
        object.__setattr__(self, "meaning", PresenceEventMeaning(self.meaning))
        object.__setattr__(
            self, "source_change_kind", PresenceChangeKind(self.source_change_kind)
        )
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
            raise ValueError("presence event timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError("presence event confidence must be between zero and one")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence event rationale must not be empty")
        forbidden = (
            self.identity_inference_allowed,
            self.biometric_analysis_allowed,
            self.precise_person_counting_allowed,
            self.activity_inference_allowed,
            self.intent_inference_allowed,
            self.individual_tracking_allowed,
            self.movement_tracking_allowed,
            self.sensor_access_allowed,
            self.automation_allowed,
        )
        if any(forbidden):
            raise ValueError("M139 cannot authorize downstream presence capabilities")
        if self.status is PresenceEventInterpretationStatus.INTERPRETED:
            if self.source_detection is None:
                raise ValueError("interpreted event requires source detection")
            if self.meaning is PresenceEventMeaning.NONE:
                raise ValueError("interpreted event requires semantic meaning")
            if self.source_change_kind is PresenceChangeKind.NONE:
                raise ValueError("interpreted event requires source change kind")
            if self.previous_presence is None or self.current_presence is None:
                raise ValueError("interpreted event requires presence states")
            if not self.event_interpreted or not self.event_exposed:
                raise ValueError("interpreted event flags are inconsistent")
            if self.confidence <= 0 or self.confirmation_required:
                raise ValueError("interpreted event confidence is inconsistent")
        elif self.status is PresenceEventInterpretationStatus.NO_EVENT:
            if self.source_detection is None:
                raise ValueError("no-event result requires source detection")
            if self.meaning is not PresenceEventMeaning.NONE:
                raise ValueError("no-event result cannot expose meaning")
            if self.source_change_kind is not PresenceChangeKind.NONE:
                raise ValueError("no-event result cannot expose change kind")
            if (
                self.event_interpreted
                or self.event_exposed
                or self.confirmation_required
            ):
                raise ValueError("no-event flags are inconsistent")
            if self.confidence <= 0:
                raise ValueError("no-event confidence is inconsistent")
        else:
            if self.source_detection is not None:
                raise ValueError(
                    "inactive interpretation cannot expose source detection"
                )
            if self.meaning is not PresenceEventMeaning.NONE:
                raise ValueError("inactive interpretation cannot expose meaning")
            if self.source_change_kind is not PresenceChangeKind.NONE:
                raise ValueError("inactive interpretation cannot expose change kind")
            if self.previous_presence is not None or self.current_presence is not None:
                raise ValueError(
                    "inactive interpretation cannot expose presence states"
                )
            if self.confidence != 0 or self.event_interpreted or self.event_exposed:
                raise ValueError("inactive interpretation cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence event confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.interpretation_id and self.interpretation_id != expected:
            raise ValueError("presence event interpretation id is inconsistent")
        object.__setattr__(self, "interpretation_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.detection_id for item in self.request.detection_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.interpretation_declared),
                self.status.value,
                self.action.value,
                self.meaning.value,
                self.source_detection.detection_id if self.source_detection else "none",
                self.source_change_kind.value,
                self.previous_presence.value if self.previous_presence else "none",
                self.current_presence.value if self.current_presence else "none",
                str(self.confidence),
                str(self.event_interpreted),
                str(self.event_exposed),
                str(self.confirmation_required),
                str(self.identity_inference_allowed),
                str(self.biometric_analysis_allowed),
                str(self.precise_person_counting_allowed),
                str(self.activity_inference_allowed),
                str(self.intent_inference_allowed),
                str(self.individual_tracking_allowed),
                str(self.movement_tracking_allowed),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceEventInterpretationRepository(Protocol):
    def add(self, result: PresenceEventInterpretationResult) -> None: ...
    def get(
        self, interpretation_id: str
    ) -> PresenceEventInterpretationResult | None: ...
    def list_all(self) -> tuple[PresenceEventInterpretationResult, ...]: ...


class InMemoryPresenceEventInterpretationRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceEventInterpretationResult] = {}

    def add(self, result: PresenceEventInterpretationResult) -> None:
        if result.interpretation_id in self._items:
            raise ValueError("presence event interpretation result already exists")
        self._items[result.interpretation_id] = result

    def get(self, interpretation_id: str) -> PresenceEventInterpretationResult | None:
        return self._items.get(interpretation_id)

    def list_all(self) -> tuple[PresenceEventInterpretationResult, ...]:
        return tuple(self._items.values())
