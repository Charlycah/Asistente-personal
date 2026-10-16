from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.location_resolution import ResolvedLocation
from core.maps_foundation import MapContext
from core.navigation_coordination import NavigationCoordinationDecision
from core.places_knowledge import PlaceKnowledgeProfile
from core.route_intent_modeling import RouteIntent


class MapIntegrationStatus(str, Enum):
    READY = "ready"
    PARTIAL = "partial"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    NOT_APPLICABLE = "not_applicable"


class MapIntegrationAction(str, Enum):
    INTEGRATE = "integrate"
    RETAIN_PARTIAL = "retain_partial"
    CONFIRM = "confirm"
    WITHHOLD = "withhold"
    NONE = "none"


@dataclass(frozen=True)
class MapContextIntegrationPolicy:
    require_ready_map_context: bool = True
    allow_partial_context: bool = True
    require_navigation_lineage: bool = True
    maximum_locations: int = 20
    maximum_place_profiles: int = 20

    def __post_init__(self) -> None:
        if self.maximum_locations <= 0:
            raise ValueError("map integration location limit must be positive")
        if self.maximum_place_profiles <= 0:
            raise ValueError("map integration profile limit must be positive")


@dataclass(frozen=True)
class MapContextIntegrationRequest:
    owner: str
    map_context: MapContext
    resolved_locations: tuple[ResolvedLocation, ...] = ()
    place_profiles: tuple[PlaceKnowledgeProfile, ...] = ()
    route_intent: RouteIntent | None = None
    navigation_decision: NavigationCoordinationDecision | None = None
    integration_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        if not owner:
            raise ValueError("map integration owner must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "resolved_locations", tuple(self.resolved_locations))
        object.__setattr__(self, "place_profiles", tuple(self.place_profiles))


@dataclass(frozen=True)
class IntegratedMapContext:
    request: MapContextIntegrationRequest
    status: MapIntegrationStatus | str
    action: MapIntegrationAction | str
    map_context_id: str | None
    location_ids: tuple[str, ...]
    place_profile_ids: tuple[str, ...]
    route_intent_id: str | None
    navigation_decision_id: str | None
    spatial_context_available: bool
    place_knowledge_available: bool
    route_intent_available: bool
    routing_preparation_allowed: bool
    navigation_start_allowed: bool
    live_guidance_allowed: bool
    confirmation_required: bool
    rationale: tuple[str, ...]
    created_at: datetime
    integration_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", MapIntegrationStatus(self.status))
        object.__setattr__(self, "action", MapIntegrationAction(self.action))
        object.__setattr__(self, "location_ids", tuple(self.location_ids))
        object.__setattr__(self, "place_profile_ids", tuple(self.place_profile_ids))
        object.__setattr__(self, "rationale", tuple(self.rationale))
        if self.created_at.tzinfo is None:
            raise ValueError("map integration timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("map integration rationale must not be empty")
        if self.navigation_start_allowed or self.live_guidance_allowed:
            raise ValueError("M127 cannot authorize navigation execution")
        if self.status in {
            MapIntegrationStatus.BLOCKED,
            MapIntegrationStatus.NOT_APPLICABLE,
        }:
            if any(
                (
                    self.map_context_id,
                    self.location_ids,
                    self.place_profile_ids,
                    self.route_intent_id,
                    self.navigation_decision_id,
                )
            ):
                raise ValueError(
                    "inactive integration cannot expose integrated lineage"
                )
            if any(
                (
                    self.spatial_context_available,
                    self.place_knowledge_available,
                    self.route_intent_available,
                    self.routing_preparation_allowed,
                )
            ):
                raise ValueError("inactive integration cannot expose capabilities")
        if (
            self.status is MapIntegrationStatus.REVIEW_REQUIRED
            and not self.confirmation_required
        ):
            raise ValueError("review-required integration must require confirmation")
        expected = sha256(
            "|".join(
                (
                    self.request.owner.casefold(),
                    self.request.map_context.context_id,
                    ";".join(
                        item.resolution_id for item in self.request.resolved_locations
                    ),
                    ";".join(item.profile_id for item in self.request.place_profiles),
                    self.request.route_intent.intent_id
                    if self.request.route_intent
                    else "none",
                    self.request.navigation_decision.decision_id
                    if self.request.navigation_decision
                    else "none",
                    str(self.request.integration_requested),
                    self.status.value,
                    self.action.value,
                    self.map_context_id or "none",
                    ";".join(self.location_ids),
                    ";".join(self.place_profile_ids),
                    self.route_intent_id or "none",
                    self.navigation_decision_id or "none",
                    str(self.spatial_context_available),
                    str(self.place_knowledge_available),
                    str(self.route_intent_available),
                    str(self.routing_preparation_allowed),
                    str(self.navigation_start_allowed),
                    str(self.live_guidance_allowed),
                    str(self.confirmation_required),
                    ";".join(self.rationale),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.integration_id and self.integration_id != expected:
            raise ValueError("map integration id is inconsistent")
        object.__setattr__(self, "integration_id", expected)


@runtime_checkable
class MapContextIntegrationRepository(Protocol):
    def add(self, context: IntegratedMapContext) -> None: ...
    def get(self, integration_id: str) -> IntegratedMapContext | None: ...
    def list_all(self) -> tuple[IntegratedMapContext, ...]: ...


class InMemoryMapContextIntegrationRepository:
    def __init__(self) -> None:
        self._items: dict[str, IntegratedMapContext] = {}

    def add(self, context: IntegratedMapContext) -> None:
        if context.integration_id in self._items:
            raise ValueError("integrated map context already exists")
        self._items[context.integration_id] = context

    def get(self, integration_id: str) -> IntegratedMapContext | None:
        return self._items.get(integration_id)

    def list_all(self) -> tuple[IntegratedMapContext, ...]:
        return tuple(self._items.values())
