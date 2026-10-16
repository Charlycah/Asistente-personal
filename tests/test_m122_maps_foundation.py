from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.maps_foundation import (
    GeoPointSignal,
    InMemoryMapsFoundationRepository,
    MapFoundationAction,
    MapFoundationStatus,
    MapPrecision,
    MapPurpose,
    MapScope,
    MapsFoundationEngine,
    MapsFoundationPolicy,
    MapsFoundationRequest,
)

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)


def signal(**changes):
    values = {
        "latitude": -34.6037,
        "longitude": -58.3816,
        "confidence": 0.95,
        "observed_at": NOW,
        "source": "declared",
    }
    values.update(changes)
    return GeoPointSignal(**values)


def request(**changes):
    values = {
        "owner": "Carlos",
        "purpose": MapPurpose.ORIENTATION,
        "requested_precision": MapPrecision.NEIGHBORHOOD,
        "requested_scope": MapScope.LOCAL,
        "location": signal(),
        "maps_context_declared": True,
        "explicit_user_consent": True,
    }
    values.update(changes)
    return MapsFoundationRequest(**values)


def establish(*, policy=None, now=NOW, **changes):
    return MapsFoundationEngine(policy=policy).establish(request(**changes), now=now)


def test_ready_context():
    result = establish()
    assert result.status is MapFoundationStatus.READY
    assert result.action is MapFoundationAction.ESTABLISH
    assert result.location_available
    assert result.provider_required
    assert not result.route_computation_allowed


@pytest.mark.parametrize("purpose", list(MapPurpose))
def test_all_purposes_are_supported(purpose):
    result = establish(purpose=purpose)
    assert result.request.purpose is purpose


@pytest.mark.parametrize("precision", list(MapPrecision))
def test_all_precisions_are_preserved(precision):
    result = establish(requested_precision=precision)
    assert result.effective_precision is precision


@pytest.mark.parametrize("scope", list(MapScope))
def test_all_scopes_are_preserved(scope):
    result = establish(requested_scope=scope)
    assert result.effective_scope is scope


def test_undeclared_context_is_not_applicable():
    result = establish(maps_context_declared=False)
    assert result.status is MapFoundationStatus.NOT_APPLICABLE
    assert result.action is MapFoundationAction.NONE


def test_missing_consent_requires_review():
    result = establish(explicit_user_consent=False)
    assert result.status is MapFoundationStatus.REVIEW_REQUIRED


def test_consent_requirement_can_be_relaxed():
    result = establish(
        explicit_user_consent=False,
        policy=MapsFoundationPolicy(require_explicit_consent=False),
    )
    assert result.status is MapFoundationStatus.READY


def test_precise_location_can_be_blocked():
    result = establish(
        requested_precision=MapPrecision.PRECISE,
        policy=MapsFoundationPolicy(allow_precise_location=False),
    )
    assert result.status is MapFoundationStatus.BLOCKED


def test_non_precise_location_survives_precise_block_policy():
    result = establish(policy=MapsFoundationPolicy(allow_precise_location=False))
    assert result.status is MapFoundationStatus.READY


def test_route_preparation_can_be_blocked():
    result = establish(
        purpose=MapPurpose.ROUTE_PREPARATION,
        policy=MapsFoundationPolicy(allow_route_preparation=False),
    )
    assert result.status is MapFoundationStatus.BLOCKED


def test_route_preparation_never_authorizes_route_computation():
    result = establish(purpose=MapPurpose.ROUTE_PREPARATION)
    assert result.status is MapFoundationStatus.READY
    assert not result.route_computation_allowed


def test_orientation_requires_location():
    result = establish(location=None)
    assert result.status is MapFoundationStatus.REVIEW_REQUIRED


@pytest.mark.parametrize(
    "purpose",
    [MapPurpose.PLACE_CONTEXT, MapPurpose.ROUTE_PREPARATION, MapPurpose.SAFETY_CONTEXT],
)
def test_non_orientation_context_may_be_established_without_location(purpose):
    result = establish(purpose=purpose, location=None)
    assert result.status is MapFoundationStatus.READY
    assert not result.location_available


def test_stale_location_requires_review():
    result = establish(location=signal(observed_at=NOW - timedelta(minutes=6)))
    assert result.status is MapFoundationStatus.REVIEW_REQUIRED


def test_future_location_requires_review():
    result = establish(location=signal(observed_at=NOW + timedelta(seconds=1)))
    assert result.status is MapFoundationStatus.REVIEW_REQUIRED


def test_low_confidence_requires_review():
    result = establish(location=signal(confidence=0.2))
    assert result.status is MapFoundationStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_configurable():
    result = establish(
        location=signal(confidence=0.5),
        policy=MapsFoundationPolicy(minimum_confidence=0.5),
    )
    assert result.status is MapFoundationStatus.READY


