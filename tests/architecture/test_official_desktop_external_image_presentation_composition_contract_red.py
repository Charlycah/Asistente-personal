from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

COMPOSITION_MODULE = "app.desktop_external_image_presentation_composition"


def _raw_image(external_id: str = "JWST-001") -> dict[str, object]:
    return {
        "source_id": "nasa",
        "external_id": external_id,
        "title": f"Webb image {external_id}",
        "description": "Official NASA image",
        "published_at": "2026-10-01T12:00:00+00:00",
        "media_type": "image",
        "preview_url": f"https://images-assets.nasa.gov/{external_id}.jpg",
        "verification": "confirmed",
    }


class _Item:
    def __init__(self, raw: dict[str, object]) -> None:
        self.raw = raw


class _GovernedResult:
    def __init__(self, items: tuple[_Item, ...]) -> None:
        self.items = items


class _AppliedResult:
    def __init__(self, text: str, conversational_result: object) -> None:
        self.natural_answer_text = text
        self.conversational_result = conversational_result


def test_composition_builds_same_turn_companion_from_existing_result() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult(
        "Encontré imágenes oficiales.",
        _GovernedResult((_Item(_raw_image()),)),
    )

    companion = module.compose_external_image_turn(result)

    assert companion.text == "Encontré imágenes oficiales."
    assert len(companion.artifacts) == 1
    assert companion.artifacts[0].external_id == "JWST-001"
    assert companion.artifacts[0].source_id == "nasa"


def test_composition_companion_is_immutable() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult("texto", _GovernedResult((_Item(_raw_image()),)))

    companion = module.compose_external_image_turn(result)

    with pytest.raises(FrozenInstanceError):
        companion.text = "mutado"
    with pytest.raises(FrozenInstanceError):
        replace(companion.artifacts[0], title="mutado").title = "otra cosa"


def test_composition_does_not_parse_visual_identity_from_answer_text() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult(
        "https://evil.example/fake.jpg nasa fake",
        _GovernedResult(()),
    )

    companion = module.compose_external_image_turn(result)

    assert companion.text == "https://evil.example/fake.jpg nasa fake"
    assert companion.artifacts == ()


def test_composition_preserves_existing_text_only_desktop_contracts() -> None:
    from app.desktop_ui import DesktopMessage
    from app.ui_adapter import UIResponse

    module = importlib.import_module(COMPOSITION_MODULE)

    assert module.DesktopVisualTurnCompanion is not DesktopMessage
    assert set(UIResponse.__dataclass_fields__) == {
        "text",
        "status",
        "session_id",
        "needs_input",
    }
    assert set(DesktopMessage.__dataclass_fields__) == {"sender", "text"}


def test_composition_reuses_certified_projection_and_presenter_contract() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult("texto", _GovernedResult((_Item(_raw_image()),)))
    companion = module.compose_external_image_turn(result)
    calls = []

    class Presenter:
        def present_inline(self, artifact):
            calls.append(artifact)
            return SimpleNamespace(presented=True)

    outcome = module.present_desktop_visual_companion(companion, Presenter())

    assert calls == [companion.artifacts[0]]
    assert outcome.text == "texto"
    assert outcome.visual_presented is True
    assert outcome.text_fallback_required is False


def test_visual_failure_preserves_successful_text_result() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult("texto canónico", _GovernedResult((_Item(_raw_image()),)))
    companion = module.compose_external_image_turn(result)

    class FailingPresenter:
        def present_inline(self, artifact):
            raise OSError("preview unavailable")

    outcome = module.present_desktop_visual_companion(
        companion,
        FailingPresenter(),
    )

    assert outcome.text == "texto canónico"
    assert outcome.visual_presented is False
    assert outcome.text_fallback_required is True


def test_desktop_visual_render_is_handed_to_existing_dispatcher() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    callbacks = []

    class Dispatcher:
        def post(self, callback):
            callbacks.append(callback)

    called = []

    def callback():
        return called.append("rendered")

    module.dispatch_desktop_visual_render(Dispatcher(), callback)

    assert callbacks == [callback]
    assert called == []
    callbacks[0]()
    assert called == ["rendered"]


def test_composition_preserves_gallery_order_and_identity() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult(
        "texto",
        _GovernedResult(
            (
                _Item(_raw_image("A")),
                _Item(_raw_image("B")),
                _Item(_raw_image("C")),
            )
        ),
    )

    companion = module.compose_external_image_turn(result)

    assert [artifact.external_id for artifact in companion.artifacts] == [
        "A",
        "B",
        "C",
    ]


