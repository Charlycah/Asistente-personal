from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

WIRING_MODULE = "app.external_image_presentation_wiring"


def _artifact():
    module = importlib.import_module("app.external_image_presentation")
    return module.project_external_image(
        {
            "source_id": "nasa",
            "external_id": "JWST-001",
            "title": "Webb deep field",
            "description": "Official NASA image",
            "published_at": "2026-10-01T12:00:00+00:00",
            "media_type": "image",
            "preview_url": "https://images-assets.nasa.gov/jwst.jpg",
            "verification": "confirmed",
        }
    )


def _wiring():
    return importlib.import_module(WIRING_MODULE)


def test_wiring_companion_is_immutable_and_preserves_text_contract() -> None:
    module = _wiring()
    artifact = _artifact()
    companion = module.ExternalImageTurnPresentation(
        text="Encontré una imagen.",
        artifacts=(artifact,),
    )
    assert companion.text == "Encontré una imagen."
    assert companion.artifacts == (artifact,)
    with pytest.raises(FrozenInstanceError):
        replace(companion, text="changed").artifacts = ()


def test_wiring_projects_only_items_from_same_governed_result() -> None:
    module = _wiring()
    result = module.project_governed_external_images(
        answer_text="Encontré resultados.",
        raw_items=(
            {
                "source_id": "nasa",
                "external_id": "MARS-1",
                "title": "Mars",
                "media_type": "image",
                "preview_url": "https://images-assets.nasa.gov/mars.jpg",
            },
            {
                "source_id": "nasa",
                "external_id": "VIDEO-1",
                "title": "Video",
                "media_type": "video",
                "preview_url": "https://images-assets.nasa.gov/video.jpg",
            },
        ),
    )
    assert result.text == "Encontré resultados."
    assert tuple(item.external_id for item in result.artifacts) == ("MARS-1",)


def test_wiring_does_not_require_text_contract_mutation() -> None:
    module = _wiring()
    source = Path(module.__file__).read_text(encoding="utf-8").casefold()
    assert "desktopmessage(" not in source
    assert "uiresponse(" not in source


def test_preview_transport_is_https_only_and_bounded() -> None:
    module = _wiring()
    calls = []

    def transport(url: str, timeout: float, max_bytes: int):
        calls.append((url, timeout, max_bytes))
        return b"image", "image/jpeg"

    fetcher = module.BoundedExternalImagePreviewFetcher(transport=transport)
    artifact = _artifact()
    payload = fetcher(artifact.preview_url, 3.0, 4096)
    assert payload == (b"image", "image/jpeg")
    assert calls == [(artifact.preview_url, 3.0, 4096)]
    with pytest.raises(ValueError):
        fetcher("http://example.com/image.jpg", 3.0, 4096)


def test_preview_transport_rejects_oversized_payload() -> None:
    module = _wiring()

    def transport(url: str, timeout: float, max_bytes: int):
        return b"x" * (max_bytes + 1), "image/jpeg"

    fetcher = module.BoundedExternalImagePreviewFetcher(transport=transport)
    with pytest.raises(ValueError):
        fetcher("https://example.com/image.jpg", 3.0, 4)


def test_preview_transport_rejects_non_image_content_type() -> None:
    module = _wiring()

    def transport(url: str, timeout: float, max_bytes: int):
        return b"not-image", "text/html"

    fetcher = module.BoundedExternalImagePreviewFetcher(transport=transport)
    with pytest.raises(ValueError):
        fetcher("https://example.com/image.jpg", 3.0, 4096)


def test_turn_wiring_reuses_presenter_without_requery() -> None:
    module = _wiring()
    artifact = _artifact()
    presented = []

    class Presenter:
        def present_inline(self, candidate):
            presented.append(candidate)
            return "presented"

    companion = module.ExternalImageTurnPresentation(
        text="Texto conservado.", artifacts=(artifact,)
    )
    results = module.present_external_image_turn(companion, Presenter())
    assert results == ("presented",)
    assert presented == [artifact]
    assert companion.text == "Texto conservado."


def test_visual_failure_preserves_text_fallback() -> None:
    module = _wiring()
    artifact = _artifact()

    class Presenter:
        def present_inline(self, candidate):
            raise OSError("preview unavailable")

    companion = module.ExternalImageTurnPresentation(
        text="La consulta gobernada fue exitosa.", artifacts=(artifact,)
    )
    outcome = module.present_external_image_turn_safely(companion, Presenter())
    assert outcome.text == companion.text
    assert outcome.visual_presented is False
    assert outcome.text_fallback_required is True


def test_ui_dispatch_uses_existing_dispatcher_contract() -> None:
    module = _wiring()
    callbacks = []

    class Dispatcher:
        def post(self, callback):
            callbacks.append(callback)

    rendered = []
    module.dispatch_external_image_render(
        Dispatcher(), lambda: rendered.append("ui")
    )
    assert rendered == []
    assert len(callbacks) == 1
    callbacks[0]()
    assert rendered == ["ui"]


def test_wiring_source_has_no_new_cognitive_or_source_authority() -> None:
    module = _wiring()
    source = Path(module.__file__).read_text(encoding="utf-8").casefold()
    forbidden = (
        "reasoning",
        "memory",
        "learning",
        "proposal",
        "planning",
        "execution",
        "visioncore",
        "nasagovernedsourceadapter",
        "governedsourcequeryexecutor(",
        "thread(",
    )
    for token in forbidden:
        assert token not in source
