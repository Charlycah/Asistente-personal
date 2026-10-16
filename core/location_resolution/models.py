from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.maps_foundation import GeoPointSignal, MapContext


class LocationReferenceKind(str, Enum):
    CURRENT_LOCATION = "current_location"
    COORDINATES = "coordinates"
    ADDRESS = "address"
    PLACE = "place"
    REGION = "region"


class LocationResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    AMBIGUOUS = "ambiguous"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class LocationResolutionAction(str, Enum):
    ACCEPT = "accept"
    CLARIFY = "clarify"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class LocationCandidate:
    label: str
    kind: LocationReferenceKind | str
    confidence: float
    point: GeoPointSignal | None = None
    source: str = "declared"
    external_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", LocationReferenceKind(self.kind))
        normalized_label = " ".join(self.label.strip().split())
        if not normalized_label:
            raise ValueError("location candidate label must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "location candidate confidence must be between zero and one"
            )
        normalized_source = self.source.strip().casefold()
        if not normalized_source:
            raise ValueError("location candidate source must not be blank")
        normalized_external_id = None
        if self.external_id is not None:
            normalized_external_id = self.external_id.strip()
            if not normalized_external_id:
                raise ValueError("location candidate external id must not be blank")
        object.__setattr__(self, "label", normalized_label)
        object.__setattr__(self, "source", normalized_source)
        object.__setattr__(self, "external_id", normalized_external_id)


@dataclass(frozen=True)
class LocationResolutionPolicy:
    minimum_confidence: float = 0.75
    ambiguity_margin: float = 0.1
    require_point_for_coordinates: bool = True
    allow_external_candidates: bool = True
    maximum_candidates: int = 25

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("location resolution minimum confidence is invalid")
        if not 0 <= self.ambiguity_margin <= 1:
            raise ValueError("location resolution ambiguity margin is invalid")
        if self.maximum_candidates <= 0:
            raise ValueError("location resolution candidate limit must be positive")


@dataclass(frozen=True)
class LocationResolutionRequest:
    owner: str
    map_context: MapContext
    reference: str
    reference_kind: LocationReferenceKind | str
    candidates: tuple[LocationCandidate, ...] = ()
    resolution_declared: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "reference_kind", LocationReferenceKind(self.reference_kind)
        )
        normalized_owner = self.owner.strip()
        normalized_reference = " ".join(self.reference.strip().split())
        if not normalized_owner:
            raise ValueError("location resolution owner must not be blank")
        if not normalized_reference:
            raise ValueError("location reference must not be blank")
        object.__setattr__(self, "owner", normalized_owner)
        object.__setattr__(self, "reference", normalized_reference)
        object.__setattr__(self, "candidates", tuple(self.candidates))


@dataclass(frozen=True)
class ResolvedLocation:
    request: LocationResolutionRequest
    status: LocationResolutionStatus | str
    action: LocationResolutionAction | str
    selected_candidate: LocationCandidate | None
    resolved_label: str | None
    resolved_point: GeoPointSignal | None
    confidence: float
    provider_required: bool
    clarification_required: bool
    rationale: tuple[str, ...]
    created_at: datetime
    resolution_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", LocationResolutionStatus(self.status))
        object.__setattr__(self, "action", LocationResolutionAction(self.action))
        if self.created_at.tzinfo is None:
            raise ValueError("location resolution timestamp must be aware")
        if not 0 <= self.confidence <= 1:
            raise ValueError(
                "location resolution confidence must be between zero and one"
            )
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("location resolution rationale must not be empty")
        if self.status is LocationResolutionStatus.RESOLVED:
            if self.resolved_label is None:
                raise ValueError("resolved location requires a label")
            if self.clarification_required:
                raise ValueError("resolved location cannot require clarification")
        else:
            if self.selected_candidate is not None or self.resolved_point is not None:
                raise ValueError("unresolved location cannot expose selected evidence")
        if (
            self.status is LocationResolutionStatus.AMBIGUOUS
            and not self.clarification_required
        ):
            raise ValueError("ambiguous location must require clarification")
        candidate_key = "none"
        if self.selected_candidate is not None:
            point = self.selected_candidate.point
            point_key = (
                "none"
                if point is None
                else "|".join(
                    (
                        str(point.latitude),
                        str(point.longitude),
                        str(point.confidence),
                        point.observed_at.isoformat(),
                        point.source,
                    )
                )
            )
            candidate_key = "|".join(
                (
                    self.selected_candidate.label,
                    self.selected_candidate.kind.value,
                    str(self.selected_candidate.confidence),
                    point_key,
                    self.selected_candidate.source,
                    self.selected_candidate.external_id or "none",
                )
            )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    self.request.map_context.context_id,
                    self.request.reference.casefold(),
                    self.request.reference_kind.value,
                    self.status.value,
                    self.action.value,
                    candidate_key,
                    self.resolved_label or "none",
                    str(self.confidence),
                    str(self.provider_required),
                    str(self.clarification_required),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.resolution_id and self.resolution_id != expected:
            raise ValueError("location resolution id is inconsistent")
        object.__setattr__(self, "resolution_id", expected)


@runtime_checkable
class LocationResolutionRepository(Protocol):
    def add(self, resolution: ResolvedLocation) -> None: ...
    def get(self, resolution_id: str) -> ResolvedLocation | None: ...
    def list_all(self) -> tuple[ResolvedLocation, ...]: ...


class InMemoryLocationResolutionRepository:
    def __init__(self) -> None:
        self._items: dict[str, ResolvedLocation] = {}

    def add(self, resolution: ResolvedLocation) -> None:
        if resolution.resolution_id in self._items:
            raise ValueError("location resolution already exists")
        self._items[resolution.resolution_id] = resolution

    def get(self, resolution_id: str) -> ResolvedLocation | None:
        return self._items.get(resolution_id)

    def list_all(self) -> tuple[ResolvedLocation, ...]:
        return tuple(self._items.values())