def test_composition_source_has_no_duplicate_authority_or_thread_loop() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    source = Path(module.__file__).read_text(encoding="utf-8").casefold()

    forbidden = (
        "nasagovernedsourceadapter",
        "governedsourcequeryexecutor(",
        "officialconversationgateway(",
        "visioncore",
        "imagerepository",
        "memory",
        "learning",
        "proposal",
        "planning",
        "execution",
        "thread(",
        "threadpool",
        "mainloop(",
    )
    for token in forbidden:
        assert token not in source


def test_composition_does_not_claim_reachability_or_latest_ordering() -> None:
    module = importlib.import_module(COMPOSITION_MODULE)
    source = Path(module.__file__).read_text(encoding="utf-8").casefold()

    for token in ("mostrame fotos", "últimas", "ultimas", "newest", "latest"):
        assert token not in source


def test_r_visual_01_authorized_empty_topic_image_reaches_composition():
    from dataclasses import replace

    from app.applied_conversational_intelligence import (
        AppliedConversationalIntelligenceInterpretation,
        AppliedConversationalIntelligenceResult,
        AppliedConversationalIntelligenceStatus,
    )
    from app.governed_conversational_query import (
        GovernedConversationalQuery,
        GovernedConversationalQueryResult,
        GovernedConversationalQueryStatus,
    )
    from app.governed_conversational_request_mode import (
        GovernedConversationalRequestMode,
    )
    from app.governed_conversational_source_selection import (
        GovernedConversationalSourceSelection,
        GovernedConversationalSourceSelectionRequest,
        GovernedConversationalSourceSelectionStatus,
    )
    from app.governed_information_sources import (
        GovernedInformationSources,
        InformationSourceCapability,
    )
    from app.governed_source_query import (
        GovernedSourceQuery,
        GovernedSourceQueryResponse,
        GovernedSourceQueryResult,
        GovernedSourceQueryStatus,
    )

    source = replace(
        GovernedInformationSources().source_for("nasa"),
        source_id="synthetic-r-visual-01",
        name="Synthetic R Visual 01",
        topics=frozenset(),
        capabilities=frozenset({
            InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY,
        }),
    )

    request = GovernedConversationalSourceSelectionRequest(
        text="Mostrame fotos de Marte",
        topics=frozenset(),
        query_text="Marte",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )

    query = GovernedSourceQuery(
        source_id=source.source_id,
        topics=frozenset(),
        query_text="Marte",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )

    selection = GovernedConversationalSourceSelection(
        request=request,
        status=GovernedConversationalSourceSelectionStatus.SELECTED,
        source=source,
        query=query,
        eligible_sources=(source.source_id,),
    )

    response = GovernedSourceQueryResponse(
        source_id=source.source_id,
        status=GovernedSourceQueryStatus.SUCCEEDED,
        raw_items=({
            "source_id": source.source_id,
            "external_id": "MARS-001",
            "title": "Mars image",
            "description": "Governed visual candidate",
            "media_type": "image",
            "preview_url": "https://example.org/mars.jpg",
        },),
    )

    source_result = GovernedSourceQueryResult(
        query=query,
        source=source,
        status=GovernedSourceQueryStatus.SUCCEEDED,
        response=response,
    )

    conversational_result = GovernedConversationalQueryResult(
        request=GovernedConversationalQuery(
            text=request.text,
            query=query,
        ),
        status=GovernedConversationalQueryStatus.EMPTY,
        source_result=source_result,
        items=(),
        answer_text="Sin resultados tem?ticos.",
        discarded_items=1,
    )

    interpretation = AppliedConversationalIntelligenceInterpretation(
        text=request.text,
        status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
        request=request,
        matched_topics=frozenset(),
    )

    applied = AppliedConversationalIntelligenceResult(
        interpretation=interpretation,
        selection=selection,
        conversational_result=conversational_result,
        natural_answer_text="No encontr? novedades v?lidas.",
    )

    module = importlib.import_module(COMPOSITION_MODULE)
    companion = module.compose_external_image_turn(applied)

    assert tuple(
        artifact.external_id for artifact in companion.artifacts
    ) == ("MARS-001",)


