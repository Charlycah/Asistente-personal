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
from core.map_context_integration import (
    InMemoryMapContextIntegrationRepository,
    IntegratedMapContext,
    MapContextIntegrationEngine,
    MapContextIntegrationPolicy,
    MapContextIntegrationRequest,
    MapIntegrationAction,
    MapIntegrationStatus,
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
    NavigationCoordinationAction,
    NavigationCoordinationDecision,
    NavigationCoordinationRequest,
    NavigationCoordinationStatus,
)
from core.places_knowledge import (
    PlaceFact,
    PlaceFactKind,
    PlaceKnowledgeAction,
    PlaceKnowledgeProfile,
    PlaceKnowledgeStatus,
    PlacesKnowledgeRequest,
)
from core.route_intent_modeling import (
    RouteIntent,
    RouteIntentAction,
    RouteIntentRequest,
    RouteIntentStatus,
)

NOW = datetime(2026, 7, 11, 21, 0, tzinfo=timezone.utc)


def map_context(*, owner="Carlos", status=MapFoundationStatus.READY):
    point = GeoPointSignal(-34.60, -58.40, 0.95, NOW, "declared")
    request = MapsFoundationRequest(
        owner=owner,
        purpose=MapPurpose.ROUTE_PREPARATION,
        requested_precision=MapPrecision.PRECISE,
        requested_scope=MapScope.LOCAL,
        location=point,
        explicit_user_consent=True,
    )
    ready = status is MapFoundationStatus.READY
    return MapContext(
        request=request,
        status=status,
        action=MapFoundationAction.ESTABLISH if ready else MapFoundationAction.WITHHOLD,
        effective_precision=MapPrecision.PRECISE if ready else MapPrecision.APPROXIMATE,
        effective_scope=MapScope.LOCAL,
        location_available=ready,
        provider_required=ready,
        route_computation_allowed=False,
        rationale=(f"map_{status.value}",),
        created_at=NOW,
    )


def location(
    label,
    lat,
    *,
    context=None,
    owner="Carlos",
    status=LocationResolutionStatus.RESOLVED,
):
    context = context or map_context(owner=owner)
    point = GeoPointSignal(lat, -58.4, 0.95, NOW, "declared")
    candidate = LocationCandidate(label, LocationReferenceKind.PLACE, 0.95, point)
    request = LocationResolutionRequest(
        owner=owner,
        map_context=context,
        reference=label,
        reference_kind=LocationReferenceKind.PLACE,
        candidates=(candidate,),
    )
    resolved = status is LocationResolutionStatus.RESOLVED
    return ResolvedLocation(
        request=request,
        status=status,
        action=LocationResolutionAction.ACCEPT
        if resolved
        else LocationResolutionAction.CLARIFY,
        selected_candidate=candidate if resolved else None,
        resolved_label=label if resolved else None,
        resolved_point=point if resolved else None,
        confidence=0.95 if resolved else 0.0,
        provider_required=False,
        clarification_required=status is LocationResolutionStatus.AMBIGUOUS,
        rationale=(f"location_{status.value}",),
        created_at=NOW,
    )


def profile(loc, *, owner="Carlos", status=PlaceKnowledgeStatus.READY):
    fact = PlaceFact(PlaceFactKind.CATEGORY, "kind", "home", 0.95, "declared")
    request = PlacesKnowledgeRequest(owner=owner, resolved_location=loc, facts=(fact,))
    ready = status is PlaceKnowledgeStatus.READY
    return PlaceKnowledgeProfile(
        request=request,
        status=status,
        action=PlaceKnowledgeAction.ESTABLISH
        if ready
        else PlaceKnowledgeAction.CONFIRM,
        place_label=loc.resolved_label if ready else None,
        accepted_facts=(fact,) if ready else (),
        rejected_fact_count=0,
        provider_required=False,
        confirmation_required=status is PlaceKnowledgeStatus.REVIEW_REQUIRED,
        rationale=(f"profile_{status.value}",),
        created_at=NOW,
    )


def route(origin, destination, *, owner="Carlos", status=RouteIntentStatus.READY):
    request = RouteIntentRequest(owner=owner, origin=origin, destination=destination)
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
        origin_label=origin.resolved_label if ready else None,
        destination_label=destination.resolved_label if ready else None,
        waypoint_labels=(),
        accepted_constraints=(),
        rejected_constraint_count=0,
        route_computation_required=ready,
        clarification_required=status is RouteIntentStatus.INCOMPLETE,
        confirmation_required=status is RouteIntentStatus.REVIEW_REQUIRED,
        rationale=(f"route_{status.value}",),
        created_at=NOW,
    )


