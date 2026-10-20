from __future__ import annotations

from collections.abc import Callable, Sequence
from concurrent.futures import CancelledError, Executor, Future
from typing import Protocol

from app.desktop_governed_image_preview_decoder import (
    decode_governed_jpeg_preview,
)


class PreviewViewer(Protocol):
    def open(self, artifacts: tuple[object, ...]) -> None: ...

    def render_preview(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
    ) -> bool: ...


class PreviewDispatcher(Protocol):
    def post(self, callback: Callable[[], None]) -> None: ...


class PreviewArtifact(Protocol):
    @property
    def preview_url(self) -> str: ...


PreviewFetcher = Callable[[str, float, int], tuple[bytes, str]]


class GovernedImagePreviewCoordinator:
    """Coordinate bounded previews without rendering from workers."""

    def __init__(
        self,
        *,
        viewer: PreviewViewer,
        dispatcher: PreviewDispatcher,
        fetcher: PreviewFetcher,
        executor: Executor,
        timeout: float = 5.0,
        max_bytes: int = 1_000_000,
    ) -> None:
        self._viewer = viewer
        self._dispatcher = dispatcher
        self._fetcher = fetcher
        self._executor = executor
        self._timeout = timeout
        self._max_bytes = max_bytes
        self._generation = 0
        self._shutdown = False

    def cancel(self) -> None:
        """Invalidate callbacks belonging to earlier presentations."""
        self._generation += 1

    def shutdown(self) -> None:
        """Invalidate pending work and stop the executor."""
        if self._shutdown:
            return
        self._shutdown = True
        self.cancel()
        self._executor.shutdown(
            wait=False,
            cancel_futures=True,
        )

    def present(
        self,
        artifacts: Sequence[PreviewArtifact],
    ) -> None:
        """Open admitted artifacts and schedule bounded previews."""
        if self._shutdown:
            raise RuntimeError("Preview coordinator is shut down")
        supplied = tuple(artifacts)
        self.cancel()

        if not supplied:
            return

        generation = self._generation
        self._viewer.open(supplied)

        for artifact in supplied:
            future = self._executor.submit(
                self._fetch_and_prepare,
                artifact.preview_url,
                self._timeout,
                self._max_bytes,
            )
            future.add_done_callback(
                lambda completed, item=artifact, token=generation: (
                    self._schedule_result(completed, item, token)
                )
            )

    def _fetch_and_prepare(
        self,
        url: str,
        timeout: float,
        max_bytes: int,
    ) -> tuple[bytes, str] | None:
        payload, content_type = self._fetcher(url, timeout, max_bytes)
        if content_type.casefold() != "image/jpeg":
            return payload, content_type

        converted = decode_governed_jpeg_preview(payload, content_type)
        if converted is None:
            return None
        return converted, "image/png"

    def _schedule_result(
        self,
        future: Future[tuple[bytes, str] | None],
        artifact: PreviewArtifact,
        generation: int,
    ) -> None:
        try:
            result = future.result()
        except (CancelledError, OSError, ValueError, TypeError):
            return
        if result is None:
            return
        payload, content_type = result

        self._dispatcher.post(
            lambda: self._deliver(
                artifact,
                payload,
                content_type,
                generation,
            )
        )

    def _deliver(
        self,
        artifact: PreviewArtifact,
        payload: bytes,
        content_type: str,
        generation: int,
    ) -> None:
        if generation != self._generation:
            return

        if not any(item is artifact for item in self._viewer.artifacts):
            return

        self._viewer.render_preview(
            artifact,
            payload,
            content_type,
        )
