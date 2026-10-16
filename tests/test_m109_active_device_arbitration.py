from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.context_transfer import (
    ContextFragmentKind,
    ContextSensitivity,
    ContextTransferRequest,
    CrossDeviceContextTransfer,
    TransferableContextFragment,
)
from core.device_arbitration import (
    ActiveDeviceArbitrator,
    DeviceArbitrationAction,
    DeviceArbitrationCandidate,
    DeviceArbitrationPolicy,
    DeviceArbitrationRequest,
    DeviceArbitrationStatus,
    InMemoryDeviceArbitrationRepository,
)
from core.device_capabilities import (
    CapabilityMatchStatus,
    DeviceCapabilityMatch,
    DeviceCapabilityRequirement,
)
from core.device_continuity import (
    CompanionSession,
    DeviceIdentity,
    DeviceKind,
    DeviceSessionEndpoint,
    DeviceTrustLevel,
    SessionContinuityAction,
    SessionContinuityDecision,
    SessionContinuityRequest,
    SessionContinuityStatus,
)

NOW = datetime(2026, 7, 11, 16, 0, tzinfo=timezone.utc)


def identity(device_id, kind=DeviceKind.DESKTOP, trust=DeviceTrustLevel.TRUSTED):
    return DeviceIdentity(
        device_id,
        "Carlos",
        kind,
        device_id,
        trust,
        ("text",),
        NOW - timedelta(days=1),
    )


def endpoint(device, **kwargs):
    return DeviceSessionEndpoint(
        device,
        kwargs.pop("local_session_id", f"local-{device.device_id}"),
        kwargs.pop("observed_at", NOW),
        kwargs.pop("available", True),
        kwargs.pop("authenticated", True),
        **kwargs,
    )


def match(device, status=CapabilityMatchStatus.SATISFIED):
    return DeviceCapabilityMatch(
        device,
        (DeviceCapabilityRequirement("text"),),
        (f"reg-{device.device_id}",)
        if status is CapabilityMatchStatus.SATISFIED
        else (),
        ("text",) if status is CapabilityMatchStatus.UNSATISFIED else (),
        ("text",) if status is CapabilityMatchStatus.REVIEW_REQUIRED else (),
        status,
        ("test_match",),
        NOW,
    )


def transfer(source, target):
    session = CompanionSession("session-1", "Carlos", source.device_id, "conv-1")
    continuity_request = SessionContinuityRequest(
        "Carlos", session, endpoint(source), endpoint(target), NOW
    )
    continuity = SessionContinuityDecision(
        continuity_request,
        SessionContinuityStatus.READY,
        SessionContinuityAction.RESUME,
        True,
        "cursor-1",
        ("text",),
        ("test_continuity",),
        NOW,
    )
    fragment = TransferableContextFragment(
        "f1",
        "Carlos",
        "session-1",
        ContextFragmentKind.CONVERSATION,
        "ref-1",
        1,
        "digest-1",
        ContextSensitivity.PERSONAL,
        None,
        ("text",),
    )
    request = ContextTransferRequest(
        "Carlos", continuity, match(target), (fragment,), NOW
    )
    return CrossDeviceContextTransfer().prepare(request, now=NOW)


def session(active="desktop-1", owner="Carlos"):
    return CompanionSession("session-1", owner, active, "conv-1")


def candidate(
    device,
    *,
    manifest=None,
    preference=0.0,
    status=CapabilityMatchStatus.SATISFIED,
    **endpoint_kwargs,
):
    return DeviceArbitrationCandidate(
        endpoint(device, **endpoint_kwargs),
        match(device, status),
        manifest,
        preference,
    )


def request(*candidates, active="desktop-1", owner="Carlos"):
    return DeviceArbitrationRequest(
        owner, session(active, owner), tuple(candidates), NOW
    )


def test_current_device_is_selected_when_only_candidate():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)
    assert result.status is DeviceArbitrationStatus.READY
    assert result.action is DeviceArbitrationAction.STAY
    assert result.selected_device_id == "desktop-1"


