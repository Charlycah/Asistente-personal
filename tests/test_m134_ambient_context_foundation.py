from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.ambient_context_foundation import (
    AmbientContext,
    AmbientContextFoundationEngine,
    AmbientContextFoundationPolicy,
    AmbientContextFoundationRequest,
    AmbientFoundationAction,
    AmbientFoundationStatus,
    AmbientObservationSignal,
    AmbientObservationSource,
    AmbientPrivacyLevel,
    AmbientScope,
    InMemoryAmbientContextFoundationRepository,
)

NOW = datetime(2026, 7, 11, 22, 30, tzinfo=timezone.utc)


def signal(**changes):
    values = dict(
        observation_ref="ambient-001",
        source=AmbientObservationSource.MOBILE_DEVICE,
        scope=AmbientScope.PERSONAL,
        privacy_level=AmbientPrivacyLevel.PERSONAL,
        confidence=0.95,
        observed_at=NOW,
        source_device_id="phone-main",
    )
    values.update(changes)
    return AmbientObservationSignal(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        observation=signal(),
        explicit_user_consent=True,
    )
    values.update(changes)
    return AmbientContextFoundationRequest(**values)


def establish(*, policy=None, repository=None, **changes):
    return AmbientContextFoundationEngine(
        policy=policy, repository=repository
    ).establish(request(**changes), now=NOW)


def test_ready_context():
    result = establish()
    assert result.status is AmbientFoundationStatus.READY
    assert result.action is AmbientFoundationAction.ESTABLISH


def test_ready_context_exposes_governed_observation():
    result = establish()
    assert result.observation_available
    assert result.context_resolution_required


def test_ready_context_does_not_require_external_provider():
    assert not establish().external_provider_required


def test_never_authorizes_presence_inference():
    assert not establish().presence_inference_allowed


def test_never_authorizes_activity_inference():
    assert not establish().activity_inference_allowed


def test_never_authorizes_acoustic_analysis():
    assert not establish().acoustic_analysis_allowed


def test_never_authorizes_environmental_condition_analysis():
    assert not establish().environmental_condition_analysis_allowed


def test_never_authorizes_spatial_inference():
    assert not establish().spatial_inference_allowed


def test_never_authorizes_automation():
    assert not establish().automation_allowed


def test_context_not_declared_is_not_applicable():
    result = establish(ambient_context_declared=False)
    assert result.status is AmbientFoundationStatus.NOT_APPLICABLE
    assert result.action is AmbientFoundationAction.NONE


def test_missing_consent_requires_review():
    result = establish(explicit_user_consent=False)
    assert result.status is AmbientFoundationStatus.REVIEW_REQUIRED
    assert result.action is AmbientFoundationAction.CONFIRM


def test_policy_can_disable_consent_requirement():
    policy = AmbientContextFoundationPolicy(require_explicit_consent=False)
    assert (
        establish(policy=policy, explicit_user_consent=False).status
        is AmbientFoundationStatus.READY
    )


def test_missing_observation_requires_review():
    result = establish(observation=None)
    assert result.status is AmbientFoundationStatus.REVIEW_REQUIRED


def test_low_confidence_requires_review():
    result = establish(observation=signal(confidence=0.69))
    assert result.status is AmbientFoundationStatus.REVIEW_REQUIRED
    assert result.rationale == ("ambient_observation_confidence_low",)


def test_confidence_threshold_is_inclusive():
    result = establish(observation=signal(confidence=0.7))
    assert result.status is AmbientFoundationStatus.READY


def test_stale_observation_requires_review():
    result = establish(observation=signal(observed_at=NOW - timedelta(seconds=301)))
    assert result.status is AmbientFoundationStatus.REVIEW_REQUIRED


def test_signal_at_age_boundary_is_ready():
    result = establish(observation=signal(observed_at=NOW - timedelta(seconds=300)))
    assert result.status is AmbientFoundationStatus.READY


def test_future_observation_requires_review():
    result = establish(observation=signal(observed_at=NOW + timedelta(seconds=1)))
    assert result.status is AmbientFoundationStatus.REVIEW_REQUIRED


def test_external_observation_is_blocked_by_default():
    result = establish(observation=signal(externally_supplied=True))
    assert result.status is AmbientFoundationStatus.BLOCKED


def test_policy_can_allow_external_observation():
    policy = AmbientContextFoundationPolicy(allow_external_observations=True)
    result = establish(policy=policy, observation=signal(externally_supplied=True))
    assert result.status is AmbientFoundationStatus.READY


def test_restricted_privacy_is_blocked_by_default():
    result = establish(observation=signal(privacy_level=AmbientPrivacyLevel.RESTRICTED))
    assert result.status is AmbientFoundationStatus.BLOCKED


def test_policy_can_allow_restricted_privacy():
    policy = AmbientContextFoundationPolicy(
        allowed_privacy_levels=tuple(AmbientPrivacyLevel)
    )
    result = establish(
        policy=policy,
        observation=signal(privacy_level=AmbientPrivacyLevel.RESTRICTED),
    )
    assert result.status is AmbientFoundationStatus.READY


@pytest.mark.parametrize("source", list(AmbientObservationSource))
def test_all_sources_are_modeled(source):
    result = establish(observation=signal(source=source))
    assert result.request.observation.source is source


