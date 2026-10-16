from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.intelligent_vision import VisionCapability, VisionEventType
from infrastructure.camera.camera_client import CameraFrame


class FakeCameraProvider:
    def __init__(self) -> None:
        self.indices: list[int] = []

    def capture(self, camera_index: int) -> CameraFrame:
        self.indices.append(camera_index)
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"private-frame-bytes",
            width=1280,
            height=720,
            captured_at=datetime.now(timezone.utc),
            frame_id="frame-m348-9",
        )


def authorized_request(**changes: object) -> VisionCaptureRequest:
    values: dict[str, object] = {
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(changes)
    return VisionCaptureRequest(**values)


def test_vision_core_captures_one_authorized_frame_and_governs_it():
    provider = FakeCameraProvider()
    core = OfficialVisionCore(camera_provider=provider)

    result = core.capture(authorized_request(camera_index=1))

    assert provider.indices == [1]
    assert result.frame_id == "frame-m348-9"
    assert result.event.event_type is VisionEventType.ACCEPTED
    assert result.event.accepted_capabilities == (
        VisionCapability.SCENE_DESCRIPTION,
    )


def test_vision_core_result_never_exposes_raw_frame_bytes():
    core = OfficialVisionCore(camera_provider=FakeCameraProvider())

    result = core.capture(authorized_request())

    assert not hasattr(result, "image_bytes")
    assert result.size_bytes == len(b"private-frame-bytes")


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("camera_permission", "camera permission"),
        ("explicit_user_consent", "explicit vision consent"),
        ("user_requested", "explicitly requested"),
    ],
)
def test_vision_core_refuses_capture_before_touching_hardware(field, message):
    provider = FakeCameraProvider()
    core = OfficialVisionCore(camera_provider=provider)

    with pytest.raises(PermissionError, match=message):
        core.capture(authorized_request(**{field: False}))

    assert provider.indices == []
    assert core.snapshot.capture_attempts == 1
    assert core.snapshot.frames_captured == 0


def test_vision_core_snapshot_is_safe_and_observable():
    core = OfficialVisionCore(camera_provider=FakeCameraProvider())

    core.capture(authorized_request())
    snapshot = core.snapshot

    assert snapshot.capture_attempts == 1
    assert snapshot.frames_captured == 1
    assert snapshot.accepted_observations == 1
    assert snapshot.last_frame_id == "frame-m348-9"
    assert snapshot.governance.queued_observation_refs == ("frame-m348-9",)


def test_vision_capture_request_normalizes_capabilities_and_privacy():
    request = authorized_request(
        capabilities=("text_extraction", "document_understanding"),
        privacy_level="sensitive",
    )

    assert request.capabilities == (
        VisionCapability.TEXT_EXTRACTION,
        VisionCapability.DOCUMENT_UNDERSTANDING,
    )
    assert request.privacy_level.value == "sensitive"


def test_vision_capture_request_rejects_invalid_shape():
    with pytest.raises(ValueError, match="negative"):
        VisionCaptureRequest(camera_index=-1)
    with pytest.raises(ValueError, match="at least one"):
        VisionCaptureRequest(capabilities=())
    with pytest.raises(ValueError, match="unique"):
        VisionCaptureRequest(
            capabilities=("scene_description", "scene_description")
        )
