from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

PROJECTION_MODULE = "app.external_image_presentation"
PRESENTER_MODULE = "app.desktop_external_image_presenter"


def _projection():
    return importlib.import_module(PROJECTION_MODULE)


def _presenter():
    return importlib.import_module(PRESENTER_MODULE)


def _raw_image(**changes):
    values = {
        "source_id": "nasa",
        "external_id": "JWST-001",
        "title": "Webb deep field",
        "description": "Official NASA image",
        "published_at": "2026-10-01T12:00:00+00:00",
        "media_type": "image",
        "preview_url": "https://images-assets.nasa.gov/jwst.jpg",
        "verification": "confirmed",
    }
    values.update(changes)
    return values


def test_projection_contract_exposes_immutable_external_image_artifact():
    module = _projection()
    artifact = module.ExternalImagePresentationArtifact.from_raw(_raw_image())

    assert artifact.source_id == "nasa"
    assert artifact.external_id == "JWST-001"
    assert artifact.title == "Webb deep field"
    assert artifact.preview_url == "https://images-assets.nasa.gov/jwst.jpg"
    assert artifact.media_type == "image"
    with pytest.raises(FrozenInstanceError):
        artifact.title = "mutated"


def test_projection_preserves_provenance_and_descriptive_metadata():
    module = _projection()
    artifact = module.ExternalImagePresentationArtifact.from_raw(_raw_image())

    assert artifact.description == "Official NASA image"
    assert artifact.published_at == "2026-10-01T12:00:00+00:00"
    assert artifact.verification == "confirmed"
    assert artifact.provenance.source_id == "nasa"
    assert artifact.provenance.external_id == "JWST-001"


def test_projection_admits_only_governed_image_items_with_https_preview():
    module = _projection()

    assert module.project_external_image(_raw_image()) is not None
    assert module.project_external_image(_raw_image(media_type="video")) is None
    assert module.project_external_image(_raw_image(preview_url=None)) is None
    assert (
        module.project_external_image(
            _raw_image(preview_url="http://images-assets.nasa.gov/jwst.jpg")
        )
        is None
    )


def test_projection_is_provider_neutral_and_does_not_require_nasa_identity():
    module = _projection()
    artifact = module.project_external_image(
        _raw_image(source_id="esa", external_id="ESA-001")
    )

    assert artifact is not None
    assert artifact.source_id == "esa"
    assert artifact.external_id == "ESA-001"


def test_projection_does_not_create_network_or_cognitive_authority():
    _projection()
    source = Path("app/external_image_presentation.py").read_text(encoding="utf-8")
    lowered = source.casefold()

    forbidden = (
        "urlopen",
        "requests",
        "httpx",
        "reasoning",
        "memory",
        "learning",
        "proposal",
        "planning",
        "execution",
        "visioncore",
    )
    assert all(token not in lowered for token in forbidden)


def test_desktop_presenter_accepts_projected_artifact_not_source_query():
    projection = _projection()
    presenter_module = _presenter()
    artifact = projection.ExternalImagePresentationArtifact.from_raw(_raw_image())
    received = []

    presenter = presenter_module.DesktopExternalImagePresenter(
        inline_renderer=lambda candidate, _payload: received.append(candidate) or True,
        preview_fetcher=lambda _url, _timeout, _limit: (b"image", "image/jpeg"),
    )
    result = presenter.present_inline(artifact)

    assert received == [artifact]
    assert result.presented is True
    assert result.surface == "inline_image"


def test_preview_fetch_is_https_only_bounded_and_explicit_artifact_bound():
    projection = _projection()
    presenter_module = _presenter()
    observed = {}
    artifact = projection.ExternalImagePresentationArtifact.from_raw(_raw_image())

    def fetch(url, timeout_seconds, max_bytes):
        observed.update(url=url, timeout=timeout_seconds, max_bytes=max_bytes)
        return b"image", "image/jpeg"

    config = presenter_module.DesktopExternalImagePresenterConfig(
        preview_timeout_seconds=4.0,
        max_preview_bytes=750_000,
    )
    presenter = presenter_module.DesktopExternalImagePresenter(
        config=config,
        preview_fetcher=fetch,
        inline_renderer=lambda _artifact, _payload: True,
    )
    presenter.present_inline(artifact)

    assert observed == {
        "url": artifact.preview_url,
        "timeout": 4.0,
        "max_bytes": 750_000,
    }


def test_preview_content_type_is_restricted_to_supported_images():
    projection = _projection()
    presenter_module = _presenter()
    artifact = projection.ExternalImagePresentationArtifact.from_raw(_raw_image())
    called = False

    def render(_artifact, _payload):
        nonlocal called
        called = True
        return True

    presenter = presenter_module.DesktopExternalImagePresenter(
        preview_fetcher=lambda _url, _timeout, _limit: (b"html", "text/html"),
        inline_renderer=render,
    )
    result = presenter.present_inline(artifact)

    assert called is False
    assert result.presented is False
    assert result.text_fallback_required is True


def test_preview_failure_degrades_to_text_without_changing_artifact():
    projection = _projection()
    presenter_module = _presenter()
    artifact = projection.ExternalImagePresentationArtifact.from_raw(_raw_image())

    def fail(*_args):
        raise OSError("preview unavailable")

    presenter = presenter_module.DesktopExternalImagePresenter(preview_fetcher=fail)
    result = presenter.present_inline(artifact)

    assert result.presented is False
    assert result.text_fallback_required is True
    assert result.artifact == artifact


def test_gallery_preserves_result_order_and_uses_same_projected_artifacts():
    projection = _projection()
    presenter_module = _presenter()
    artifacts = tuple(
        projection.ExternalImagePresentationArtifact.from_raw(
            _raw_image(external_id=f"IMG-{index}")
        )
        for index in range(3)
    )
    received = []

    presenter = presenter_module.DesktopExternalImagePresenter(
        gallery_renderer=lambda candidates: received.extend(candidates) or True
    )
    result = presenter.present_gallery(artifacts)

    assert tuple(received) == artifacts
    assert result.presented is True
    assert result.surface == "image_gallery"


def test_detail_view_reuses_same_artifact_without_refetch_or_requery():
    projection = _projection()
    presenter_module = _presenter()
    artifact = projection.ExternalImagePresentationArtifact.from_raw(_raw_image())
    received = []

    presenter = presenter_module.DesktopExternalImagePresenter(
        detail_renderer=lambda candidate: received.append(candidate) or True
    )
    result = presenter.present_detail(artifact)

    assert received == [artifact]
    assert result.artifact is artifact
    assert result.surface == "image_detail"


def test_presentation_result_is_immutable_and_cannot_claim_false_surface():
    presenter_module = _presenter()
    result = presenter_module.ExternalImagePresentationResult(
        artifact=None,
        presented=False,
        surface=None,
        text_fallback_required=True,
        rationale=("preview_unavailable",),
    )

    with pytest.raises(FrozenInstanceError):
        result.presented = True
    with pytest.raises(ValueError):
        replace(result, presented=False, surface="inline_image")
