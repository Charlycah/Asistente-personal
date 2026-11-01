from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)
from tests.test_pkg02_vic_contract import (
    PNG_PAYLOAD,
    setup,
    artifacts,
    deliver,
)
from tests.test_r_visual_01c_05b_viewer_render_red import (
    FakeWindow,
    FakeLabel,
    FakePhotoImage,
)


class FailingLabel(FakeLabel):
    failure = None

    def pack(self, **kwargs):
        if self.failure == "pack":
            raise RuntimeError("pack failure")
        return super().pack(**kwargs)


class FailingPhotoImage(FakePhotoImage):
    failure = None

    def __init__(self, **kwargs):
        if self.failure == "photo":
            raise RuntimeError("photo failure")
        super().__init__(**kwargs)


def make_fault_viewer():
    windows = []

    def create_window(root):
        window = FakeWindow(root)
        windows.append(window)
        return window

    toolkit = SimpleNamespace(
        Toplevel=create_window,
        Label=FailingLabel,
        PhotoImage=FailingPhotoImage,
    )

    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=toolkit,
    )
    return viewer, windows


@pytest.mark.parametrize("failure", ["photo", "pack"])
def test_res01_failed_publication_leaves_no_widget(failure):
    FailingLabel.failure = failure
    FailingPhotoImage.failure = failure
    try:
        viewer, windows = make_fault_viewer()
        artifact = object()
        viewer.open((artifact,))

        accepted = viewer.render_preview_vic(
            artifact,
            PNG_PAYLOAD,
            "image/png",
            visible_ordinal=1,
        )

        assert accepted is False
        assert windows[0].children == []
        assert viewer._preview_widgets == []
    finally:
        FailingLabel.failure = None
        FailingPhotoImage.failure = None


def test_res02_cancel_during_render_does_not_emit_receipt():
    coordinator, viewer, dispatcher, executor = setup()

    original_render = viewer.render_preview_vic

    def cancel_during_render(
        artifact, payload, content_type, *, visible_ordinal
    ):
        accepted = original_render(
            artifact,
            payload,
            content_type,
            visible_ordinal=visible_ordinal,
        )
        coordinator.cancel()
        return accepted

    viewer.render_preview_vic = cancel_during_render

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert not coordinator.active_vic_receipts
    assert not coordinator.vic_receipts
    assert coordinator.results[0].state == "DELIVERY_PENDING" or (
        coordinator.results[0].state == "CANCELLED"
    )


def test_res02_cancel_after_delivery_invalidates_active_receipt():
    coordinator, viewer, dispatcher, executor = setup()

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert len(coordinator.active_vic_receipts) == 1

    coordinator.cancel()

    assert coordinator.active_vic_receipts == ()
    assert len(coordinator.vic_receipts) == 1


def test_res03_viewer_close_invalidates_active_receipts():
    from tests.test_r_visual_01c_05b_viewer_render_red import (
        FakeWindow,
        FakeLabel,
        FakePhotoImage,
    )

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

    coordinator, _, dispatcher, executor = setup(viewer=viewer)
    coordinator._fetcher = lambda *_: (PNG_PAYLOAD, "image/png")
    viewer._on_close = coordinator.cancel

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert len(coordinator.active_vic_receipts) == 1

    viewer.close()

    assert viewer._window is None
    assert viewer.artifacts == ()
    assert not viewer._preview_widgets
    assert coordinator.active_vic_receipts == ()
    assert len(coordinator.vic_receipts) == 1


def test_res02_delivered_receipt_and_cancel_consistency():
    coordinator, viewer, dispatcher, executor = setup()

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    assert coordinator.results[0].state == "DELIVERED"
    assert len(coordinator.vic_receipts) == 1
    assert len(coordinator.active_vic_receipts) == 1

    receipt = coordinator.vic_receipts[0]
    result = coordinator.results[0]

    assert receipt.presentation_id == result.presentation_id
    assert receipt.slot_id == result.slot_id
    assert receipt.artifact_id == result.artifact_id
    assert receipt.visible_ordinal == result.visible_ordinal
    assert receipt.generation_token == result.generation_token
    assert receipt.attempt_id == result.attempt_id

    coordinator.cancel()

    assert coordinator.active_vic_receipts == ()
    assert len(coordinator.vic_receipts) == 1


