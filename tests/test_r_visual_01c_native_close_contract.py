from __future__ import annotations

from dataclasses import dataclass
from threading import Thread

from app.desktop_governed_floating_image_viewer import (
    DesktopGovernedFloatingImageViewer,
)


@dataclass(frozen=True)
class _Artifact:
    external_id: str


class _FakeRoot:
    def __init__(self) -> None:
        self.destroyed = False

    def destroy(self) -> None:
        self.destroyed = True


class _FakeWindow:
    def __init__(self, master: object) -> None:
        self.master = master
        self.destroyed = False
        self.protocols: dict[str, object] = {}

    def title(self, value: str) -> None:
        self.window_title = value

    def resizable(self, width: bool, height: bool) -> None:
        self.resizable_args = (width, height)

    def protocol(self, name: str, callback: object) -> None:
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


def _setup() -> tuple[
    DesktopGovernedFloatingImageViewer,
    _FakeRoot,
    _FakeTk,
]:
    root = _FakeRoot()
    toolkit = _FakeTk()
    viewer = DesktopGovernedFloatingImageViewer(
        root=root,
        toolkit=toolkit,
    )
    return viewer, root, toolkit


def test_native_close_protocol_is_registered() -> None:
    viewer, root, toolkit = _setup()

    viewer.open(())

    assert len(toolkit.windows) == 1
    assert toolkit.windows[0].master is root
    assert callable(
        toolkit.windows[0].protocols.get("WM_DELETE_WINDOW")
    )


def test_native_close_destroys_child_but_preserves_root() -> None:
    viewer, root, toolkit = _setup()
    artifact = _Artifact(external_id="image-1")

    viewer.open((artifact,))

    callback = toolkit.windows[0].protocols["WM_DELETE_WINDOW"]
    assert callable(callback)

    callback()

    assert toolkit.windows[0].destroyed is True
    assert root.destroyed is False
    assert viewer.artifacts == ()


def test_native_close_allows_reopen() -> None:
    viewer, root, toolkit = _setup()

    viewer.open((_Artifact(external_id="image-1"),))
    callback = toolkit.windows[0].protocols["WM_DELETE_WINDOW"]
    assert callable(callback)
    callback()

    viewer.open((_Artifact(external_id="image-2"),))

    assert len(toolkit.windows) == 2
    assert toolkit.windows[0].destroyed is True
    assert toolkit.windows[1].destroyed is False
    assert toolkit.windows[1].master is root
    assert viewer.artifacts == (
        _Artifact(external_id="image-2"),
    )


def test_native_close_rejects_foreign_thread() -> None:
    viewer, root, toolkit = _setup()
    viewer.open(())

    callback = toolkit.windows[0].protocols["WM_DELETE_WINDOW"]
    assert callable(callback)
    errors: list[BaseException] = []

    def attempt_close() -> None:
        try:
            callback()
        except BaseException as exc:
            errors.append(exc)

    worker = Thread(target=attempt_close)
    worker.start()
    worker.join(timeout=5)

    assert not worker.is_alive()
    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)
    assert toolkit.windows[0].destroyed is False
    assert root.destroyed is False
