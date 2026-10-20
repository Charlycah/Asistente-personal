from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.external_image_presentation_wiring import (
    ExternalImageTurnPresentation,
    present_external_image_turn_safely,
)


@dataclass(frozen=True)
class _Artifact:
    external_id: str


@dataclass(frozen=True)
class _PresentationResult:
    presented: bool


class _Presenter:
    def __init__(self, outcomes: tuple[bool, ...]) -> None:
        self._outcomes = iter(outcomes)
        self.received: list[object] = []

    def present_inline(self, artifact: object) -> _PresentationResult:
        self.received.append(artifact)
        return _PresentationResult(presented=next(self._outcomes))


@pytest.mark.parametrize(
    ("outcomes", "expected_presented", "expected_fallback"),
    (
        ((), False, True),
        ((False,), False, True),
        ((False, False, False, False, False), False, True),
        ((True,), True, False),
        ((False, True), True, False),
    ),
)
def test_visual_presentation_reflects_actual_renderer_outcomes(
    outcomes: tuple[bool, ...],
    expected_presented: bool,
    expected_fallback: bool,
) -> None:
    artifacts = tuple(
        _Artifact(external_id=f"image-{index}")
        for index in range(len(outcomes))
    )
    presenter = _Presenter(outcomes)

    result = present_external_image_turn_safely(
        ExternalImageTurnPresentation(
            text="Imágenes de Marte",
            artifacts=artifacts,
        ),
        presenter,
    )

    assert result.visual_presented is expected_presented
    assert result.text_fallback_required is expected_fallback
    assert result.text == "Imágenes de Marte"
    assert tuple(presenter.received) == artifacts
    assert len(result.presentation_results) == len(artifacts)
