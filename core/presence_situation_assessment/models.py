from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.presence_event_interpretation import (
    PresenceEventInterpretationResult,
    PresenceEventMeaning,
)
from core.presence_understanding import PresenceState


class PresenceSituationAssessmentStatus(str, Enum):
    ASSESSED = "assessed"
    STABLE = "stable"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceSituationAssessmentAction(str, Enum):
    EXPOSE = "expose"
    SUPPRESS = "suppress"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


class PresenceSituationKind(str, Enum):
    NONE = "none"
    STABLE = "stable"
    TRANSITION = "transition"
    UNCERTAIN = "uncertain"
    INTERRUPTED = "interrupted"


class PresenceSituationSignal(str, Enum):
    NONE = "none"
    STABLE_PRESENCE = "stable_presence"
    PRESENCE_APPEARED = "presence_appeared"
    PRESENCE_DISAPPEARED = "presence_disappeared"
    OCCUPANCY_CHANGED = "occupancy_changed"
    TRANSIENT_CHANGE = "transient_change"
    CERTAINTY_CHANGED = "certainty_changed"
    CONTINUITY_INTERRUPTED = "continuity_interrupted"


@dataclass(frozen=True)
class PresenceSituationAssessmentPolicy:
    maximum_results: int = 64
    maximum_result_age: timedelta = timedelta(hours=2)
    minimum_confidence: float = 0.7

    def __post_init__(self) -> None:
        if self.maximum_results <= 0:
            raise ValueError("presence situation result limit must be positive")
        if self.maximum_result_age <= timedelta(0):
            raise ValueError("presence situation result age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError(
                "presence situation confidence must be between zero and one"
            )


@dataclass(frozen=True)
class PresenceSituationAssessmentRequest:
    owner: str
    interpretation_results: tuple[PresenceEventInterpretationResult, ...]
    assessment_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence situation owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(
            self, "interpretation_results", tuple(self.interpretation_results)
        )


