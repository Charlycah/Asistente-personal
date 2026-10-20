from __future__ import annotations

from threading import Thread
from types import SimpleNamespace

import pytest

from app.desktop_external_image_presenter import (
    DesktopExternalImagePresenter,
)


def _connect(
    *,
    presenter: object,
    viewer: object,
    artifacts: tuple[object, ...],
) -> bool:
    from app.desktop_governed_floating_viewer_integration import (
        connect_governed_floating_viewer,
    )

    return connect_governed_floating_viewer(
        presenter=presenter,
        viewer=viewer,
        artifacts=artifacts,
    )


class _Viewer:
    def __init__(self) -> None:
        self.calls: list[tuple[object, ...]] = []

    def open(self, artifacts: tuple[object, ...]) -> None:
        self.calls.append(tuple(artifacts))


def test_existing_presenter_is_reused() -> None:
    presenter = DesktopExternalImagePresenter()
    viewer = _Viewer()
    artifact = SimpleNamespace(external_id="image-1")

    result = _connect(
        presenter=presenter,
        viewer=viewer,
        artifacts=(artifact,),
    )

    assert result is False
    assert viewer.calls == [(artifact,)]


def test_only_supplied_artifacts_reach_viewer() -> None:
    presenter = DesktopExternalImagePresenter()
    viewer = _Viewer()
    first = SimpleNamespace(external_id="image-1")
    second = SimpleNamespace(external_id="image-2")

    result = _connect(
        presenter=presenter,
        viewer=viewer,
        artifacts=(first, second),
    )

    assert result is False
    assert viewer.calls == [(first, second)]


def test_empty_artifacts_do_not_open_viewer() -> None:
    presenter = DesktopExternalImagePresenter()
    viewer = _Viewer()

    result = _connect(
        presenter=presenter,
        viewer=viewer,
        artifacts=(),
    )

    assert result is False
    assert viewer.calls == []


def test_foreign_thread_cannot_open_real_viewer() -> None:
    from app.desktop_governed_floating_image_viewer import (
        DesktopGovernedFloatingImageViewer,
    )

    class _Toolkit:
        def Toplevel(self, root: object) -> object:
            raise AssertionError("Foreign thread created a window")

    viewer = DesktopGovernedFloatingImageViewer(
        root=object(),
        toolkit=_Toolkit(),
    )
    presenter = DesktopExternalImagePresenter()
    errors: list[BaseException] = []

    def attempt() -> None:
        try:
            _connect(
                presenter=presenter,
                viewer=viewer,
                artifacts=(object(),),
            )
        except BaseException as exc:
            errors.append(exc)

    worker = Thread(target=attempt)
    worker.start()
    worker.join(timeout=5)

    assert not worker.is_alive()
    assert len(errors) == 1
    assert isinstance(errors[0], RuntimeError)


def test_opening_viewer_never_claims_rendered_image() -> None:
    presenter = DesktopExternalImagePresenter()
    viewer = _Viewer()

    result = _connect(
        presenter=presenter,
        viewer=viewer,
        artifacts=(object(),),
    )

    assert result is False
    assert len(viewer.calls) == 1


def test_invalid_presenter_is_rejected() -> None:
    viewer = _Viewer()

    with pytest.raises(TypeError):
        _connect(
            presenter=object(),
            viewer=viewer,
            artifacts=(object(),),
        )

    assert viewer.calls == []
