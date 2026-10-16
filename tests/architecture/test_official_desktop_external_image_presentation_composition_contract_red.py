from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

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
            return "rendered"

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
