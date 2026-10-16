from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.location_resolution import (
    InMemoryLocationResolutionRepository,
    LocationCandidate,
    LocationReferenceKind,
    LocationResolutionAction,
    LocationResolutionEngine,
    LocationResolutionPolicy,
    LocationResolutionRequest,
    LocationResolutionStatus,
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

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)
POINT = GeoPointSignal(-34.6037, -58.3816, 0.95, NOW, "declared")


def map_context(**changes):
    request_values = {
        "owner": "Carlos",
        "purpose": MapPurpose.ORIENTATION,
        "requested_precision": MapPrecision.NEIGHBORHOOD,
        "requested_scope": MapScope.LOCAL,
        "location": POINT,
        "maps_context_declared": True,
        "explicit_user_consent": True,
    }
    request_values.update(changes.pop("request_changes", {}))
    values = {
        "request": MapsFoundationRequest(**request_values),
        "status": MapFoundationStatus.READY,
        "action": MapFoundationAction.ESTABLISH,
        "effective_precision": MapPrecision.NEIGHBORHOOD,
        "effective_scope": MapScope.LOCAL,
        "location_available": True,
        "provider_required": True,
        "route_computation_allowed": False,
        "rationale": ("maps_context_ready",),
        "created_at": NOW,
    }
    values.update(changes)
    return MapContext(**values)


def candidate(
    label="Casa", kind=LocationReferenceKind.PLACE, confidence=0.9, **changes
):
    values = {
        "label": label,
        "kind": kind,
        "confidence": confidence,
        "point": POINT,
        "source": "declared",
    }
    values.update(changes)
    return LocationCandidate(**values)


def request(**changes):
    values = {
        "owner": "Carlos",
        "map_context": map_context(),
        "reference": "Casa",
        "reference_kind": LocationReferenceKind.PLACE,
        "candidates": (candidate(),),
        "resolution_declared": True,
    }
    values.update(changes)
    return LocationResolutionRequest(**values)


def resolve(*, policy=None, now=NOW, **changes):
    return LocationResolutionEngine(policy=policy).resolve(request(**changes), now=now)


def test_declared_candidate_resolves():
    result = resolve()
    assert result.status is LocationResolutionStatus.RESOLVED
    assert result.action is LocationResolutionAction.ACCEPT
    assert result.resolved_label == "Casa"
    assert result.resolved_point == POINT


def test_current_location_resolves_from_map_context():
    result = resolve(
        reference="my location",
        reference_kind=LocationReferenceKind.CURRENT_LOCATION,
        candidates=(),
    )
    assert result.status is LocationResolutionStatus.RESOLVED
    assert result.resolved_label == "Current location"
    assert result.selected_candidate.point == POINT


@pytest.mark.parametrize("kind", list(LocationReferenceKind))
def test_all_reference_kinds_are_supported(kind):
    if kind is LocationReferenceKind.CURRENT_LOCATION:
        result = resolve(reference="here", reference_kind=kind, candidates=())
    else:
        result = resolve(
            reference="Target",
            reference_kind=kind,
            candidates=(candidate("Target", kind),),
        )
    assert result.request.reference_kind is kind


def test_undeclared_resolution_is_not_applicable():
    result = resolve(resolution_declared=False)
    assert result.status is LocationResolutionStatus.NOT_APPLICABLE
    assert result.action is LocationResolutionAction.NONE


def test_owner_mismatch_is_blocked():
    result = resolve(owner="Other")
    assert result.status is LocationResolutionStatus.BLOCKED


def test_owner_comparison_is_case_insensitive():
    result = resolve(owner="carlos")
    assert result.status is LocationResolutionStatus.RESOLVED


@pytest.mark.parametrize(
    "status",
    [
        MapFoundationStatus.REVIEW_REQUIRED,
        MapFoundationStatus.BLOCKED,
        MapFoundationStatus.NOT_APPLICABLE,
    ],
)
def test_non_ready_map_context_blocks_resolution(status):
    context = map_context(
        status=status,
        action=MapFoundationAction.WITHHOLD,
        location_available=False,
        provider_required=False,
    )
    result = resolve(map_context=context)
    assert result.status is LocationResolutionStatus.BLOCKED


def test_missing_candidates_requests_provider_evidence():
    result = resolve(candidates=())
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED
    assert result.provider_required


def test_kind_mismatch_requests_confirmation():
    result = resolve(candidates=(candidate(kind=LocationReferenceKind.ADDRESS),))
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_exact_label_is_preferred_over_higher_non_exact_label():
    result = resolve(
        candidates=(
            candidate("Casa", confidence=0.8),
            candidate("Casa de Ana", confidence=0.99),
        )
    )
    assert result.resolved_label == "Casa"


def test_highest_confidence_candidate_wins():
    result = resolve(
        reference="destination",
        candidates=(candidate("A", confidence=0.8), candidate("B", confidence=0.95)),
    )
    assert result.resolved_label == "B"


def test_candidate_order_does_not_change_selection():
    first = resolve(
        reference="destination",
        candidates=(candidate("B", confidence=0.95), candidate("A", confidence=0.8)),
    )
    second = resolve(
        reference="destination",
        candidates=(candidate("A", confidence=0.8), candidate("B", confidence=0.95)),
    )
    assert first.resolved_label == second.resolved_label == "B"


def test_close_candidates_are_ambiguous():
    result = resolve(
        reference="destination",
        candidates=(candidate("A", confidence=0.9), candidate("B", confidence=0.85)),
    )
    assert result.status is LocationResolutionStatus.AMBIGUOUS
    assert result.action is LocationResolutionAction.CLARIFY
    assert result.clarification_required


