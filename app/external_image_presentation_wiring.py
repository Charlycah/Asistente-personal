from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

from .external_image_presentation import (
    ExternalImagePresentationArtifact,
    project_external_image,
)

PreviewPayload = tuple[bytes, str]
PreviewTransport = Callable[[str, float, int], PreviewPayload]

_SUPPORTED_IMAGE_CONTENT_TYPES = frozenset(
    {
        "image/gif",
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)


class ExternalImagePresenter(Protocol):
    def present_inline(
        self,
        artifact: ExternalImagePresentationArtifact,
    ) -> object: ...


class UIDispatcher(Protocol):
    def post(self, callback: Callable[[], None]) -> None: ...


@dataclass(frozen=True)
class ExternalImageTurnPresentation:
    text: str
    artifacts: tuple[ExternalImagePresentationArtifact, ...] = ()


@dataclass(frozen=True)
class ExternalImageTurnPresentationOutcome:
    text: str
    visual_presented: bool
    text_fallback_required: bool
    presentation_results: tuple[object, ...] = ()


class BoundedExternalImagePreviewFetcher:
    def __init__(self, *, transport: PreviewTransport) -> None:
        self._transport = transport

    def __call__(
        self,
        url: str,
        timeout: float,
        max_bytes: int,
    ) -> PreviewPayload:
        if timeout <= 0:
            raise ValueError("preview timeout must be greater than zero")
        if max_bytes <= 0:
            raise ValueError("preview byte limit must be greater than zero")
        parsed = urlparse(url)
        if parsed.scheme.casefold() != "https" or not parsed.netloc:
            raise ValueError("preview URL must use HTTPS")
        payload, content_type = self._transport(url, timeout, max_bytes)
        if len(payload) > max_bytes:
            raise ValueError("preview payload exceeds byte limit")
        normalized_content_type = content_type.partition(";")[0].strip().casefold()
        if normalized_content_type not in _SUPPORTED_IMAGE_CONTENT_TYPES:
            raise ValueError("unsupported preview content type")
        return payload, normalized_content_type


def project_governed_external_images(
    *,
    answer_text: str,
    raw_items: Sequence[Mapping[str, object]],
) -> ExternalImageTurnPresentation:
    artifacts = tuple(
        artifact
        for raw_item in raw_items
        if (artifact := project_external_image(raw_item)) is not None
    )
    return ExternalImageTurnPresentation(
        text=answer_text,
        artifacts=artifacts,
    )


def present_external_image_turn(
    presentation: ExternalImageTurnPresentation,
    presenter: ExternalImagePresenter,
) -> tuple[object, ...]:
    return tuple(
        presenter.present_inline(artifact)
        for artifact in presentation.artifacts
    )


def present_external_image_turn_safely(
    presentation: ExternalImageTurnPresentation,
    presenter: ExternalImagePresenter,
) -> ExternalImageTurnPresentationOutcome:
    results: list[object] = []
    try:
        for artifact in presentation.artifacts:
            results.append(presenter.present_inline(artifact))
    except (OSError, TypeError, ValueError):
        return ExternalImageTurnPresentationOutcome(
            text=presentation.text,
            visual_presented=False,
            text_fallback_required=True,
            presentation_results=tuple(results),
        )
    presented = bool(presentation.artifacts)
    return ExternalImageTurnPresentationOutcome(
        text=presentation.text,
        visual_presented=presented,
        text_fallback_required=not presented,
        presentation_results=tuple(results),
    )


def dispatch_external_image_render(
    dispatcher: UIDispatcher,
    callback: Callable[[], None],
) -> None:
    dispatcher.post(callback)
