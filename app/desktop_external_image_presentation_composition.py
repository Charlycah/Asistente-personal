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
from .governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from .governed_visual_image_admission import (
    admit_governed_visual_images,
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

    @property
    def selection(self) -> object: ...


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
    artifacts = presentation.artifacts
    selection = getattr(result, "selection", None)
    if selection is not None and governed_result is not None:
        admitted = admit_governed_visual_images(
            selection=selection,
            result=governed_result,
        )
        if (
            selection.request.mode
            is GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
        ):
            artifacts = admitted
    return DesktopVisualTurnCompanion(
        text=presentation.text,
        artifacts=artifacts,
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
