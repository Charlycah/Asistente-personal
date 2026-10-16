from __future__ import annotations

from datetime import datetime, timezone

from core.route_intent_modeling import RouteIntentStatus

from .models import (
    InMemoryNavigationCoordinationRepository,
    NavigationCoordinationAction,
    NavigationCoordinationDecision,
    NavigationCoordinationPolicy,
    NavigationCoordinationRequest,
    NavigationCoordinationStatus,
)


class NavigationCoordinationEngine:
    """Coordinates a governed route intent without computing or executing a route."""

    def __init__(self, *, repository=None, policy=None) -> None:
        self.repository = repository or InMemoryNavigationCoordinationRepository()
        self.policy = policy or NavigationCoordinationPolicy()

    def coordinate(
        self,
        request: NavigationCoordinationRequest,
        *,
        now: datetime | None = None,
    ) -> NavigationCoordinationDecision:
        created_at = now or datetime.now(timezone.utc)
        values = self._evaluate(request)
        decision = NavigationCoordinationDecision(
            request=request,
            created_at=created_at,
            navigation_start_allowed=False,
            live_guidance_allowed=False,
            **values,
        )
        self.repository.add(decision)
        return decision

    def _evaluate(self, request: NavigationCoordinationRequest) -> dict:
        intent = request.route_intent
        if not request.coordination_requested:
            return self._inactive(
                NavigationCoordinationStatus.NOT_APPLICABLE,
                NavigationCoordinationAction.NONE,
                "navigation_coordination_not_requested",
            )
        if request.owner.casefold() != intent.request.owner.casefold():
            return self._inactive(
                NavigationCoordinationStatus.BLOCKED,
                NavigationCoordinationAction.WITHHOLD,
                "navigation_owner_lineage_mismatch",
            )
        if intent.status is RouteIntentStatus.NOT_APPLICABLE:
            return self._inactive(
                NavigationCoordinationStatus.NOT_APPLICABLE,
                NavigationCoordinationAction.NONE,
                "route_intent_not_applicable",
            )
        if intent.status is RouteIntentStatus.BLOCKED:
            return self._inactive(
                NavigationCoordinationStatus.BLOCKED,
                NavigationCoordinationAction.WITHHOLD,
                "route_intent_blocked",
            )
        if intent.status is RouteIntentStatus.INCOMPLETE:
            return self._inactive(
                NavigationCoordinationStatus.AWAITING_INPUT,
                NavigationCoordinationAction.CLARIFY,
                "route_intent_incomplete",
            )
        if intent.status is RouteIntentStatus.REVIEW_REQUIRED:
            return self._inactive(
                NavigationCoordinationStatus.REVIEW_REQUIRED,
                NavigationCoordinationAction.CONFIRM,
                "route_intent_requires_review",
            )
        if not intent.route_computation_required:
            return self._inactive(
                NavigationCoordinationStatus.BLOCKED,
                NavigationCoordinationAction.WITHHOLD,
                "route_intent_does_not_require_computation",
            )
        if (
            self.policy.require_explicit_user_authorization
            and not request.explicit_user_authorization
        ):
            return self._inactive(
                NavigationCoordinationStatus.REVIEW_REQUIRED,
                NavigationCoordinationAction.CONFIRM,
                "explicit_navigation_authorization_required",
                user_authorization_required=True,
            )
        if (
            self.policy.require_routing_provider
            and not request.routing_provider_available
        ):
            return self._inactive(
                NavigationCoordinationStatus.AWAITING_INPUT,
                NavigationCoordinationAction.WITHHOLD,
                "routing_provider_required",
                provider_required=True,
            )
        if (
            self.policy.require_navigation_surface
            and not request.navigation_surface_available
        ):
            return self._inactive(
                NavigationCoordinationStatus.AWAITING_INPUT,
                NavigationCoordinationAction.WITHHOLD,
                "navigation_surface_required",
                surface_required=True,
            )
        background_allowed = (
            request.background_preparation_requested
            and self.policy.allow_background_preparation
        )
        return {
            "status": NavigationCoordinationStatus.READY_FOR_ROUTING,
            "action": NavigationCoordinationAction.PREPARE_ROUTE_REQUEST,
            "routing_request_allowed": True,
            "provider_required": False,
            "surface_required": False,
            "user_authorization_required": False,
            "background_preparation_allowed": background_allowed,
            "route_intent_id": intent.intent_id,
            "rationale": ("route_intent_ready_for_provider_routing",),
        }

    @staticmethod
    def _inactive(
        status,
        action,
        reason,
        *,
        provider_required=False,
        surface_required=False,
        user_authorization_required=False,
    ) -> dict:
        return {
            "status": status,
            "action": action,
            "routing_request_allowed": False,
            "provider_required": provider_required,
            "surface_required": surface_required,
            "user_authorization_required": user_authorization_required,
            "background_preparation_allowed": False,
            "route_intent_id": None,
            "rationale": (reason,),
        }
