"""R-VISUAL-01-F04: JPEG rendering contract."""

from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace

import pytest

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)


class FakeWindow:
    def __init__(self, root):
        self.children = []

    def title(self, value):
        pass

    def resizable(self, width, height):
        pass

    def protocol(self, name, callback):
        pass

    def destroy(self):
        pass


class FakeLabel:
    def __init__(self, parent, **kwargs):
        self.options = kwargs
        parent.children.append(self)

    def pack(self, **kwargs):
        pass

    def destroy(self):
        pass


class FakePhotoImage:
    def __init__(self, **kwargs):
        self.options = kwargs


def test_jpeg_preview_creates_image_widget():
    windows = []

    def make_window(root):
        window = FakeWindow(root)
        windows.append(window)
        return window

    toolkit = SimpleNamespace(
        Toplevel=make_window,
        Label=FakeLabel,
        PhotoImage=FakePhotoImage,
    )
    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=toolkit,
    )
    artifact = object()

    viewer.open((artifact,))

    jpeg = bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000"
    ) + b"test-jpeg-payload" + bytes.fromhex("ffd9")

    rendered = viewer.render_preview(
        artifact,
        jpeg,
        "image/jpeg",
    )

    assert rendered is True
    assert len(windows[0].children) == 1