def test_better_target_is_selected_with_ready_transfer():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    result = ActiveDeviceArbitrator().arbitrate(
        request(
            candidate(desktop, preference=-0.5),
            candidate(mobile, manifest=transfer(desktop, mobile), preference=0.8),
        ),
        now=NOW,
    )
    assert result.status is DeviceArbitrationStatus.READY
    assert result.action is DeviceArbitrationAction.SWITCH
    assert result.selected_device_id == "mobile-1"


def test_target_without_transfer_is_not_eligible():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop), candidate(mobile, preference=1.0)), now=NOW
    )
    assert result.selected_device_id == "desktop-1"


def test_policy_can_allow_switch_without_transfer():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    policy = DeviceArbitrationPolicy(require_ready_transfer_for_switch=False)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(candidate(desktop, preference=-1), candidate(mobile, preference=1)),
        now=NOW,
    )
    assert result.action is DeviceArbitrationAction.SWITCH


def test_empty_candidates_is_not_applicable():
    result = ActiveDeviceArbitrator().arbitrate(request(), now=NOW)
    assert result.status is DeviceArbitrationStatus.NOT_APPLICABLE
    assert result.action is DeviceArbitrationAction.NONE


@pytest.mark.parametrize("field", ["available", "authenticated"])
def test_unusable_current_device_blocks_when_no_alternative(field):
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop, **{field: False})), now=NOW
    )
    assert result.status is DeviceArbitrationStatus.BLOCKED


def test_stale_observation_requires_review():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop, observed_at=NOW - timedelta(hours=1))), now=NOW
    )
    assert result.status is DeviceArbitrationStatus.REVIEW_REQUIRED
    assert result.action is DeviceArbitrationAction.CONFIRM


def test_future_observation_requires_review():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop, observed_at=NOW + timedelta(seconds=1))), now=NOW
    )
    assert result.status is DeviceArbitrationStatus.REVIEW_REQUIRED


def test_untrusted_device_is_blocked_by_default():
    desktop = identity("desktop-1", trust=DeviceTrustLevel.UNTRUSTED)
    result = ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)
    assert result.status is DeviceArbitrationStatus.BLOCKED


def test_policy_can_allow_untrusted_device():
    desktop = identity("desktop-1", trust=DeviceTrustLevel.UNTRUSTED)
    policy = DeviceArbitrationPolicy(allow_untrusted_devices=True)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(candidate(desktop)), now=NOW
    )
    assert result.status is DeviceArbitrationStatus.READY


def test_unsatisfied_capability_blocks_candidate():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop, status=CapabilityMatchStatus.UNSATISFIED)), now=NOW
    )
    assert result.status is DeviceArbitrationStatus.BLOCKED


def test_capability_review_requires_confirmation():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(
        request(candidate(desktop, status=CapabilityMatchStatus.REVIEW_REQUIRED)),
        now=NOW,
    )
    assert result.status is DeviceArbitrationStatus.REVIEW_REQUIRED


def test_switch_margin_preserves_current_device():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    policy = DeviceArbitrationPolicy(minimum_switch_margin=1.0)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(
            candidate(desktop),
            candidate(mobile, manifest=transfer(desktop, mobile), preference=0.1),
        ),
        now=NOW,
    )
    assert result.selected_device_id == "desktop-1"


def test_zero_margin_allows_higher_score_switch():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    policy = DeviceArbitrationPolicy(minimum_switch_margin=0.0)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(
            candidate(desktop, preference=-0.1),
            candidate(mobile, manifest=transfer(desktop, mobile), preference=0.1),
        ),
        now=NOW,
    )
    assert result.selected_device_id == "mobile-1"


def test_tie_is_deterministic_by_device_id_without_current_candidate():
    a = identity("a-device", DeviceKind.MOBILE)
    b = identity("b-device", DeviceKind.TABLET)
    policy = DeviceArbitrationPolicy(require_ready_transfer_for_switch=False)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(candidate(b), candidate(a), active="missing"), now=NOW
    )
    assert result.selected_device_id == "a-device"