@pytest.mark.parametrize(
    "scenario",
    (
        "selection_unavailable",
        "source_without_visual_capability",
        "execution_failed",
        "source_identity_mismatch",
        "insecure_preview_url",
        "topic_constrained_query",
    ),
)
def test_r_visual_02_rejects_unauthorized_raw_images(scenario):
    from dataclasses import replace

    from app.applied_conversational_intelligence import (
        AppliedConversationalIntelligenceInterpretation,
        AppliedConversationalIntelligenceResult,
        AppliedConversationalIntelligenceStatus,
    )
    from app.governed_conversational_query import (
        GovernedConversationalQuery,
        GovernedConversationalQueryResult,
        GovernedConversationalQueryStatus,
    )
    from app.governed_conversational_request_mode import (
        GovernedConversationalRequestMode,
    )
    from app.governed_conversational_source_selection import (
        GovernedConversationalSourceSelection,
        GovernedConversationalSourceSelectionRequest,
        GovernedConversationalSourceSelectionStatus,
    )
    from app.governed_information_sources import (
        GovernedInformationSources,
        InformationSourceCapability,
    )
    from app.governed_source_query import (
        GovernedSourceQuery,
        GovernedSourceQueryError,
        GovernedSourceQueryErrorKind,
        GovernedSourceQueryResponse,
        GovernedSourceQueryResult,
        GovernedSourceQueryStatus,
    )

    visual_mode = GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT
    thematic_mode = GovernedConversationalRequestMode.TOPIC_CONSTRAINED

    source = replace(
        GovernedInformationSources().source_for("nasa"),
        source_id="synthetic-r-visual-02",
        name="Synthetic R Visual 02",
        topics=frozenset(),
        capabilities=frozenset({
            InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY,
        }),
    )

    mode = (
        thematic_mode
        if scenario == "topic_constrained_query"
        else visual_mode
    )

    if scenario == "source_without_visual_capability":
        source = replace(
            source,
            topics=GovernedInformationSources().source_for("nasa").topics,
            capabilities=frozenset(),
        )

    from app.governed_information_sources import InterestTopic

    topics = (
        frozenset({InterestTopic.SPACE_EXPLORATION})
        if scenario == "topic_constrained_query"
        else frozenset()
    )

    request = GovernedConversationalSourceSelectionRequest(
        text="Mostrame fotos de Marte",
        topics=topics,
        query_text="Marte",
        mode=mode,
    )

    query = GovernedSourceQuery(
        source_id=source.source_id,
        topics=topics,
        query_text="Marte",
        mode=mode,
    )

    selection_status = GovernedConversationalSourceSelectionStatus.SELECTED
    if scenario == "selection_unavailable":
        selection_status = (
            GovernedConversationalSourceSelectionStatus.UNAVAILABLE
        )

    selection = GovernedConversationalSourceSelection(
        request=request,
        status=selection_status,
        source=source if scenario != "selection_unavailable" else None,
        query=query if scenario != "selection_unavailable" else None,
        eligible_sources=(
            (source.source_id,)
            if scenario != "selection_unavailable"
            else ()
        ),
    )

    response_status = GovernedSourceQueryStatus.SUCCEEDED
    if scenario == "execution_failed":
        response_status = GovernedSourceQueryStatus.FAILED

    preview_url = "https://example.org/mars.jpg"
    if scenario == "insecure_preview_url":
        preview_url = "http://example.org/mars.jpg"

    raw_source_id = source.source_id
    if scenario == "source_identity_mismatch":
        raw_source_id = "untrusted-other-source"

    error = None
    if scenario == "execution_failed":
        error = GovernedSourceQueryError(
            kind=next(iter(GovernedSourceQueryErrorKind)),
            message="Synthetic source execution failure",
        )

    response = GovernedSourceQueryResponse(
        source_id=source.source_id,
        status=response_status,
        error=error,
        raw_items=({
            "source_id": raw_source_id,
            "external_id": "MARS-UNTRUSTED",
            "title": "Mars image",
            "media_type": "image",
            "preview_url": preview_url,
        },),
    )

    source_result = GovernedSourceQueryResult(
        query=query,
        source=source,
        status=response_status,
        response=response,
    )

    conversational_result = GovernedConversationalQueryResult(
        request=GovernedConversationalQuery(
            text=request.text,
            query=query,
        ),
        status=GovernedConversationalQueryStatus.EMPTY,
        source_result=source_result,
        items=(),
        answer_text="Sin resultados tem?ticos.",
        discarded_items=1,
    )

    interpretation = AppliedConversationalIntelligenceInterpretation(
        text=request.text,
        status=AppliedConversationalIntelligenceStatus.RECOGNIZED,
        request=request,
        matched_topics=frozenset(),
    )

    applied = AppliedConversationalIntelligenceResult(
        interpretation=interpretation,
        selection=selection,
        conversational_result=conversational_result,
        natural_answer_text="No encontr? novedades v?lidas.",
    )

    module = importlib.import_module(COMPOSITION_MODULE)
    companion = module.compose_external_image_turn(applied)

    assert companion.artifacts == ()


