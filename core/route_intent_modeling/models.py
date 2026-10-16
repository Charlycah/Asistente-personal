from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.location_resolution import ResolvedLocation
from core.places_knowledge import PlaceKnowledgeProfile


class TravelMode(str, Enum):
    DRIVING = "driving"
    WALKING = "walking"
    CYCLING = "cycling"
    TRANSIT = "transit"
    MIXED = "mixed"


class RoutePriority(str, Enum):
    FASTEST = "fastest"
    SHORTEST = "shortest"
    SIMPLEST = "simplest"
    ACCESSIBLE = "accessible"
    SAFEST = "safest"


class RouteConstraintKind(str, Enum):
    AVOID = "avoid"
    REQUIRE = "require"
    PREFER = "prefer"
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class RouteIntentStatus(str, Enum):
    READY = "ready"
    INCOMPLETE = "incomplete"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class RouteIntentAction(str, Enum):
    MODEL = "model"
    CLARIFY = "clarify"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class RouteConstraint:
    kind: RouteConstraintKind | str
    name: str
    value: str
    confidence: float = 1.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", RouteConstraintKind(self.kind))
        name = " ".join(self.name.strip().split()).casefold()
        value = " ".join(self.value.strip().split())
        if not name or not value:
            raise ValueError("route constraint name and value must not be blank")
        if not 0 <= self.confidence <= 1:
            raise ValueError("route constraint confidence must be between zero and one")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)

    @property
    def semantic_key(self) -> tuple[str, str]:
        return self.kind.value, self.name


@dataclass(frozen=True)
class RouteTimeWindow:
    earliest_departure: datetime | None = None
    latest_arrival: datetime | None = None

    def __post_init__(self) -> None:
        if (
            self.earliest_departure is not None
            and self.earliest_departure.tzinfo is None
        ):
            raise ValueError("route earliest departure must be timezone-aware")
        if self.latest_arrival is not None and self.latest_arrival.tzinfo is None:
            raise ValueError("route latest arrival must be timezone-aware")
        if (
            self.earliest_departure is not None
            and self.latest_arrival is not None
            and self.earliest_departure > self.latest_arrival
        ):
            raise ValueError("route time window is inconsistent")


@dataclass(frozen=True)
class RouteIntentPolicy:
    minimum_location_confidence: float = 0.75
    minimum_constraint_confidence: float = 0.7
    maximum_waypoints: int = 12
    maximum_constraints: int = 30
    require_distinct_origin_destination: bool = True
    allow_mixed_mode: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.minimum_location_confidence <= 1:
            raise ValueError("route minimum location confidence is invalid")
        if not 0 <= self.minimum_constraint_confidence <= 1:
            raise ValueError("route minimum constraint confidence is invalid")
        if self.maximum_waypoints < 0:
            raise ValueError("route waypoint limit must not be negative")
        if self.maximum_constraints <= 0:
            raise ValueError("route constraint limit must be positive")


@dataclass(frozen=True)
class RouteIntentRequest:
    owner: str
    origin: ResolvedLocation | None
    destination: ResolvedLocation | None
    waypoints: tuple[ResolvedLocation, ...] = ()
    origin_knowledge: PlaceKnowledgeProfile | None = None
    destination_knowledge: PlaceKnowledgeProfile | None = None
    travel_mode: TravelMode | str = TravelMode.DRIVING
    priority: RoutePriority | str = RoutePriority.FASTEST
    constraints: tuple[RouteConstraint, ...] = ()
    purpose: str = "travel"
    time_window: RouteTimeWindow | None = None
    intent_declared: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        purpose = " ".join(self.purpose.strip().split()).casefold()
        if not owner:
            raise ValueError("route intent owner must not be blank")
        if not purpose:
            raise ValueError("route purpose must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "purpose", purpose)
        object.__setattr__(self, "travel_mode", TravelMode(self.travel_mode))
        object.__setattr__(self, "priority", RoutePriority(self.priority))
        object.__setattr__(self, "waypoints", tuple(self.waypoints))
        object.__setattr__(self, "constraints", tuple(self.constraints))


@dataclass(frozen=True)
class RouteIntent:
    request: RouteIntentRequest
    status: RouteIntentStatus | str
    action: RouteIntentAction | str
    origin_label: str | None
    destination_label: str | None
    waypoint_labels: tuple[str, ...]
    accepted_constraints: tuple[RouteConstraint, ...]
    rejected_constraint_count: int
    route_computation_required: bool
    clarification_required: bool
    confirmation_required: bool
    rationale: tuple[str, ...]
    created_at: datetime
    intent_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", RouteIntentStatus(self.status))
        object.__setattr__(self, "action", RouteIntentAction(self.action))
        object.__setattr__(self, "waypoint_labels", tuple(self.waypoint_labels))
        object.__setattr__(
            self, "accepted_constraints", tuple(self.accepted_constraints)
        )
        if self.created_at.tzinfo is None:
            raise ValueError("route intent timestamp must be timezone-aware")
        if self.rejected_constraint_count < 0:
            raise ValueError("rejected route constraint count must not be negative")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("route intent rationale must not be empty")
        if self.status is RouteIntentStatus.READY:
            if self.origin_label is None or self.destination_label is None:
                raise ValueError("ready route intent requires origin and destination")
            if self.clarification_required or self.confirmation_required:
                raise ValueError("ready route intent cannot require user resolution")
            if not self.route_computation_required:
                raise ValueError("ready route intent requires future route computation")
        elif (
            self.origin_label is not None
            or self.destination_label is not None
            or self.waypoint_labels
            or self.accepted_constraints
        ):
            raise ValueError("non-ready route intent cannot expose modeled route data")
        constraint_key = ";".join(
            "|".join(
                (
                    item.kind.value,
                    item.name,
                    item.value.casefold(),
                    str(item.confidence),
                )
            )
            for item in self.accepted_constraints
        )
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    (
                        self.request.origin.resolution_id
                        if self.request.origin
                        else "none"
                    ),
                    (
                        self.request.destination.resolution_id
                        if self.request.destination
                        else "none"
                    ),
                    ";".join(item.resolution_id for item in self.request.waypoints),
                    self.request.origin_knowledge.profile_id
                    if self.request.origin_knowledge
                    else "none",
                    self.request.destination_knowledge.profile_id
                    if self.request.destination_knowledge
                    else "none",
                    self.request.travel_mode.value,
                    self.request.priority.value,
                    self.request.purpose,
                    self.status.value,
                    self.action.value,
                    self.origin_label or "none",
                    self.destination_label or "none",
                    ";".join(self.waypoint_labels),
                    constraint_key,
                    str(self.rejected_constraint_count),
                    str(self.route_computation_required),
                    str(self.clarification_required),
                    str(self.confirmation_required),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.intent_id and self.intent_id != expected:
            raise ValueError("route intent id is inconsistent")
        object.__setattr__(self, "intent_id", expected)


@runtime_checkable
class RouteIntentRepository(Protocol):
    def add(self, intent: RouteIntent) -> None: ...
    def get(self, intent_id: str) -> RouteIntent | None: ...
    def list_all(self) -> tuple[RouteIntent, ...]: ...


class InMemoryRouteIntentRepository:
    def __init__(self) -> None:
        self._items: dict[str, RouteIntent] = {}

    def add(self, intent: RouteIntent) -> None:
        if intent.intent_id in self._items:
            raise ValueError("route intent already exists")
        self._items[intent.intent_id] = intent

    def get(self, intent_id: str) -> RouteIntent | None:
        return self._items.get(intent_id)

    def list_all(self) -> tuple[RouteIntent, ...]:
        return tuple(self._items.values())
