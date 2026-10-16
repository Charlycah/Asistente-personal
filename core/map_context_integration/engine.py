from __future__ import annotations

from datetime import datetime, timezone

from core.location_resolution import LocationResolutionStatus
from core.maps_foundation import MapFoundationStatus
from core.navigation_coordination import NavigationCoordinationStatus
from core.places_knowledge import PlaceKnowledgeStatus
from core.route_intent_modeling import RouteIntentStatus

from .models import (
    InMemoryMapContextIntegrationRepository,
    IntegratedMapContext,
    MapContextIntegrationPolicy,
    MapContextIntegrationRequest,
    MapIntegrationAction,
    MapIntegrationStatus,
)


class MapContextIntegrationEngine:
    """Integrates governed M122-M126 outputs without routing or navigation execution."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryMapContextIntegrationRepository()
        self.policy = policy or MapContextIntegrationPolicy()

    def integrate(
        self, request: MapContextIntegrationRequest, *, now: datetime | None = None
    ) -> IntegratedMapContext:
        created_at = now or datetime.now(timezone.utc)
        values = self._evaluate(request)
        result = IntegratedMapContext(
            request=request,
            created_at=created_at,
            navigation_start_allowed=False,
            live_guidance_allowed=False,
            **values,
        )
        self.repository.add(result)
        return result

    def _evaluate(self, request: MapContextIntegrationRequest) -> dict:
        if not request.integration_requested:
            return self._inactive(
                MapIntegrationStatus.NOT_APPLICABLE,
                MapIntegrationAction.NONE,
                "map_context_integration_not_requested",
            )
        if request.owner.casefold() != request.map_context.request.owner.casefold():
            return self._inactive(
                MapIntegrationStatus.BLOCKED,
                MapIntegrationAction.WITHHOLD,
                "map_context_owner_lineage_mismatch",
            )
        if (
            self.policy.require_ready_map_context
            and request.map_context.status is not MapFoundationStatus.READY
        ):
            return self._inactive(
                MapIntegrationStatus.BLOCKED,
                MapIntegrationAction.WITHHOLD,
                "map_context_not_ready",
            )
        if len(request.resolved_locations) > self.policy.maximum_locations:
            return self._inactive(
                MapIntegrationStatus.BLOCKED,
                MapIntegrationAction.WITHHOLD,
                "map_location_limit_exceeded",
            )
        if len(request.place_profiles) > self.policy.maximum_place_profiles:
            return self._inactive(
                MapIntegrationStatus.BLOCKED,
                MapIntegrationAction.WITHHOLD,
                "map_place_profile_limit_exceeded",
            )
        for location in request.resolved_locations:
            if (
                request.owner.casefold() != location.request.owner.casefold()
                or location.request.map_context.context_id
                != request.map_context.context_id
            ):
                return self._inactive(
                    MapIntegrationStatus.BLOCKED,
                    MapIntegrationAction.WITHHOLD,
                    "location_lineage_mismatch",
                )
        location_ids = {item.resolution_id for item in request.resolved_locations}
        for profile in request.place_profiles:
            location = profile.request.resolved_location
            if (
                request.owner.casefold() != profile.request.owner.casefold()
                or location.resolution_id not in location_ids
            ):
                return self._inactive(
                    MapIntegrationStatus.BLOCKED,
                    MapIntegrationAction.WITHHOLD,
                    "place_profile_lineage_mismatch",
                )
        intent = request.route_intent
        navigation = request.navigation_decision
        if intent is not None:
            if request.owner.casefold() != intent.request.owner.casefold():
                return self._inactive(
                    MapIntegrationStatus.BLOCKED,
                    MapIntegrationAction.WITHHOLD,
                    "route_intent_owner_lineage_mismatch",
                )
            referenced = [
                intent.request.origin,
                intent.request.destination,
                *intent.request.waypoints,
            ]
            if any(
                item is not None and item.resolution_id not in location_ids
                for item in referenced
            ):
                return self._inactive(
                    MapIntegrationStatus.BLOCKED,
                    MapIntegrationAction.WITHHOLD,
                    "route_intent_location_lineage_mismatch",
                )
        if navigation is not None:
            if (
                intent is None
                or navigation.request.route_intent.intent_id != intent.intent_id
            ):
                return self._inactive(
                    MapIntegrationStatus.BLOCKED,
                    MapIntegrationAction.WITHHOLD,
                    "navigation_lineage_mismatch",
                )
        review = any(
            item.status
            in {
                LocationResolutionStatus.AMBIGUOUS,
                LocationResolutionStatus.REVIEW_REQUIRED,
            }
            for item in request.resolved_locations
        )
        review = review or any(
            item.status is PlaceKnowledgeStatus.REVIEW_REQUIRED
            for item in request.place_profiles
        )
        review = review or (
            intent is not None and intent.status is RouteIntentStatus.REVIEW_REQUIRED
        )
        review = review or (
            navigation is not None
            and navigation.status is NavigationCoordinationStatus.REVIEW_REQUIRED
        )
        if review:
            return self._active(
                request,
                MapIntegrationStatus.REVIEW_REQUIRED,
                MapIntegrationAction.CONFIRM,
                True,
                "map_context_requires_review",
            )
        if (
            navigation is None
            and intent is not None
            and self.policy.require_navigation_lineage
        ):
            return self._partial(request, "navigation_coordination_missing")
        incomplete = any(
            item.status is not LocationResolutionStatus.RESOLVED
            for item in request.resolved_locations
        )
        incomplete = incomplete or any(
            item.status is not PlaceKnowledgeStatus.READY
            for item in request.place_profiles
        )
        incomplete = incomplete or (
            intent is not None and intent.status is not RouteIntentStatus.READY
        )
        incomplete = incomplete or (
            navigation is not None
            and navigation.status is not NavigationCoordinationStatus.READY_FOR_ROUTING
        )
        if incomplete:
            return self._partial(request, "map_context_contains_partial_upstream_state")
        return self._active(
            request,
            MapIntegrationStatus.READY,
            MapIntegrationAction.INTEGRATE,
            False,
            "map_context_integration_ready",
        )

    def _partial(self, request, reason):
        if not self.policy.allow_partial_context:
            return self._inactive(
                MapIntegrationStatus.BLOCKED, MapIntegrationAction.WITHHOLD, reason
            )
        return self._active(
            request,
            MapIntegrationStatus.PARTIAL,
            MapIntegrationAction.RETAIN_PARTIAL,
            False,
            reason,
        )

    @staticmethod
    def _active(request, status, action, confirmation_required, reason):
        locations = tuple(
            sorted({item.resolution_id for item in request.resolved_locations})
        )
        profiles = tuple(sorted({item.profile_id for item in request.place_profiles}))
        navigation = request.navigation_decision
        return {
            "status": status,
            "action": action,
            "map_context_id": request.map_context.context_id,
            "location_ids": locations,
            "place_profile_ids": profiles,
            "route_intent_id": request.route_intent.intent_id
            if request.route_intent
            else None,
            "navigation_decision_id": navigation.decision_id if navigation else None,
            "spatial_context_available": request.map_context.location_available
            or bool(locations),
            "place_knowledge_available": bool(profiles),
            "route_intent_available": request.route_intent is not None,
            "routing_preparation_allowed": bool(
                navigation
                and navigation.routing_request_allowed
                and status is MapIntegrationStatus.READY
            ),
            "confirmation_required": confirmation_required,
            "rationale": (reason,),
        }

    @staticmethod
    def _inactive(status, action, reason):
        return {
            "status": status,
            "action": action,
            "map_context_id": None,
            "location_ids": (),
            "place_profile_ids": (),
            "route_intent_id": None,
            "navigation_decision_id": None,
            "spatial_context_available": False,
            "place_knowledge_available": False,
            "route_intent_available": False,
            "routing_preparation_allowed": False,
            "confirmation_required": False,
            "rationale": (reason,),
        }
