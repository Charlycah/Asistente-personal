from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.ambient_context_foundation import AmbientContext


class AmbientObservationPurpose(str, Enum):
    GENERAL_CONTEXT = "general_context"
    PRESENCE_CONTEXT = "presence_context"
    ACTIVITY_CONTEXT = "activity_context"
    ACOUSTIC_CONTEXT = "acoustic_context"
    ENVIRONMENTAL_CONDITION_CONTEXT = "environmental_condition_context"
    SPATIAL_CONTEXT = "spatial_context"


class AmbientRepresentationKind(str, Enum):
    RAW_SIGNAL = "raw_signal"
    SNAPSHOT = "snapshot"
    TEMPORAL_WINDOW = "temporal_window"
    AGGREGATE = "aggregate"
    EVENT = "event"


class AmbientResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class AmbientResolutionAction(str, Enum):
    SELECT = "select"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class AmbientObservationCandidate:
    candidate_ref: str
    observation_ref: str
    representation_kind: AmbientRepresentationKind | str
    confidence: float
    declared_purposes: tuple[AmbientObservationPurpose | str, ...] = (
        AmbientObservationPurpose.GENERAL_CONTEXT,
    )
    externally_supplied: bool = False

    def __post_init__(self) -> None:
        candidate_ref = self.candidate_ref.strip()
        observation_ref = self.observation_ref.strip()
        if not candidate_ref or not observation_ref:
            raise ValueError("ambient candidate references must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "ambient candidate confidence must be between zero and one"
            )
        purposes = tuple(
            AmbientObservationPurpose(item) for item in self.declared_purposes
        )
        if not purposes:
            raise ValueError("ambient candidate purposes must not be empty")
        if len(set(purposes)) != len(purposes):
            raise ValueError("ambient candidate purposes must be unique")
        object.__setattr__(self, "candidate_ref", candidate_ref)
        object.__setattr__(self, "observation_ref", observation_ref)
        object.__setattr__(
            self,
            "representation_kind",
            AmbientRepresentationKind(self.representation_kind),
        )
        object.__setattr__(self, "declared_purposes", purposes)


@dataclass(frozen=True)
class AmbientObservationResolutionPolicy:
    minimum_candidate_confidence: float = 0.7
    maximum_candidates: int = 16
    maximum_reference_length: int = 512
    allow_external_candidates: bool = False
    prefer_snapshot_representation: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_candidate_confidence <= 1:
            raise ValueError(
                "ambient resolution confidence must be between zero and one"
            )
        if self.maximum_candidates <= 0:
            raise ValueError("ambient candidate limit must be positive")
        if self.maximum_reference_length <= 0:
            raise ValueError("ambient resolution reference limit must be positive")


@dataclass(frozen=True)
class AmbientObservationResolutionRequest:
    owner: str
    ambient_context: AmbientContext
    purpose: AmbientObservationPurpose | str = AmbientObservationPurpose.GENERAL_CONTEXT
    candidates: tuple[AmbientObservationCandidate, ...] = ()
    resolution_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("ambient resolution owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "purpose", AmbientObservationPurpose(self.purpose))
        object.__setattr__(self, "candidates", tuple(self.candidates))


@dataclass(frozen=True)
class ResolvedAmbientObservation:
    request: AmbientObservationResolutionRequest
    status: AmbientResolutionStatus | str
    action: AmbientResolutionAction | str
    selected_candidate: AmbientObservationCandidate | None
    observation_resolved: bool
    presence_understanding_required: bool
    activity_understanding_required: bool
    acoustic_understanding_required: bool
    environmental_condition_understanding_required: bool
    spatial_understanding_required: bool
    sensor_access_allowed: bool
    automation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolution_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", AmbientResolutionStatus(self.status))
        object.__setattr__(self, "action", AmbientResolutionAction(self.action))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("ambient resolution timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("ambient resolution rationale must not be empty")
        if self.sensor_access_allowed or self.automation_allowed:
            raise ValueError("M135 cannot authorize sensor access or automation")
        if self.status is AmbientResolutionStatus.RESOLVED:
            if not self.observation_resolved or self.selected_candidate is None:
                raise ValueError(
                    "resolved ambient observation requires a selected candidate"
                )
        elif self.observation_resolved or self.selected_candidate is not None:
            raise ValueError(
                "non-resolved ambient observation cannot expose a candidate"
            )
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.resolution_id and self.resolution_id != expected:
            raise ValueError("ambient resolution id is inconsistent")
        object.__setattr__(self, "resolution_id", expected)

    def _identity_payload(self) -> str:
        selected = self.selected_candidate
        selected_key = "none" if selected is None else self._candidate_key(selected)
        candidate_keys = sorted(
            self._candidate_key(item) for item in self.request.candidates
        )
        return "|".join(
            (
                self.request.owner.casefold(),
                self.request.ambient_context.context_id,
                self.request.purpose.value,
                ";".join(candidate_keys),
                str(self.request.resolution_declared),
                self.status.value,
                self.action.value,
                selected_key,
                str(self.observation_resolved),
                str(self.presence_understanding_required),
                str(self.activity_understanding_required),
                str(self.acoustic_understanding_required),
                str(self.environmental_condition_understanding_required),
                str(self.spatial_understanding_required),
                str(self.sensor_access_allowed),
                str(self.automation_allowed),
                ";".join(self.rationale),
                self.created_at.isoformat(),
            )
        )

    @staticmethod
    def _candidate_key(item: AmbientObservationCandidate) -> str:
        return "|".join(
            (
                item.candidate_ref,
                item.observation_ref,
                item.representation_kind.value,
                str(item.confidence),
                ",".join(purpose.value for purpose in item.declared_purposes),
                str(item.externally_supplied),
            )
        )


@runtime_checkable
class AmbientObservationResolutionRepository(Protocol):
    def add(self, resolution: ResolvedAmbientObservation) -> None: ...
    def get(self, resolution_id: str) -> ResolvedAmbientObservation | None: ...
    def list_all(self) -> tuple[ResolvedAmbientObservation, ...]: ...


class InMemoryAmbientObservationResolutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, ResolvedAmbientObservation] = {}

    def add(self, resolution: ResolvedAmbientObservation) -> None:
        if resolution.resolution_id in self._items:
            raise ValueError("ambient resolution already exists")
        self._items[resolution.resolution_id] = resolution

    def get(self, resolution_id: str) -> ResolvedAmbientObservation | None:
        return self._items.get(resolution_id)

    def list_all(self) -> tuple[ResolvedAmbientObservation, ...]:
        return tuple(self._items.values())
