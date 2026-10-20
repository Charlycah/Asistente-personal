from __future__ import annotations

from concurrent.futures import CancelledError, Future
from dataclasses import dataclass
from unittest.mock import patch
from unittest.mock import Mock

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)


@dataclass(frozen=True)
class Artifact:
    preview_url: str


class FakeViewer:
    def __init__(self) -> None:
        self.artifacts: tuple[object, ...] = ()
        self.rendered: list[object] = []

    def open(self, artifacts: tuple[object, ...]) -> None:
        self.artifacts = artifacts

    def close(self) -> None:
        self.artifacts = ()

    def render_preview(
        self,
        artifact: object,
        payload: bytes,
        content_type: str,
    ) -> bool:
        self.rendered.append(artifact)
        return True


class FakeDispatcher:
    def __init__(self) -> None:
        self.callbacks: list[object] = []

    def post(self, callback: object) -> None:
        self.callbacks.append(callback)

    def drain(self) -> None:
        callbacks = self.callbacks[:]
        self.callbacks.clear()
        for callback in callbacks:
            callback()


class FakeExecutor:
    def __init__(self) -> None:
        self.futures: list[Future[tuple[bytes, str]]] = []
        self.shutdown_calls: list[tuple[bool, bool]] = []

    def submit(self, *args: object) -> Future[tuple[bytes, str]]:
        future: Future[tuple[bytes, str]] = Future()
        self.futures.append(future)
        return future

    def shutdown(
        self,
        wait: bool,
        cancel_futures: bool,
    ) -> None:
        self.shutdown_calls.append((wait, cancel_futures))
        if cancel_futures:
            for future in self.futures:
                future.cancel()


def _coordinator(
    viewer: FakeViewer,
    dispatcher: FakeDispatcher,
    executor: FakeExecutor,
) -> GovernedImagePreviewCoordinator:
    return GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=Mock(),
        executor=executor,
    )


def test_shutdown_handles_cancelled_future_without_callback_error():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = FakeExecutor()
    coordinator = _coordinator(viewer, dispatcher, executor)

    coordinator.present((Artifact("https://example.org/a.png"),))

    future = executor.futures[0]

    with patch(
        "concurrent.futures._base.LOGGER.exception"
    ) as logged_exception:
        coordinator.shutdown()

    logged_exception.assert_not_called()
    assert future.cancelled()
    assert executor.shutdown_calls == [(False, True)]
    assert dispatcher.callbacks == []
    assert viewer.rendered == []


def test_manual_close_then_reopen_rejects_old_preview():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = FakeExecutor()
    coordinator = _coordinator(viewer, dispatcher, executor)

    first = Artifact("https://example.org/first.png")
    second = Artifact("https://example.org/second.png")

    coordinator.present((first,))
    old_future = executor.futures[0]

    viewer.close()

    coordinator.present((second,))
    new_future = executor.futures[1]

    old_future.set_result((b"old", "image/png"))
    new_future.set_result((b"new", "image/png"))

    dispatcher.drain()

    assert viewer.artifacts == (second,)
    assert viewer.rendered == [second]


def test_shutdown_invalidates_completed_queued_delivery():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = FakeExecutor()
    coordinator = _coordinator(viewer, dispatcher, executor)

    artifact = Artifact("https://example.org/a.png")
    coordinator.present((artifact,))

    executor.futures[0].set_result((b"preview", "image/png"))

    assert len(dispatcher.callbacks) == 1

    coordinator.shutdown()
    dispatcher.drain()

    assert viewer.rendered == []
