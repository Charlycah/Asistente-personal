from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.intelligent_vision import VisionCapability
from core.object_detection import ObjectDetection, ObjectRegion
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"transient-object-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="object-frame",
        )


class FakeObjectDetector:
    def detect(self, frame: CameraFrame) -> ObjectDetection:
        assert frame.frame_id == "object-frame"
        return ObjectDetection(
            regions=(
                ObjectRegion("keys", 0.91, 10, 20, 40, 25),
                ObjectRegion("cup", 0.84, 100, 50, 60, 90),
            ),
            detector_name="fake_local_object_detector",
        )


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.OBJECT_DETECTION,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def test_detect_objects_returns_labels_regions_and_no_source_image():
    core = OfficialVisionCore(
        camera_provider=FakeCamera(),
        object_detector=FakeObjectDetector(),
    )

    result = core.detect_objects(request())

    assert result.object_present is True
    assert result.object_count == 2
    assert [region.label for region in result.regions] == ["keys", "cup"]
    assert not hasattr(result, "image_bytes")
    assert core.snapshot.object_detection_attempts == 1
    assert core.snapshot.objects_detected == 2


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_object_detection_never_touches_camera_without_authorization(field: str):
    camera = FakeCamera()
    core = OfficialVisionCore(
        camera_provider=camera,
        object_detector=FakeObjectDetector(),
    )
    with pytest.raises(PermissionError):
        core.detect_objects(request(**{field: False}))
    assert camera.calls == 0


def test_object_detection_requires_capability_and_configured_detector():
    core = OfficialVisionCore(
        camera_provider=FakeCamera(),
        object_detector=FakeObjectDetector(),
    )
    with pytest.raises(ValueError, match="object_detection"):
        core.detect_objects(request(capabilities=(VisionCapability.FACE_DETECTION,)))
    with pytest.raises(RuntimeError, match="object detector"):
        OfficialVisionCore(camera_provider=FakeCamera()).detect_objects(request())


def test_object_region_validates_label_confidence_and_geometry():
    with pytest.raises(ValueError):
        ObjectRegion("  ", 0.8)
    with pytest.raises(ValueError):
        ObjectRegion("cup", 1.1)
    with pytest.raises(ValueError):
        ObjectRegion("cup", 0.8, x=1)
    with pytest.raises(ValueError):
        ObjectRegion("cup", 0.8, 0, 0, 0, 10)


def test_empty_object_detection_is_valid():
    result = ObjectDetection(detector_name="empty_local_detector")
    assert result.object_present is False
    assert result.object_count == 0
