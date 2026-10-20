from __future__ import annotations

from concurrent.futures import Future
from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from app.desktop_governed_image_preview_coordinator import (
    GovernedImagePreviewCoordinator,
)


@dataclass(frozen=True)
class Artifact:
    preview_url: str


def test_shutdown_prevents_new_preview_presentations():
    viewer = Mock()
    viewer.artifacts = ()
    dispatcher = Mock()
    executor = Mock()
    executor.submit.return_value = Future()

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=Mock(),
        executor=executor,
    )

    coordinator.shutdown()

    with pytest.raises(RuntimeError, match="shut down"):
        coordinator.present((Artifact("https://example.org/a.png"),))

    viewer.open.assert_not_called()
    executor.submit.assert_not_called()
    executor.shutdown.assert_called_once_with(
        wait=False,
        cancel_futures=True,
    )


def test_shutdown_is_idempotent():
    viewer = Mock()
    dispatcher = Mock()
    executor = Mock()

    coordinator = GovernedImagePreviewCoordinator(
        viewer=viewer,
        dispatcher=dispatcher,
        fetcher=Mock(),
        executor=executor,
    )

    coordinator.shutdown()
    generation_after_first_shutdown = coordinator._generation

    coordinator.shutdown()

    assert coordinator._generation == generation_after_first_shutdown
    executor.shutdown.assert_called_once_with(
        wait=False,
        cancel_futures=True,
    )
