from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.device_capabilities import (
    CapabilityMatchStatus,
    DeviceCapabilityAccess,
    DeviceCapabilityDescriptor,
    DeviceCapabilityKind,
    DeviceCapabilityRegistry,
    DeviceCapabilityRegistryPolicy,
    DeviceCapabilityRequirement,
    DeviceCapabilityState,
    InMemoryDeviceCapabilityRegistryRepository,
    RegisteredDeviceCapability,
)
from core.device_continuity import DeviceIdentity, DeviceKind, DeviceTrustLevel

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)


def device(capabilities=("text", "voice", "camera")):
    return DeviceIdentity(
        "mobile-1",
        "Carlos",
        DeviceKind.MOBILE,
        "Phone",
        DeviceTrustLevel.TRUSTED,
        capabilities,
        NOW - timedelta(days=1),
    )


def item(
    name="voice",
    *,
    kind=DeviceCapabilityKind.OUTPUT,
    state=DeviceCapabilityState.AVAILABLE,
    access=DeviceCapabilityAccess.ALLOWED,
    age=5,
    confidence=1.0,
    version="1.0",
    features=("hands_free",),
    identity=None,
):
    return RegisteredDeviceCapability(
        identity or device(),
        DeviceCapabilityDescriptor(name, kind, version, features),
        state,
        access,
        NOW - timedelta(seconds=age),
        confidence,
    )


def registry(*items, policy=None):
    result = DeviceCapabilityRegistry(policy=policy)
    for value in items or (item(),):
        result.register(value)
    return result


def requirement(name="voice", **kwargs):
    return DeviceCapabilityRequirement(name, **kwargs)


def test_satisfied_requirement():
    result = registry().evaluate("mobile-1", (requirement(),), now=NOW)
    assert result.status is CapabilityMatchStatus.SATISFIED
    assert len(result.matched_registration_ids) == 1


def test_missing_requirement_is_unsatisfied():
    result = registry().evaluate("mobile-1", (requirement("camera"),), now=NOW)
    assert result.status is CapabilityMatchStatus.UNSATISFIED
    assert result.missing_capabilities == ("camera",)


def test_empty_requirements_are_not_applicable():
    assert (
        registry().evaluate("mobile-1", (), now=NOW).status
        is CapabilityMatchStatus.NOT_APPLICABLE
    )


@pytest.mark.parametrize("state", ["unknown", "degraded"])
def test_uncertain_states_require_review(state):
    result = registry(item(state=state)).evaluate("mobile-1", (requirement(),), now=NOW)
    assert result.status is CapabilityMatchStatus.REVIEW_REQUIRED


def test_degraded_can_be_allowed():
    result = registry(item(state="degraded")).evaluate(
        "mobile-1", (requirement(allow_degraded=True),), now=NOW
    )
    assert result.status is CapabilityMatchStatus.SATISFIED


def test_unavailable_is_unsatisfied():
    assert (
        registry(item(state="unavailable"))
        .evaluate("mobile-1", (requirement(),), now=NOW)
        .status
        is CapabilityMatchStatus.UNSATISFIED
    )


def test_consent_required_needs_review_by_default():
    assert (
        registry(item(access="consent_required"))
        .evaluate("mobile-1", (requirement(),), now=NOW)
        .status
        is CapabilityMatchStatus.REVIEW_REQUIRED
    )


def test_policy_can_allow_consent_required():
    policy = DeviceCapabilityRegistryPolicy(allow_consent_required=True)
    assert (
        registry(item(access="consent_required"), policy=policy)
        .evaluate("mobile-1", (requirement(),), now=NOW)
        .status
        is CapabilityMatchStatus.SATISFIED
    )


def test_denied_access_is_unsatisfied():
    assert (
        registry(item(access="denied"))
        .evaluate("mobile-1", (requirement(),), now=NOW)
        .status
        is CapabilityMatchStatus.UNSATISFIED
    )


def test_access_requirement_can_be_disabled():
    assert (
        registry(item(access="denied"))
        .evaluate("mobile-1", (requirement(require_access=False),), now=NOW)
        .status
        is CapabilityMatchStatus.SATISFIED
    )


