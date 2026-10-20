from __future__ import annotations

from unittest.mock import Mock

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)
from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)

from tests.test_r_visual_01c_05d_async_integration_red import (
    FakeDispatcher,
    FakeExecutor,
    FakeViewer,
)


def test_manual_close_invalidates_pending_preview():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = FakeExecutor()
    fetcher = Mock(return_value=(b"payload", "image/png"))

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=fetcher,
        executor=executor,
    )

    artifact = Mock(preview_url="https://example.org/a.png")
    coordinator.present((artifact,))

    viewer.artifacts = ()
    executor.complete(0)
    dispatcher.drain()

    assert viewer.rendered == []


def test_coordinator_can_release_executor_without_waiting():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = Mock()
    executor.shutdown = Mock()

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=Mock(),
        executor=executor,
    )

    coordinator.shutdown()

    executor.shutdown.assert_called_once_with(
        wait=False,
        cancel_futures=True,
    )


def test_viewer_replaces_old_preview_on_new_turn():
    root = object()
    toolkit = Mock()
    window = Mock()
    image = object()
    widget = Mock()

    toolkit.Toplevel.return_value = window
    toolkit.PhotoImage.return_value = image
    toolkit.Label.return_value = widget

    viewer = DesktopGovernedFloatingImageViewer(
        root=root,
        toolkit=toolkit,
    )

    first = object()
    second = object()
    payload = b"\x89PNG\r\n\x1a\nimage"

    viewer.open((first,))
    assert viewer.render_preview(first, payload, "image/png")

    viewer.open((second,))

    assert viewer.artifacts == (second,)
    assert viewer._preview_images == []
    assert viewer._preview_widgets == []
    widget.destroy.assert_called_once()
