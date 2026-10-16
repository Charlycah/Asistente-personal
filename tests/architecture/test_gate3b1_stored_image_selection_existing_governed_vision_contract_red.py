from __future__ import annotations

import hashlib
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.vision_core import OfficialVisionCore
from app.vision_gateway import GovernedVisionGateway
from core.governed_image_repository import ImageStoreRequest
from infrastructure.camera.camera_client import CameraFrame
from infrastructure.vision.file_image_repository import FileImageRepository


class _FailIfCameraUsed:
    def capture(self, camera_index: int) -> CameraFrame:
        raise AssertionError("stored-image analysis must not capture a camera frame")


class _RecordingStoredImageCore:
    def __init__(self) -> None:
        self.calls: list[object] = []

    def analyze_stored_image(self, request: object, visual_input: object) -> object:
        self.calls.append((request, visual_input))
        return {
            "summary": "stored image analyzed",
            "source_ref": getattr(visual_input, "source_ref", ""),
        }


def _stored_image_request(owner: str = "Carlos") -> ImageStoreRequest:
    return ImageStoreRequest(
        owner=owner,
        label="Foto privada",
        tags=("gate3b1",),
        explicit_user_consent=True,
        user_requested=True,
    )


def _store_image(repository: FileImageRepository, *, owner: str = "Carlos"):
    image_bytes = b"gate3b1-private-image-bytes"
    stored = repository.store(
        _stored_image_request(owner),
        image_bytes=image_bytes,
        mime_type="image/jpeg",
    )
    return stored, image_bytes


def _read_asset(repository: FileImageRepository, image_id: str, *, owner: str):
    reader = getattr(repository, "read_asset")
    return reader(image_id, owner=owner)


def _stored_analysis_request_class():
    from app.vision_gateway import StoredImageAnalysisRequest

    return StoredImageAnalysisRequest


def test_image_repository_contract_exposes_owner_scoped_asset_read() -> None:
    from core import governed_image_repository

    source = inspect.getsource(governed_image_repository.ImageRepository)
    assert "read_asset" in source
    assert "owner" in source


def test_file_repository_reads_selected_asset_without_exposing_internal_path(
    tmp_path: Path,
) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, expected_bytes = _store_image(repository)

    asset = _read_asset(repository, stored.image_id, owner="Carlos")

    assert asset.stored_image == stored
    assert asset.image_bytes == expected_bytes
    assert not hasattr(asset, "path")
    assert not hasattr(asset, "root")


def test_file_repository_asset_read_is_owner_scoped(tmp_path: Path) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, _ = _store_image(repository, owner="Carlos")

    with pytest.raises(PermissionError, match="owner"):
        _read_asset(repository, stored.image_id, owner="Cristina")


def test_file_repository_verifies_hash_before_returning_asset(tmp_path: Path) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, _ = _store_image(repository)
    asset_path = next((tmp_path / "images" / "assets").glob(f"{stored.image_id}.*"))
    asset_path.write_bytes(b"tampered-private-image-bytes")

    with pytest.raises(ValueError, match="hash|sha256|integrity"):
        _read_asset(repository, stored.image_id, owner="Carlos")


def test_gateway_exposes_explicit_stored_image_analysis_boundary() -> None:
    assert callable(getattr(GovernedVisionGateway, "analyze_stored_image"))
    request_class = _stored_analysis_request_class()
    parameters = inspect.signature(request_class).parameters
    assert "owner" in parameters
    assert "image_id" in parameters
    assert "explicit_user_consent" in parameters
    assert "user_requested" in parameters


def test_stored_image_analysis_requires_fresh_explicit_consent(tmp_path: Path) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, _ = _store_image(repository)
    request_class = _stored_analysis_request_class()
    gateway = GovernedVisionGateway(
        vision_core=_RecordingStoredImageCore(),
        image_repository=repository,
    )
    request = request_class(
        owner="Carlos",
        image_id=stored.image_id,
        explicit_user_consent=False,
        user_requested=True,
    )

    with pytest.raises(PermissionError, match="consent"):
        gateway.analyze_stored_image(request)


