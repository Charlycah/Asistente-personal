from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

from .external_image_presentation import ExternalImagePresentationArtifact

PreviewPayload = tuple[bytes, str]
PreviewFetcher = Callable[[str, float, int], PreviewPayload]
InlineRenderer = Callable[[ExternalImagePresentationArtifact, bytes], bool]
GalleryRenderer = Callable[[Sequence[ExternalImagePresentationArtifact]], bool]
DetailRenderer = Callable[[ExternalImagePresentationArtifact], bool]

_SUPPORTED_IMAGE_CONTENT_TYPES = frozenset(
    {
        "image/gif",
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)


@dataclass(frozen=True)
class DesktopExternalImagePresenterConfig:
    preview_timeout_seconds: float = 5.0
    max_preview_bytes: int = 1_000_000

    def __post_init__(self) -> None:
        if self.preview_timeout_seconds <= 0:
            raise ValueError("preview timeout must be greater than zero")
        if self.max_preview_bytes <= 0:
            raise ValueError("preview byte limit must be greater than zero")


@dataclass(frozen=True)
class ExternalImagePresentationResult:
    artifact: ExternalImagePresentationArtifact | None
    presented: bool
    surface: str | None
    text_fallback_required: bool
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.presented and self.surface is not None:
            raise ValueError("unpresented external image cannot claim a surface")
        if self.presented and self.surface is None:
            raise ValueError("presented external image must identify its surface")


class DesktopExternalImagePresenter:
    def __init__(
        self,
        *,
        config: DesktopExternalImagePresenterConfig | None = None,
        preview_fetcher: PreviewFetcher | None = None,
        inline_renderer: InlineRenderer | None = None,
        gallery_renderer: GalleryRenderer | None = None,
        detail_renderer: DetailRenderer | None = None,
    ) -> None:
        self._config = config or DesktopExternalImagePresenterConfig()
        self._preview_fetcher = preview_fetcher
        self._inline_renderer = inline_renderer
        self._gallery_renderer = gallery_renderer
        self._detail_renderer = detail_renderer

    def present_inline(
        self,
        artifact: ExternalImagePresentationArtifact,
    ) -> ExternalImagePresentationResult:
        if self._preview_fetcher is None or self._inline_renderer is None:
            return _fallback(artifact, "preview_presentation_unavailable")
        try:
            payload, content_type = self._preview_fetcher(
                artifact.preview_url,
                self._config.preview_timeout_seconds,
                self._config.max_preview_bytes,
            )
        except (OSError, ValueError, TypeError):
            return _fallback(artifact, "preview_unavailable")
        if content_type.casefold() not in _SUPPORTED_IMAGE_CONTENT_TYPES:
            return _fallback(artifact, "unsupported_preview_content_type")
        if len(payload) > self._config.max_preview_bytes:
            return _fallback(artifact, "preview_size_limit_exceeded")
        try:
            presented = bool(self._inline_renderer(artifact, payload))
        except (OSError, ValueError, TypeError):
            return _fallback(artifact, "inline_renderer_failed")
        if not presented:
            return _fallback(artifact, "inline_renderer_declined")
        return ExternalImagePresentationResult(
            artifact=artifact,
            presented=True,
            surface="inline_image",
            text_fallback_required=False,
            rationale=("external_image_presented",),
        )

    def present_gallery(
        self,
        artifacts: Sequence[ExternalImagePresentationArtifact],
    ) -> ExternalImagePresentationResult:
        candidates = tuple(artifacts)
        representative = candidates[0] if candidates else None
        if not candidates or self._gallery_renderer is None:
            return _fallback(representative, "gallery_presentation_unavailable")
        try:
            presented = bool(self._gallery_renderer(candidates))
        except (OSError, ValueError, TypeError):
            return _fallback(representative, "gallery_renderer_failed")
        if not presented:
            return _fallback(representative, "gallery_renderer_declined")
        return ExternalImagePresentationResult(
            artifact=representative,
            presented=True,
            surface="image_gallery",
            text_fallback_required=False,
            rationale=("external_image_gallery_presented",),
        )

    def present_detail(
        self,
        artifact: ExternalImagePresentationArtifact,
    ) -> ExternalImagePresentationResult:
        if self._detail_renderer is None:
            return _fallback(artifact, "detail_presentation_unavailable")
        try:
            presented = bool(self._detail_renderer(artifact))
        except (OSError, ValueError, TypeError):
            return _fallback(artifact, "detail_renderer_failed")
        if not presented:
            return _fallback(artifact, "detail_renderer_declined")
        return ExternalImagePresentationResult(
            artifact=artifact,
            presented=True,
            surface="image_detail",
            text_fallback_required=False,
            rationale=("external_image_detail_presented",),
        )


def _fallback(
    artifact: ExternalImagePresentationArtifact | None,
    reason: str,
) -> ExternalImagePresentationResult:
    return ExternalImagePresentationResult(
        artifact=artifact,
        presented=False,
        surface=None,
        text_fallback_required=True,
        rationale=(reason,),
    )