@dataclass(frozen=True)
class PresenceSituationAssessmentResult:
    request: PresenceSituationAssessmentRequest
    status: PresenceSituationAssessmentStatus | str
    action: PresenceSituationAssessmentAction | str
    situation_kind: PresenceSituationKind | str
    situation_signal: PresenceSituationSignal | str
    source_interpretation: PresenceEventInterpretationResult | None
    source_meaning: PresenceEventMeaning | str
    previous_presence: PresenceState | str | None
    current_presence: PresenceState | str | None
    confidence: float
    situation_assessed: bool
    situation_exposed: bool
    confirmation_required: bool
    identity_inference_allowed: bool
    biometric_analysis_allowed: bool
    precise_person_counting_allowed: bool
    activity_inference_allowed: bool
    intent_inference_allowed: bool
    individual_tracking_allowed: bool
    movement_tracking_allowed: bool
    response_decision_allowed: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "status", PresenceSituationAssessmentStatus(self.status)
        )
        object.__setattr__(
            self, "action", PresenceSituationAssessmentAction(self.action)
        )
        object.__setattr__(
            self, "situation_kind", PresenceSituationKind(self.situation_kind)
        )
        object.__setattr__(
            self, "situation_signal", PresenceSituationSignal(self.situation_signal)
        )
        object.__setattr__(
            self, "source_meaning", PresenceEventMeaning(self.source_meaning)
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
            raise ValueError("presence situation timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence situation confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence situation rationale must not be empty")
        forbidden = (
            self.identity_inference_allowed,
            self.biometric_analysis_allowed,
            self.precise_person_counting_allowed,
            self.activity_inference_allowed,
            self.intent_inference_allowed,
            self.individual_tracking_allowed,
            self.movement_tracking_allowed,
            self.response_decision_allowed,
            self.sensor_access_allowed,
            self.automation_allowed,
        )
        if any(forbidden):
            raise ValueError("M140 cannot authorize downstream presence capabilities")
        if self.status in {
            PresenceSituationAssessmentStatus.ASSESSED,
            PresenceSituationAssessmentStatus.STABLE,
        }:
            if self.source_interpretation is None:
                raise ValueError("active assessment requires source interpretation")
            if self.situation_kind is PresenceSituationKind.NONE:
                raise ValueError("active assessment requires situation kind")
            if self.situation_signal is PresenceSituationSignal.NONE:
                raise ValueError("active assessment requires situation signal")
            if self.previous_presence is None or self.current_presence is None:
                raise ValueError("active assessment requires presence states")
            if not self.situation_assessed or self.confidence <= 0:
                raise ValueError("active assessment flags are inconsistent")
            if self.confirmation_required:
                raise ValueError("active assessment cannot require confirmation")
            if self.status is PresenceSituationAssessmentStatus.ASSESSED:
                if self.situation_kind is PresenceSituationKind.STABLE:
                    raise ValueError("assessed transition cannot be stable")
                if not self.situation_exposed:
                    raise ValueError("assessed situation must be exposed")
            else:
                if self.situation_kind is not PresenceSituationKind.STABLE:
                    raise ValueError("stable assessment requires stable kind")
                if self.situation_exposed:
                    raise ValueError("stable assessment must be suppressed")
        else:
            if self.source_interpretation is not None:
                raise ValueError(
                    "inactive assessment cannot expose source interpretation"
                )
            if self.source_meaning is not PresenceEventMeaning.NONE:
                raise ValueError("inactive assessment cannot expose source meaning")
            if self.situation_kind is not PresenceSituationKind.NONE:
                raise ValueError("inactive assessment cannot expose situation kind")
            if self.situation_signal is not PresenceSituationSignal.NONE:
                raise ValueError("inactive assessment cannot expose situation signal")
            if self.previous_presence is not None or self.current_presence is not None:
                raise ValueError("inactive assessment cannot expose presence states")
            if (
                self.confidence != 0
                or self.situation_assessed
                or self.situation_exposed
            ):
                raise ValueError("inactive assessment cannot expose active values")
        if self.confirmation_required != (
            self.status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED
        ):
            raise ValueError("presence situation confirmation flag is inconsistent")
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("presence situation assessment id is inconsistent")
        object.__setattr__(self, "assessment_id", expected)

    def _identity_payload(self) -> str:
        source_ids = ";".join(
            item.interpretation_id for item in self.request.interpretation_results
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                source_ids,
                str(self.request.assessment_declared),
                self.status.value,
                self.action.value,
                self.situation_kind.value,
                self.situation_signal.value,
                self.source_interpretation.interpretation_id
                if self.source_interpretation
                else "none",
                self.source_meaning.value,
                self.previous_presence.value if self.previous_presence else "none",
                self.current_presence.value if self.current_presence else "none",
                str(self.confidence),
                str(self.situation_assessed),
                str(self.situation_exposed),
                str(self.confirmation_required),
                str(self.identity_inference_allowed),
                str(self.biometric_analysis_allowed),
                str(self.precise_person_counting_allowed),
                str(self.activity_inference_allowed),
                str(self.intent_inference_allowed),
                str(self.individual_tracking_allowed),
                str(self.movement_tracking_allowed),
                str(self.response_decision_allowed),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceSituationAssessmentRepository(Protocol):
    def add(self, result: PresenceSituationAssessmentResult) -> None: ...
    def get(self, assessment_id: str) -> PresenceSituationAssessmentResult | None: ...
    def list_all(self) -> tuple[PresenceSituationAssessmentResult, ...]: ...


class InMemoryPresenceSituationAssessmentRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceSituationAssessmentResult] = {}

    def add(self, result: PresenceSituationAssessmentResult) -> None:
        if result.assessment_id in self._items:
            raise ValueError("presence situation assessment result already exists")
        self._items[result.assessment_id] = result

    def get(self, assessment_id: str) -> PresenceSituationAssessmentResult | None:
        return self._items.get(assessment_id)

    def list_all(self) -> tuple[PresenceSituationAssessmentResult, ...]:
        return tuple(self._items.values())
