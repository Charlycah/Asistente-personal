"""Contractual bridge to the governed floating image viewer."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .desktop_external_image_presenter import (
    DesktopExternalImagePresenter,
)


class FloatingImageViewer(Protocol):
    def open(self, artifacts: tuple[object, ...]) -> None: ...


def connect_governed_floating_viewer(
    *,
    presenter: DesktopExternalImagePresenter,
    viewer: FloatingImageViewer,
    artifacts: Sequence[object],
) -> bool:
    """Open admitted artifacts without claiming image rendering."""
    if not isinstance(presenter, DesktopExternalImagePresenter):
        raise TypeError("Existing desktop image presenter required")

    supplied = tuple(artifacts)
    if not supplied:
        return False

    viewer.open(supplied)
    return False
