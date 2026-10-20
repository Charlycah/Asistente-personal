from __future__ import annotations

from threading import Thread
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)


class FakeWindow:
    def __init__(self, root):
        self.root = root
        self.destroyed = False
        self.children = []
        self.callbacks = {}

    def title(self, value):
        self.window_title = value

    def resizable(self, width, height):
        self.resize_state = (width, height)

    def protocol(self, name, callback):
        self.callbacks[name] = callback

    def destroy(self):
        self.destroyed = True


class FakeLabel:
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.options = kwargs
        self.packed = False
        parent.children.append(self)

    def pack(self, **kwargs):
        self.packed = True

    def destroy(self):
        self.parent.children.remove(self)


class FakePhotoImage:
    def __init__(self, **kwargs):
        self.options = kwargs


def make_viewer():
    windows = []

    def create_window(root):
        window = FakeWindow(root)
        windows.append(window)
        return window

    toolkit = SimpleNamespace(
        Toplevel=create_window,
        Label=FakeLabel,
        PhotoImage=FakePhotoImage,
    )

    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=toolkit,
    )
    return viewer, windows


def test_png_payload_creates_visible_image_widget():
    viewer, windows = make_viewer()
    artifact = object()
    payload = (
        b"\x89PNG\r\n\x1a\n"
        b"simulated-png-payload"
    )

    viewer.open((artifact,))

    assert len(windows) == 1

    rendered = viewer.render_preview(
        artifact,
        payload,
        "image/png",
    )

    assert rendered is True
    assert len(windows[0].children) == 1
    assert windows[0].children[0].packed is True


def test_unsupported_media_does_not_claim_rendering():
    viewer, windows = make_viewer()
    artifact = object()

    viewer.open((artifact,))

    rendered = viewer.render_preview(
        artifact,
        b"jpeg-data",
        "image/jpeg",
    )

    assert rendered is False
    assert windows[0].children == []


def test_render_requires_owner_ui_thread():
    viewer, _ = make_viewer()
    viewer.open((object(),))

    errors = []

    def render_from_worker():
        try:
            viewer.render_preview(
                object(),
                b"png-data",
                "image/png",
            )
        except RuntimeError as exc:
            errors.append(str(exc))

    worker = Thread(target=render_from_worker)
    worker.start()
    worker.join(timeout=2)

    assert not worker.is_alive()
    assert len(errors) == 1
    assert "UI thread" in errors[0]


def test_close_and_reopen_do_not_retain_old_image():
    viewer, windows = make_viewer()
    artifact = object()

    viewer.open((artifact,))
    viewer.render_preview(
        artifact,
        b"\x89PNG\r\n\x1a\nsimulated",
        "image/png",
    )

    viewer.close()

    assert windows[0].destroyed is True
    assert viewer.artifacts == ()

    viewer.open((artifact,))

    assert len(windows) == 2
    assert windows[1].children == []


def test_rendering_without_open_window_is_declined():
    viewer, windows = make_viewer()

    rendered = viewer.render_preview(
        object(),
        b"\x89PNG\r\n\x1a\nsimulated",
        "image/png",
    )

    assert rendered is False
    assert windows == []