def test_res01_scroll_failure_after_pack_cleans_widget():
    viewer, windows = make_fault_viewer()
    artifact = object()

    viewer.open((artifact,))

    # Registrar el widget efectivamente creado.
    created_widgets = []
    original_label = viewer._toolkit.Label

    def tracked_label(*args, **kwargs):
        widget = original_label(*args, **kwargs)
        created_widgets.append(widget)
        return widget

    viewer._toolkit.Label = tracked_label

    # Provocar el fallo exclusivamente despu?s de pack().
    def fail_scroll_update():
        assert len(created_widgets) == 1
        assert created_widgets[0].packed is True
        raise RuntimeError("injected scroll update failure")

    viewer._update_scroll_region = fail_scroll_update

    accepted = viewer.render_preview_vic(
        artifact,
        PNG_PAYLOAD,
        "image/png",
        visible_ordinal=1,
    )

    assert accepted is False
    assert len(created_widgets) == 1

    widget = created_widgets[0]

    # No debe quedar un widget publicado tras el rechazo.
    assert widget not in windows[0].children
    assert viewer._preview_widgets == []
    assert viewer._preview_images == []


def test_res01_destroy_failure_preserves_widget_ownership():
    viewer, windows = make_fault_viewer()
    artifact = object()
    viewer.open((artifact,))

    created_widgets = []
    original_label = viewer._toolkit.Label

    def tracked_label(*args, **kwargs):
        widget = original_label(*args, **kwargs)
        created_widgets.append(widget)

        def failing_destroy():
            raise RuntimeError("injected destroy failure")

        widget.destroy = failing_destroy
        return widget

    viewer._toolkit.Label = tracked_label

    def failing_scroll():
        assert len(created_widgets) == 1
        assert created_widgets[0].packed is True
        raise RuntimeError("injected scroll failure")

    viewer._update_scroll_region = failing_scroll

    accepted = viewer.render_preview_vic(
        artifact,
        PNG_PAYLOAD,
        "image/png",
        visible_ordinal=1,
    )

    assert accepted is False
    assert len(created_widgets) == 1

    widget = created_widgets[0]

    assert widget in windows[0].children
    assert viewer._preview_widgets == [widget]
    assert len(viewer._preview_images) == 1

    # A new presentation must not silently forget the residual widget.
    with pytest.raises(RuntimeError, match="injected destroy failure"):
        viewer.open((object(),))

    assert viewer._preview_widgets == [widget]
    assert len(viewer._preview_images) == 1


def test_res02_cancel_cannot_split_vic_commit():
    import threading

    coordinator, viewer, dispatcher, executor = setup()
    coordinator.present(artifacts(1))

    append_entered = threading.Event()
    release_append = threading.Event()
    cancel_started = threading.Event()
    cancel_finished = threading.Event()
    errors = []

    original_receipts = coordinator._vic_receipts

    class InterceptedReceipts(list):
        def append(self, receipt):
            super().append(receipt)
            append_entered.set()

            if not release_append.wait(timeout=5):
                raise TimeoutError("VIC append synchronization timeout")

    coordinator._vic_receipts = InterceptedReceipts(original_receipts)

    def cancel_worker():
        try:
            if not append_entered.wait(timeout=5):
                raise TimeoutError("VIC commit was not reached")

            cancel_started.set()
            coordinator.cancel()
        except BaseException as exc:
            errors.append(exc)
        finally:
            cancel_finished.set()

    worker = threading.Thread(target=cancel_worker, daemon=True)
    worker.start()

    try:
        # Complete the fetch; the dispatcher will enter VIC commit.
        executor.complete(0)

        def release_worker():
            try:
                if not append_entered.wait(timeout=5):
                    raise TimeoutError("VIC append not reached")

                if not cancel_started.wait(timeout=5):
                    raise TimeoutError("Cancel worker did not start")

                # Cancellation must not complete while append is paused.
                assert not cancel_finished.is_set()

            except BaseException as exc:
                errors.append(exc)
            finally:
                release_append.set()

        release_thread = threading.Thread(
            target=release_worker,
            daemon=True,
        )
        release_thread.start()

        dispatcher.drain()

        release_thread.join(timeout=5)
        worker.join(timeout=5)

        assert not release_thread.is_alive()
        assert not worker.is_alive()
        assert not errors, repr(errors)

        result = coordinator.results[0]
        receipts = coordinator.vic_receipts

        assert result.state == "DELIVERED"
        assert len(receipts) == 1
        assert receipts[0].slot_id == result.slot_id
        assert receipts[0].generation_token == result.generation_token

        assert coordinator.active_vic_receipts == ()

        print("RES-02-F02: atomic_commit = PASS")
        print("RES-02-F02: final_state =", result.state)
        print("RES-02-F02: historical_receipts =", len(receipts))
        print("RES-02-F02: active_receipts =", len(
            coordinator.active_vic_receipts
        ))

    finally:
        release_append.set()
        worker.join(timeout=5)


