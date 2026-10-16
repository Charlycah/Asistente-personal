from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.intelligent_vision import VisionCapability
from core.text_extraction import TextExtraction, TextRegion
from infrastructure.camera.camera_client import CameraFrame


class FakeCamera:
    def __init__(self) -> None:
        self.calls = 0

    def capture(self, camera_index: int) -> CameraFrame:
        self.calls += 1
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"transient-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="ocr-frame",
        )


class FakeTextExtractor:
    def extract(self, frame: CameraFrame) -> TextExtraction:
        assert frame.frame_id == "ocr-frame"
        return TextExtraction(
            regions=(
                TextRegion("ROBY", 0.98, 10, 20, 80, 25),
                TextRegion("XI.2", 0.96, 95, 20, 60, 25),
            ),
            extractor_name="fake_local_ocr",
            language="spa",
        )


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.TEXT_EXTRACTION,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def test_extract_text_returns_safe_text_without_source_image():
    camera = FakeCamera()
    core = OfficialVisionCore(
        camera_provider=camera,
        text_extractor=FakeTextExtractor(),
    )

    result = core.extract_text(request())

    assert result.text_present is True
    assert result.full_text == "ROBY\nXI.2"
    assert len(result.regions) == 2
    assert result.extractor_name == "fake_local_ocr"
    assert result.language == "spa"
    assert not hasattr(result, "image_bytes")
    assert core.snapshot.text_extraction_attempts == 1
    assert core.snapshot.text_regions_extracted == 2


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_extract_text_never_touches_camera_without_full_authorization(field: str):
    camera = FakeCamera()
    core = OfficialVisionCore(
        camera_provider=camera,
        text_extractor=FakeTextExtractor(),
    )

    with pytest.raises(PermissionError):
        core.extract_text(request(**{field: False}))

    assert camera.calls == 0


def test_extract_text_requires_explicit_capability():
    core = OfficialVisionCore(
        camera_provider=FakeCamera(),
        text_extractor=FakeTextExtractor(),
    )
    with pytest.raises(ValueError, match="text_extraction"):
        core.extract_text(request(capabilities=(VisionCapability.FACE_DETECTION,)))


def test_extract_text_requires_configured_extractor():
    core = OfficialVisionCore(camera_provider=FakeCamera())
    with pytest.raises(RuntimeError, match="text extractor"):
        core.extract_text(request())


def test_text_region_validates_content_confidence_and_geometry():
    with pytest.raises(ValueError):
        TextRegion("  ", 0.5)
    with pytest.raises(ValueError):
        TextRegion("text", 1.1)
    with pytest.raises(ValueError):
        TextRegion("text", 0.8, x=1)
    with pytest.raises(ValueError):
        TextRegion("text", 0.8, 0, 0, 0, 10)


def test_empty_ocr_result_is_valid_and_reports_no_text():
    extraction = TextExtraction(
        regions=(),
        extractor_name="empty_local_ocr",
        language="spa",
    )

    assert extraction.text_present is False
    assert extraction.full_text == ""
