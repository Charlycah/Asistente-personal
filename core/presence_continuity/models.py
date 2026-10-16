from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_understanding import PresenceState, PresenceUnderstandingResult


class PresenceContinuityStatus(str, Enum):
    CONTINUOUS = "continuous"
    TRANSITION = "transition"
    INTERRUPTED = "interrupted"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceContinuityAction(str, Enum):
    PRESERVE = "preserve"
    RECORD_TRANSITION = "record_transition"
    CLOSE = "close"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceTransitionKind(str, Enum):
    NONE = "none"
    ARRIVAL = "arrival"
    DEPARTURE = "departure"
    OCCUPANCY_CHANGE = "occupancy_change"
    TRANSIENT_CHANGE = "transient_change"
    UNCERTAIN_CHANGE = "uncertain_change"


@dataclass(frozen=True)
class PresenceContinuityPolicy:
    maximum_samples: int = 48
    maximum_sample_age: timedelta = timedelta(hours=2)
    maximum_gap: timedelta = timedelta(minutes=20)
    minimum_samples_for_continuity: int = 2
    minimum_confidence: float = 0.7
    confidence_variation_limit: float = 0.35

    def __post_init__(self) -> None:
        if self.maximum_samples <= 0:
            raise ValueError("presence continuity sample limit must be positive")
        if self.maximum_sample_age <= timedelta(0):
            raise ValueError("presence continuity sample age must be positive")
        if self.maximum_gap <= timedelta(0):
            raise ValueError("presence continuity gap must be positive")
        if self.minimum_samples_for_continuity < 2:
            raise ValueError("presence continuity requires at least two samples")
        if self.minimum_samples_for_continuity > self.maximum_samples:
            raise ValueError("presence continuity minimum exceeds sample limit")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence continuity confidence must be between zero and one"
            )
        if not 0 <= self.confidence_variation_limit <= 1:
            raise ValueError(
                "presence confidence variation must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceContinuityRequest:
    owner: str
    samples: tuple[PresenceUnderstandingResult, ...]
    continuity_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence continuity owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "samples", tuple(self.samples))


@dataclass(frozen=True)
class PresenceContinuityResult:
    request: PresenceContinuityRequest
    status: PresenceContinuityStatus | str
    action: PresenceContinuityAction | str
    transition_kind: PresenceTransitionKind | str
    previous_presence: PresenceState | str | None
    current_presence: PresenceState | str | None
    accepted_samples: tuple[PresenceUnderstandingResult, ...]
    confidence: float
    continuity_established: bool
    transition_recorded: bool
    interruption_detected: bool
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
    continuity_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PresenceContinuityStatus(self.status))
        object.__setattr__(self, "action", PresenceContinuityAction(self.action))
        object.__setattr__(
            self, "transition_kind", PresenceTransitionKind(self.transition_kind)
        )
        if self.previous_presence is not None:
            object.__setattr__(
                self, "previous_presence", PresenceState(self.previous_presence)
            )
        if self.current_presence is not None:
            object.__setattr__(
                self, "current_presence", PresenceState(self.current_presence)
            )
        object.__setattr__(self, "accepted_samples", tuple(self.accepted_samples))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence continuity timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence continuity confidence must be between zero and one"
            )
        if not self.rationale or any(not reason.strip() for reason in self.rationale):
            raise ValueError("presence continuity rationale must not be empty")
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
            raise ValueError("M137 cannot authorize downstream presence capabilities")
        active = {
            PresenceContinuityStatus.CONTINUOUS,
            PresenceContinuityStatus.TRANSITION,
            PresenceContinuityStatus.INTERRUPTED,
        }
        if self.status in active:
            if self.previous_presence is None or self.current_presence is None:
                raise ValueError(
                    "active continuity requires previous and current states"
                )
            if len(self.accepted_samples) < 2 or self.confidence <= 0:
                raise ValueError(
                    "active continuity requires accepted samples and confidence"
                )
            if self.confirmation_required:
                raise ValueError("active continuity cannot require confirmation")
        else:
            if self.previous_presence is not None or self.current_presence is not None:
                raise ValueError("inactive continuity cannot expose presence states")
            if self.accepted_samples or self.confidence != 0:
                raise ValueError("inactive continuity cannot expose accepted samples")
        if self.status is PresenceContinuityStatus.CONTINUOUS:
            if (
                not self.continuity_established
                or self.transition_recorded
                or self.interruption_detected
            ):
                raise ValueError("continuous status flags are inconsistent")
            if self.transition_kind is not PresenceTransitionKind.NONE:
                raise ValueError("continuous status cannot expose a transition")
        elif self.status is PresenceContinuityStatus.TRANSITION:
            if (
                self.continuity_established
                or not self.transition_recorded
                or self.interruption_detected
            ):
                raise ValueError("transition status flags are inconsistent")
            if self.transition_kind is PresenceTransitionKind.NONE:
                raise ValueError("transition status requires a transition kind")
        elif self.status is PresenceContinuityStatus.INTERRUPTED:
            if (
                self.continuity_established
                or self.transition_recorded
                or not self.interruption_detected
            ):
                raise ValueError("interrupted status flags are inconsistent")
        elif (
            self.continuity_established
            or self.transition_recorded
            or self.interruption_detected
        ):
            raise ValueError("inactive continuity cannot expose active flags")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.continuity_id and self.continuity_id != expected:
            raise ValueError("presence continuity id is inconsistent")
        object.__setattr__(self, "continuity_id", expected)

    def _identity_payload(self) -> str:
        sample_ids = ";".join(item.understanding_id for item in self.request.samples)
        accepted_ids = ";".join(item.understanding_id for item in self.accepted_samples)
        return "|".join(
            (
                self.request.owner.casefold(),
                sample_ids,
                str(self.request.continuity_declared),
                self.status.value,
                self.action.value,
                self.transition_kind.value,
                self.previous_presence.value if self.previous_presence else "none",
                self.current_presence.value if self.current_presence else "none",
                accepted_ids,
                str(self.confidence),
                str(self.continuity_established),
                str(self.transition_recorded),
                str(self.interruption_detected),
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
class PresenceContinuityRepository(Protocol):
    def add(self, result: PresenceContinuityResult) -> None: ...
    def get(self, continuity_id: str) -> PresenceContinuityResult | None: ...
    def list_all(self) -> tuple[PresenceContinuityResult, ...]: ...


class InMemoryPresenceContinuityRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceContinuityResult] = {}

    def add(self, result: PresenceContinuityResult) -> None:
        if result.continuity_id in self._items:
            raise ValueError("presence continuity result already exists")
        self._items[result.continuity_id] = result

    def get(self, continuity_id: str) -> PresenceContinuityResult | None:
        return self._items.get(continuity_id)

    def list_all(self) -> tuple[PresenceContinuityResult, ...]:
        return tuple(self._items.values())