def navigation(
    intent, *, owner="Carlos", status=NavigationCoordinationStatus.READY_FOR_ROUTING
):
    request = NavigationCoordinationRequest(
        owner=owner,
        route_intent=intent,
        explicit_user_authorization=True,
        routing_provider_available=True,
    )
    ready = status is NavigationCoordinationStatus.READY_FOR_ROUTING
    action = (
        NavigationCoordinationAction.PREPARE_ROUTE_REQUEST
        if ready
        else NavigationCoordinationAction.CONFIRM
    )
    return NavigationCoordinationDecision(
        request=request,
        status=status,
        action=action,
        routing_request_allowed=ready,
        provider_required=False,
        surface_required=False,
        user_authorization_required=False,
        background_preparation_allowed=False,
        navigation_start_allowed=False,
        live_guidance_allowed=False,
        route_intent_id=intent.intent_id if ready else None,
        rationale=(f"navigation_{status.value}",),
        created_at=NOW,
    )


CONTEXT = map_context()
ORIGIN = location("Casa", -34.60, context=CONTEXT)
DESTINATION = location("Trabajo", -34.58, context=CONTEXT)
PROFILE = profile(ORIGIN)
INTENT = route(ORIGIN, DESTINATION)
NAVIGATION = navigation(INTENT)


def request(**changes):
    values = dict(
        owner="Carlos",
        map_context=CONTEXT,
        resolved_locations=(ORIGIN, DESTINATION),
        place_profiles=(PROFILE,),
        route_intent=INTENT,
        navigation_decision=NAVIGATION,
    )
    values.update(changes)
    return MapContextIntegrationRequest(**values)


def integrate(*, policy=None, **changes):
    return MapContextIntegrationEngine(policy=policy).integrate(
        request(**changes), now=NOW
    )


def test_ready_integration():
    result = integrate()
    assert result.status is MapIntegrationStatus.READY
    assert result.action is MapIntegrationAction.INTEGRATE
    assert result.routing_preparation_allowed


def test_integrates_all_lineage_ids():
    result = integrate()
    assert result.map_context_id == CONTEXT.context_id
    assert set(result.location_ids) == {ORIGIN.resolution_id, DESTINATION.resolution_id}
    assert result.place_profile_ids == (PROFILE.profile_id,)
    assert result.route_intent_id == INTENT.intent_id
    assert result.navigation_decision_id == NAVIGATION.decision_id


def test_capability_summary():
    result = integrate()
    assert result.spatial_context_available
    assert result.place_knowledge_available
    assert result.route_intent_available


def test_never_authorizes_navigation_execution():
    result = integrate()
    assert not result.navigation_start_allowed
    assert not result.live_guidance_allowed


