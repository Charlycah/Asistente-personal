from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

BINDING_MODULE = "app.desktop_visual_companion_runtime_binding"


def _applied_result(text: str = "Respuesta"):
    raw = {
        "media_type": "image",
        "preview_url": "https://example.test/image.jpg",
        "title": "Mars",
        "source_id": "nasa",
        "external_id": "mars-1",
    }
    item = SimpleNamespace(raw=raw)
    governed = SimpleNamespace(items=(item,))
    return SimpleNamespace(
        natural_answer_text=text,
        conversational_result=governed,
    )


def test_binding_executes_same_turn_once_and_exposes_visual_companion() -> None:
    module = importlib.import_module(BINDING_MODULE)
    calls = []

    def execute_turn(text, session_id=None):
        calls.append((text, session_id))
        return _applied_result("Una respuesta")

    outcome = module.execute_desktop_visual_turn(
        execute_turn,
        "mostrame una imagen",
        session_id="session-1",
    )

    assert calls == [("mostrame una imagen", "session-1")]
    assert outcome.text == "Una respuesta"
    assert len(outcome.visual_companion.artifacts) == 1


def test_runtime_turn_outcome_is_immutable() -> None:
    module = importlib.import_module(BINDING_MODULE)
    outcome = module.execute_desktop_visual_turn(
        lambda text, session_id=None: _applied_result(),
        "consulta",
    )

    with pytest.raises(FrozenInstanceError):
        outcome.text = "cambio"


def test_binding_reuses_certified_companion_composition() -> None:
    module = importlib.import_module(BINDING_MODULE)
    companion_module = importlib.import_module(
        "app.desktop_external_image_presentation_composition"
    )
    result = _applied_result()

    outcome = module.bind_applied_result_to_desktop(result)

    expected = companion_module.compose_external_image_turn(result)
    assert outcome.visual_companion == expected
    assert outcome.text == expected.text


def test_binding_does_not_parse_visual_identity_from_text() -> None:
    module = importlib.import_module(BINDING_MODULE)
    result = SimpleNamespace(
        natural_answer_text=(
            "https://example.test/not-admitted.jpg "
            "https://example.test/not-admitted-2.png"
        ),
        conversational_result=SimpleNamespace(items=()),
    )

    outcome = module.bind_applied_result_to_desktop(result)

    assert outcome.visual_companion.artifacts == ()


def test_existing_text_contracts_remain_unchanged() -> None:
    from app.desktop_ui import DesktopMessage
    from app.ui_adapter import UIResponse

    importlib.import_module(BINDING_MODULE)

    assert tuple(DesktopMessage.__dataclass_fields__) == ("sender", "text")
    assert tuple(UIResponse.__dataclass_fields__) == (
        "text",
        "status",
        "session_id",
        "needs_input",
    )


def test_visual_presentation_reuses_certified_presenter_contract() -> None:
    module = importlib.import_module(BINDING_MODULE)
    outcome = module.bind_applied_result_to_desktop(_applied_result())
    seen = []

    class Presenter:
        def present_inline(self, artifact):
            seen.append(artifact)
            return artifact.preview_url

    result = module.present_desktop_runtime_visuals(outcome, Presenter())

    assert seen == list(outcome.visual_companion.artifacts)
    assert result.text == outcome.text
    assert result.visual_presented is True


def test_visual_failure_preserves_successful_text() -> None:
    module = importlib.import_module(BINDING_MODULE)
    outcome = module.bind_applied_result_to_desktop(_applied_result("Texto seguro"))

    class FailingPresenter:
        def present_inline(self, artifact):
            raise OSError("preview unavailable")

    result = module.present_desktop_runtime_visuals(
        outcome,
        FailingPresenter(),
    )

    assert result.text == "Texto seguro"
    assert result.visual_presented is False
    assert result.text_fallback_required is True


def test_visual_render_uses_existing_dispatcher_contract() -> None:
    module = importlib.import_module(BINDING_MODULE)
    callbacks = []

    class Dispatcher:
        def post(self, callback):
            callbacks.append(callback)

    called = []

    def callback():
        called.append("rendered")

    module.dispatch_desktop_runtime_visual_render(Dispatcher(), callback)

    assert callbacks == [callback]
    assert called == []
    callbacks[0]()
    assert called == ["rendered"]


def test_binding_source_has_no_second_query_or_authority() -> None:
    module = importlib.import_module(BINDING_MODULE)
    source = inspect.getsource(module).casefold()
    forbidden = (
        "officialconversationgateway(",
        "execute_applied_conversational_intelligence(",
        "governedsourcequeryexecutor(",
        "nasagovernedsourceadapter",
        "visioncore",
        "imagerepository",
        "thread(",
        "threadpool",
        "mainloop(",
    )

    for token in forbidden:
        assert token not in source


def test_binding_does_not_claim_reachability_or_freshness_ordering() -> None:
    module = importlib.import_module(BINDING_MODULE)
    source = inspect.getsource(module).casefold()

    assert "mostrame fotos" not in source
    assert "últimas" not in source
    assert "ultimas" not in source
    assert "newest" not in source
    assert "latest" not in source
