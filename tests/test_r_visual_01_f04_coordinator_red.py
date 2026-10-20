"""F04 integration RED: JPEG decoding remains off the UI thread."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from threading import get_ident
from types import SimpleNamespace

from PIL import Image

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)


class Viewer:
    def __init__(self):
        self.artifacts = ()
        self.received = []

    def open(self, artifacts):
        self.artifacts = tuple(artifacts)

    def render_preview(self, artifact, payload, content_type):
        self.received.append((artifact, payload, content_type, get_ident()))
        return True


class Dispatcher:
    def __init__(self):
        self.callbacks = []

    def post(self, callback):
        self.callbacks.append(callback)

    def drain(self):
        while self.callbacks:
            self.callbacks.pop(0)()


def image_bytes(image_format):
    image = Image.new("RGB", (2, 2), "red")
    output = BytesIO()
    image.save(output, format=image_format)
    return output.getvalue()


def run_case(payload, content_type):
    ui_thread = get_ident()
    artifact = SimpleNamespace(preview_url="https://example.test/a")
    viewer = Viewer()
    dispatcher = Dispatcher()
    worker_threads = []

    def fetcher(url, timeout, max_bytes):
        worker_threads.append(get_ident())
        return payload, content_type

    with ThreadPoolExecutor(max_workers=1) as executor:
        coordinator = GovernedImagePreviewCoordinator(
            viewer=viewer,
            dispatcher=dispatcher,
            fetcher=fetcher,
            executor=executor,
        )
        coordinator.present((artifact,))
        executor.submit(lambda: None).result()

    dispatcher.drain()
    return viewer.received, worker_threads, ui_thread


def test_jpeg_reaches_viewer_as_png():
    received, workers, ui_thread = run_case(image_bytes("JPEG"), "image/jpeg")
    assert len(received) == 1
    _, payload, content_type, render_thread = received[0]
    assert content_type == "image/png"
    assert payload.startswith(bytes.fromhex("89504e470d0a1a0a"))
    assert workers and all(t != ui_thread for t in workers)
    assert render_thread == ui_thread


def test_corrupt_jpeg_is_not_delivered():
    received, _, _ = run_case(bytes.fromhex("ffd8") + b"invalid", "image/jpeg")
    assert received == []


def test_png_passthrough():
    original = image_bytes("PNG")
    received, _, _ = run_case(original, "image/png")
    assert len(received) == 1
    assert received[0][1] == original
    assert received[0][2] == "image/png"
