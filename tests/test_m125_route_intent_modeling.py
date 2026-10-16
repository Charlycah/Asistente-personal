from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

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
from core.places_knowledge import (
    PlaceFact,
    PlaceFactKind,
    PlaceKnowledgeAction,
    PlaceKnowledgeProfile,
    PlaceKnowledgeStatus,
    PlacesKnowledgeRequest,
)
from core.route_intent_modeling import (
    InMemoryRouteIntentRepository,
    RouteConstraint,
    RouteConstraintKind,
    RouteIntentAction,
    RouteIntentModelingEngine,
    RouteIntentPolicy,
    RouteIntentRequest,
    RouteIntentStatus,
    RoutePriority,
    RouteTimeWindow,
    TravelMode,
)

NOW = datetime(2026, 7, 11, 15, 0, tzinfo=timezone.utc)


def resolved(
    label,
    lat,
    lon,
    *,
    owner="Carlos",
    confidence=0.95,
    status=LocationResolutionStatus.RESOLVED,
):
    point = GeoPointSignal(lat, lon, confidence, NOW, "declared")
    map_request = MapsFoundationRequest(
        owner=owner,
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
    candidate = LocationCandidate(label, LocationReferenceKind.PLACE, confidence, point)
    request = LocationResolutionRequest(
        owner=owner,
        map_context=context,
        reference=label,
        reference_kind=LocationReferenceKind.PLACE,
        candidates=(candidate,),
    )
    ready = status is LocationResolutionStatus.RESOLVED
    return ResolvedLocation(
        request=request,
        status=status,
        action=(
            LocationResolutionAction.ACCEPT
            if ready
            else LocationResolutionAction.CONFIRM
        ),
        selected_candidate=candidate if ready else None,
        resolved_label=label if ready else None,
        resolved_point=point if ready else None,
        confidence=confidence if ready else 0.0,
        provider_required=not ready,
        clarification_required=status is LocationResolutionStatus.AMBIGUOUS,
        rationale=(
            ("location_resolution_ready",) if ready else ("location_resolution_review",)
        ),
        created_at=NOW,
    )


ORIGIN = resolved("Casa", -34.60, -58.38)
DESTINATION = resolved("Trabajo", -34.58, -58.42)
WAYPOINT = resolved("Café", -34.59, -58.40)


def knowledge(location, *, owner="Carlos", status=PlaceKnowledgeStatus.READY):
    fact = PlaceFact(PlaceFactKind.CATEGORY, "category", "place", 0.9)
    request = PlacesKnowledgeRequest(
        owner=owner, resolved_location=location, facts=(fact,)
    )
    ready = status is PlaceKnowledgeStatus.READY
    return PlaceKnowledgeProfile(
        request=request,
        status=status,
        action=(
            PlaceKnowledgeAction.ESTABLISH if ready else PlaceKnowledgeAction.CONFIRM
        ),
        place_label=location.resolved_label if ready else None,
        accepted_facts=(fact,) if ready else (),
        rejected_fact_count=0,
        provider_required=not ready,
        confirmation_required=not ready,
        rationale=("place_knowledge_ready",) if ready else ("place_knowledge_review",),
        created_at=NOW,
    )


def constraint(
    kind=RouteConstraintKind.AVOID,
    name="road",
    value="tolls",
    confidence=0.9,
):
    return RouteConstraint(kind, name, value, confidence)


def request(**changes):
    values = dict(owner="Carlos", origin=ORIGIN, destination=DESTINATION)
    values.update(changes)
    return RouteIntentRequest(**values)


def model(*, policy=None, now=NOW, **changes):
    return RouteIntentModelingEngine(policy=policy).model(request(**changes), now=now)


def test_ready_route_intent():
    result = model()
    assert result.status is RouteIntentStatus.READY
    assert result.action is RouteIntentAction.MODEL
    assert result.origin_label == "Casa"
    assert result.destination_label == "Trabajo"
    assert result.route_computation_required


@pytest.mark.parametrize("mode", list(TravelMode))
def test_all_travel_modes_supported(mode):
    assert model(travel_mode=mode).request.travel_mode is mode


@pytest.mark.parametrize("priority", list(RoutePriority))
def test_all_route_priorities_supported(priority):
    assert model(priority=priority).request.priority is priority


@pytest.mark.parametrize("kind", list(RouteConstraintKind))
def test_all_constraint_kinds_supported(kind):
    result = model(constraints=(constraint(kind=kind),))
    assert result.accepted_constraints[0].kind is kind


def test_not_declared_is_not_applicable():
    assert model(intent_declared=False).status is RouteIntentStatus.NOT_APPLICABLE


@pytest.mark.parametrize("missing", ["origin", "destination"])
def test_missing_endpoint_is_incomplete(missing):
    result = model(**{missing: None})
    assert result.status is RouteIntentStatus.INCOMPLETE
    assert result.clarification_required


def test_owner_mismatch_is_blocked():
    result = model(destination=resolved("Trabajo", -34.58, -58.42, owner="Other"))
    assert result.status is RouteIntentStatus.BLOCKED


def test_owner_match_is_case_insensitive():
    assert model(owner="carlos").status is RouteIntentStatus.READY


@pytest.mark.parametrize(
    "status",
    [
        LocationResolutionStatus.AMBIGUOUS,
        LocationResolutionStatus.REVIEW_REQUIRED,
        LocationResolutionStatus.BLOCKED,
        LocationResolutionStatus.NOT_APPLICABLE,
    ],
)
def test_unresolved_location_is_incomplete(status):
    result = model(destination=resolved("Trabajo", -34.58, -58.42, status=status))
    assert result.status is RouteIntentStatus.INCOMPLETE


def test_low_confidence_location_requires_confirmation():
    result = model(destination=resolved("Trabajo", -34.58, -58.42, confidence=0.5))
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_location_confidence_policy_is_configurable():
    result = model(
        destination=resolved("Trabajo", -34.58, -58.42, confidence=0.5),
        policy=RouteIntentPolicy(minimum_location_confidence=0.4),
    )
    assert result.status is RouteIntentStatus.READY


def test_waypoint_labels_are_preserved():
    result = model(waypoints=(WAYPOINT,))
    assert result.waypoint_labels == ("Café",)


def test_waypoint_limit_requires_confirmation():
    result = model(waypoints=(WAYPOINT,), policy=RouteIntentPolicy(maximum_waypoints=0))
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_constraint_limit_requires_confirmation():
    result = model(
        constraints=(constraint(), constraint(name="bridge", value="none")),
        policy=RouteIntentPolicy(maximum_constraints=1),
    )
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_same_resolution_requires_confirmation():
    result = model(destination=ORIGIN)
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_same_coordinates_require_confirmation():
    result = model(destination=resolved("Other", -34.60, -58.38))
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_same_location_can_be_allowed_by_policy():
    result = model(
        destination=ORIGIN,
        policy=RouteIntentPolicy(require_distinct_origin_destination=False),
    )
    assert result.status is RouteIntentStatus.READY


def test_mixed_mode_can_be_disabled():
    result = model(
        travel_mode=TravelMode.MIXED,
        policy=RouteIntentPolicy(allow_mixed_mode=False),
    )
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_matching_place_knowledge_is_accepted():
    result = model(
        origin_knowledge=knowledge(ORIGIN),
        destination_knowledge=knowledge(DESTINATION),
    )
    assert result.status is RouteIntentStatus.READY


def test_origin_knowledge_lineage_mismatch_is_blocked():
    assert (
        model(origin_knowledge=knowledge(DESTINATION)).status
        is RouteIntentStatus.BLOCKED
    )


def test_destination_knowledge_lineage_mismatch_is_blocked():
    assert (
        model(destination_knowledge=knowledge(ORIGIN)).status
        is RouteIntentStatus.BLOCKED
    )


def test_non_ready_knowledge_is_blocked():
    profile = knowledge(DESTINATION, status=PlaceKnowledgeStatus.REVIEW_REQUIRED)
    assert model(destination_knowledge=profile).status is RouteIntentStatus.BLOCKED


def test_low_confidence_constraint_is_rejected_but_intent_ready():
    result = model(constraints=(constraint(confidence=0.2),))
    assert result.status is RouteIntentStatus.READY
    assert result.accepted_constraints == ()
    assert result.rejected_constraint_count == 1


def test_constraint_confidence_policy_is_configurable():
    result = model(
        constraints=(constraint(confidence=0.2),),
        policy=RouteIntentPolicy(minimum_constraint_confidence=0.1),
    )
    assert len(result.accepted_constraints) == 1


def test_duplicate_constraint_keeps_highest_confidence():
    result = model(
        constraints=(constraint(confidence=0.8), constraint(confidence=0.95))
    )
    assert len(result.accepted_constraints) == 1
    assert result.accepted_constraints[0].confidence == 0.95
    assert result.rejected_constraint_count == 1


def test_conflicting_constraints_require_confirmation():
    result = model(
        constraints=(constraint(value="tolls"), constraint(value="highways"))
    )
    assert result.status is RouteIntentStatus.REVIEW_REQUIRED


def test_constraint_order_is_deterministic():
    a = constraint(name="z", value="one")
    b = constraint(name="a", value="two")
    result = model(constraints=(a, b))
    assert [item.name for item in result.accepted_constraints] == ["a", "z"]


def test_request_normalizes_owner_and_purpose():
    item = request(owner=" Carlos ", purpose="  Work Trip ")
    assert item.owner == "Carlos"
    assert item.purpose == "work trip"


def test_constraint_normalizes_name_and_value():
    item = RouteConstraint("avoid", "  Toll   Road ", "  Highway  1 ", 0.8)
    assert item.name == "toll road"
    assert item.value == "Highway 1"


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_constraint_confidence_validated(confidence):
    with pytest.raises(ValueError):
        constraint(confidence=confidence)


@pytest.mark.parametrize("field", ["name", "value"])
def test_constraint_blank_fields_rejected(field):
    values = {field: "   "}
    with pytest.raises(ValueError):
        constraint(**values)


def test_time_window_accepts_aware_values():
    window = RouteTimeWindow(NOW, NOW + timedelta(hours=2))
    assert request(time_window=window).time_window == window


def test_time_window_rejects_naive_values():
    with pytest.raises(ValueError):
        RouteTimeWindow(datetime(2026, 7, 11, 15), None)


def test_time_window_rejects_inverted_bounds():
    with pytest.raises(ValueError):
        RouteTimeWindow(NOW, NOW - timedelta(minutes=1))


@pytest.mark.parametrize(
    "policy",
    [
        RouteIntentPolicy(minimum_location_confidence=0),
        RouteIntentPolicy(minimum_constraint_confidence=1),
        RouteIntentPolicy(maximum_waypoints=0),
        RouteIntentPolicy(maximum_constraints=1),
    ],
)
def test_valid_policy_edges(policy):
    assert policy is not None


def test_invalid_policy_values():
    with pytest.raises(ValueError):
        RouteIntentPolicy(minimum_location_confidence=1.1)
    with pytest.raises(ValueError):
        RouteIntentPolicy(minimum_constraint_confidence=-0.1)
    with pytest.raises(ValueError):
        RouteIntentPolicy(maximum_waypoints=-1)
    with pytest.raises(ValueError):
        RouteIntentPolicy(maximum_constraints=0)


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_intent_is_immutable():
    item = model()
    with pytest.raises(FrozenInstanceError):
        item.status = RouteIntentStatus.BLOCKED


def test_deterministic_identifier_for_same_input_and_time():
    assert model().intent_id == model().intent_id


def test_identifier_changes_with_mode():
    assert model().intent_id != model(travel_mode=TravelMode.WALKING).intent_id


def test_identifier_consistency_is_enforced():
    item = model()
    with pytest.raises(ValueError):
        replace(item, intent_id="wrong")


def test_repository_add_get_and_list():
    repository = InMemoryRouteIntentRepository()
    engine = RouteIntentModelingEngine(repository=repository)
    item = engine.model(request(), now=NOW)
    assert repository.get(item.intent_id) == item
    assert repository.list_all() == (item,)


def test_repository_rejects_duplicate_identifier():
    repository = InMemoryRouteIntentRepository()
    item = RouteIntentModelingEngine(repository=repository).model(request(), now=NOW)
    with pytest.raises(ValueError):
        repository.add(item)


def test_naive_evaluation_time_rejected():
    with pytest.raises(ValueError):
        model(now=datetime(2026, 7, 11, 15))


def test_non_ready_intent_exposes_no_route_data():
    item = model(destination=None)
    assert item.origin_label is None
    assert item.destination_label is None
    assert item.waypoint_labels == ()
    assert item.accepted_constraints == ()
    assert not item.route_computation_required


def test_engine_does_not_calculate_distance_or_duration():
    item = model()
    assert not hasattr(item, "distance")
    assert not hasattr(item, "duration")
    assert not hasattr(item, "route")


def test_route_computation_is_only_declared_as_future_requirement():
    item = model()
    assert item.route_computation_required is True
    assert item.rationale == ("route_intent_ready_for_future_computation",)
