"""RED contracts for bounded, scrollable image gallery."""

from __future__ import annotations

from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)


def make_png(width: int = 1200, height: int = 900) -> bytes:
    image = Image.new("RGB", (width, height), "orange")
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def make_viewer():
    toolkit = Mock()
    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=toolkit,
    )
    return viewer, toolkit


def test_large_image_is_bounded_before_tk_rendering():
    viewer, toolkit = make_viewer()
    artifact = SimpleNamespace(preview_url="https://example.test/a.png")

    viewer.open((artifact,))
    assert viewer.render_preview(
        artifact,
        make_png(1200, 900),
        "image/png",
    )

    kwargs = toolkit.PhotoImage.call_args.kwargs
    image = Image.open(BytesIO(kwargs["data"]))

    assert image.width <= 400
    assert image.height <= 300
    assert image.size == (400, 300)


def test_gallery_creates_scrollable_region():
    viewer, toolkit = make_viewer()
    artifact = SimpleNamespace(preview_url="https://example.test/a.png")

    viewer.open((artifact,))

    assert toolkit.Canvas.call_count == 1
    assert toolkit.Scrollbar.call_count == 1

    canvas = toolkit.Canvas.return_value
    scrollbar = toolkit.Scrollbar.return_value

    assert canvas.create_window.call_count >= 1
    assert canvas.configure.call_count >= 1
    assert scrollbar.configure.call_count >= 1


def test_multiple_images_share_scrollable_gallery():
    viewer, toolkit = make_viewer()
    artifacts = (
        SimpleNamespace(preview_url="https://example.test/a.png"),
        SimpleNamespace(preview_url="https://example.test/b.png"),
    )

    viewer.open(artifacts)

    for artifact in artifacts:
        assert viewer.render_preview(
            artifact,
            make_png(),
            "image/png",
        )

    assert toolkit.Canvas.call_count == 1
    assert toolkit.Scrollbar.call_count == 1
    assert toolkit.Label.call_count == 2


def test_gallery_registers_mouse_wheel_scrolling():
    viewer, toolkit = make_viewer()
    viewer.open((object(),))

    canvas = toolkit.Canvas.return_value
    calls = canvas.bind.call_args_list

    sequences = [call.args[0] for call in calls if call.args]

    assert "<MouseWheel>" in sequences
