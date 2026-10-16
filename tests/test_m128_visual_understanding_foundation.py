from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.visual_understanding_foundation import (
    InMemoryVisualUnderstandingFoundationRepository,
    VisualFoundationAction,
    VisualFoundationStatus,
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
    VisualUnderstandingFoundationEngine,
    VisualUnderstandingFoundationPolicy,
    VisualUnderstandingFoundationRequest,
)

NOW = datetime(2026, 7, 11, 22, 0, tzinfo=timezone.utc)


def signal(**changes):
    values = dict(
        observation_ref="obs-001",
        source=VisualObservationSource.MOBILE_CAMERA,
        media_type=VisualMediaType.PHOTO,
        privacy_level=VisualPrivacyLevel.PERSONAL,
        confidence=0.95,
        observed_at=NOW,
        source_device_id="phone-main",
    )
    values.update(changes)
    return VisualObservationSignal(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        observation=signal(),
        explicit_user_consent=True,
    )
    values.update(changes)
    return VisualUnderstandingFoundationRequest(**values)


def establish(*, policy=None, **changes):
    return VisualUnderstandingFoundationEngine(policy=policy).establish(
        request(**changes), now=NOW
    )


def test_ready_context():
    result = establish()
    assert result.status is VisualFoundationStatus.READY
    assert result.action is VisualFoundationAction.ESTABLISH


def test_ready_context_exposes_governed_observation():
    result = establish()
    assert result.observation_available
    assert result.observation_resolution_required


def test_ready_context_does_not_require_external_provider():
    assert not establish().external_provider_required


def test_never_authorizes_scene_understanding():
    assert not establish().scene_understanding_allowed


def test_never_authorizes_object_recognition():
    assert not establish().object_recognition_allowed


def test_never_authorizes_text_extraction():
    assert not establish().text_extraction_allowed


def test_never_authorizes_biometrics():
    assert not establish().biometric_analysis_allowed


def test_context_not_declared_is_not_applicable():
    result = establish(visual_context_declared=False)
    assert result.status is VisualFoundationStatus.NOT_APPLICABLE
    assert result.action is VisualFoundationAction.NONE


def test_missing_consent_requires_review():
    result = establish(explicit_user_consent=False)
    assert result.status is VisualFoundationStatus.REVIEW_REQUIRED
    assert result.action is VisualFoundationAction.CONFIRM


def test_policy_can_disable_consent_requirement():
    policy = VisualUnderstandingFoundationPolicy(require_explicit_consent=False)
    assert (
        establish(policy=policy, explicit_user_consent=False).status
        is VisualFoundationStatus.READY
    )


def test_missing_observation_requires_review():
    result = establish(observation=None)
    assert result.status is VisualFoundationStatus.REVIEW_REQUIRED


def test_low_confidence_requires_review():
    result = establish(observation=signal(confidence=0.69))
    assert result.status is VisualFoundationStatus.REVIEW_REQUIRED
    assert result.rationale == ("visual_observation_confidence_low",)


def test_confidence_threshold_is_inclusive():
    result = establish(observation=signal(confidence=0.7))
    assert result.status is VisualFoundationStatus.READY


def test_stale_observation_requires_review():
    old = NOW - timedelta(seconds=301)
    result = establish(observation=signal(observed_at=old))
    assert result.status is VisualFoundationStatus.REVIEW_REQUIRED


def test_signal_at_age_boundary_is_ready():
    old = NOW - timedelta(seconds=300)
    assert (
        establish(observation=signal(observed_at=old)).status
        is VisualFoundationStatus.READY
    )


def test_future_observation_requires_review():
    future = NOW + timedelta(seconds=1)
    result = establish(observation=signal(observed_at=future))
    assert result.status is VisualFoundationStatus.REVIEW_REQUIRED


def test_external_observation_is_blocked_by_default():
    result = establish(observation=signal(externally_supplied=True))
    assert result.status is VisualFoundationStatus.BLOCKED


def test_policy_can_allow_external_observation():
    policy = VisualUnderstandingFoundationPolicy(allow_external_observations=True)
    result = establish(policy=policy, observation=signal(externally_supplied=True))
    assert result.status is VisualFoundationStatus.READY


def test_restricted_privacy_is_blocked_by_default():
    result = establish(observation=signal(privacy_level=VisualPrivacyLevel.RESTRICTED))
    assert result.status is VisualFoundationStatus.BLOCKED


def test_policy_can_allow_restricted_privacy():
    policy = VisualUnderstandingFoundationPolicy(
        allowed_privacy_levels=tuple(VisualPrivacyLevel)
    )
    result = establish(
        policy=policy,
        observation=signal(privacy_level=VisualPrivacyLevel.RESTRICTED),
    )
    assert result.status is VisualFoundationStatus.READY


@pytest.mark.parametrize("source", list(VisualObservationSource))
def test_all_sources_are_modeled(source):
    result = establish(observation=signal(source=source))
    assert result.request.observation.source is source


@pytest.mark.parametrize("media_type", list(VisualMediaType))
def test_all_media_types_are_modeled(media_type):
    result = establish(observation=signal(media_type=media_type))
    assert result.request.observation.media_type is media_type