def test_res02_cancel_during_real_viewer_render_diagnostic():
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

    coordinator, _, dispatcher, executor = setup(viewer=viewer)
    coordinator._fetcher = lambda *_: (PNG_PAYLOAD, "image/png")

    original_render = getattr(
        viewer,
        "render_preview_vic_identified",
        None,
    )

    assert callable(original_render), (
        "RED: identified VIC rendering is not implemented"
    )

    assert callable(
        getattr(viewer, "discard_preview_vic", None)
    ), "RED: individual VIC discard is not implemented"

    observations = {}

    def render_then_cancel(
        artifact,
        payload,
        content_type,
        *,
        visible_ordinal,
        unit_key,
    ):
        accepted = original_render(
            artifact,
            payload,
            content_type,
            visible_ordinal=visible_ordinal,
            unit_key=unit_key,
        )

        observations["render_accepted"] = accepted
        observations["widgets_before_cancel"] = len(
            viewer._preview_widgets
        )

        coordinator.cancel()

        observations["widgets_after_cancel"] = len(
            viewer._preview_widgets
        )

        return accepted

    viewer.render_preview_vic_identified = render_then_cancel

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    result = coordinator.results[0]

    observations["slot_state"] = result.state
    observations["historical_receipts"] = len(
        coordinator.vic_receipts
    )
    observations["active_receipts"] = len(
        coordinator.active_vic_receipts
    )
    observations["widgets_final"] = len(
        viewer._preview_widgets
    )
    observations["visible_children"] = len(
        windows[0].children
    )

    for name, value in observations.items():
        print(f"RES-02-F03: {name} = {value}")

    assert observations["render_accepted"] is True
    assert observations["widgets_before_cancel"] == 1
    assert observations["slot_state"] == "CANCELLED"
    assert observations["historical_receipts"] == 0
    assert observations["active_receipts"] == 0
    assert observations["widgets_final"] == 0
    assert observations["visible_children"] == 0


def test_res02_f03_t01_cancel_compensates_identified_visual_unit():
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

    coordinator, _, dispatcher, executor = setup(viewer=viewer)
    coordinator._fetcher = lambda *_: (PNG_PAYLOAD, "image/png")

    original_render = getattr(
        viewer,
        "render_preview_vic_identified",
        None,
    )

    assert callable(original_render), (
        "RED: identified VIC rendering is not implemented"
    )

    assert callable(
        getattr(viewer, "discard_preview_vic", None)
    ), "RED: individual VIC discard is not implemented"

    observations = {}

    def render_then_cancel(
        artifact,
        payload,
        content_type,
        *,
        visible_ordinal,
        unit_key,
    ):
        accepted = original_render(
            artifact,
            payload,
            content_type,
            visible_ordinal=visible_ordinal,
            unit_key=unit_key,
        )

        observations["render_accepted"] = accepted
        observations["widgets_before_cancel"] = len(
            viewer._preview_widgets
        )

        coordinator.cancel()

        observations["widgets_after_cancel"] = len(
            viewer._preview_widgets
        )

        return accepted

    viewer.render_preview_vic_identified = render_then_cancel

    coordinator.present(artifacts(1))
    deliver(executor, dispatcher, 0)

    result = coordinator.results[0]

    observations["slot_state"] = result.state
    observations["historical_receipts"] = len(
        coordinator.vic_receipts
    )
    observations["active_receipts"] = len(
        coordinator.active_vic_receipts
    )
    observations["widgets_final"] = len(
        viewer._preview_widgets
    )
    observations["visible_children"] = len(
        windows[0].children
    )

    for name, value in observations.items():
        print(f"RES-02-F03-T01: {name} = {value}")

    assert observations["render_accepted"] is True
    assert observations["widgets_before_cancel"] == 1
    assert observations["slot_state"] == "CANCELLED"
    assert observations["historical_receipts"] == 0
    assert observations["active_receipts"] == 0
    assert observations["widgets_final"] == 0
    assert observations["visible_children"] == 0


