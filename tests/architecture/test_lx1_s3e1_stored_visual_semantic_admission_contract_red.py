from __future__ import annotations

from datetime import datetime, timezone

from app.vision_core import OfficialVisionCore, StoredVisualInput
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
)


class _FailIfCameraUsed:
    def capture(self, camera_index):
        raise AssertionError("stored-image admission must not use camera")


NOW = datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
IMAGE_ID = "a" * 32
SOURCE_REF = f"stored_image:{IMAGE_ID}"


def _core() -> OfficialVisionCore:
    return OfficialVisionCore(camera_provider=_FailIfCameraUsed())


def _stored_input(*, consent: bool = True) -> StoredVisualInput:
    return StoredVisualInput(
        source_ref=SOURCE_REF,
        image_bytes=b"stored-private-image",
        mime_type="image/png",
        observed_at=NOW,
        explicit_user_consent=consent,
        user_requested=True,
    )


def test_lx1_s3e1_stored_analysis_exposes_canonical_observation_signal():
    result = _core().analyze_stored_image(object(), _stored_input())

    assert hasattr(result, "visual_observation")
    assert isinstance(result.visual_observation, VisualObservationSignal)


def test_lx1_s3e1_observation_preserves_stored_image_lineage():
    result = _core().analyze_stored_image(object(), _stored_input())

    observation = result.visual_observation
    assert observation.observation_ref == SOURCE_REF
    assert observation.source is VisualObservationSource.IMAGE_FILE
    assert observation.media_type is VisualMediaType.PHOTO


def test_lx1_s3e1_stored_private_image_remains_personal_and_local():
    result = _core().analyze_stored_image(object(), _stored_input())

    observation = result.visual_observation
    assert observation.privacy_level is VisualPrivacyLevel.PERSONAL
    assert observation.externally_supplied is False


def test_lx1_s3e1_semantic_admission_does_not_transport_image_bytes():
    result = _core().analyze_stored_image(object(), _stored_input())

    observation = result.visual_observation
    assert not hasattr(observation, "image_bytes")
    assert SOURCE_REF in observation.observation_ref


def test_lx1_s3e1_fresh_consent_blocks_before_semantic_admission():
    try:
        _core().analyze_stored_image(object(), _stored_input(consent=False))
    except PermissionError:
        pass
    else:
        raise AssertionError("stored-image semantic admission requires fresh consent")
