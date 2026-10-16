from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.vision_core import OfficialVisionCore, VisionCaptureRequest
from app.vision_gateway import GovernedVisionGateway
from core.governed_image_repository import ImageCategory, ImageStoreRequest
from infrastructure.camera.camera_client import CameraFrame
from infrastructure.vision.file_image_repository import FileImageRepository


class FakeCameraProvider:
    def capture(self, camera_index: int) -> CameraFrame:
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"transient-frame",
            width=640,
            height=480,
            captured_at=datetime.now(timezone.utc),
            frame_id="frame-m362",
        )


def _gateway(tmp_path: Path) -> GovernedVisionGateway:
    return GovernedVisionGateway(
        vision_core=OfficialVisionCore(camera_provider=FakeCameraProvider()),
        image_repository=FileImageRepository(tmp_path / "images"),
    )


def _store_request(**changes: object) -> ImageStoreRequest:
    values: dict[str, object] = {
        "owner": "Carlos",
        "label": "rostro principal",
        "category": ImageCategory.PERSON_REFERENCE,
        "tags": ("persona", "rostro"),
        "explicit_user_consent": True,
        "user_requested": True,
    }
    values.update(changes)
    return ImageStoreRequest(**values)


def test_gateway_delegates_capture_to_existing_official_core(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    result = gateway.capture(
        VisionCaptureRequest(
            camera_permission=True,
            explicit_user_consent=True,
            user_requested=True,
        )
    )
    assert result.frame_id == "frame-m362"
    assert not hasattr(result, "image_bytes")


def test_gateway_stores_user_supplied_person_reference_with_metadata(
    tmp_path: Path,
) -> None:
    gateway = _gateway(tmp_path)
    stored = gateway.store_image(
        _store_request(),
        image_bytes=b"private-reference-image",
        mime_type="image/jpeg",
    )
    assert stored.owner == "Carlos"
    assert stored.category is ImageCategory.PERSON_REFERENCE
    assert stored.size_bytes == len(b"private-reference-image")
    assert gateway.get_stored_image(stored.image_id) == stored


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"explicit_user_consent": False}, "explicit user consent"),
        ({"user_requested": False}, "explicitly requested"),
    ],
)
def test_repository_refuses_implicit_image_storage(
    tmp_path: Path,
    change: dict[str, object],
    message: str,
) -> None:
    gateway = _gateway(tmp_path)
    with pytest.raises(PermissionError, match=message):
        gateway.store_image(
            _store_request(**change),
            image_bytes=b"private-reference-image",
            mime_type="image/jpeg",
        )
    assert gateway.list_stored_images() == ()


def test_repository_rejects_empty_or_unsupported_media(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    with pytest.raises(ValueError, match="must not be empty"):
        gateway.store_image(
            _store_request(),
            image_bytes=b"",
            mime_type="image/jpeg",
        )
    with pytest.raises(ValueError, match="unsupported"):
        gateway.store_image(
            _store_request(),
            image_bytes=b"image",
            mime_type="image/gif",
        )


def test_repository_lists_by_owner_and_deletes_both_artifacts(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    carlos = gateway.store_image(
        _store_request(),
        image_bytes=b"carlos-image",
        mime_type="image/png",
    )
    gateway.store_image(
        _store_request(owner="Cristina", label="referencia de Cristina"),
        image_bytes=b"cristina-image",
        mime_type="image/webp",
    )
    assert gateway.list_stored_images(owner="Carlos") == (carlos,)
    assert gateway.delete_stored_image(carlos.image_id) is True
    assert gateway.get_stored_image(carlos.image_id) is None
    assert gateway.delete_stored_image(carlos.image_id) is False


def test_person_reference_is_not_a_biometric_template(tmp_path: Path) -> None:
    gateway = _gateway(tmp_path)
    stored = gateway.store_image(
        _store_request(),
        image_bytes=b"reference-only",
        mime_type="image/jpeg",
    )
    assert not hasattr(stored, "embedding")
    assert not hasattr(stored, "biometric_template")
    assert not hasattr(stored, "identity_match")


def test_gateway_requires_configured_repository_for_retention() -> None:
    gateway = GovernedVisionGateway(
        vision_core=OfficialVisionCore(camera_provider=FakeCameraProvider())
    )
    with pytest.raises(RuntimeError, match="not configured"):
        gateway.list_stored_images()
