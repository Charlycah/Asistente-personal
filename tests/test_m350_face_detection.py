from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.face_detection import FaceDetection, FaceRegion
from core.intelligent_vision import VisionCapability
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="face-frame",
        )


class FakeFaceDetector:
    def detect(self, frame: CameraFrame) -> FaceDetection:
        assert frame.frame_id == "face-frame"
        return FaceDetection(
            regions=(FaceRegion(10, 20, 100, 120, 0.95),),
            detector_name="fake_local_face_locator",
        )


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.FACE_DETECTION,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def test_detect_faces_returns_only_safe_location_metadata():
    camera = FakeCamera()
    core = OfficialVisionCore(camera_provider=camera, face_detector=FakeFaceDetector())

    result = core.detect_faces(request())

    assert result.face_present is True
    assert result.face_count == 1
    assert result.regions == (FaceRegion(10, 20, 100, 120, 0.95),)
    assert result.detector_name == "fake_local_face_locator"
    assert not hasattr(result, "image_bytes")
    assert not hasattr(result, "identity")
    assert core.snapshot.face_detection_attempts == 1
    assert core.snapshot.faces_detected == 1


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_detect_faces_never_touches_camera_without_full_authorization(field: str):
    camera = FakeCamera()
    core = OfficialVisionCore(camera_provider=camera, face_detector=FakeFaceDetector())

    with pytest.raises(PermissionError):
        core.detect_faces(request(**{field: False}))

    assert camera.calls == 0


def test_detect_faces_requires_explicit_capability():
    core = OfficialVisionCore(
        camera_provider=FakeCamera(), face_detector=FakeFaceDetector()
    )
    with pytest.raises(ValueError, match="face_detection"):
        core.detect_faces(request(capabilities=(VisionCapability.OBJECT_DETECTION,)))


def test_detect_faces_requires_configured_detector():
    core = OfficialVisionCore(camera_provider=FakeCamera())
    with pytest.raises(RuntimeError, match="face detector"):
        core.detect_faces(request())


def test_face_region_validates_geometry_and_confidence():
    with pytest.raises(ValueError):
        FaceRegion(-1, 0, 10, 10, 0.5)
    with pytest.raises(ValueError):
        FaceRegion(0, 0, 0, 10, 0.5)
    with pytest.raises(ValueError):
        FaceRegion(0, 0, 10, 10, 1.1)