def test_gateway_preserves_selected_image_provenance_and_hides_raw_bytes(
    tmp_path: Path,
) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, expected_bytes = _store_image(repository)
    request_class = _stored_analysis_request_class()
    core = _RecordingStoredImageCore()
    gateway = GovernedVisionGateway(vision_core=core, image_repository=repository)
    request = request_class(
        owner="Carlos",
        image_id=stored.image_id,
        explicit_user_consent=True,
        user_requested=True,
    )

    result = gateway.analyze_stored_image(request)

    assert result.image_id == stored.image_id
    assert result.owner == stored.owner
    assert result.sha256 == stored.sha256
    assert result.mime_type == stored.mime_type
    assert result.source_ref == f"stored_image:{stored.image_id}"
    assert not hasattr(result, "image_bytes")
    assert expected_bytes not in repr(result).encode("utf-8")
    assert core.calls


def test_official_vision_core_has_non_camera_stored_input_boundary() -> None:
    method = getattr(OfficialVisionCore, "analyze_stored_image")
    parameters = inspect.signature(method).parameters
    assert "visual_input" in parameters


def test_stored_image_analysis_does_not_use_camera_or_increment_capture_semantics(
    tmp_path: Path,
) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, _ = _store_image(repository)
    request_class = _stored_analysis_request_class()
    core = OfficialVisionCore(camera_provider=_FailIfCameraUsed())
    gateway = GovernedVisionGateway(vision_core=core, image_repository=repository)
    before = core.snapshot
    request = request_class(
        owner="Carlos",
        image_id=stored.image_id,
        explicit_user_consent=True,
        user_requested=True,
    )

    gateway.analyze_stored_image(request)

    after = core.snapshot
    assert after.capture_attempts == before.capture_attempts
    assert after.frames_captured == before.frames_captured


def test_runtime_exposes_single_private_visual_collection_builder(
    tmp_path: Path,
) -> None:
    from app import runtime_environment_wiring

    builder = getattr(
        runtime_environment_wiring, "build_vision_gateway_from_environment"
    )
    assert callable(builder)


def test_runtime_visual_builder_reuses_existing_file_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app import runtime_environment_wiring

    monkeypatch.setenv("ROBY_VISUAL_COLLECTION_ROOT", str(tmp_path / "visual"))
    gateway = runtime_environment_wiring.build_vision_gateway_from_environment()

    assert isinstance(gateway, GovernedVisionGateway)
    assert isinstance(gateway.image_repository, FileImageRepository)
    assert gateway.image_repository.root == tmp_path / "visual"


def test_contract_does_not_introduce_parallel_visual_authority() -> None:
    import app.vision_core as vision_core
    import app.vision_gateway as vision_gateway
    import core.governed_image_repository as image_repository

    core_source = inspect.getsource(vision_core)
    gateway_source = inspect.getsource(vision_gateway)
    repository_source = inspect.getsource(image_repository)

    assert core_source.count("class OfficialVisionCore") == 1
    assert gateway_source.count("class GovernedVisionGateway") == 1
    forbidden = (
        "PinacotecaManager",
        "VisualCollectionManager",
        "PersonalVisionManager",
        "SecondVisionCore",
    )
    joined = core_source + gateway_source + repository_source
    assert all(name not in joined for name in forbidden)


def test_stored_image_provenance_hash_is_content_based(tmp_path: Path) -> None:
    repository = FileImageRepository(tmp_path / "images")
    stored, image_bytes = _store_image(repository)
    assert stored.sha256 == hashlib.sha256(image_bytes).hexdigest()
    assert stored.stored_at.tzinfo is not None
    assert stored.stored_at <= datetime.now(timezone.utc)