@pytest.mark.parametrize("age", [301, -1])
def test_stale_or_future_observation_requires_review(age):
    assert (
        registry(item(age=age)).evaluate("mobile-1", (requirement(),), now=NOW).status
        is CapabilityMatchStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():
    assert (
        registry(item(confidence=0.69))
        .evaluate("mobile-1", (requirement(),), now=NOW)
        .status
        is CapabilityMatchStatus.REVIEW_REQUIRED
    )


def test_version_requirement_is_enforced():
    result = registry(item(version="1.2")).evaluate(
        "mobile-1", (requirement(minimum_version="2.0"),), now=NOW
    )
    assert result.status is CapabilityMatchStatus.UNSATISFIED


def test_version_requirement_can_be_satisfied():
    assert (
        registry(item(version="2.1"))
        .evaluate("mobile-1", (requirement(minimum_version="2.0"),), now=NOW)
        .status
        is CapabilityMatchStatus.SATISFIED
    )


def test_feature_requirement_is_enforced():
    result = registry().evaluate(
        "mobile-1", (requirement(required_features=("wake_word",)),), now=NOW
    )
    assert result.status is CapabilityMatchStatus.UNSATISFIED


def test_feature_requirement_can_be_satisfied():
    assert (
        registry()
        .evaluate(
            "mobile-1", (requirement(required_features=("hands_free",)),), now=NOW
        )
        .status
        is CapabilityMatchStatus.SATISFIED
    )


def test_latest_registration_is_used():
    older = item(state="unavailable", age=20)
    newer = item(state="available", age=5)
    assert (
        registry(older, newer).evaluate("mobile-1", (requirement(),), now=NOW).status
        is CapabilityMatchStatus.SATISFIED
    )


def test_multiple_requirements_all_must_match():
    voice = item()
    text = item("text", kind="output", features=("screen",))
    result = registry(voice, text).evaluate(
        "mobile-1", (requirement(), requirement("text")), now=NOW
    )
    assert result.status is CapabilityMatchStatus.SATISFIED


def test_any_missing_requirement_makes_result_unsatisfied():
    result = registry().evaluate(
        "mobile-1", (requirement(), requirement("camera")), now=NOW
    )
    assert result.status is CapabilityMatchStatus.UNSATISFIED


def test_registration_must_be_declared_by_identity():
    with pytest.raises(ValueError, match="declared"):
        registry(item("location", identity=device(("voice",))))


def test_repository_round_trip():
    repository = InMemoryDeviceCapabilityRegistryRepository()
    value = item()
    repository.add(value)
    assert repository.get(value.registration_id) == value
    assert repository.list_for_device("mobile-1") == (value,)


def test_repository_rejects_duplicate():
    repository = InMemoryDeviceCapabilityRegistryRepository()
    value = item()
    repository.add(value)
    with pytest.raises(ValueError):
        repository.add(value)


def test_registry_rejects_duplicate_requirements():
    with pytest.raises(ValueError, match="unique"):
        registry().evaluate("mobile-1", (requirement(), requirement("VOICE")), now=NOW)


def test_unknown_device_raises():
    with pytest.raises(ValueError, match="no registered"):
        registry().evaluate("desktop-1", (requirement(),), now=NOW)


def test_blank_device_id_raises():
    with pytest.raises(ValueError):
        registry().evaluate(" ", (requirement(),), now=NOW)


def test_naive_evaluation_time_raises():
    with pytest.raises(ValueError):
        registry().evaluate("mobile-1", (requirement(),), now=datetime(2026, 1, 1))


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_invalid_confidence_raises(confidence):
    with pytest.raises(ValueError):
        item(confidence=confidence)


def test_descriptor_normalizes_name_and_features():
    descriptor = DeviceCapabilityDescriptor(" Voice ", "output", "1", (" Hands_Free ",))
    assert descriptor.name == "voice"
    assert descriptor.features == ("hands_free",)


def test_requirement_normalizes_name_and_features():
    value = DeviceCapabilityRequirement(" VOICE ", required_features=(" Hands_Free ",))
    assert value.name == "voice"
    assert value.required_features == ("hands_free",)


def test_invalid_descriptor_features_raise():
    with pytest.raises(ValueError):
        DeviceCapabilityDescriptor("voice", "output", features=("x", "X"))


def test_invalid_requirement_features_raise():
    with pytest.raises(ValueError):
        DeviceCapabilityRequirement("voice", required_features=("x", "X"))


def test_policy_validation():
    with pytest.raises(ValueError):
        DeviceCapabilityRegistryPolicy(max_observation_age_seconds=0)


def test_registration_is_immutable():
    value = item()
    with pytest.raises(FrozenInstanceError):
        value.state = DeviceCapabilityState.UNAVAILABLE


def test_match_is_immutable():
    value = registry().evaluate("mobile-1", (requirement(),), now=NOW)
    with pytest.raises(FrozenInstanceError):
        value.status = CapabilityMatchStatus.UNSATISFIED


def test_ids_are_deterministic():
    first = item()
    second = item()
    assert first.registration_id == second.registration_id
    one = registry(first).evaluate("mobile-1", (requirement(),), now=NOW)
    two = registry(second).evaluate("mobile-1", (requirement(),), now=NOW)
    assert one.match_id == two.match_id