def test_not_requested_is_not_applicable():
    assert (
        integrate(integration_requested=False).status
        is MapIntegrationStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_blocks():
    assert integrate(owner="Other").status is MapIntegrationStatus.BLOCKED


def test_owner_is_case_insensitive():
    assert integrate(owner="carlos").status is MapIntegrationStatus.READY


def test_non_ready_map_context_blocks_by_default():
    blocked = map_context(status=MapFoundationStatus.BLOCKED)
    assert (
        integrate(
            map_context=blocked,
            resolved_locations=(),
            place_profiles=(),
            route_intent=None,
            navigation_decision=None,
        ).status
        is MapIntegrationStatus.BLOCKED
    )


def test_non_ready_map_context_can_be_retained_by_policy():
    blocked = map_context(status=MapFoundationStatus.BLOCKED)
    policy = MapContextIntegrationPolicy(require_ready_map_context=False)
    result = integrate(
        policy=policy,
        map_context=blocked,
        resolved_locations=(),
        place_profiles=(),
        route_intent=None,
        navigation_decision=None,
    )
    assert result.status is MapIntegrationStatus.READY


def test_location_lineage_mismatch_blocks():
    other = location("Other", -34.5, context=map_context())
    assert (
        integrate(resolved_locations=(ORIGIN, other)).status
        is MapIntegrationStatus.BLOCKED
    )


def test_place_profile_must_reference_included_location():
    other = location("Other", -34.5, context=CONTEXT)
    assert (
        integrate(place_profiles=(profile(other),)).status
        is MapIntegrationStatus.BLOCKED
    )


def test_place_profile_owner_mismatch_blocks():
    other_context = map_context(owner="Other")
    other = location("Other", -34.5, context=other_context, owner="Other")
    assert (
        integrate(place_profiles=(profile(other, owner="Other"),)).status
        is MapIntegrationStatus.BLOCKED
    )


def test_route_owner_mismatch_blocks():
    other = route(ORIGIN, DESTINATION, owner="Other")
    assert (
        integrate(route_intent=other, navigation_decision=None).status
        is MapIntegrationStatus.BLOCKED
    )


def test_route_location_lineage_mismatch_blocks():
    other = location("Other", -34.5, context=CONTEXT)
    mismatched = route(ORIGIN, other)
    assert (
        integrate(route_intent=mismatched, navigation_decision=None).status
        is MapIntegrationStatus.BLOCKED
    )


def test_navigation_must_match_route_intent():
    other = route(DESTINATION, ORIGIN)
    assert (
        integrate(navigation_decision=navigation(other)).status
        is MapIntegrationStatus.BLOCKED
    )


def test_missing_navigation_is_partial_by_default():
    result = integrate(navigation_decision=None)
    assert result.status is MapIntegrationStatus.PARTIAL
    assert not result.routing_preparation_allowed


def test_navigation_lineage_requirement_can_be_disabled():
    policy = MapContextIntegrationPolicy(require_navigation_lineage=False)
    result = integrate(policy=policy, navigation_decision=None)
    assert result.status is MapIntegrationStatus.READY


def test_partial_can_be_blocked_by_policy():
    policy = MapContextIntegrationPolicy(allow_partial_context=False)
    assert (
        integrate(policy=policy, navigation_decision=None).status
        is MapIntegrationStatus.BLOCKED
    )


@pytest.mark.parametrize(
    "status",
    [LocationResolutionStatus.BLOCKED, LocationResolutionStatus.NOT_APPLICABLE],
)
def test_non_resolved_locations_make_partial(status):
    item = location("Unknown", -34.4, context=CONTEXT, status=status)
    assert (
        integrate(
            resolved_locations=(item,),
            place_profiles=(),
            route_intent=None,
            navigation_decision=None,
        ).status
        is MapIntegrationStatus.PARTIAL
    )


def test_ambiguous_location_requires_review():
    item = location(
        "Unknown", -34.4, context=CONTEXT, status=LocationResolutionStatus.AMBIGUOUS
    )
    result = integrate(
        resolved_locations=(item,),
        place_profiles=(),
        route_intent=None,
        navigation_decision=None,
    )
    assert result.status is MapIntegrationStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_review_place_profile_requires_review():
    review = profile(ORIGIN, status=PlaceKnowledgeStatus.REVIEW_REQUIRED)
    result = integrate(place_profiles=(review,))
    assert result.status is MapIntegrationStatus.REVIEW_REQUIRED


def test_review_route_requires_review():
    review = route(ORIGIN, DESTINATION, status=RouteIntentStatus.REVIEW_REQUIRED)
    result = integrate(route_intent=review, navigation_decision=None)
    assert result.status is MapIntegrationStatus.REVIEW_REQUIRED


def test_review_navigation_requires_review():
    review = navigation(INTENT, status=NavigationCoordinationStatus.REVIEW_REQUIRED)
    result = integrate(navigation_decision=review)
    assert result.status is MapIntegrationStatus.REVIEW_REQUIRED


@pytest.mark.parametrize(
    "status",
    [
        RouteIntentStatus.INCOMPLETE,
        RouteIntentStatus.BLOCKED,
        RouteIntentStatus.NOT_APPLICABLE,
    ],
)
def test_non_ready_route_is_partial(status):
    item = route(ORIGIN, DESTINATION, status=status)
    result = integrate(route_intent=item, navigation_decision=None)
    assert result.status is MapIntegrationStatus.PARTIAL


@pytest.mark.parametrize(
    "status",
    [
        NavigationCoordinationStatus.AWAITING_INPUT,
        NavigationCoordinationStatus.BLOCKED,
        NavigationCoordinationStatus.NOT_APPLICABLE,
    ],
)
def test_non_ready_navigation_is_partial(status):
    item = navigation(INTENT, status=status)
    assert integrate(navigation_decision=item).status is MapIntegrationStatus.PARTIAL


def test_empty_maps_only_context_is_ready():
    result = integrate(
        resolved_locations=(),
        place_profiles=(),
        route_intent=None,
        navigation_decision=None,
    )
    assert result.status is MapIntegrationStatus.READY
    assert result.spatial_context_available


def test_location_limit_blocks():
    policy = MapContextIntegrationPolicy(maximum_locations=1)
    assert integrate(policy=policy).status is MapIntegrationStatus.BLOCKED


def test_profile_limit_blocks():
    policy = MapContextIntegrationPolicy(maximum_place_profiles=1)
    assert (
        integrate(policy=policy, place_profiles=(PROFILE, PROFILE)).status
        is MapIntegrationStatus.BLOCKED
    )


def test_policy_limits_validate():
    with pytest.raises(ValueError):
        MapContextIntegrationPolicy(maximum_locations=0)
    with pytest.raises(ValueError):
        MapContextIntegrationPolicy(maximum_place_profiles=0)


def test_request_owner_is_trimmed():
    assert request(owner="  Carlos ").owner == "Carlos"


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner=" ")


