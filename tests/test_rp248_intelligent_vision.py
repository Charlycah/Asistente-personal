from datetime import datetime, timedelta, timezone

import pytest

from core.intelligent_vision import (
    IntelligentVisionService,
    VisionCapability,
    VisionEventType,
    VisionMode,
    VisionObservation,
    VisionPolicy,
)

NOW = datetime(2026, 7, 20, 16, 0, tzinfo=timezone.utc)


def observation(**changes):
    values = dict(
        observation_ref="image-001",
        observed_at=NOW,
        privacy_level="personal",
        requested_capabilities=(VisionCapability.SCENE_DESCRIPTION,),
        confidence=0.95,
        camera_permission=True,
        explicit_user_consent=True,
        user_requested=True,
        summary="Una mesa con documentos.",
    )
    values.update(changes)
    return VisionObservation(**values)


def test_on_demand_accepts_explicit_authorized_observation():
    service = IntelligentVisionService()
    event = service.process(observation())
    assert event.event_type is VisionEventType.ACCEPTED
    assert service.pop_observation().observation_ref == "image-001"


def test_on_demand_ignores_unsolicited_observation():
    service = IntelligentVisionService()
    event = service.process(observation(user_requested=False))
    assert event.event_type is VisionEventType.IGNORED


def test_permission_and_consent_are_required():
    service = IntelligentVisionService()
    event = service.process(
        observation(camera_permission=False, explicit_user_consent=False)
    )
    assert event.event_type is VisionEventType.REJECTED
    assert len(event.rationale) == 2


def test_biometric_identification_is_always_rejected():
    service = IntelligentVisionService()
    event = service.process(
        observation(
            requested_capabilities=(VisionCapability.BIOMETRIC_IDENTIFICATION,)
        )
    )
    assert event.event_type is VisionEventType.REJECTED


def test_restricted_privacy_is_rejected_by_default():
    service = IntelligentVisionService()
    event = service.process(observation(privacy_level="restricted"))
    assert event.event_type is VisionEventType.REJECTED


def test_stale_and_future_observations_are_rejected():
    service = IntelligentVisionService()
    stale = service.process(
        observation(observed_at=NOW - timedelta(minutes=6)), now=NOW
    )
    future = service.process(
        observation(observation_ref="future", observed_at=NOW + timedelta(seconds=1)),
        now=NOW,
    )
    assert stale.event_type is VisionEventType.REJECTED
    assert future.event_type is VisionEventType.REJECTED


def test_authorized_session_accepts_follow_up_until_expiration():
    policy = VisionPolicy(mode=VisionMode.AUTHORIZED_SESSION)
    service = IntelligentVisionService(policy)
    first = service.process(observation())
    second = service.process(
        observation(
            observation_ref="image-002",
            observed_at=NOW + timedelta(seconds=5),
            user_requested=False,
        )
    )
    assert first.event_type is VisionEventType.ACCEPTED
    assert second.event_type is VisionEventType.ACCEPTED
    assert service.snapshot.active


def test_authorized_session_expires_after_inactivity():
    policy = VisionPolicy(mode=VisionMode.AUTHORIZED_SESSION)
    service = IntelligentVisionService(policy)
    service.process(observation())
    event = service.process(
        observation(
            observation_ref="image-late",
            observed_at=NOW + timedelta(seconds=31),
            user_requested=False,
        )
    )
    assert event.event_type is VisionEventType.IGNORED
    assert any(
        item.event_type is VisionEventType.SESSION_EXPIRED
        for item in service.snapshot.events
    )


def test_queue_is_bounded_and_drops_oldest_observation():
    service = IntelligentVisionService(VisionPolicy(queue_limit=2))
    for index in range(3):
        service.process(
            observation(
                observation_ref=f"image-{index}",
                observed_at=NOW + timedelta(seconds=index),
            ),
            now=NOW + timedelta(seconds=index),
        )
    assert service.snapshot.queued_observation_refs == ("image-1", "image-2")


def test_raw_media_is_not_retained_and_event_is_auditable():
    service = IntelligentVisionService()
    event = service.process(observation(raw_media_present=True))
    assert "raw visual media must not be retained" in event.rationale
    assert len(event.event_id) == 64
    assert service.pop_observation().raw_media_present is True


def test_invalid_policy_and_naive_timestamps_are_rejected():
    with pytest.raises(ValueError, match="biometric"):
        VisionPolicy(
            allowed_capabilities=(VisionCapability.BIOMETRIC_IDENTIFICATION,)
        )
    with pytest.raises(ValueError, match="timezone-aware"):
        observation(observed_at=datetime(2026, 7, 20, 16, 0))
