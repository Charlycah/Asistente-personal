from __future__ import annotations

from dataclasses import dataclass

from app.vision_core import (
    OfficialVisionCore,
    StoredVisualInput,
    VisionCaptureRequest,
    VisionCaptureResult,
)
from core.governed_image_repository import (
    ImageRepository,
    ImageStoreRequest,
    StoredImage,
)


@dataclass(frozen=True)
class StoredImageAnalysisRequest:
    owner: str
    image_id: str
    explicit_user_consent: bool = False
    user_requested: bool = True

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        image_id = self.image_id.strip()
        if not owner:
            raise ValueError("stored-image owner must not be blank")
        if not image_id:
            raise ValueError("stored-image id must not be blank")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "image_id", image_id)


@dataclass(frozen=True)
class StoredImageAnalysisResult:
    image_id: str
    owner: str
    sha256: str
    mime_type: str
    source_ref: str
    analysis: object


class GovernedVisionGateway:
    """Single application boundary for governed vision and image retention."""

    def __init__(
        self,
        *,
        vision_core: OfficialVisionCore,
        image_repository: ImageRepository | None = None,
    ) -> None:
        self.vision_core = vision_core
        self.image_repository = image_repository

    def capture(self, request: VisionCaptureRequest) -> VisionCaptureResult:
        return self.vision_core.capture(request)

    def analyze_stored_image(
        self, request: StoredImageAnalysisRequest
    ) -> StoredImageAnalysisResult:
        """Analyze one explicitly selected stored image through the official core."""

        if not request.explicit_user_consent:
            raise PermissionError("stored-image analysis requires explicit consent")
        if not request.user_requested:
            raise PermissionError("stored-image analysis must be explicitly requested")
        if self.image_repository is None:
            raise RuntimeError("image repository is not configured")
        asset = self.image_repository.read_asset(
            request.image_id,
            owner=request.owner,
        )
        stored = asset.stored_image
        source_ref = f"stored_image:{stored.image_id}"
        visual_input = StoredVisualInput(
            source_ref=source_ref,
            image_bytes=asset.image_bytes,
            mime_type=stored.mime_type,
            observed_at=stored.stored_at,
            explicit_user_consent=request.explicit_user_consent,
            user_requested=request.user_requested,
        )
        analysis = self.vision_core.analyze_stored_image(request, visual_input)
        return StoredImageAnalysisResult(
            image_id=stored.image_id,
            owner=stored.owner,
            sha256=stored.sha256,
            mime_type=stored.mime_type,
            source_ref=source_ref,
            analysis=analysis,
        )

    def store_image(
        self,
        request: ImageStoreRequest,
        *,
        image_bytes: bytes,
        mime_type: str,
    ) -> StoredImage:
        if self.image_repository is None:
            raise RuntimeError("image repository is not configured")
        return self.image_repository.store(
            request,
            image_bytes=image_bytes,
            mime_type=mime_type,
        )

    def get_stored_image(self, image_id: str) -> StoredImage | None:
        if self.image_repository is None:
            raise RuntimeError("image repository is not configured")
        return self.image_repository.get(image_id)

    def list_stored_images(
        self,
        *,
        owner: str | None = None,
    ) -> tuple[StoredImage, ...]:
        if self.image_repository is None:
            raise RuntimeError("image repository is not configured")
        return self.image_repository.list(owner=owner)

    def delete_stored_image(self, image_id: str) -> bool:
        if self.image_repository is None:
            raise RuntimeError("image repository is not configured")
        return self.image_repository.delete(image_id)
