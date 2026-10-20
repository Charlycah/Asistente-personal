from concurrent.futures import Future
from dataclasses import dataclass
from unittest.mock import Mock

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)
from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)


PNG = bytes.fromhex("89504e470d0a1a0a") + b"image"


@dataclass(frozen=True)
class Artifact:
    preview_url: str


class ControlledExecutor:
    def __init__(self):
        self.futures = []

    def submit(self, *args):
        future = Future()
        self.futures.append(future)
        return future

    def shutdown(self, *, wait, cancel_futures):
        if cancel_futures:
            for future in self.futures:
                future.cancel()


class ControlledDispatcher:
    def __init__(self):
        self.callbacks = []

    def post(self, callback):
        self.callbacks.append(callback)

    def drain(self):
        callbacks = self.callbacks[:]
        self.callbacks.clear()
        for callback in callbacks:
            callback()


def test_real_viewer_close_rejects_late_preview_and_allows_reopen():
    toolkit = Mock()
    dispatcher = ControlledDispatcher()
    executor = ControlledExecutor()
    holder = {}

    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=toolkit,
        on_close=lambda: holder["coordinator"].cancel(),
    )

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=Mock(),
        executor=executor,
    )
    holder["coordinator"] = coordinator

    first = Artifact("https://example.org/first.png")
    second = Artifact("https://example.org/second.png")

    coordinator.present((first,))
    old_future = executor.futures[0]

    window = toolkit.Toplevel.return_value
    close_callback = window.protocol.call_args.args[1]
    close_callback()

    assert viewer.artifacts == ()
    assert window.destroy.call_count == 1

    old_future.set_result((PNG, "image/png"))
    dispatcher.drain()

    assert toolkit.PhotoImage.call_count == 0
    assert toolkit.Label.call_count == 0

    coordinator.present((second,))
    new_future = executor.futures[1]
    new_future.set_result((PNG, "image/png"))
    dispatcher.drain()

    assert viewer.artifacts == (second,)
    assert toolkit.PhotoImage.call_count == 1
    assert toolkit.Label.call_count == 1
    assert len(viewer._preview_images) == 1
