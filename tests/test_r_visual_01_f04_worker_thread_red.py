"""Verify governed JPEG decoding executes outside the UI thread."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import get_ident
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)
from app.desktop_governed_image_preview_decoder import (
    decode_governed_jpeg_preview,
)


def test_jpeg_decoder_runs_on_worker_thread():
    ui_thread = get_ident()
    decoder_threads = []
    callbacks = []

    image = Image.new("RGB", (2, 2), "red")
    stream = BytesIO()
    image.save(stream, format="JPEG")
    jpeg = stream.getvalue()

    artifact = SimpleNamespace(preview_url="https://example.test/image")

    class Viewer:
        artifacts = ()

        def open(self, artifacts):
            self.artifacts = tuple(artifacts)

        def render_preview(self, item, payload, content_type):
            assert get_ident() == ui_thread
            assert item is artifact
            assert content_type == "image/png"
            assert payload.startswith(bytes.fromhex("89504e470d0a1a0a"))
            return True

    class Dispatcher:
        def post(self, callback):
            callbacks.append(callback)

    def fetcher(url, timeout, max_bytes):
        return jpeg, "image/jpeg"

    def observed_decoder(payload, content_type):
        decoder_threads.append(get_ident())
        return decode_governed_jpeg_preview(payload, content_type)

    with patch(
        "app.desktop_governed_image_preview_coordinator.decode_governed_jpeg_preview",
        side_effect=observed_decoder,
    ):
        with ThreadPoolExecutor(max_workers=1) as executor:
            coordinator = GovernedImagePreviewCoordinator(
                viewer=Viewer(),
                dispatcher=Dispatcher(),
                fetcher=fetcher,
                executor=executor,
            )
            coordinator.present((artifact,))
            executor.submit(lambda: None).result()

    assert len(decoder_threads) == 1
    assert decoder_threads[0] != ui_thread
    assert len(callbacks) == 1

    callbacks.pop(0)()
