from __future__ import annotations

from datetime import datetime, timezone

from core.location_resolution import LocationResolutionStatus, ResolvedLocation
from core.places_knowledge import PlaceKnowledgeStatus

from .models import (
    InMemoryRouteIntentRepository,
    RouteConstraint,
    RouteIntent,
    RouteIntentAction,
    RouteIntentPolicy,
    RouteIntentRequest,
    RouteIntentStatus,
    TravelMode,
)


class RouteIntentModelingEngine:
    """Models governed route intent without calculating a route."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryRouteIntentRepository()
        self.policy = policy or RouteIntentPolicy()

    def model(self, request: RouteIntentRequest, *, now=None) -> RouteIntent:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("route intent evaluation timestamp must be timezone-aware")
        result = self._assess(request)
        intent = RouteIntent(request=request, created_at=timestamp, **result)
        self.repository.add(intent)
        return intent

    def _assess(self, request: RouteIntentRequest) -> dict:
        if not request.intent_declared:
            return self._inactive(
                RouteIntentStatus.NOT_APPLICABLE,
                RouteIntentAction.NONE,
                "route_intent_not_declared",
            )
        if request.travel_mode is TravelMode.MIXED and not self.policy.allow_mixed_mode:
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_mixed_mode_not_allowed",
                confirmation_required=True,
            )
        if request.origin is None or request.destination is None:
            return self._inactive(
                RouteIntentStatus.INCOMPLETE,
                RouteIntentAction.CLARIFY,
                "route_intent_endpoint_missing",
                clarification_required=True,
            )
        locations = (request.origin, *request.waypoints, request.destination)
        if any(not self._owner_matches(request.owner, item) for item in locations):
            return self._inactive(
                RouteIntentStatus.BLOCKED,
                RouteIntentAction.WITHHOLD,
                "route_intent_owner_mismatch",
            )
        if any(
            item.status is not LocationResolutionStatus.RESOLVED for item in locations
        ):
            return self._inactive(
                RouteIntentStatus.INCOMPLETE,
                RouteIntentAction.CLARIFY,
                "route_intent_location_unresolved",
                clarification_required=True,
            )
        if any(
            item.confidence < self.policy.minimum_location_confidence
            for item in locations
        ):
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_location_confidence_insufficient",
                confirmation_required=True,
            )
        if len(request.waypoints) > self.policy.maximum_waypoints:
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_waypoint_limit_exceeded",
                confirmation_required=True,
            )
        if len(request.constraints) > self.policy.maximum_constraints:
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_constraint_limit_exceeded",
                confirmation_required=True,
            )
        if self.policy.require_distinct_origin_destination and self._same_location(
            request.origin, request.destination
        ):
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_origin_equals_destination",
                confirmation_required=True,
            )
        if not self._knowledge_matches(
            request.owner, request.origin, request.origin_knowledge
        ):
            return self._inactive(
                RouteIntentStatus.BLOCKED,
                RouteIntentAction.WITHHOLD,
                "route_intent_origin_knowledge_mismatch",
            )
        if not self._knowledge_matches(
            request.owner, request.destination, request.destination_knowledge
        ):
            return self._inactive(
                RouteIntentStatus.BLOCKED,
                RouteIntentAction.WITHHOLD,
                "route_intent_destination_knowledge_mismatch",
            )
        accepted, rejected, conflict = self._govern_constraints(request.constraints)
        if conflict:
            return self._inactive(
                RouteIntentStatus.REVIEW_REQUIRED,
                RouteIntentAction.CONFIRM,
                "route_intent_conflicting_constraints",
                confirmation_required=True,
                rejected_constraint_count=rejected,
            )
        return {
            "status": RouteIntentStatus.READY,
            "action": RouteIntentAction.MODEL,
            "origin_label": request.origin.resolved_label,
            "destination_label": request.destination.resolved_label,
            "waypoint_labels": tuple(
                item.resolved_label or "" for item in request.waypoints
            ),
            "accepted_constraints": accepted,
            "rejected_constraint_count": rejected,
            "route_computation_required": True,
            "clarification_required": False,
            "confirmation_required": False,
            "rationale": ("route_intent_ready_for_future_computation",),
        }

    def _govern_constraints(
        self, constraints: tuple[RouteConstraint, ...]
    ) -> tuple[tuple[RouteConstraint, ...], int, bool]:
        eligible = [
            item
            for item in constraints
            if item.confidence >= self.policy.minimum_constraint_confidence
        ]
        rejected = len(constraints) - len(eligible)
        grouped: dict[tuple[str, str], list[RouteConstraint]] = {}
        for item in eligible:
            grouped.setdefault(item.semantic_key, []).append(item)
        accepted: list[RouteConstraint] = []
        for key in sorted(grouped):
            values = sorted(
                grouped[key],
                key=lambda item: (-item.confidence, item.value.casefold()),
            )
            best = values[0]
            distinct = {item.value.casefold() for item in values}
            if len(distinct) > 1:
                return (), rejected, True
            accepted.append(best)
            rejected += len(values) - 1
        accepted.sort(
            key=lambda item: (item.kind.value, item.name, item.value.casefold())
        )
        return tuple(accepted), rejected, False

    @staticmethod
    def _owner_matches(owner: str, location: ResolvedLocation) -> bool:
        return owner.casefold() == location.request.owner.casefold()

    @staticmethod
    def _same_location(origin: ResolvedLocation, destination: ResolvedLocation) -> bool:
        if origin.resolution_id == destination.resolution_id:
            return True
        if origin.resolved_point is not None and destination.resolved_point is not None:
            return (
                origin.resolved_point.latitude == destination.resolved_point.latitude
                and origin.resolved_point.longitude
                == destination.resolved_point.longitude
            )
        return (origin.resolved_label or "").casefold() == (
            destination.resolved_label or ""
        ).casefold()

    @staticmethod
    def _knowledge_matches(owner, location, knowledge) -> bool:
        if knowledge is None:
            return True
        if knowledge.status is not PlaceKnowledgeStatus.READY:
            return False
        return (
            owner.casefold() == knowledge.request.owner.casefold()
            and knowledge.request.resolved_location.resolution_id
            == location.resolution_id
        )

    @staticmethod
    def _inactive(
        status,
        action,
        reason,
        *,
        clarification_required=False,
        confirmation_required=False,
        rejected_constraint_count=0,
    ) -> dict:
        return {
            "status": status,
            "action": action,
            "origin_label": None,
            "destination_label": None,
            "waypoint_labels": (),
            "accepted_constraints": (),
            "rejected_constraint_count": rejected_constraint_count,
            "route_computation_required": False,
            "clarification_required": clarification_required,
            "confirmation_required": confirmation_required,
            "rationale": (reason,),
        }
