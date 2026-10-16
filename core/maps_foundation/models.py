from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable


class MapPurpose(str, Enum):
    ORIENTATION = "orientation"
    PLACE_CONTEXT = "place_context"
    ROUTE_PREPARATION = "route_preparation"
    SAFETY_CONTEXT = "safety_context"


class MapPrecision(str, Enum):
    APPROXIMATE = "approximate"
    NEIGHBORHOOD = "neighborhood"
    PRECISE = "precise"


class MapScope(str, Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    GLOBAL = "global"


class MapFoundationStatus(str, Enum):
    READY = "ready"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class MapFoundationAction(str, Enum):
    ESTABLISH = "establish"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class GeoPointSignal:
    latitude: float
    longitude: float
    confidence: float
    observed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "declared"

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValueError("map latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("map longitude must be between -180 and 180")
        if not 0 <= self.confidence <= 1:
            raise ValueError("map confidence must be between zero and one")
        if self.observed_at.tzinfo is None:
            raise ValueError("map observation timestamp must be aware")
        normalized = self.source.strip().casefold()
        if not normalized:
            raise ValueError("map source must not be blank")
        object.__setattr__(self, "source", normalized)


@dataclass(frozen=True)
class MapsFoundationPolicy:
    max_signal_age_seconds: float = 300.0
    minimum_confidence: float = 0.7
    require_explicit_consent: bool = True
    allow_precise_location: bool = True
    allow_route_preparation: bool = True

    def __post_init__(self) -> None:
        if self.max_signal_age_seconds <= 0:
            raise ValueError("map signal age must be positive")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("map minimum confidence must be between zero and one")


@dataclass(frozen=True)
class MapsFoundationRequest:
    owner: str
    purpose: MapPurpose | str
    requested_precision: MapPrecision | str
    requested_scope: MapScope | str
    location: GeoPointSignal | None = None
    maps_context_declared: bool = True
    explicit_user_consent: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "purpose", MapPurpose(self.purpose))
        object.__setattr__(
            self, "requested_precision", MapPrecision(self.requested_precision)
        )
        object.__setattr__(self, "requested_scope", MapScope(self.requested_scope))
        if not self.owner.strip():
            raise ValueError("maps owner must not be blank")


@dataclass(frozen=True)
class MapContext:
    request: MapsFoundationRequest
    status: MapFoundationStatus | str
    action: MapFoundationAction | str
    effective_precision: MapPrecision | str
    effective_scope: MapScope | str
    location_available: bool
    provider_required: bool
    route_computation_allowed: bool
    rationale: tuple[str, ...]
    created_at: datetime
    context_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", MapFoundationStatus(self.status))
        object.__setattr__(self, "action", MapFoundationAction(self.action))
        object.__setattr__(
            self, "effective_precision", MapPrecision(self.effective_precision)
        )
        object.__setattr__(self, "effective_scope", MapScope(self.effective_scope))
        if self.created_at.tzinfo is None:
            raise ValueError("map context timestamp must be aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("map rationale must not be empty")
        if self.status is not MapFoundationStatus.READY:
            if self.location_available or self.route_computation_allowed:
                raise ValueError("non-ready map context cannot expose capabilities")
        if self.route_computation_allowed:
            raise ValueError("M122 cannot authorize route computation")
        location = self.request.location
        location_key = (
            "none"
            if location is None
            else "|".join(
                (
                    str(location.latitude),
                    str(location.longitude),
                    str(location.confidence),
                    location.observed_at.isoformat(),
                    location.source,
                )
            )
        )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    self.request.purpose.value,
                    self.request.requested_precision.value,
                    self.request.requested_scope.value,
                    location_key,
                    self.status.value,
                    self.action.value,
                    self.effective_precision.value,
                    self.effective_scope.value,
                    str(self.location_available),
                    str(self.provider_required),
                    str(self.route_computation_allowed),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.context_id and self.context_id != expected:
            raise ValueError("map context id is inconsistent")
        object.__setattr__(self, "context_id", expected)


@runtime_checkable
class MapsFoundationRepository(Protocol):
    def add(self, context: MapContext) -> None: ...
    def get(self, context_id: str) -> MapContext | None: ...
    def list_all(self) -> tuple[MapContext, ...]: ...


class InMemoryMapsFoundationRepository:
    def __init__(self) -> None:
        self._items: dict[str, MapContext] = {}

    def add(self, context: MapContext) -> None:
        if context.context_id in self._items:
            raise ValueError("map context already exists")
        self._items[context.context_id] = context

    def get(self, context_id: str) -> MapContext | None:
        return self._items.get(context_id)

    def list_all(self) -> tuple[MapContext, ...]:
        return tuple(self._items.values())