@pytest.mark.parametrize(
    "privacy",
    [
        VisualPrivacyLevel.PUBLIC,
        VisualPrivacyLevel.PERSONAL,
        VisualPrivacyLevel.SENSITIVE,
    ],
)
def test_default_allowed_privacy_levels_are_ready(privacy):
    assert (
        establish(observation=signal(privacy_level=privacy)).status
        is VisualFoundationStatus.READY
    )


def test_string_enums_are_normalized():
    item = VisualObservationSignal(
        "obs", "image_file", "screenshot", "public", 0.9, NOW
    )
    assert item.source is VisualObservationSource.IMAGE_FILE
    assert item.media_type is VisualMediaType.SCREENSHOT
    assert item.privacy_level is VisualPrivacyLevel.PUBLIC


def test_reference_is_trimmed():
    assert signal(observation_ref="  obs  ").observation_ref == "obs"


def test_owner_is_trimmed():
    assert request(owner="  Carlos  ").owner == "Carlos"


def test_blank_reference_rejected():
    with pytest.raises(ValueError):
        signal(observation_ref="   ")


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner="   ")


def test_invalid_confidence_rejected():
    with pytest.raises(ValueError):
        signal(confidence=1.1)


def test_naive_observation_time_rejected():
    with pytest.raises(ValueError):
        signal(observed_at=datetime(2026, 7, 11, 22, 0))


def test_blank_device_id_rejected():
    with pytest.raises(ValueError):
        signal(source_device_id=" ")


def test_invalid_policy_age_rejected():
    with pytest.raises(ValueError):
        VisualUnderstandingFoundationPolicy(max_signal_age_seconds=0)


def test_invalid_policy_confidence_rejected():
    with pytest.raises(ValueError):
        VisualUnderstandingFoundationPolicy(minimum_confidence=1.1)


def test_empty_privacy_policy_rejected():
    with pytest.raises(ValueError):
        VisualUnderstandingFoundationPolicy(allowed_privacy_levels=())


def test_duplicate_privacy_policy_rejected():
    with pytest.raises(ValueError):
        VisualUnderstandingFoundationPolicy(
            allowed_privacy_levels=(
                VisualPrivacyLevel.PUBLIC,
                VisualPrivacyLevel.PUBLIC,
            )
        )


def test_reference_limit_blocks():
    policy = VisualUnderstandingFoundationPolicy(maximum_reference_length=3)
    result = establish(policy=policy, observation=signal(observation_ref="abcd"))
    assert result.status is VisualFoundationStatus.BLOCKED


def test_reference_limit_boundary_is_ready():
    policy = VisualUnderstandingFoundationPolicy(maximum_reference_length=3)
    assert (
        establish(policy=policy, observation=signal(observation_ref="abc")).status
        is VisualFoundationStatus.READY
    )


def test_context_is_immutable():
    result = establish()
    with pytest.raises(FrozenInstanceError):
        result.status = VisualFoundationStatus.BLOCKED


def test_signal_is_immutable():
    item = signal()
    with pytest.raises(FrozenInstanceError):
        item.confidence = 0.1


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_deterministic_context_id():
    first = VisualUnderstandingFoundationEngine().establish(request(), now=NOW)
    second = VisualUnderstandingFoundationEngine().establish(request(), now=NOW)
    assert first.context_id == second.context_id


def test_changed_input_changes_context_id():
    first = VisualUnderstandingFoundationEngine().establish(request(), now=NOW)
    second = VisualUnderstandingFoundationEngine().establish(
        request(observation=signal(observation_ref="obs-002")), now=NOW
    )
    assert first.context_id != second.context_id


def test_inconsistent_context_id_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, context_id="invalid")


def test_naive_evaluation_time_rejected():
    with pytest.raises(ValueError):
        VisualUnderstandingFoundationEngine().establish(
            request(), now=datetime(2026, 7, 11, 22, 0)
        )


def test_repository_add_get_and_list():
    repository = InMemoryVisualUnderstandingFoundationRepository()
    engine = VisualUnderstandingFoundationEngine(repository=repository)
    result = engine.establish(request(), now=NOW)
    assert repository.get(result.context_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryVisualUnderstandingFoundationRepository()
    result = VisualUnderstandingFoundationEngine(repository=repository).establish(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_inactive_context_exposes_no_capabilities():
    result = establish(explicit_user_consent=False)
    assert not result.observation_available
    assert not result.observation_resolution_required
    assert not result.external_provider_required


def test_ready_context_requires_observation_capability():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, observation_available=False)


def test_manual_analysis_authorization_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, scene_understanding_allowed=True)


def test_empty_rationale_rejected():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, rationale=())


def test_context_timestamp_must_be_aware():
    result = establish()
    with pytest.raises(ValueError):
        replace(result, created_at=datetime(2026, 7, 11, 22, 0), context_id="")


def test_foundation_module_has_no_visual_io_methods():
    forbidden = {
        "analyze_image",
        "detect_objects",
        "extract_text",
        "recognize_face",
        "open_camera",
        "read_file",
        "call_provider",
    }
    assert forbidden.isdisjoint(dir(VisualUnderstandingFoundationEngine))
