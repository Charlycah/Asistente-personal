from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from threading import Thread

import pytest


@dataclass(frozen=True)
class _Artifact:
    external_id: str


class _FakeWindow:
    def __init__(self, master: object) -> None:
        self.master = master
        self.destroyed = False
        self.resizable_args: tuple[bool, bool] | None = None

    def title(self, value: str) -> None:
        self.window_title = value

    def resizable(self, width: bool, height: bool) -> None:
        self.resizable_args = (width, height)

    def protocol(self, name: str, callback: object) -> None:
        if not hasattr(self, 'protocols'):
            self.protocols = {}
        self.protocols[name] = callback

    def destroy(self) -> None:
        self.destroyed = True


class _FakeTk:
    def __init__(self) -> None:
        self.windows: list[_FakeWindow] = []

    def Toplevel(self, master: object) -> _FakeWindow:
        window = _FakeWindow(master)
        self.windows.append(window)
        return window


def _viewer_class() -> type:
    module = import_module("app.desktop_governed_floating_image_viewer")
    return module.DesktopGovernedFloatingImageViewer


def test_floating_viewer_module_exists() -> None:
    assert _viewer_class() is not None


def test_viewer_opens_nonmodal_child_of_existing_root() -> None:
    viewer_class = _viewer_class()
    toolkit = _FakeTk()
    root = object()
    viewer = viewer_class(root=root, toolkit=toolkit)

    viewer.open(())

    assert len(toolkit.windows) == 1
    assert toolkit.windows[0].master is root
    assert toolkit.windows[0].resizable_args == (True, True)


def test_viewer_close_preserves_root_and_allows_reopen() -> None:
    viewer_class = _viewer_class()
    toolkit = _FakeTk()
    root = object()
    viewer = viewer_class(root=root, toolkit=toolkit)

    viewer.open(())
    viewer.close()
    viewer.open(())

    assert len(toolkit.windows) == 2
    assert toolkit.windows[0].destroyed is True
    assert toolkit.windows[1].master is root


def test_viewer_receives_only_explicit_artifacts() -> None:
    viewer_class = _viewer_class()
    toolkit = _FakeTk()
    viewer = viewer_class(root=object(), toolkit=toolkit)
    artifacts = (
        _Artifact(external_id="image-1"),
        _Artifact(external_id="image-2"),
    )

    viewer.open(artifacts)

    assert viewer.artifacts == artifacts


def test_viewer_rejects_unowned_thread_access() -> None:
    viewer_class = _viewer_class()
    toolkit = _FakeTk()
    viewer = viewer_class(root=object(), toolkit=toolkit)
    errors: list[BaseException] = []

    def attempt_open() -> None:
        try:
            viewer.open(())
        except BaseException as exc:
            errors.append(exc)

    worker = Thread(target=attempt_open)
    worker.start()
    worker.join(timeout=5)

    assert not worker.is_alive()
    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)
    assert toolkit.windows == []