def test_age_threshold_is_configurable():
    result = establish(
        location=signal(observed_at=NOW - timedelta(minutes=10)),
        policy=MapsFoundationPolicy(max_signal_age_seconds=601),
    )
    assert result.status is MapFoundationStatus.READY


@pytest.mark.parametrize("latitude", [-90, 90, 0])
def test_valid_latitude_boundaries(latitude):
    assert signal(latitude=latitude).latitude == latitude


@pytest.mark.parametrize("longitude", [-180, 180, 0])
def test_valid_longitude_boundaries(longitude):
    assert signal(longitude=longitude).longitude == longitude


@pytest.mark.parametrize("latitude", [-90.1, 90.1])
def test_invalid_latitude_rejected(latitude):
    with pytest.raises(ValueError, match="latitude"):
        signal(latitude=latitude)


@pytest.mark.parametrize("longitude", [-180.1, 180.1])
def test_invalid_longitude_rejected(longitude):
    with pytest.raises(ValueError, match="longitude"):
        signal(longitude=longitude)


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_rejected(confidence):
    with pytest.raises(ValueError, match="confidence"):
        signal(confidence=confidence)


def test_blank_source_rejected():
    with pytest.raises(ValueError, match="source"):
        signal(source=" ")


def test_source_is_normalized():
    assert signal(source=" Declared ").source == "declared"


def test_naive_observation_rejected():
    with pytest.raises(ValueError, match="timestamp must be aware"):
        signal(observed_at=NOW.replace(tzinfo=None))


def test_blank_owner_rejected():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_invalid_policy_age_rejected():
    with pytest.raises(ValueError, match="age"):
        MapsFoundationPolicy(max_signal_age_seconds=0)


def test_invalid_policy_confidence_rejected():
    with pytest.raises(ValueError, match="confidence"):
        MapsFoundationPolicy(minimum_confidence=1.1)


def test_naive_evaluation_timestamp_rejected():
    with pytest.raises(ValueError, match="timestamp must be aware"):
        MapsFoundationEngine().establish(request(), now=NOW.replace(tzinfo=None))


def test_context_is_immutable():
    result = establish()
    with pytest.raises(FrozenInstanceError):
        result.location_available = False


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_signal_is_immutable():
    item = signal()
    with pytest.raises(FrozenInstanceError):
        item.latitude = 0


def test_deterministic_id_for_equal_inputs_and_time():
    first = MapsFoundationEngine().establish(request(), now=NOW)
    second = MapsFoundationEngine().establish(request(), now=NOW)
    assert first.context_id == second.context_id


def test_id_changes_with_timestamp():
    first = MapsFoundationEngine().establish(request(), now=NOW)
    second = MapsFoundationEngine().establish(request(), now=NOW + timedelta(seconds=1))
    assert first.context_id != second.context_id


def test_inconsistent_id_rejected():
    result = establish()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, context_id="bad")


def test_repository_add_get_and_list():
    repository = InMemoryMapsFoundationRepository()
    result = MapsFoundationEngine(repository=repository).establish(request(), now=NOW)
    assert repository.get(result.context_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicates():
    repository = InMemoryMapsFoundationRepository()
    result = MapsFoundationEngine(repository=repository).establish(request(), now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_repository_protocol_shape():
    repository = InMemoryMapsFoundationRepository()
    assert hasattr(repository, "add")
    assert hasattr(repository, "get")
    assert hasattr(repository, "list_all")


def test_non_ready_context_cannot_expose_location():
    base = establish(explicit_user_consent=False)
    with pytest.raises(ValueError, match="cannot expose capabilities"):
        replace(base, location_available=True)


def test_m122_cannot_authorize_routes():
    base = establish()
    with pytest.raises(ValueError, match="cannot authorize route computation"):
        replace(base, route_computation_allowed=True)


def test_enum_string_coercion():
    item = MapsFoundationRequest(
        owner="Carlos",
        purpose="orientation",
        requested_precision="approximate",
        requested_scope="global",
        location=signal(),
        explicit_user_consent=True,
    )
    assert item.purpose is MapPurpose.ORIENTATION
    assert item.requested_precision is MapPrecision.APPROXIMATE
    assert item.requested_scope is MapScope.GLOBAL


def test_ready_rationale_is_present():
    assert establish().rationale == ("maps_context_ready",)


def test_context_without_location_requires_provider_but_not_route_engine():
    result = establish(purpose=MapPurpose.PLACE_CONTEXT, location=None)
    assert result.provider_required
    assert not result.route_computation_allowed
