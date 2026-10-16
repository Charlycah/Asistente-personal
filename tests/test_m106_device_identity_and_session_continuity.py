from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.device_continuity import (
    CompanionSession,
    DeviceIdentity,
    DeviceKind,
    DeviceSessionContinuityEngine,
    DeviceSessionEndpoint,
    DeviceTrustLevel,
    InMemorySessionContinuityRepository,
    SessionContinuityAction,
    SessionContinuityDecision,
    SessionContinuityPolicy,
    SessionContinuityRequest,
    SessionContinuityStatus,
)

NOW = datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc)


def device(
    device_id="desktop-1",
    *,
    owner="Carlos",
    kind=DeviceKind.DESKTOP,
    trust=DeviceTrustLevel.TRUSTED,
    capabilities=("text", "voice"),
):
    return DeviceIdentity(
        device_id, owner, kind, device_id, trust, capabilities, NOW - timedelta(days=1)
    )


def session(*, owner="Carlos", active="desktop-1", revision=3):
    return CompanionSession(
        "session-1",
        owner,
        active,
        "integration-105",
        revision,
        NOW - timedelta(hours=1),
        NOW - timedelta(minutes=1),
    )


def endpoint(
    identity, *, available=True, authenticated=True, age=5, local_session_id=None
):
    return DeviceSessionEndpoint(
        identity,
        local_session_id or f"local-{identity.device_id}",
        NOW - timedelta(seconds=age),
        available,
        authenticated,
    )


def request(*, source=None, target=None, owner="Carlos", current_session=None):
    source = source or endpoint(device())
    target = target or endpoint(device("mobile-1", kind=DeviceKind.MOBILE))
    return SessionContinuityRequest(
        owner, current_session or session(), source, target, NOW
    )


def test_ready_handoff_between_trusted_devices():
    result = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    assert result.status is SessionContinuityStatus.READY
    assert result.action is SessionContinuityAction.RESUME
    assert result.eligible_for_handoff is True
    assert result.resume_cursor


def test_cursor_is_deterministic_for_same_session_path():
    engine = DeviceSessionContinuityEngine()
    first = engine.evaluate(request(), now=NOW)
    second = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    assert first.resume_cursor == second.resume_cursor
    assert first.decision_id == second.decision_id


def test_cursor_changes_with_session_revision():
    first = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    second = DeviceSessionContinuityEngine().evaluate(
        request(current_session=session(revision=4)), now=NOW
    )
    assert first.resume_cursor != second.resume_cursor


def test_recognized_target_requires_confirmation_by_default():
    target = endpoint(device("mobile-1", kind="mobile", trust="recognized"))
    result = DeviceSessionContinuityEngine().evaluate(request(target=target), now=NOW)
    assert result.status is SessionContinuityStatus.REVIEW_REQUIRED
    assert result.action is SessionContinuityAction.CONFIRM


def test_policy_can_allow_recognized_target():
    target = endpoint(device("mobile-1", kind="mobile", trust="recognized"))
    engine = DeviceSessionContinuityEngine(
        policy=SessionContinuityPolicy(require_trusted_target=False)
    )
    assert (
        engine.evaluate(request(target=target), now=NOW).status
        is SessionContinuityStatus.READY
    )


def test_untrusted_target_is_blocked_even_when_trust_not_required():
    target = endpoint(device("mobile-1", kind="mobile", trust="untrusted"))
    engine = DeviceSessionContinuityEngine(
        policy=SessionContinuityPolicy(require_trusted_target=False)
    )
    assert (
        engine.evaluate(request(target=target), now=NOW).status
        is SessionContinuityStatus.BLOCKED
    )


@pytest.mark.parametrize("which", ["source", "target"])
def test_unavailable_endpoint_blocks(which):
    source = endpoint(device(), available=which != "source")
    target = endpoint(device("mobile-1", kind="mobile"), available=which != "target")
    result = DeviceSessionContinuityEngine().evaluate(
        request(source=source, target=target), now=NOW
    )
    assert result.status is SessionContinuityStatus.BLOCKED
    assert result.resume_cursor is None


@pytest.mark.parametrize("which", ["source", "target"])
def test_unauthenticated_endpoint_blocks(which):
    source = endpoint(device(), authenticated=which != "source")
    target = endpoint(
        device("mobile-1", kind="mobile"), authenticated=which != "target"
    )
    result = DeviceSessionContinuityEngine().evaluate(
        request(source=source, target=target), now=NOW
    )
    assert result.status is SessionContinuityStatus.BLOCKED


def test_policy_can_disable_endpoint_authentication_requirement():
    target = endpoint(device("mobile-1", kind="mobile"), authenticated=False)
    engine = DeviceSessionContinuityEngine(
        policy=SessionContinuityPolicy(require_authenticated_endpoints=False)
    )
    assert (
        engine.evaluate(request(target=target), now=NOW).status
        is SessionContinuityStatus.READY
    )


def test_stale_observation_requires_review():
    target = endpoint(device("mobile-1", kind="mobile"), age=301)
    result = DeviceSessionContinuityEngine().evaluate(request(target=target), now=NOW)
    assert result.status is SessionContinuityStatus.REVIEW_REQUIRED


