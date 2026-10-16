from __future__ import annotations

from datetime import datetime, timezone

from app.runtime_environment_wiring import build_vision_gateway_from_environment
from app.vision_core import OfficialVisionCore, StoredVisualInput
from core.person_detection import PersonDetection
from core.scene_understanding import SceneFusion
from infrastructure.camera.camera_client import CameraFrame
from infrastructure.vision import (
    OpenCVCascadeFaceDetector,
    OpenCVHOGPersonDetector,
    PyzbarVisualCodeDecoder,
    TesseractTextExtractor,
)

NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
IMAGE_ID = "b" * 32
SOURCE_REF = f"stored_image:{IMAGE_ID}"


class _FailIfCameraUsed:
    def capture(self, camera_index):
        raise AssertionError("stored-image perception must not capture camera input")


class _RecordingPersonDetector:
    def __init__(self) -> None:
        self.frames: list[CameraFrame] = []

    def detect(self, frame: CameraFrame) -> PersonDetection:
        self.frames.append(frame)
        return PersonDetection(regions=(), detector_name="recording_person_detector")


def _stored_input() -> StoredVisualInput:
    return StoredVisualInput(
        source_ref=SOURCE_REF,
        image_bytes=b"stored-private-image",
        mime_type="image/png",
        observed_at=NOW,
        explicit_user_consent=True,
        user_requested=True,
    )


def test_lx1_s3e2b_stored_image_reuses_existing_perceptual_analyzers():
    detector = _RecordingPersonDetector()
    core = OfficialVisionCore(
        camera_provider=_FailIfCameraUsed(),
        person_detector=detector,
    )

    result = core.analyze_stored_image(object(), _stored_input())

    assert len(detector.frames) == 1
    assert isinstance(result.perceptual_scene, SceneFusion)


def test_lx1_s3e2b_stored_perception_uses_neutral_frame_with_lineage():
    detector = _RecordingPersonDetector()
    core = OfficialVisionCore(
        camera_provider=_FailIfCameraUsed(),
        person_detector=detector,
    )

    core.analyze_stored_image(object(), _stored_input())

    frame = detector.frames[0]
    assert isinstance(frame, CameraFrame)
    assert frame.frame_id == SOURCE_REF
    assert frame.image_bytes == b"stored-private-image"
    assert frame.captured_at == NOW


def test_lx1_s3e2b_stored_perception_never_invokes_camera_capture():
    detector = _RecordingPersonDetector()
    core = OfficialVisionCore(
        camera_provider=_FailIfCameraUsed(),
        person_detector=detector,
    )

    core.analyze_stored_image(object(), _stored_input())

    assert detector.frames


def test_lx1_s3e2b_runtime_provisions_existing_local_analyzers(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_VISUAL_COLLECTION_ROOT", str(tmp_path / "visual"))

    gateway = build_vision_gateway_from_environment()
    core = gateway.vision_core

    assert isinstance(core.person_detector, OpenCVHOGPersonDetector)
    assert isinstance(core.face_detector, OpenCVCascadeFaceDetector)
    assert isinstance(core.text_extractor, TesseractTextExtractor)
    assert isinstance(core.visual_code_decoder, PyzbarVisualCodeDecoder)


def test_lx1_s3e2b_contract_reuses_canonical_vision_core_only():
    core = OfficialVisionCore(
        camera_provider=_FailIfCameraUsed(),
        person_detector=_RecordingPersonDetector(),
    )

    result = core.analyze_stored_image(object(), _stored_input())

    assert not hasattr(result, "reasoning")
    assert not hasattr(result, "cognitive_runtime")
    assert not hasattr(result, "image_bytes")