def test_ambiguity_margin_is_configurable():
    result = resolve(
        reference="destination",
        candidates=(candidate("A", confidence=0.9), candidate("B", confidence=0.85)),
        policy=LocationResolutionPolicy(ambiguity_margin=0.01),
    )
    assert result.status is LocationResolutionStatus.RESOLVED


def test_low_confidence_requires_review():
    result = resolve(candidates=(candidate(confidence=0.5),))
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_configurable():
    result = resolve(
        candidates=(candidate(confidence=0.5),),
        policy=LocationResolutionPolicy(minimum_confidence=0.5),
    )
    assert result.status is LocationResolutionStatus.RESOLVED


def test_coordinate_candidate_requires_point():
    result = resolve(
        reference="coordinates",
        reference_kind=LocationReferenceKind.COORDINATES,
        candidates=(
            candidate("coordinates", LocationReferenceKind.COORDINATES, point=None),
        ),
    )
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_coordinate_point_requirement_can_be_relaxed():
    result = resolve(
        reference="coordinates",
        reference_kind=LocationReferenceKind.COORDINATES,
        candidates=(
            candidate("coordinates", LocationReferenceKind.COORDINATES, point=None),
        ),
        policy=LocationResolutionPolicy(require_point_for_coordinates=False),
    )
    assert result.status is LocationResolutionStatus.RESOLVED


def test_external_candidates_can_be_disallowed():
    result = resolve(
        candidates=(candidate(external_id="provider:1"),),
        policy=LocationResolutionPolicy(allow_external_candidates=False),
    )
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_declared_candidate_survives_external_block_policy():
    result = resolve(policy=LocationResolutionPolicy(allow_external_candidates=False))
    assert result.status is LocationResolutionStatus.RESOLVED


def test_candidate_limit_is_enforced():
    candidates = tuple(candidate(str(index)) for index in range(3))
    result = resolve(
        candidates=candidates,
        policy=LocationResolutionPolicy(maximum_candidates=2),
    )
    assert result.status is LocationResolutionStatus.BLOCKED


def test_current_location_requires_available_location():
    context = map_context(location_available=False)
    result = resolve(
        map_context=context,
        reference="here",
        reference_kind=LocationReferenceKind.CURRENT_LOCATION,
        candidates=(),
    )
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_current_location_respects_confidence_policy():
    low_point = GeoPointSignal(-34.6, -58.3, 0.2, NOW, "declared")
    context = map_context(request_changes={"location": low_point})
    result = resolve(
        map_context=context,
        reference="here",
        reference_kind=LocationReferenceKind.CURRENT_LOCATION,
        candidates=(),
    )
    assert result.status is LocationResolutionStatus.REVIEW_REQUIRED


def test_candidate_label_is_normalized():
    assert candidate("  Casa   Central ").label == "Casa Central"


def test_candidate_source_is_normalized():
    assert candidate(source=" Declared ").source == "declared"


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_candidate_confidence_rejected(value):
    with pytest.raises(ValueError, match="confidence"):
        candidate(confidence=value)


def test_blank_candidate_label_rejected():
    with pytest.raises(ValueError, match="label"):
        candidate(" ")


def test_blank_candidate_source_rejected():
    with pytest.raises(ValueError, match="source"):
        candidate(source=" ")


def test_blank_external_id_rejected():
    with pytest.raises(ValueError, match="external id"):
        candidate(external_id=" ")


def test_blank_owner_rejected():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_blank_reference_rejected():
    with pytest.raises(ValueError, match="reference"):
        request(reference=" ")


def test_request_reference_is_normalized():
    assert request(reference="  Casa   Central ").reference == "Casa Central"


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_policy_confidence_rejected(value):
    with pytest.raises(ValueError, match="minimum confidence"):
        LocationResolutionPolicy(minimum_confidence=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_policy_margin_rejected(value):
    with pytest.raises(ValueError, match="ambiguity margin"):
        LocationResolutionPolicy(ambiguity_margin=value)


def test_invalid_candidate_limit_rejected():
    with pytest.raises(ValueError, match="candidate limit"):
        LocationResolutionPolicy(maximum_candidates=0)


def test_naive_evaluation_time_rejected():
    with pytest.raises(ValueError, match="timestamp must be aware"):
        resolve(now=NOW.replace(tzinfo=None))


def test_models_are_frozen():
    result = resolve()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_resolution_id_is_deterministic():
    first = resolve()
    second = LocationResolutionEngine().resolve(request(), now=NOW)
    assert first.resolution_id == second.resolution_id


def test_resolution_id_changes_with_reference():
    assert resolve().resolution_id != resolve(reference="Other").resolution_id


def test_inconsistent_resolution_id_rejected():
    result = resolve()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, resolution_id="wrong")


def test_repository_round_trip():
    repository = InMemoryLocationResolutionRepository()
    engine = LocationResolutionEngine(repository=repository)
    result = engine.resolve(request(), now=NOW)
    assert repository.get(result.resolution_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_identifier():
    repository = InMemoryLocationResolutionRepository()
    engine = LocationResolutionEngine(repository=repository)
    engine.resolve(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        engine.resolve(request(), now=NOW)


def test_repository_protocol_surface():
    repository = InMemoryLocationResolutionRepository()
    assert hasattr(repository, "add")
    assert hasattr(repository, "get")
    assert hasattr(repository, "list_all")


def test_unresolved_result_exposes_no_candidate_or_point():
    result = resolve(candidates=())
    assert result.selected_candidate is None
    assert result.resolved_point is None
    assert result.confidence == 0


def test_m123_never_computes_routes_or_calls_providers():
    result = resolve()
    assert not hasattr(result, "route")
    assert not hasattr(result, "navigation")
    assert not hasattr(LocationResolutionEngine, "geocode")