def test_owner_mismatch_is_rejected():
    desktop = identity("desktop-1")
    with pytest.raises(ValueError):
        ActiveDeviceArbitrator().arbitrate(
            DeviceArbitrationRequest("Cristina", session(), (candidate(desktop),), NOW),
            now=NOW,
        )


def test_candidate_owner_mismatch_is_rejected():
    desktop = replace(identity("desktop-1"), owner="Cristina")
    with pytest.raises(ValueError):
        ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)


def test_candidate_rejects_capability_match_for_other_device():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    with pytest.raises(ValueError):
        DeviceArbitrationCandidate(endpoint(desktop), match(mobile))


def test_candidate_rejects_manifest_for_other_target():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    tablet = identity("tablet-1", DeviceKind.TABLET)
    with pytest.raises(ValueError):
        DeviceArbitrationCandidate(
            endpoint(tablet), match(tablet), transfer(desktop, mobile)
        )


@pytest.mark.parametrize("value", [-1.1, 1.1])
def test_candidate_rejects_invalid_preference(value):
    desktop = identity("desktop-1")
    with pytest.raises(ValueError):
        candidate(desktop, preference=value)


def test_request_rejects_duplicate_candidates():
    desktop = identity("desktop-1")
    with pytest.raises(ValueError):
        request(candidate(desktop), candidate(desktop))


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        DeviceArbitrationRequest(" ", session(), (), NOW)


def test_request_rejects_naive_timestamp():
    with pytest.raises(ValueError):
        replace(request(), requested_at=datetime(2026, 7, 11))


def test_policy_rejects_non_positive_age():
    with pytest.raises(ValueError):
        DeviceArbitrationPolicy(max_observation_age_seconds=0)


def test_policy_rejects_negative_margin():
    with pytest.raises(ValueError):
        DeviceArbitrationPolicy(minimum_switch_margin=-0.1)


def test_naive_evaluation_time_is_rejected():
    with pytest.raises(ValueError):
        ActiveDeviceArbitrator().arbitrate(request(), now=datetime(2026, 7, 11))


def test_repository_stores_decision():
    desktop = identity("desktop-1")
    repo = InMemoryDeviceArbitrationRepository()
    result = ActiveDeviceArbitrator(repository=repo).arbitrate(
        request(candidate(desktop)), now=NOW
    )
    assert repo.get(result.decision_id) == result
    assert repo.list_all() == (result,)


def test_repository_rejects_duplicate_decision():
    desktop = identity("desktop-1")
    repo = InMemoryDeviceArbitrationRepository()
    result = ActiveDeviceArbitrator(repository=repo).arbitrate(
        request(candidate(desktop)), now=NOW
    )
    with pytest.raises(ValueError):
        repo.add(result)


def test_decision_is_immutable():
    desktop = identity("desktop-1")
    result = ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = DeviceArbitrationStatus.BLOCKED


def test_decision_is_deterministic_for_same_input_and_time():
    desktop = identity("desktop-1")
    first = ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)
    second = ActiveDeviceArbitrator().arbitrate(request(candidate(desktop)), now=NOW)
    assert first.decision_id == second.decision_id


def test_candidate_scores_are_sorted_by_device_id():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    policy = DeviceArbitrationPolicy(require_ready_transfer_for_switch=False)
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(candidate(mobile), candidate(desktop)), now=NOW
    )
    assert tuple(item[0] for item in result.candidate_scores) == (
        "desktop-1",
        "mobile-1",
    )


def test_prefer_current_device_can_be_disabled():
    desktop = identity("desktop-1")
    mobile = identity("mobile-1", DeviceKind.MOBILE)
    policy = DeviceArbitrationPolicy(
        prefer_current_device=False,
        require_ready_transfer_for_switch=False,
        minimum_switch_margin=0,
    )
    result = ActiveDeviceArbitrator(policy=policy).arbitrate(
        request(candidate(desktop), candidate(mobile, preference=0.1)), now=NOW
    )
    assert result.selected_device_id == "mobile-1"
