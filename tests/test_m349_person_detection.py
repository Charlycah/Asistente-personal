from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.intelligent_vision import VisionCapability, VisionEventType
from core.person_detection import PersonDetection, PersonRegion
from infrastructure.camera.camera_client import CameraFrame
from infrastructure.vision import OpenCVHOGPersonDetectorConfig


class FakeCameraProvider:
    def __init__(self) -> None:
        self.indices: list[int] = []

    def capture(self, camera_index: int) -> CameraFrame:
        self.indices.append(camera_index)
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"private-person-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="frame-m349",
        )


class FakePersonDetector:
    def __init__(self, detection: PersonDetection) -> None:
        self.detection = detection
        self.frames: list[CameraFrame] = []

    def detect(self, frame: CameraFrame) -> PersonDetection:
        self.frames.append(frame)
        return self.detection


def authorized_request(**changes: object) -> VisionCaptureRequest:
    values: dict[str, object] = {
        "capabilities": (VisionCapability.OBJECT_DETECTION,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(changes)
    return VisionCaptureRequest(**values)


def person_detection() -> PersonDetection:
    return PersonDetection(
        regions=(
            PersonRegion(x=10, y=20, width=100, height=220, confidence=0.91),
            PersonRegion(x=210, y=30, width=90, height=210, confidence=0.83),
        ),
        detector_name="fake-local-detector",
    )


def test_person_detection_uses_one_authorized_frame_and_governance():
    provider = FakeCameraProvider()
    detector = FakePersonDetector(person_detection())
    core = OfficialVisionCore(
        camera_provider=provider,
        person_detector=detector,
    )

    result = core.detect_people(authorized_request(camera_index=1))

    assert provider.indices == [1]
    assert len(detector.frames) == 1
    assert result.person_present is True
    assert result.person_count == 2
    assert result.event.event_type is VisionEventType.ACCEPTED
    assert result.event.accepted_capabilities == (
        VisionCapability.OBJECT_DETECTION,
    )


def test_person_detection_result_never_exposes_raw_image_or_identity():
    core = OfficialVisionCore(
        camera_provider=FakeCameraProvider(),
        person_detector=FakePersonDetector(person_detection()),
    )

    result = core.detect_people(authorized_request())

    assert not hasattr(result, "image_bytes")
    assert not hasattr(result, "identity")
    assert not hasattr(result, "face")
    assert result.detector_name == "fake-local-detector"


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("camera_permission", "camera permission"),
        ("explicit_user_consent", "explicit vision consent"),
        ("user_requested", "explicitly requested"),
    ],
)
def test_person_detection_refuses_unauthorized_hardware_access(field, message):
    provider = FakeCameraProvider()
    detector = FakePersonDetector(person_detection())
    core = OfficialVisionCore(
        camera_provider=provider,
        person_detector=detector,
    )

    with pytest.raises(PermissionError, match=message):
        core.detect_people(authorized_request(**{field: False}))

    assert provider.indices == []
    assert detector.frames == []


def test_person_detection_requires_explicit_object_detection_capability():
    provider = FakeCameraProvider()
    core = OfficialVisionCore(
        camera_provider=provider,
        person_detector=FakePersonDetector(person_detection()),
    )

    with pytest.raises(ValueError, match="object_detection"):
        core.detect_people(
            authorized_request(capabilities=(VisionCapability.SCENE_DESCRIPTION,))
        )

    assert provider.indices == []


def test_person_detection_requires_configured_detector():
    core = OfficialVisionCore(camera_provider=FakeCameraProvider())

    with pytest.raises(RuntimeError, match="not configured"):
        core.detect_people(authorized_request())


def test_person_detection_can_report_no_person_without_false_identity_data():
    core = OfficialVisionCore(
        camera_provider=FakeCameraProvider(),
        person_detector=FakePersonDetector(
            PersonDetection(regions=(), detector_name="fake-local-detector")
        ),
    )

    result = core.detect_people(authorized_request())

    assert result.person_present is False
    assert result.person_count == 0
    assert result.regions == ()
    assert result.event.event_type is VisionEventType.ACCEPTED


def test_person_detection_snapshot_tracks_only_safe_counters():
    core = OfficialVisionCore(
        camera_provider=FakeCameraProvider(),
        person_detector=FakePersonDetector(person_detection()),
    )

    core.detect_people(authorized_request())
    snapshot = core.snapshot

    assert snapshot.capture_attempts == 1
    assert snapshot.frames_captured == 1
    assert snapshot.accepted_observations == 1
    assert snapshot.person_detection_attempts == 1
    assert snapshot.people_detected == 2
    assert snapshot.last_frame_id == "frame-m349"


def test_person_region_and_detection_validate_safe_shape():
    with pytest.raises(ValueError, match="coordinates"):
        PersonRegion(x=-1, y=0, width=1, height=1, confidence=0.8)
    with pytest.raises(ValueError, match="dimensions"):
        PersonRegion(x=0, y=0, width=0, height=1, confidence=0.8)
    with pytest.raises(ValueError, match="confidence"):
        PersonRegion(x=0, y=0, width=1, height=1, confidence=1.1)
    with pytest.raises(ValueError, match="name"):
        PersonDetection(detector_name=" ")


def test_opencv_detector_config_is_conservative_and_validated():
    config = OpenCVHOGPersonDetectorConfig()

    assert config.minimum_confidence == 0.5
    assert config.scale > 1
    with pytest.raises(ValueError, match="confidence"):
        OpenCVHOGPersonDetectorConfig(minimum_confidence=1.1)
    with pytest.raises(ValueError, match="scale"):
        OpenCVHOGPersonDetectorConfig(scale=1.0)
