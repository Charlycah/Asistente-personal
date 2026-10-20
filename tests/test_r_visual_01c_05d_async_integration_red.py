from __future__ import annotations

from concurrent.futures import Future
from unittest.mock import Mock

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)


class FakeDispatcher:
    def __init__(self):
        self.pending = []

    def post(self, callback):
        self.pending.append(callback)

    def drain(self):
        while self.pending:
            self.pending.pop(0)()


class FakeViewer:
    def __init__(self):
        self.artifacts = ()
        self.rendered = []
        self.open_calls = 0

    def open(self, artifacts):
        self.artifacts = tuple(artifacts)
        self.open_calls += 1

    def render_preview(self, artifact, payload, content_type):
        if artifact not in self.artifacts:
            return False
        self.rendered.append((artifact, payload, content_type))
        return True


class FakeExecutor:
    def __init__(self):
        self.jobs = []

    def submit(self, callback, *args):
        future = Future()
        self.jobs.append((callback, args, future))
        return future

    def complete(self, index):
        callback, args, future = self.jobs[index]
        try:
            future.set_result(callback(*args))
        except Exception as exc:
            future.set_exception(exc)


def make_coordinator():
    viewer = FakeViewer()
    dispatcher = FakeDispatcher()
    executor = FakeExecutor()
    fetcher = Mock(return_value=(b"png-data", "image/png"))

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=fetcher,
        executor=executor,
    )
    return coordinator, viewer, dispatcher, executor, fetcher


def test_fetch_does_not_run_on_ui_thread():
    coordinator, viewer, dispatcher, executor, fetcher = (
        make_coordinator()
    )
    artifact = Mock(preview_url="https://example.org/a.png")

    coordinator.present((artifact,))

    assert viewer.open_calls == 1
    assert len(executor.jobs) == 1
    fetcher.assert_not_called()

    executor.complete(0)
    dispatcher.drain()

    fetcher.assert_called_once()
    assert viewer.rendered == [
        (artifact, b"png-data", "image/png")
    ]


def test_old_turn_result_is_discarded():
    coordinator, viewer, dispatcher, executor, _ = (
        make_coordinator()
    )
    first = Mock(preview_url="https://example.org/first.png")
    second = Mock(preview_url="https://example.org/second.png")

    coordinator.present((first,))
    coordinator.present((second,))

    executor.complete(0)
    dispatcher.drain()

    assert viewer.rendered == []

    executor.complete(1)
    dispatcher.drain()

    assert viewer.rendered == [
        (second, b"png-data", "image/png")
    ]


def test_closed_viewer_does_not_reopen_from_late_result():
    coordinator, viewer, dispatcher, executor, _ = (
        make_coordinator()
    )
    artifact = Mock(preview_url="https://example.org/a.png")

    coordinator.present((artifact,))
    coordinator.cancel()

    executor.complete(0)
    dispatcher.drain()

    assert viewer.open_calls == 1
    assert viewer.rendered == []


def test_transport_failure_does_not_claim_presentation():
    coordinator, viewer, dispatcher, executor, fetcher = (
        make_coordinator()
    )
    artifact = Mock(preview_url="https://example.org/a.png")
    fetcher.side_effect = ValueError("transport rejected")

    coordinator.present((artifact,))
    executor.complete(0)
    dispatcher.drain()

    assert viewer.rendered == []