class TestC3R02PersistentRecovery:
    """Pruebas permanentes de recuperacion VIC individual."""

    @staticmethod
    def _prepare(initial_behavior):
        from types import SimpleNamespace

        from app.desktop_governed_floating_image_viewer import (
            DesktopGovernedFloatingImageViewer,
        )
        from tests.test_pkg02_vic_contract import (
            PNG_PAYLOAD,
            setup,
            artifacts,
            deliver,
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
                self.parent = parent
                parent.children.append(self)

            def pack(self, **kwargs):
                pass

            def destroy(self):
                self.parent.children.remove(self)

        class FakePhotoImage:
            def __init__(self, **kwargs):
                pass

        viewer = DesktopGovernedFloatingImageViewer(
            root=object(),
            toolkit=SimpleNamespace(
                Toplevel=FakeWindow,
                Label=FakeLabel,
                PhotoImage=FakePhotoImage,
            ),
        )

        coordinator, _, dispatcher, executor = setup(viewer=viewer)
        coordinator._fetcher = lambda *_: (
            PNG_PAYLOAD,
            "image/png",
        )

        original_render = viewer.render_preview_vic_identified
        original_discard = viewer.discard_preview_vic

        state = {
            "behavior": initial_behavior,
            "cancel_first": True,
        }
        calls = []

        def controlled_render(
            artifact,
            payload,
            content_type,
            *,
            visible_ordinal,
            unit_key,
        ):
            accepted = original_render(
                artifact,
                payload,
                content_type,
                visible_ordinal=visible_ordinal,
                unit_key=unit_key,
            )

            if accepted and state["cancel_first"]:
                state["cancel_first"] = False
                coordinator.cancel()

            return accepted

        def controlled_discard(unit_key):
            calls.append(unit_key)

            if state["behavior"] == "FALSE":
                return False

            if state["behavior"] == "EXCEPTION":
                raise RuntimeError("injected_failure")

            if state["behavior"] == "REENTRANT":
                state["nested"].append(
                    coordinator.recover_compensation(unit_key)
                )
                return original_discard(unit_key)

            return original_discard(unit_key)

        viewer.render_preview_vic_identified = controlled_render
        viewer.discard_preview_vic = controlled_discard

        coordinator.present(artifacts(1))
        deliver(executor, dispatcher, 0)

        events = coordinator.compensation_events
        assert len(events) == 1

        key = events[0][0]

        return (
            coordinator,
            viewer,
            dispatcher,
            executor,
            state,
            calls,
            key,
        )

    def test_persist_t01_recovery_after_false(self):
        c, v, _, _, state, _, key = self._prepare("FALSE")

        state["behavior"] = "TRUE"

        assert c.recover_compensation(key) is True
        assert [e[1] for e in c.compensation_events] == [
            "COMPENSATION_PENDING",
            "RECOVERED",
        ]
        assert [e[2] for e in c.compensation_events] == [1, 2]
        assert key not in v._vic_units
        assert len(c.vic_receipts) == 0

    def test_persist_t02_recovery_after_exception(self):
        c, v, _, _, state, _, key = self._prepare("EXCEPTION")

        state["behavior"] = "TRUE"

        assert c.recover_compensation(key) is True
        assert [e[1] for e in c.compensation_events] == [
            "COMPENSATION_ERROR",
            "RECOVERED",
        ]
        assert key not in v._vic_units

    def test_persist_t03_failed_retry_then_success(self):
        c, _, _, _, state, _, key = self._prepare("FALSE")

        assert c.recover_compensation(key) is False

        state["behavior"] = "TRUE"

        assert c.recover_compensation(key) is True
        assert [e[1] for e in c.compensation_events] == [
            "COMPENSATION_PENDING",
            "COMPENSATION_PENDING",
            "RECOVERED",
        ]
        assert [e[2] for e in c.compensation_events] == [1, 2, 3]

    def test_persist_t04_reject_duplicates_and_unknown(self):
        c, _, _, _, state, calls, key = self._prepare("FALSE")

        state["behavior"] = "TRUE"
        assert c.recover_compensation(key) is True

        previous_events = c.compensation_events
        previous_calls = len(calls)

        assert c.recover_compensation(key) is False
        assert c.recover_compensation(
            (999, 999, 999, 999, 999, 999)
        ) is False
        assert c.recover_compensation((1, 2, 3)) is False

        assert c.compensation_events == previous_events
        assert len(calls) == previous_calls

    def test_persist_t05_generation_isolation(self):
        from tests.test_pkg02_vic_contract import (
            artifacts,
            deliver,
        )

        c, v, dispatcher, executor, state, _, old_key = (
            self._prepare("FALSE")
        )

        assert old_key in v._vic_units

        state["behavior"] = "TRUE"

        c.present(artifacts(1))
        deliver(executor, dispatcher, 1)

        new_keys = set(v._vic_units)

        assert old_key not in new_keys
        assert len(new_keys) == 1
        assert next(iter(new_keys)) != old_key
        assert len(c.active_vic_receipts) == 1

        previous_receipts = c.vic_receipts
        previous_results = c.results

        assert c.recover_compensation(old_key) is False

        assert set(v._vic_units) == new_keys
        assert c.vic_receipts == previous_receipts
        assert c.results == previous_results

    def test_persist_t06_reentrant_recovery_rejected(self):
        c, v, _, _, state, calls, key = self._prepare("FALSE")

        state["behavior"] = "REENTRANT"
        state["nested"] = []

        assert c.recover_compensation(key) is True

        assert state["nested"] == [False]
        assert calls == [key, key]
        assert c.compensation_events[-1] == (
            key,
            "RECOVERED",
            2,
            "TRUE",
        )
        assert key not in v._vic_units

        assert c.recover_compensation(key) is False
        assert len(calls) == 2

    def test_persist_t07_results_and_receipts_unchanged(self):
        c, _, _, _, state, _, key = self._prepare("FALSE")

        previous_results = c.results
        previous_receipts = c.vic_receipts

        state["behavior"] = "TRUE"

        assert c.recover_compensation(key) is True
        assert c.results == previous_results
        assert c.vic_receipts == previous_receipts

class TestC3R03VICConfirmation:
    @staticmethod
    def _viewer(fail_destroy=False, fail_scroll=False):
        from threading import get_ident
        from app.desktop_governed_floating_image_viewer import (
            DesktopGovernedFloatingImageViewer,
        )

        class Widget:
            def __init__(self):
                self.destroyed = False
                self.calls = 0

            def destroy(self):
                self.calls += 1
                if fail_destroy:
                    raise RuntimeError("destroy_failure")
                self.destroyed = True

        viewer = object.__new__(
            DesktopGovernedFloatingImageViewer
        )
        viewer._owner_thread = get_ident()
        viewer._vic_secondary_errors = []

        widget = Widget()
        image = object()
        key = (101, 1, 201, 1, 301, 401)

        viewer._vic_units = {key: (widget, image)}
        viewer._preview_widgets = [widget]
        viewer._preview_images = [image]

        def scroll():
            if fail_scroll:
                raise RuntimeError("scroll_failure")

        viewer._update_scroll_region = scroll

        return viewer, widget, image, key

    def test_c3_r03_scroll_failure_preserves_vic_confirmation(self):
        viewer, widget, image, key = self._viewer(
            fail_scroll=True
        )

        assert viewer.discard_preview_vic(key) is True
        assert widget.destroyed is True
        assert widget.calls == 1
        assert key not in viewer._vic_units
        assert viewer._preview_widgets == []
        assert viewer._preview_images == []
        assert viewer._vic_secondary_errors == [
            (key, "RuntimeError")
        ]

        # El historial secundario no puede crecer indefinidamente.
        for ordinal in range(40):
            another_widget = type(widget)()
            another_image = object()
            another_key = (
                102, ordinal + 1, 202,
                ordinal + 1, 302, 402,
            )

            viewer._vic_units[another_key] = (
                another_widget, another_image
            )
            viewer._preview_widgets.append(another_widget)
            viewer._preview_images.append(another_image)

            assert viewer.discard_preview_vic(
                another_key
            ) is True

        assert len(viewer._vic_secondary_errors) == 32
        assert viewer._vic_secondary_errors[-1][0] == (
            102, 40, 202, 40, 302, 402
        )

    def test_c3_r03_destroy_failure_preserves_vic_ownership(self):
        viewer, widget, image, key = self._viewer(
            fail_destroy=True
        )

        assert viewer.discard_preview_vic(key) is False
        assert widget.destroyed is False
        assert widget.calls == 1
        assert viewer._vic_units[key] == (
            widget, image
        )
        assert viewer._preview_widgets == [widget]
        assert viewer._preview_images == [image]
        assert viewer._vic_secondary_errors == []
