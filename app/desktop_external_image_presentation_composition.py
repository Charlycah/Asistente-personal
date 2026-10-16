from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol

from .external_image_presentation import ExternalImagePresentationArtifact
from .external_image_presentation_wiring import (
    ExternalImagePresenter,
    ExternalImageTurnPresentation,
    ExternalImageTurnPresentationOutcome,
    UIDispatcher,
    dispatch_external_image_render,
    present_external_image_turn_safely,
    project_governed_external_images,
)


class GovernedItem(Protocol):
    @property
    def raw(self) -> Mapping[str, object]: ...


class GovernedResult(Protocol):
    @property
    def items(self) -> tuple[GovernedItem, ...]: ...


class AppliedResult(Protocol):
    @property
    def natural_answer_text(self) -> str | None: ...

    @property
    def conversational_result(self) -> GovernedResult | None: ...


@dataclass(frozen=True)
class DesktopVisualTurnCompanion:
    text: str
    artifacts: tuple[ExternalImagePresentationArtifact, ...] = ()


def compose_external_image_turn(
    result: AppliedResult,
) -> DesktopVisualTurnCompanion:
    governed_result = result.conversational_result
    items = governed_result.items if governed_result is not None else ()
    raw_items = tuple(
        item.raw
        for item in items
        if isinstance(item.raw, Mapping)
    )
    presentation = project_governed_external_images(
        answer_text=result.natural_answer_text or "",
        raw_items=raw_items,
    )
    return DesktopVisualTurnCompanion(
        text=presentation.text,
        artifacts=presentation.artifacts,
    )


def present_desktop_visual_companion(
    companion: DesktopVisualTurnCompanion,
    presenter: ExternalImagePresenter,
) -> ExternalImageTurnPresentationOutcome:
    presentation = ExternalImageTurnPresentation(
        text=companion.text,
        artifacts=companion.artifacts,
    )
    return present_external_image_turn_safely(presentation, presenter)


def dispatch_desktop_visual_render(
    dispatcher: UIDispatcher,
    callback: Callable[[], None],
) -> None:
    dispatch_external_image_render(dispatcher, callback)
