from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.location_resolution import (
    LocationCandidate,
    LocationReferenceKind,
    LocationResolutionAction,
    LocationResolutionRequest,
    LocationResolutionStatus,
    ResolvedLocation,
)
from core.maps_foundation import (
    GeoPointSignal,
    MapContext,
    MapFoundationAction,
    MapFoundationStatus,
    MapPrecision,
    MapPurpose,
    MapScope,
    MapsFoundationRequest,
)
from core.navigation_coordination import (
    InMemoryNavigationCoordinationRepository,
    NavigationCoordinationAction,
    NavigationCoordinationDecision,
    NavigationCoordinationEngine,
    NavigationCoordinationPolicy,
    NavigationCoordinationRequest,
    NavigationCoordinationStatus,
)
from core.route_intent_modeling import (
    RouteIntent,
    RouteIntentAction,
    RouteIntentRequest,
    RouteIntentStatus,
)

NOW = datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc)


def location(label, lat):
    point = GeoPointSignal(lat, -58.4, 0.95, NOW, "declared")
    map_request = MapsFoundationRequest(
        owner="Carlos",
        purpose=MapPurpose.ROUTE_PREPARATION,
        requested_precision=MapPrecision.PRECISE,
        requested_scope=MapScope.LOCAL,
        location=point,
        explicit_user_consent=True,
    )
    context = MapContext(
        request=map_request,
        status=MapFoundationStatus.READY,
        action=MapFoundationAction.ESTABLISH,
        effective_precision=MapPrecision.PRECISE,
        effective_scope=MapScope.LOCAL,
        location_available=True,
        provider_required=True,
        route_computation_allowed=False,
        rationale=("maps_context_ready",),
        created_at=NOW,
    )
    candidate = LocationCandidate(label, LocationReferenceKind.PLACE, 0.95, point)
    request = LocationResolutionRequest(
        owner="Carlos",
        map_context=context,
        reference=label,
        reference_kind=LocationReferenceKind.PLACE,
        candidates=(candidate,),
    )
    return ResolvedLocation(
        request=request,
        status=LocationResolutionStatus.RESOLVED,
        action=LocationResolutionAction.ACCEPT,
        selected_candidate=candidate,
        resolved_label=label,
        resolved_point=point,
        confidence=0.95,
        provider_required=False,
        clarification_required=False,
        rationale=("location_resolution_ready",),
        created_at=NOW,
    )


ORIGIN = location("Casa", -34.60)
DESTINATION = location("Trabajo", -34.58)


def intent(status=RouteIntentStatus.READY, *, owner="Carlos", route_required=True):
    request = RouteIntentRequest(owner=owner, origin=ORIGIN, destination=DESTINATION)
    ready = status is RouteIntentStatus.READY
    action = {
        RouteIntentStatus.READY: RouteIntentAction.MODEL,
        RouteIntentStatus.INCOMPLETE: RouteIntentAction.CLARIFY,
        RouteIntentStatus.REVIEW_REQUIRED: RouteIntentAction.CONFIRM,
        RouteIntentStatus.BLOCKED: RouteIntentAction.WITHHOLD,
        RouteIntentStatus.NOT_APPLICABLE: RouteIntentAction.NONE,
    }[status]
    return RouteIntent(
        request=request,
        status=status,
        action=action,
        origin_label="Casa" if ready else None,
        destination_label="Trabajo" if ready else None,
        waypoint_labels=(),
        accepted_constraints=(),
        rejected_constraint_count=0,
        route_computation_required=route_required if ready else False,
        clarification_required=status is RouteIntentStatus.INCOMPLETE,
        confirmation_required=status is RouteIntentStatus.REVIEW_REQUIRED,
        rationale=(f"route_{status.value}",),
        created_at=NOW,
    )


def request(**changes):
    values = dict(
        owner="Carlos",
        route_intent=intent(),
        explicit_user_authorization=True,
        routing_provider_available=True,
    )
    values.update(changes)
    return NavigationCoordinationRequest(**values)


def coordinate(*, policy=None, **changes):
    return NavigationCoordinationEngine(policy=policy).coordinate(
        request(**changes), now=NOW
    )


def test_ready_for_routing():
    result = coordinate()
    assert result.status is NavigationCoordinationStatus.READY_FOR_ROUTING
    assert result.action is NavigationCoordinationAction.PREPARE_ROUTE_REQUEST
    assert result.routing_request_allowed
    assert result.route_intent_id == result.request.route_intent.intent_id


def test_never_authorizes_navigation_execution():
    result = coordinate()
    assert not result.navigation_start_allowed
    assert not result.live_guidance_allowed


def test_coordination_not_requested():
    result = coordinate(coordination_requested=False)
    assert result.status is NavigationCoordinationStatus.NOT_APPLICABLE


def test_owner_mismatch_blocked():
    result = coordinate(owner="Other")
    assert result.status is NavigationCoordinationStatus.BLOCKED


def test_owner_match_case_insensitive():
    result = coordinate(owner="carlos")
    assert result.status is NavigationCoordinationStatus.READY_FOR_ROUTING