@pytest.mark.parametrize(
    ("has_visual_image", "expects_absence"),
    (
        (True, False),
        (False, True),
    ),
)
def test_r_visual_03_natural_response_matches_visual_results(
    has_visual_image,
    expects_absence,
):
    from dataclasses import replace

    from app.governed_conversational_query import (
        GovernedConversationalQuery,
        GovernedConversationalQueryResult,
        GovernedConversationalQueryStatus,
    )
    from app.governed_conversational_request_mode import (
        GovernedConversationalRequestMode,
    )
    from app.governed_conversational_source_selection import (
        GovernedConversationalSourceSelection,
        GovernedConversationalSourceSelectionRequest,
        GovernedConversationalSourceSelectionStatus,
    )
    from app.governed_information_sources import (
        GovernedInformationSources,
        InformationSourceCapability,
    )
    from app.governed_source_query import (
        GovernedSourceQuery,
        GovernedSourceQueryResponse,
        GovernedSourceQueryResult,
        GovernedSourceQueryStatus,
    )
    from app.natural_governed_conversational_response import (
        NaturalGovernedConversationalResponse,
    )

    source = replace(
        GovernedInformationSources().source_for("nasa"),
        source_id="synthetic-r-visual-03",
        name="Synthetic R Visual 03",
        topics=frozenset(),
        capabilities=frozenset({
            InformationSourceCapability.OPEN_VISUAL_SUBJECT_QUERY,
        }),
    )

    request = GovernedConversationalSourceSelectionRequest(
        text="Mostrame las ?ltimas fotos de Marte",
        topics=frozenset(),
        query_text="Marte",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )

    query = GovernedSourceQuery(
        source_id=source.source_id,
        topics=frozenset(),
        query_text="Marte",
        mode=GovernedConversationalRequestMode.OPEN_VISUAL_SUBJECT,
    )

    selection = GovernedConversationalSourceSelection(
        request=request,
        status=GovernedConversationalSourceSelectionStatus.SELECTED,
        source=source,
        query=query,
        eligible_sources=(source.source_id,),
    )

    raw_items = ()
    if has_visual_image:
        raw_items = ({
            "source_id": source.source_id,
            "external_id": "MARS-003",
            "title": "Mars image",
            "media_type": "image",
            "preview_url": "https://example.org/mars.jpg",
        },)

    response = GovernedSourceQueryResponse(
        source_id=source.source_id,
        status=GovernedSourceQueryStatus.SUCCEEDED,
        raw_items=raw_items,
    )

    source_result = GovernedSourceQueryResult(
        query=query,
        source=source,
        status=GovernedSourceQueryStatus.SUCCEEDED,
        response=response,
    )

    result = GovernedConversationalQueryResult(
        request=GovernedConversationalQuery(
            text=request.text,
            query=query,
        ),
        status=GovernedConversationalQueryStatus.EMPTY,
        source_result=source_result,
        items=(),
        answer_text="Sin resultados tem?ticos.",
        discarded_items=int(has_visual_image),
    )

    answer = NaturalGovernedConversationalResponse().compose(
        query_text="Marte",
        selection=selection,
        result=result,
    )

    absence_message = "no encontr\u00e9 novedades v\u00e1lidas"

    assert (
        absence_message in answer.casefold()
    ) is expects_absence


def test_plain_text_presenter_result_does_not_claim_visual_success():
    module = importlib.import_module(COMPOSITION_MODULE)
    result = _AppliedResult("texto", _GovernedResult((_Item(_raw_image()),)))
    companion = module.compose_external_image_turn(result)

    class TextOnlyPresenter:
        def present_inline(self, artifact):
            return "rendered"

    outcome = module.present_desktop_visual_companion(
        companion,
        TextOnlyPresenter(),
    )

    assert outcome.text == "texto"
    assert outcome.visual_presented is False
    assert outcome.text_fallback_required is True
    assert outcome.presentation_results == ("rendered",)
