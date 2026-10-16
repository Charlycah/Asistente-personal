from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.ambient_observation_resolution import ResolvedAmbientObservation


class PresenceState(str, Enum):
    UNOCCUPIED = "unoccupied"
    OCCUPIED = "occupied"
    SINGLE_PRESENCE = "single_presence"
    MULTIPLE_PRESENCES = "multiple_presences"
    TRANSIENT = "transient"
    UNKNOWN = "unknown"


class PresenceUnderstandingStatus(str, Enum):
    UNDERSTOOD = "understood"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class PresenceUnderstandingAction(str, Enum):
    CONSOLIDATE = "consolidate"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class PresenceEvidence:
    evidence_ref: str
    observation_ref: str
    presence_state: PresenceState | str
    confidence: float
    attributes: tuple[str, ...] = ()
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        evidence_ref = self.evidence_ref.strip()
        observation_ref = self.observation_ref.strip()
        if not evidence_ref or not observation_ref:
            raise ValueError("presence evidence references must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence evidence confidence must be between zero and one"
            )
        attributes = tuple(item.strip() for item in self.attributes)
        if any(not item for item in attributes):
            raise ValueError("presence evidence attributes must not be blank")
        normalized = tuple(dict.fromkeys(item.casefold() for item in attributes))
        object.__setattr__(self, "evidence_ref", evidence_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(self, "presence_state", PresenceState(self.presence_state))
        object.__setattr__(self, "attributes", normalized)


@dataclass(frozen=True)
class PresenceUnderstandingPolicy:
    minimum_evidence_confidence: float = 0.7
    ambiguity_margin: float = 0.05
    maximum_evidence_items: int = 24
    maximum_reference_length: int = 512
    maximum_attributes: int = 32
    allow_external_evidence: bool = False

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_evidence_confidence <= 1:
            raise ValueError(
                "presence confidence threshold must be between zero and one"
            )
        if not 0 <= self.ambiguity_margin <= 1:
            raise ValueError("presence ambiguity margin must be between zero and one")
        if self.maximum_evidence_items <= 0:
            raise ValueError("presence evidence limit must be positive")
        if self.maximum_reference_length <= 0:
            raise ValueError("presence reference limit must be positive")
        if self.maximum_attributes <= 0:
            raise ValueError("presence attribute limit must be positive")


@dataclass(frozen=True)
class PresenceUnderstandingRequest:
    owner: str
    resolved_observation: ResolvedAmbientObservation
    evidence: tuple[PresenceEvidence, ...] = ()
    understanding_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("presence understanding owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "evidence", tuple(self.evidence))


@dataclass(frozen=True)
class PresenceUnderstandingResult:
    request: PresenceUnderstandingRequest
    status: PresenceUnderstandingStatus | str
    action: PresenceUnderstandingAction | str
    dominant_presence: PresenceState | str | None
    accepted_evidence: tuple[PresenceEvidence, ...]
    attributes: tuple[str, ...]
    confidence: float
    presence_understood: bool
    confirmation_required: bool
    identity_inference_allowed: bool
    biometric_analysis_allowed: bool
    precise_person_counting_allowed: bool
    activity_inference_allowed: bool
    movement_tracking_allowed: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    understanding_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", PresenceUnderstandingStatus(self.status))
        object.__setattr__(self, "action", PresenceUnderstandingAction(self.action))
        if self.dominant_presence is not None:
            object.__setattr__(
                self, "dominant_presence", PresenceState(self.dominant_presence)
            )
        object.__setattr__(self, "accepted_evidence", tuple(self.accepted_evidence))
        object.__setattr__(self, "attributes", tuple(self.attributes))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("presence understanding timestamp must be timezone-aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "presence understanding confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("presence understanding rationale must not be empty")
        forbidden = (
            self.identity_inference_allowed,
            self.biometric_analysis_allowed,
            self.precise_person_counting_allowed,
            self.activity_inference_allowed,
            self.movement_tracking_allowed,
            self.sensor_access_allowed,
            self.automation_allowed,
        )
        if any(forbidden):
            raise ValueError("M136 cannot authorize downstream presence capabilities")
        if self.status is PresenceUnderstandingStatus.UNDERSTOOD:
            if not self.presence_understood or self.dominant_presence is None:
                raise ValueError("understood presence requires a dominant state")
            if self.confirmation_required:
                raise ValueError("understood presence cannot require confirmation")
        else:
            if self.presence_understood or self.dominant_presence is not None:
                raise ValueError(
                    "non-understood presence cannot expose a dominant state"
                )
            if self.accepted_evidence or self.attributes or self.confidence != 0:
                raise ValueError(
                    "non-understood presence cannot expose consolidated evidence"
                )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.understanding_id and self.understanding_id != expected:
            raise ValueError("presence understanding id is inconsistent")
        object.__setattr__(self, "understanding_id", expected)

    def _identity_payload(self) -> str:
        evidence_keys = sorted(
            "|".join(
                (
                    item.evidence_ref,
                    item.observation_ref,
                    item.presence_state.value,
                    str(item.confidence),
                    ",".join(item.attributes),
                    str(item.externally_supplied),
                )
            )
            for item in self.request.evidence
        )
        accepted_keys = sorted(item.evidence_ref for item in self.accepted_evidence)
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.resolved_observation.resolution_id,
                ";".join(evidence_keys),
                str(self.request.understanding_declared),
                self.status.value,
                self.action.value,
                self.dominant_presence.value if self.dominant_presence else "none",
                ";".join(accepted_keys),
                ";".join(self.attributes),
                str(self.confidence),
                str(self.presence_understood),
                str(self.confirmation_required),
                str(self.identity_inference_allowed),
                str(self.biometric_analysis_allowed),
                str(self.precise_person_counting_allowed),
                str(self.activity_inference_allowed),
                str(self.movement_tracking_allowed),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )


@runtime_checkable
class PresenceUnderstandingRepository(Protocol):
    def add(self, result: PresenceUnderstandingResult) -> None: ...
    def get(self, understanding_id: str) -> PresenceUnderstandingResult | None: ...
    def list_all(self) -> tuple[PresenceUnderstandingResult, ...]: ...


class InMemoryPresenceUnderstandingRepository:
    def __init__(self) -> None:
        self._items: dict[str, PresenceUnderstandingResult] = {}

    def add(self, result: PresenceUnderstandingResult) -> None:
        if result.understanding_id in self._items:
            raise ValueError("presence understanding result already exists")
        self._items[result.understanding_id] = result

    def get(self, understanding_id: str) -> PresenceUnderstandingResult | None:
        return self._items.get(understanding_id)

    def list_all(self) -> tuple[PresenceUnderstandingResult, ...]:
        return tuple(self._items.values())
