from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.face_detection import FaceDetection, FaceRegion
from core.intelligent_vision import VisionCapability
from core.object_detection import ObjectDetection, ObjectRegion
from core.person_detection import PersonDetection, PersonRegion
from core.scene_understanding import DeterministicSceneAnalyzer, SceneFusion
from core.text_extraction import TextExtraction, TextRegion
from core.visual_code_detection import CodeRegion, VisualCodeDetection
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"one-transient-scene-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="scene-frame",
        )


class People:
    def detect(self, frame: CameraFrame) -> PersonDetection:
        return PersonDetection((PersonRegion(1, 2, 30, 40, 0.94),), "people")


class Faces:
    def detect(self, frame: CameraFrame) -> FaceDetection:
        return FaceDetection((FaceRegion(4, 5, 12, 12, 0.92),), "faces")


class Objects:
    def detect(self, frame: CameraFrame) -> ObjectDetection:
        return ObjectDetection(
            (
                ObjectRegion("notebook", 0.91, 20, 30, 100, 80),
                ObjectRegion("cup", 0.86, 150, 60, 40, 70),
            ),
            "objects",
        )


class Text:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        return TextExtraction(
            (TextRegion("Factura", 0.90, 2, 3, 50, 10),), "ocr", "spa"
        )


class Codes:
    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        return VisualCodeDetection((CodeRegion("123", "QR", 0.99),), "codes")


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.SCENE_DESCRIPTION,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def build_core(camera: FakeCamera | None = None) -> OfficialVisionCore:
    return OfficialVisionCore(
        camera_provider=camera or FakeCamera(),
        person_detector=People(),
        face_detector=Faces(),
        object_detector=Objects(),
        text_extractor=Text(),
        visual_code_decoder=Codes(),
    )


def test_scene_understanding_combines_existing_analyzers_from_one_frame():
    camera = FakeCamera()
    result = build_core(camera).understand_scene(request())

    assert camera.calls == 1
    assert result.scene.person_count == 1
    assert result.scene.face_count == 1
    assert result.scene.object_labels == ("notebook", "cup")
    assert result.scene.text_region_count == 1
    assert result.scene.code_types == ("QR",)
    assert "people=1" in result.scene.summary
    assert not hasattr(result, "image_bytes")


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_scene_understanding_requires_authorization_before_capture(field: str):
    camera = FakeCamera()
    with pytest.raises(PermissionError):
        build_core(camera).understand_scene(request(**{field: False}))
    assert camera.calls == 0


def test_scene_understanding_requires_capability_and_analyzer():
    with pytest.raises(ValueError, match="scene_description"):
        build_core().understand_scene(
            request(capabilities=(VisionCapability.OBJECT_DETECTION,))
        )
    with pytest.raises(RuntimeError, match="visual analyzer"):
        OfficialVisionCore(camera_provider=FakeCamera()).understand_scene(request())


def test_scene_snapshot_tracks_safe_summary_only():
    core = build_core()
    result = core.understand_scene(request())

    assert core.snapshot.scene_analysis_attempts == 1
    assert core.snapshot.scenes_analyzed == 1
    assert core.snapshot.last_scene_summary == result.scene.summary
    assert "transient-scene-frame" not in core.snapshot.last_scene_summary


def test_deterministic_analyzer_does_not_infer_activity_or_identity():
    scene = DeterministicSceneAnalyzer().analyze(
        people=PersonDetection((PersonRegion(0, 0, 10, 20, 0.9),), "people"),
        faces=None,
        objects=ObjectDetection((ObjectRegion("keyboard", 0.9),), "objects"),
        text=None,
        codes=None,
    )

    assert scene.summary == (
        "people=1;faces=0;objects=keyboard;text_regions=0;code_types=none"
    )
    forbidden = ("working", "studying", "carlos", "emotion", "intent")
    assert all(word not in scene.summary.lower() for word in forbidden)


def test_scene_understanding_model_validates_summary_and_confidence():
    with pytest.raises(ValueError):
        SceneFusion(" ", 0.9)
    with pytest.raises(ValueError):
        SceneFusion("empty scene", 1.1)
