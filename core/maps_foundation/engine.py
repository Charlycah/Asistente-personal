from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    InMemoryMapsFoundationRepository,
    MapContext,
    MapFoundationAction,
    MapFoundationStatus,
    MapPrecision,
    MapPurpose,
    MapsFoundationPolicy,
    MapsFoundationRequest,
)


class MapsFoundationEngine:
    """Establishes governed geospatial context without provider or routing I/O."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryMapsFoundationRepository()
        self.policy = policy or MapsFoundationPolicy()

    def establish(self, request: MapsFoundationRequest, *, now=None) -> MapContext:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("map evaluation timestamp must be aware")
        result = self._assess(request, timestamp)
        context = MapContext(request=request, created_at=timestamp, **result)
        self.repository.add(context)
        return context

    def _assess(self, request: MapsFoundationRequest, now: datetime) -> dict:
        if not request.maps_context_declared:
            return self._inactive(
                MapFoundationStatus.NOT_APPLICABLE,
                MapFoundationAction.NONE,
                "maps_context_not_declared",
                request,
            )
        if self.policy.require_explicit_consent and not request.explicit_user_consent:
            return self._inactive(
                MapFoundationStatus.REVIEW_REQUIRED,
                MapFoundationAction.CONFIRM,
                "maps_user_consent_missing",
                request,
            )
        if (
            request.requested_precision is MapPrecision.PRECISE
            and not self.policy.allow_precise_location
        ):
            return self._inactive(
                MapFoundationStatus.BLOCKED,
                MapFoundationAction.WITHHOLD,
                "maps_precise_location_disallowed",
                request,
            )
        if (
            request.purpose is MapPurpose.ROUTE_PREPARATION
            and not self.policy.allow_route_preparation
        ):
            return self._inactive(
                MapFoundationStatus.BLOCKED,
                MapFoundationAction.WITHHOLD,
                "maps_route_preparation_disallowed",
                request,
            )
        location = request.location
        if location is None:
            if request.purpose is MapPurpose.ORIENTATION:
                return self._inactive(
                    MapFoundationStatus.REVIEW_REQUIRED,
                    MapFoundationAction.CONFIRM,
                    "maps_location_required_for_orientation",
                    request,
                )
            return self._ready(request, False, "maps_context_ready_without_location")
        age = (now - location.observed_at).total_seconds()
        if age < 0 or age > self.policy.max_signal_age_seconds:
            return self._inactive(
                MapFoundationStatus.REVIEW_REQUIRED,
                MapFoundationAction.CONFIRM,
                "maps_location_stale",
                request,
            )
        if location.confidence < self.policy.minimum_confidence:
            return self._inactive(
                MapFoundationStatus.REVIEW_REQUIRED,
                MapFoundationAction.CONFIRM,
                "maps_location_confidence_low",
                request,
            )
        return self._ready(request, True, "maps_context_ready")

    @staticmethod
    def _ready(request, location_available, reason) -> dict:
        return {
            "status": MapFoundationStatus.READY,
            "action": MapFoundationAction.ESTABLISH,
            "effective_precision": request.requested_precision,
            "effective_scope": request.requested_scope,
            "location_available": location_available,
            "provider_required": True,
            "route_computation_allowed": False,
            "rationale": (reason,),
        }

    @staticmethod
    def _inactive(status, action, reason, request) -> dict:
        return {
            "status": status,
            "action": action,
            "effective_precision": request.requested_precision,
            "effective_scope": request.requested_scope,
            "location_available": False,
            "provider_required": False,
            "route_computation_allowed": False,
            "rationale": (reason,),
        }
