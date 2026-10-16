from datetime import datetime, timezone

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from core.intelligent_vision import VisionCapability
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
            image_bytes=b"transient-code-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="code-frame",
        )


class FakeDecoder:
    def decode(self, frame: CameraFrame) -> VisualCodeDetection:
        assert frame.frame_id == "code-frame"
        return VisualCodeDetection(
            regions=(
                CodeRegion("https://example.invalid", "QRCODE", 1.0, 1, 2, 30, 30),
                CodeRegion("7791234567890", "EAN13", 1.0, 40, 2, 80, 25),
            ),
            decoder_name="fake_local_decoder",
        )


def request(**overrides: object) -> VisionCaptureRequest:
    values = {
        "capabilities": (VisionCapability.CODE_DECODING,),
        "camera_permission": True,
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(overrides)
    return VisionCaptureRequest(**values)


def test_decode_visual_codes_returns_safe_content_without_source_image():
    camera = FakeCamera()
    core = OfficialVisionCore(
        camera_provider=camera,
        visual_code_decoder=FakeDecoder(),
    )

    result = core.decode_visual_codes(request())

    assert result.code_present is True
    assert result.code_count == 2
    assert result.regions[0].code_type == "QRCODE"
    assert result.regions[1].content == "7791234567890"
    assert not hasattr(result, "image_bytes")
    assert core.snapshot.code_decoding_attempts == 1
    assert core.snapshot.codes_decoded == 2


@pytest.mark.parametrize(
    "field",
    ["camera_permission", "explicit_user_consent", "user_requested"],
)
def test_decode_never_touches_camera_without_full_authorization(field: str):
    camera = FakeCamera()
    core = OfficialVisionCore(
        camera_provider=camera,
        visual_code_decoder=FakeDecoder(),
    )
    with pytest.raises(PermissionError):
        core.decode_visual_codes(request(**{field: False}))
    assert camera.calls == 0


def test_decode_requires_explicit_capability_and_configured_decoder():
    core = OfficialVisionCore(
        camera_provider=FakeCamera(),
        visual_code_decoder=FakeDecoder(),
    )
    with pytest.raises(ValueError, match="code_decoding"):
        core.decode_visual_codes(
            request(capabilities=(VisionCapability.TEXT_EXTRACTION,))
        )
    with pytest.raises(RuntimeError, match="visual code decoder"):
        OfficialVisionCore(camera_provider=FakeCamera()).decode_visual_codes(request())


def test_code_region_validates_content_type_confidence_and_geometry():
    with pytest.raises(ValueError):
        CodeRegion("  ", "QR")
    with pytest.raises(ValueError):
        CodeRegion("value", "  ")
    with pytest.raises(ValueError):
        CodeRegion("value", "QR", 1.1)
    with pytest.raises(ValueError):
        CodeRegion("value", "QR", x=1)
    with pytest.raises(ValueError):
        CodeRegion("value", "QR", 1.0, 0, 0, 0, 10)


def test_empty_code_result_is_valid_and_reports_no_code():
    result = VisualCodeDetection(decoder_name="empty_decoder")
    assert result.code_present is False
