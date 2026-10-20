from __future__ import annotations

from collections.abc import Mapping

from .external_image_presentation import (
    ExternalImagePresentationArtifact,
    project_external_image,
)
from .governed_conversational_query import (
    GovernedConversationalQueryResult,
)
from .governed_conversational_request_mode import (
    GovernedConversationalRequestMode,
)
from .governed_conversational_source_selection import (
    GovernedConversationalSourceSelection,
    GovernedConversationalSourceSelectionStatus,
)
from .governed_information_sources import InformationSourceCapability
from .governed_source_query import GovernedSourceQueryStatus


def admit_governed_visual_images(
    *,
    selection: GovernedConversationalSourceSelection,
    result: GovernedConversationalQueryResult | None,
) -> tuple[ExternalImagePresentationArtifact, ...]:
    if (
        selection.status
        is not GovernedConversationalSourceSelectionStatus.SELECTED
    ):
        return ()

    request = selection.request
    source = selection.source
    query = selection.query

    if source is None or query is None or result is None:
        return ()

    visual_mode = GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT

    if request.mode is not visual_mode or query.mode is not visual_mode:
        return ()

    if request.topics or query.topics:
        return ()

    if request.query_text != query.query_text:
        return ()

    source_id = source.source_id

    if source_id not in selection.eligible_sources:
        return ()

    if query.source_id != source_id:
        return ()

    if result.source_result is None:
        return ()

    execution = result.source_result

    if execution.query != query:
        return ()

    if execution.source.source_id != source_id:
        return ()

    if execution.status is not GovernedSourceQueryStatus.SUCCEEDED:
        return ()

    response = execution.response

    if response is None:
        return ()

    if response.status is not GovernedSourceQueryStatus.SUCCEEDED:
        return ()

    if response.source_id != source_id:
        return ()

    capability = InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY

    if capability not in source.capabilities:
        return ()

    artifacts = []

    for raw in response.raw_items:
        if not isinstance(raw, Mapping):
            continue

        if raw.get("source_id") != source_id:
            continue

        artifact = project_external_image(raw)

        if artifact is not None:
            artifacts.append(artifact)

    return tuple(artifacts)
