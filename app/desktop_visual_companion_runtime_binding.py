from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .desktop_external_image_presentation_composition import (
    DesktopVisualTurnCompanion,
    compose_external_image_turn,
    dispatch_desktop_visual_render,
    present_desktop_visual_companion,
)
from .external_image_presentation_wiring import (
    ExternalImagePresenter,
    ExternalImageTurnPresentationOutcome,
    UIDispatcher,
)


class SameTurnExecutor(Protocol):
    def __call__(
        self,
        text: str,
        session_id: str | None = None,
    ) -> object: ...


@dataclass(frozen=True)
class DesktopVisualRuntimeTurn:
    text: str
    visual_companion: DesktopVisualTurnCompanion


def bind_applied_result_to_desktop(
    result: object,
) -> DesktopVisualRuntimeTurn:
    companion = compose_external_image_turn(result)
    return DesktopVisualRuntimeTurn(
        text=companion.text,
        visual_companion=companion,
    )


def execute_desktop_visual_turn(
    execute_turn: SameTurnExecutor,
    text: str,
    session_id: str | None = None,
) -> DesktopVisualRuntimeTurn:
    result = execute_turn(text, session_id=session_id)
    return bind_applied_result_to_desktop(result)


def present_desktop_runtime_visuals(
    outcome: DesktopVisualRuntimeTurn,
    presenter: ExternalImagePresenter,
) -> ExternalImageTurnPresentationOutcome:
    return present_desktop_visual_companion(
        outcome.visual_companion,
        presenter,
    )


def dispatch_desktop_runtime_visual_render(
    dispatcher: UIDispatcher,
    callback: Callable[[], None],
) -> None:
    dispatch_desktop_visual_render(dispatcher, callback)