def test_request_collections_are_tuples():
    item = MapContextIntegrationRequest(
        owner="Carlos",
        map_context=CONTEXT,
        resolved_locations=[ORIGIN],
        place_profiles=[PROFILE],
    )
    assert isinstance(item.resolved_locations, tuple)
    assert isinstance(item.place_profiles, tuple)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        integrate().status = MapIntegrationStatus.BLOCKED


def test_equal_input_and_time_are_deterministic():
    first = MapContextIntegrationEngine().integrate(request(), now=NOW)
    second = MapContextIntegrationEngine().integrate(request(), now=NOW)
    assert first == second
    assert first.integration_id == second.integration_id


def test_different_time_changes_identifier():
    first = MapContextIntegrationEngine().integrate(request(), now=NOW)
    second = MapContextIntegrationEngine().integrate(
        request(), now=NOW.replace(minute=1)
    )
    assert first.integration_id != second.integration_id


def test_repository_persists():
    repository = InMemoryMapContextIntegrationRepository()
    result = MapContextIntegrationEngine(repository=repository).integrate(
        request(), now=NOW
    )
    assert repository.get(result.integration_id) == result
    assert repository.list_all() == (result,)


def test_duplicate_rejected():
    repository = InMemoryMapContextIntegrationRepository()
    engine = MapContextIntegrationEngine(repository=repository)
    engine.integrate(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        engine.integrate(request(), now=NOW)


def test_invalid_identifier_rejected():
    with pytest.raises(ValueError, match="inconsistent"):
        replace(integrate(), integration_id="bad")


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(integrate(), created_at=datetime(2026, 7, 11))


def test_empty_rationale_rejected():
    with pytest.raises(ValueError, match="rationale"):
        replace(integrate(), rationale=())


def test_execution_authorization_rejected():
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(integrate(), navigation_start_allowed=True)
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(integrate(), live_guidance_allowed=True)


def test_inactive_context_cannot_expose_lineage():
    result = integrate(integration_requested=False)
    with pytest.raises(ValueError, match="inactive integration"):
        replace(result, map_context_id=CONTEXT.context_id)


def test_review_requires_confirmation():
    item = location(
        "Unknown", -34.4, context=CONTEXT, status=LocationResolutionStatus.AMBIGUOUS
    )
    result = integrate(
        resolved_locations=(item,),
        place_profiles=(),
        route_intent=None,
        navigation_decision=None,
    )
    with pytest.raises(ValueError, match="require confirmation"):
        replace(result, confirmation_required=False)


def test_location_ids_are_deduplicated_and_sorted():
    result = integrate(
        resolved_locations=(DESTINATION, ORIGIN, ORIGIN),
        place_profiles=(),
        route_intent=None,
        navigation_decision=None,
    )
    assert result.location_ids == tuple(
        sorted({ORIGIN.resolution_id, DESTINATION.resolution_id})
    )


def test_profile_ids_are_deduplicated():
    result = integrate(place_profiles=(PROFILE, PROFILE))
    assert result.place_profile_ids == (PROFILE.profile_id,)


def test_no_route_distance_duration_or_guidance_fields():
    fields = IntegratedMapContext.__dataclass_fields__
    forbidden = {"distance", "duration", "geometry", "steps", "instructions", "route"}
    assert not forbidden.intersection(fields)
