from concurrent.futures import Future
from types import SimpleNamespace

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
    VisualCommitReceipt,
)


class ManualExecutor:
    def __init__(self):
        self.jobs = []

    def submit(self, fn, *args):
        future = Future()
        self.jobs.append((future, fn, args))
        return future

    def complete(self, index):
        future, fn, args = self.jobs[index]
        try:
            future.set_result(fn(*args))
        except Exception as exc:
            future.set_exception(exc)

    def shutdown(self, **kwargs):
        pass


class Dispatcher:
    def __init__(self):
        self.queue = []

    def post(self, callback):
        self.queue.append(callback)

    def drain(self):
        while self.queue:
            self.queue.pop(0)()


class VICViewer:
    def __init__(self):
        self.artifacts = ()
        self.vic_calls = []
        self.legacy_calls = []
        self.accept = True

    def open(self, artifacts):
        self.artifacts = artifacts

    def render_preview(self, artifact, payload, content_type):
        self.legacy_calls.append(artifact)
        return True

    def render_preview_vic(
        self, artifact, payload, content_type, *, visible_ordinal
    ):
        self.vic_calls.append((artifact, visible_ordinal))
        return self.accept


class LegacyViewer:
    def __init__(self):
        self.artifacts = ()
        self.calls = []

    def open(self, artifacts):
        self.artifacts = artifacts

    def render_preview(self, artifact, payload, content_type):
        self.calls.append(artifact)
        return True


def setup(viewer=None, vic_enabled=True):
    viewer = viewer if viewer is not None else VICViewer()
    dispatcher = Dispatcher()
    executor = ManualExecutor()
    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        executor=executor,
        fetcher=lambda *_: (b"png", "image/png"),
        vic_enabled=vic_enabled,
    )
    return coordinator, viewer, dispatcher, executor


def artifacts(count):
    return tuple(
        SimpleNamespace(preview_url=f"https://example.test/{i}")
        for i in range(count)
    )


def deliver(executor, dispatcher, *indices):
    for index in indices:
        executor.complete(index)
    dispatcher.drain()


def test_vic_individual_ordinals_and_receipts():
    coordinator, viewer, dispatcher, executor = setup()
    supplied = artifacts(3)
    coordinator.present(supplied)

    deliver(executor, dispatcher, 2, 0, 1)

    assert [ordinal for _, ordinal in viewer.vic_calls] == [3, 1, 2]
    assert not viewer.legacy_calls

    receipts = coordinator.active_vic_receipts
    assert len(receipts) == 3
    assert all(isinstance(r, VisualCommitReceipt) for r in receipts)
    assert sorted(r.visible_ordinal for r in receipts) == [1, 2, 3]
    assert all(r.generation_token == 1 for r in receipts)
    assert all(r.state == "DELIVERED" for r in coordinator.results)


def test_vic_rejection_does_not_emit_receipt():
    coordinator, viewer, dispatcher, executor = setup()
    viewer.accept = False

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert coordinator.results[0].state == "REJECTED"
    assert not coordinator.vic_receipts


def test_vic_missing_operation_fails_without_legacy_fallback():
    coordinator, viewer, dispatcher, executor = setup(
        viewer=LegacyViewer()
    )

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert coordinator.results[0].state == "FAILED"
    assert coordinator.results[0].reason == "render_failed"
    assert not viewer.calls
    assert not coordinator.vic_receipts


def test_legacy_mode_preserves_original_delivery():
    coordinator, viewer, dispatcher, executor = setup(
        viewer=LegacyViewer(),
        vic_enabled=False,
    )

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert coordinator.results[0].state == "DELIVERED"
    assert len(viewer.calls) == 1
    assert not coordinator.vic_receipts


def test_cancel_invalidates_active_receipts():
    coordinator, viewer, dispatcher, executor = setup()

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)
    assert len(coordinator.active_vic_receipts) == 1

    coordinator.cancel()

    assert not coordinator.active_vic_receipts
    assert len(coordinator.vic_receipts) == 1


def test_supersede_preserves_history_but_not_active_receipts():
    coordinator, viewer, dispatcher, executor = setup()

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)
    previous = coordinator.vic_receipts[0]

    coordinator.present(artifacts(1))

    assert not coordinator.active_vic_receipts
    assert coordinator.vic_receipts == (previous,)


def test_late_delivery_cannot_create_vic_receipt():
    coordinator, viewer, dispatcher, executor = setup()

    coordinator.present(artifacts(1))
    executor.complete(0)
    coordinator.cancel()
    dispatcher.drain()

    assert not viewer.vic_calls
    assert not coordinator.vic_receipts


# PKG02-VIC-VIEWER-ATOMICITY-TESTS

from tests.test_r_visual_01c_05b_viewer_render_red import make_viewer


PNG_PAYLOAD = b"\x89PNG\r\n\x1a\nsimulated-png-payload"


def test_vic_visual_unit_contains_image_and_ordinal():
    viewer, windows = make_viewer()
    artifact = object()
    viewer.open((artifact,))

    accepted = viewer.render_preview_vic(
        artifact, PNG_PAYLOAD, "image/png",
        visible_ordinal=4,
    )

    assert accepted is True
    assert len(windows[0].children) == 1

    widget = windows[0].children[0]
    assert widget.packed is True
    assert widget.options["text"] == "4"
    assert widget.options["compound"] == "top"
    assert widget.options["image"] is not None


def test_vic_rejects_invalid_png_without_widget():
    viewer, windows = make_viewer()
    artifact = object()
    viewer.open((artifact,))

    accepted = viewer.render_preview_vic(
        artifact, b"not-a-png", "image/png",
        visible_ordinal=1,
    )

    assert accepted is False
    assert windows[0].children == []


def test_vic_rejects_invalid_ordinal_without_widget():
    viewer, windows = make_viewer()
    artifact = object()
    viewer.open((artifact,))

    for ordinal in (0, -1, True, "1"):
        accepted = viewer.render_preview_vic(
            artifact, PNG_PAYLOAD, "image/png",
            visible_ordinal=ordinal,
        )
        assert accepted is False

    assert windows[0].children == []


def test_vic_rejects_artifact_outside_presentation():
    viewer, windows = make_viewer()
    viewer.open((object(),))

    accepted = viewer.render_preview_vic(
        object(), PNG_PAYLOAD, "image/png",
        visible_ordinal=1,
    )

    assert accepted is False
    assert windows[0].children == []


def test_vic_rejects_rendering_without_open_window():
    viewer, _ = make_viewer()

    accepted = viewer.render_preview_vic(
        object(), PNG_PAYLOAD, "image/png",
        visible_ordinal=1,
    )

    assert accepted is False
    assert not viewer._preview_widgets