@pytest.mark.parametrize(
    "status, expected",
    [
        (RouteIntentStatus.INCOMPLETE, NavigationCoordinationStatus.AWAITING_INPUT),
        (
            RouteIntentStatus.REVIEW_REQUIRED,
            NavigationCoordinationStatus.REVIEW_REQUIRED,
        ),
        (RouteIntentStatus.BLOCKED, NavigationCoordinationStatus.BLOCKED),
        (RouteIntentStatus.NOT_APPLICABLE, NavigationCoordinationStatus.NOT_APPLICABLE),
    ],
)
def test_upstream_status_propagation(status, expected):
    assert coordinate(route_intent=intent(status)).status is expected


def test_explicit_authorization_required_by_default():
    result = coordinate(explicit_user_authorization=False)
    assert result.status is NavigationCoordinationStatus.REVIEW_REQUIRED
    assert result.user_authorization_required


def test_authorization_requirement_configurable():
    policy = NavigationCoordinationPolicy(require_explicit_user_authorization=False)
    result = coordinate(policy=policy, explicit_user_authorization=False)
    assert result.status is NavigationCoordinationStatus.READY_FOR_ROUTING


def test_provider_required_by_default():
    result = coordinate(routing_provider_available=False)
    assert result.status is NavigationCoordinationStatus.AWAITING_INPUT
    assert result.provider_required


def test_provider_requirement_configurable():
    policy = NavigationCoordinationPolicy(require_routing_provider=False)
    result = coordinate(policy=policy, routing_provider_available=False)
    assert result.status is NavigationCoordinationStatus.READY_FOR_ROUTING


def test_surface_not_required_by_default():
    result = coordinate(navigation_surface_available=False)
    assert result.status is NavigationCoordinationStatus.READY_FOR_ROUTING


def test_surface_requirement_configurable():
    policy = NavigationCoordinationPolicy(require_navigation_surface=True)
    result = coordinate(policy=policy, navigation_surface_available=False)
    assert result.surface_required
    assert result.status is NavigationCoordinationStatus.AWAITING_INPUT


def test_background_preparation_allowed_when_requested():
    result = coordinate(background_preparation_requested=True)
    assert result.background_preparation_allowed


def test_background_preparation_can_be_disabled():
    policy = NavigationCoordinationPolicy(allow_background_preparation=False)
    result = coordinate(policy=policy, background_preparation_requested=True)
    assert not result.background_preparation_allowed


def test_repository_persists_decision():
    repository = InMemoryNavigationCoordinationRepository()
    engine = NavigationCoordinationEngine(repository=repository)
    result = engine.coordinate(request(), now=NOW)
    assert repository.get(result.decision_id) == result
    assert repository.list_all() == (result,)


def test_duplicate_decision_rejected():
    repository = InMemoryNavigationCoordinationRepository()
    engine = NavigationCoordinationEngine(repository=repository)
    engine.coordinate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        engine.coordinate(request(), now=NOW)


def test_request_is_immutable():
    with pytest.raises(FrozenInstanceError):
        request().owner = "Other"


def test_decision_is_immutable():
    with pytest.raises(FrozenInstanceError):
        coordinate().status = NavigationCoordinationStatus.BLOCKED


def test_deterministic_decision_id():
    first = NavigationCoordinationEngine().coordinate(request(), now=NOW)
    second = NavigationCoordinationEngine().coordinate(request(), now=NOW)
    assert first.decision_id == second.decision_id


def test_time_changes_decision_id():
    first = NavigationCoordinationEngine().coordinate(request(), now=NOW)
    later = datetime(2026, 7, 11, 18, 1, tzinfo=timezone.utc)
    second = NavigationCoordinationEngine().coordinate(request(), now=later)
    assert first.decision_id != second.decision_id


def test_naive_timestamp_rejected():
    result = coordinate()
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(result, created_at=datetime(2026, 7, 11, 18, 0))


def test_inconsistent_decision_id_rejected():
    with pytest.raises(ValueError, match="inconsistent"):
        replace(coordinate(), decision_id="wrong")


def test_blank_owner_rejected():
    with pytest.raises(ValueError, match="must not be blank"):
        request(owner="  ")


@pytest.mark.parametrize("status", list(NavigationCoordinationStatus))
def test_status_enum_values_are_stable(status):
    assert NavigationCoordinationStatus(status.value) is status


@pytest.mark.parametrize("action", list(NavigationCoordinationAction))
def test_action_enum_values_are_stable(action):
    assert NavigationCoordinationAction(action.value) is action


def test_inactive_decisions_do_not_expose_route_intent_id():
    result = coordinate(explicit_user_authorization=False)
    assert result.route_intent_id is None
    assert not result.routing_request_allowed


def test_model_has_no_route_geometry_or_instructions():
    fields = NavigationCoordinationDecision.__dataclass_fields__
    forbidden = {"distance", "duration", "geometry", "steps", "instructions", "traffic"}
    assert forbidden.isdisjoint(fields)


def test_model_cannot_authorize_start():
    result = coordinate()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, navigation_start_allowed=True)


def test_model_cannot_authorize_live_guidance():
    result = coordinate()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, live_guidance_allowed=True)


def test_rationale_required():
    with pytest.raises(ValueError, match="must not be empty"):
        replace(coordinate(), rationale=())