def test_future_observation_requires_review():
    target = endpoint(device("mobile-1", kind="mobile"), age=-1)
    result = DeviceSessionContinuityEngine().evaluate(request(target=target), now=NOW)
    assert result.status is SessionContinuityStatus.REVIEW_REQUIRED


def test_missing_required_capability_blocks():
    target = endpoint(device("mobile-1", kind="mobile", capabilities=("text",)))
    result = DeviceSessionContinuityEngine().evaluate(
        request(target=target), now=NOW, required_capabilities=("voice",)
    )
    assert result.status is SessionContinuityStatus.BLOCKED
    assert "voice" in result.rationale


def test_required_capabilities_are_normalized():
    result = DeviceSessionContinuityEngine().evaluate(
        request(), now=NOW, required_capabilities=("VOICE", " text ")
    )
    assert result.required_capabilities == ("voice", "text")


@pytest.mark.parametrize("required", [("",), ("voice", "VOICE")])
def test_invalid_required_capabilities_raise(required):
    with pytest.raises(ValueError):
        DeviceSessionContinuityEngine().evaluate(
            request(), now=NOW, required_capabilities=required
        )


def test_same_device_is_not_applicable_by_default():
    same = device()
    result = DeviceSessionContinuityEngine().evaluate(
        request(
            source=endpoint(same), target=endpoint(same, local_session_id="local-2")
        ),
        now=NOW,
    )
    assert result.status is SessionContinuityStatus.NOT_APPLICABLE


def test_policy_can_allow_same_device_resume():
    same = device()
    engine = DeviceSessionContinuityEngine(
        policy=SessionContinuityPolicy(allow_same_device_resume=True)
    )
    result = engine.evaluate(
        request(
            source=endpoint(same), target=endpoint(same, local_session_id="local-2")
        ),
        now=NOW,
    )
    assert result.status is SessionContinuityStatus.READY


def test_owner_mismatch_raises():
    with pytest.raises(ValueError, match="owner mismatch"):
        DeviceSessionContinuityEngine().evaluate(request(owner="Cristina"), now=NOW)


def test_source_must_be_active_device():
    with pytest.raises(ValueError, match="active session device"):
        DeviceSessionContinuityEngine().evaluate(
            request(current_session=session(active="other")), now=NOW
        )


def test_repository_stores_decision():
    repository = InMemorySessionContinuityRepository()
    engine = DeviceSessionContinuityEngine(repository=repository)
    result = engine.evaluate(request(), now=NOW)
    assert repository.get(result.decision_id) == result
    assert engine.last_decision == result


def test_repository_rejects_duplicate():
    repository = InMemorySessionContinuityRepository()
    result = DeviceSessionContinuityEngine(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_decision_is_immutable():
    result = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = SessionContinuityStatus.BLOCKED


def test_device_identity_is_immutable():
    identity = device()
    with pytest.raises(FrozenInstanceError):
        identity.label = "changed"


def test_device_capabilities_are_normalized():
    identity = device(capabilities=(" Voice ", "TEXT"))
    assert identity.capabilities == ("voice", "text")


def test_duplicate_device_capabilities_raise():
    with pytest.raises(ValueError):
        device(capabilities=("voice", "VOICE"))


def test_blank_device_identity_field_raises():
    with pytest.raises(ValueError):
        device(device_id=" ")


def test_session_revision_must_be_positive():
    with pytest.raises(ValueError):
        session(revision=0)


def test_session_update_cannot_precede_start():
    with pytest.raises(ValueError):
        CompanionSession("s", "Carlos", "d", "c", 1, NOW, NOW - timedelta(seconds=1))


def test_naive_request_timestamp_raises():
    with pytest.raises(ValueError):
        replace(request(), requested_at=datetime(2026, 7, 11))


def test_naive_evaluation_timestamp_raises():
    with pytest.raises(ValueError):
        DeviceSessionContinuityEngine().evaluate(request(), now=datetime(2026, 7, 11))


def test_invalid_policy_age_raises():
    with pytest.raises(ValueError):
        SessionContinuityPolicy(max_observation_age_seconds=0)


def test_tampered_decision_id_raises():
    result = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    with pytest.raises(ValueError):
        replace(result, decision_id="bad")


def test_blocked_decision_cannot_have_cursor():
    result = DeviceSessionContinuityEngine().evaluate(
        request(target=endpoint(device("mobile-1", kind="mobile"), available=False)),
        now=NOW,
    )
    with pytest.raises(ValueError):
        SessionContinuityDecision(
            request=result.request,
            status="blocked",
            action="stay",
            eligible_for_handoff=False,
            resume_cursor="cursor",
            required_capabilities=(),
            rationale=("blocked",),
            created_at=NOW,
        )


def test_ready_decision_requires_cursor():
    result = DeviceSessionContinuityEngine().evaluate(request(), now=NOW)
    with pytest.raises(ValueError):
        replace(result, resume_cursor=None, decision_id="")


def test_unknown_device_kind_is_supported_but_governed_by_trust():
    target = endpoint(device("future-device", kind="unknown"))
    assert (
        DeviceSessionContinuityEngine().evaluate(request(target=target), now=NOW).status
        is SessionContinuityStatus.READY
    )