@pytest.mark.parametrize("scope", list(AmbientScope))
def test_all_scopes_are_modeled(scope):
    result = establish(observation=signal(scope=scope))
    assert result.request.observation.scope is scope


@pytest.mark.parametrize(
    "privacy",
    [
        AmbientPrivacyLevel.PUBLIC,
        AmbientPrivacyLevel.PERSONAL,
        AmbientPrivacyLevel.SENSITIVE,
    ],
)
def test_default_allowed_privacy_levels_are_ready(privacy):
    result = establish(observation=signal(privacy_level=privacy))
    assert result.status is AmbientFoundationStatus.READY


def test_string_enums_are_normalized():
    item = AmbientObservationSignal(
        "ambient", "home_system", "room", "public", 0.9, NOW
    )
    assert item.source is AmbientObservationSource.HOME_SYSTEM
    assert item.scope is AmbientScope.ROOM
    assert item.privacy_level is AmbientPrivacyLevel.PUBLIC


def test_reference_is_trimmed():
    assert signal(observation_ref="  ambient  ").observation_ref == "ambient"


def test_owner_is_trimmed():
    assert request(owner="  Carlos  ").owner == "Carlos"


def test_source_device_id_is_trimmed():
    assert signal(source_device_id="  phone  ").source_device_id == "phone"


def test_blank_reference_rejected():
    with pytest.raises(ValueError):
        signal(observation_ref="   ")


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner="   ")


def test_blank_source_device_id_rejected():
    with pytest.raises(ValueError):
        signal(source_device_id="   ")


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_invalid_signal_confidence_rejected(confidence):
    with pytest.raises(ValueError):
        signal(confidence=confidence)


def test_naive_signal_timestamp_rejected():
    with pytest.raises(ValueError):
        signal(observed_at=datetime(2026, 7, 11, 22, 30))


def test_naive_evaluation_timestamp_rejected():
    with pytest.raises(ValueError):
        AmbientContextFoundationEngine().establish(
            request(), now=datetime(2026, 7, 11, 22, 30)
        )


def test_reference_over_limit_is_blocked():
    policy = AmbientContextFoundationPolicy(maximum_reference_length=4)
    result = establish(policy=policy, observation=signal(observation_ref="12345"))
    assert result.status is AmbientFoundationStatus.BLOCKED


def test_reference_at_limit_is_ready():
    policy = AmbientContextFoundationPolicy(maximum_reference_length=5)
    result = establish(policy=policy, observation=signal(observation_ref="12345"))
    assert result.status is AmbientFoundationStatus.READY


@pytest.mark.parametrize(
    "changes",
    [
        {"max_signal_age_seconds": 0},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
        {"maximum_reference_length": 0},
        {"allowed_privacy_levels": ()},
        {
            "allowed_privacy_levels": (
                AmbientPrivacyLevel.PUBLIC,
                AmbientPrivacyLevel.PUBLIC,
            )
        },
    ],
)
def test_invalid_policy_rejected(changes):
    with pytest.raises(ValueError):
        AmbientContextFoundationPolicy(**changes)


def test_context_is_immutable():
    result = establish()
    with pytest.raises(FrozenInstanceError):
        result.status = AmbientFoundationStatus.BLOCKED


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_signal_is_immutable():
    item = signal()
    with pytest.raises(FrozenInstanceError):
        item.confidence = 0.1


def test_context_identifier_is_deterministic():
    first = establish()
    second = establish()
    assert first.context_id == second.context_id


def test_context_identifier_changes_with_input():
    first = establish()
    second = establish(observation=signal(scope=AmbientScope.ROOM))
    assert first.context_id != second.context_id


def test_inconsistent_context_identifier_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, context_id="wrong")


def test_non_ready_context_cannot_expose_observation():
    result = establish(observation=None)
    with pytest.raises(ValueError):
        replace(result, observation_available=True)


def test_ready_context_requires_observation_availability():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, observation_available=False)


def test_ready_context_requires_resolution():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, context_resolution_required=False)


@pytest.mark.parametrize(
    "field",
    [
        "presence_inference_allowed",
        "activity_inference_allowed",
        "acoustic_analysis_allowed",
        "environmental_condition_analysis_allowed",
        "spatial_inference_allowed",
        "automation_allowed",
    ],
)
def test_context_cannot_authorize_future_capabilities(field):
    result = establish()
    with pytest.raises(ValueError):
        replace(result, **{field: True})


def test_empty_rationale_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, rationale=())


def test_blank_rationale_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, rationale=("",))


def test_repository_stores_context():
    repository = InMemoryAmbientContextFoundationRepository()
    result = establish(repository=repository)
    assert repository.get(result.context_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_context():
    repository = InMemoryAmbientContextFoundationRepository()
    result = establish(repository=repository)
    with pytest.raises(ValueError):
        repository.add(result)


def test_repository_protocol_shape_is_usable():
    repository = InMemoryAmbientContextFoundationRepository()
    assert repository.get("missing") is None
    assert repository.list_all() == ()


def test_result_is_ambient_context():
    assert isinstance(establish(), AmbientContext)


def test_rationale_is_tuple():
    assert isinstance(establish().rationale, tuple)
