from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.context_transfer import (
    ContextFragmentKind,
    ContextSensitivity,
    ContextTransferAction,
    ContextTransferPolicy,
    ContextTransferRequest,
    ContextTransferStatus,
    CrossDeviceContextTransfer,
    InMemoryContextTransferRepository,
    TransferableContextFragment,
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

NOW = datetime(2026, 7, 11, 15, 0, tzinfo=timezone.utc)


def identity(device_id, kind, capabilities=("text", "voice")):
    return DeviceIdentity(
        device_id,
        "Carlos",
        kind,
        device_id,
        DeviceTrustLevel.TRUSTED,
        capabilities,
        NOW - timedelta(days=1),
    )


def continuity(status=SessionContinuityStatus.READY):
    source = identity("desktop-1", DeviceKind.DESKTOP)
    target = identity("mobile-1", DeviceKind.MOBILE)
    session = CompanionSession("session-1", "Carlos", "desktop-1", "conv-1")
    request = SessionContinuityRequest(
        "Carlos",
        session,
        DeviceSessionEndpoint(source, "local-a", NOW),
        DeviceSessionEndpoint(target, "local-b", NOW),
        NOW,
    )
    ready = status is SessionContinuityStatus.READY
    action = {
        SessionContinuityStatus.READY: SessionContinuityAction.RESUME,
        SessionContinuityStatus.REVIEW_REQUIRED: SessionContinuityAction.CONFIRM,
        SessionContinuityStatus.BLOCKED: SessionContinuityAction.STAY,
        SessionContinuityStatus.NOT_APPLICABLE: SessionContinuityAction.NONE,
    }[status]
    return SessionContinuityDecision(
        request,
        status,
        action,
        ready,
        "cursor-1" if ready else None,
        ("text",),
        ("test_decision",),
        NOW,
    )


def match(status=CapabilityMatchStatus.SATISFIED, target=None):
    target = target or continuity().request.target.device
    return DeviceCapabilityMatch(
        target,
        (DeviceCapabilityRequirement("text"),),
        ("registration-1",) if status is CapabilityMatchStatus.SATISFIED else (),
        ("text",) if status is CapabilityMatchStatus.UNSATISFIED else (),
        ("text",) if status is CapabilityMatchStatus.REVIEW_REQUIRED else (),
        status,
        ("test_match",),
        NOW,
    )


def fragment(fragment_id="f1", **kwargs):
    return TransferableContextFragment(
        fragment_id,
        kwargs.pop("owner", "Carlos"),
        kwargs.pop("session_id", "session-1"),
        kwargs.pop("kind", ContextFragmentKind.CONVERSATION),
        kwargs.pop("reference_id", "ref-1"),
        kwargs.pop("revision", 1),
        kwargs.pop("content_digest", "digest-1"),
        kwargs.pop("sensitivity", ContextSensitivity.PERSONAL),
        kwargs.pop("expires_at", None),
        kwargs.pop("required_capabilities", ("text",)),
        **kwargs,
    )


def request(*fragments, continuity_value=None, match_value=None, owner="Carlos"):
    decision = continuity_value or continuity()
    return ContextTransferRequest(
        owner,
        decision,
        match_value or match(target=decision.request.target.device),
        tuple(fragments),
        NOW,
    )


def test_ready_manifest_includes_context_and_cursor():
    result = CrossDeviceContextTransfer().prepare(request(fragment()), now=NOW)
    assert result.status is ContextTransferStatus.READY
    assert result.action is ContextTransferAction.PREPARE
    assert result.included_fragment_ids == ("f1",)
    assert result.resume_cursor == "cursor-1"
    assert result.manifest_digest


def test_empty_context_is_not_applicable():
    result = CrossDeviceContextTransfer().prepare(request(), now=NOW)
    assert result.status is ContextTransferStatus.NOT_APPLICABLE
    assert result.action is ContextTransferAction.NONE


@pytest.mark.parametrize(
    "status",
    [
        SessionContinuityStatus.REVIEW_REQUIRED,
        SessionContinuityStatus.BLOCKED,
        SessionContinuityStatus.NOT_APPLICABLE,
    ],
)
def test_non_ready_continuity_blocks_transfer(status):
    decision = continuity(status)
    result = CrossDeviceContextTransfer().prepare(
        request(
            fragment(),
            continuity_value=decision,
            match_value=match(target=decision.request.target.device),
        ),
        now=NOW,
    )
    assert result.status is ContextTransferStatus.BLOCKED
    assert result.action is ContextTransferAction.STAY


def test_capability_review_requires_confirmation():
    decision = continuity()
    result = CrossDeviceContextTransfer().prepare(
        request(
            fragment(),
            continuity_value=decision,
            match_value=match(
                CapabilityMatchStatus.REVIEW_REQUIRED, decision.request.target.device
            ),
        ),
        now=NOW,
    )
    assert result.status is ContextTransferStatus.REVIEW_REQUIRED


def test_unsatisfied_capabilities_block():
    decision = continuity()
    result = CrossDeviceContextTransfer().prepare(
        request(
            fragment(),
            continuity_value=decision,
            match_value=match(
                CapabilityMatchStatus.UNSATISFIED, decision.request.target.device
            ),
        ),
        now=NOW,
    )
    assert result.status is ContextTransferStatus.BLOCKED


def test_sensitive_context_requires_review_by_default():
    result = CrossDeviceContextTransfer().prepare(
        request(fragment(sensitivity="sensitive")), now=NOW
    )
    assert result.status is ContextTransferStatus.REVIEW_REQUIRED
    assert result.review_fragment_ids == ("f1",)


def test_policy_can_allow_sensitive_without_review():
    policy = ContextTransferPolicy(review_sensitive=False)
    result = CrossDeviceContextTransfer(policy=policy).prepare(
        request(fragment(sensitivity="sensitive")), now=NOW
    )
    assert result.status is ContextTransferStatus.READY


def test_sensitive_can_be_blocked():
    policy = ContextTransferPolicy(allow_sensitive=False)
    result = CrossDeviceContextTransfer(policy=policy).prepare(
        request(fragment(sensitivity="sensitive")), now=NOW
    )
    assert result.status is ContextTransferStatus.BLOCKED


def test_restricted_is_excluded_by_default():
    result = CrossDeviceContextTransfer().prepare(
        request(fragment(sensitivity="restricted")), now=NOW
    )
    assert result.status is ContextTransferStatus.BLOCKED
    assert "restricted:f1" in result.rationale


def test_policy_can_allow_restricted():
    policy = ContextTransferPolicy(allow_restricted=True, review_sensitive=False)
    result = CrossDeviceContextTransfer(policy=policy).prepare(
        request(fragment(sensitivity="restricted")), now=NOW
    )
    assert result.status is ContextTransferStatus.READY


def test_expired_fragment_is_excluded():
    result = CrossDeviceContextTransfer().prepare(
        request(fragment(expires_at=NOW - timedelta(seconds=1))), now=NOW
    )
    assert result.status is ContextTransferStatus.BLOCKED
    assert "expired:f1" in result.rationale


def test_future_expiry_is_allowed():
    result = CrossDeviceContextTransfer().prepare(
        request(fragment(expires_at=NOW + timedelta(seconds=1))), now=NOW
    )
    assert result.status is ContextTransferStatus.READY


def test_capability_gap_excludes_fragment():
    result = CrossDeviceContextTransfer().prepare(
        request(fragment(required_capabilities=("camera",))), now=NOW
    )
    assert result.status is ContextTransferStatus.BLOCKED
    assert "capability_gap:f1" in result.rationale


def test_partial_transfer_preserves_exclusions():
    result = CrossDeviceContextTransfer().prepare(
        request(
            fragment("f1"),
            fragment("f2", required_capabilities=("camera",)),
        ),
        now=NOW,
    )
    assert result.status is ContextTransferStatus.READY
    assert result.included_fragment_ids == ("f1",)
    assert result.excluded_fragment_ids == ("f2",)


def test_fragment_limit_requires_review():
    policy = ContextTransferPolicy(max_fragments=1)
    result = CrossDeviceContextTransfer(policy=policy).prepare(
        request(fragment("f1"), fragment("f2")), now=NOW
    )
    assert result.status is ContextTransferStatus.REVIEW_REQUIRED


def test_policy_rejects_invalid_limit():
    with pytest.raises(ValueError):
        ContextTransferPolicy(max_fragments=0)


@pytest.mark.parametrize(
    "field", ["fragment_id", "owner", "session_id", "reference_id", "content_digest"]
)
def test_fragment_rejects_blank_fields(field):
    kwargs = {field: " "}
    if field == "fragment_id":
        with pytest.raises(ValueError):
            fragment(" ")
    else:
        with pytest.raises(ValueError):
            fragment(**kwargs)


def test_fragment_rejects_non_positive_revision():
    with pytest.raises(ValueError):
        fragment(revision=0)


def test_fragment_rejects_naive_expiry():
    with pytest.raises(ValueError):
        fragment(expires_at=datetime(2026, 7, 11))


def test_fragment_normalizes_required_capabilities():
    value = fragment(required_capabilities=(" Text ",))
    assert value.required_capabilities == ("text",)


def test_fragment_rejects_duplicate_capabilities():
    with pytest.raises(ValueError):
        fragment(required_capabilities=("text", "TEXT"))


def test_request_rejects_duplicate_fragments():
    with pytest.raises(ValueError):
        request(fragment("f1"), fragment("f1"))


def test_request_rejects_naive_timestamp():
    with pytest.raises(ValueError):
        replace(request(fragment()), requested_at=datetime(2026, 7, 11))


def test_owner_mismatch_is_rejected():
    with pytest.raises(ValueError):
        CrossDeviceContextTransfer().prepare(
            request(fragment(), owner="Cristina"), now=NOW
        )


def test_fragment_session_mismatch_is_rejected():
    with pytest.raises(ValueError):
        CrossDeviceContextTransfer().prepare(
            request(fragment(session_id="other")), now=NOW
        )


def test_capability_match_must_describe_target():
    wrong = identity("other", DeviceKind.MOBILE)
    with pytest.raises(ValueError):
        CrossDeviceContextTransfer().prepare(
            request(fragment(), match_value=match(target=wrong)), now=NOW
        )


def test_repository_stores_manifest():
    repo = InMemoryContextTransferRepository()
    engine = CrossDeviceContextTransfer(repository=repo)
    result = engine.prepare(request(fragment()), now=NOW)
    assert repo.get(result.manifest_id) == result
    assert repo.list_all() == (result,)


def test_repository_rejects_duplicate_manifest():
    repo = InMemoryContextTransferRepository()
    engine = CrossDeviceContextTransfer(repository=repo)
    result = engine.prepare(request(fragment()), now=NOW)
    with pytest.raises(ValueError):
        repo.add(result)


def test_manifest_is_immutable():
    result = CrossDeviceContextTransfer().prepare(request(fragment()), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = ContextTransferStatus.BLOCKED


def test_manifest_is_deterministic_for_same_input_and_time():
    first = CrossDeviceContextTransfer().prepare(request(fragment()), now=NOW)
    second = CrossDeviceContextTransfer().prepare(request(fragment()), now=NOW)
    assert first.manifest_id == second.manifest_id
    assert first.manifest_digest == second.manifest_digest


def test_digest_changes_with_fragment_revision():
    first = CrossDeviceContextTransfer().prepare(request(fragment(revision=1)), now=NOW)
    second = CrossDeviceContextTransfer().prepare(
        request(fragment(revision=2)), now=NOW
    )
    assert first.manifest_digest != second.manifest_digest


def test_naive_evaluation_time_is_rejected():
    with pytest.raises(ValueError):
        CrossDeviceContextTransfer().prepare(
            request(fragment()), now=datetime(2026, 7, 11)
        )
