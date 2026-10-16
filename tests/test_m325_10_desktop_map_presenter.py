from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.map_display import (
    MapDocument,
    MapPresentationMode,
    MapPresentationStatus,
    MapPresenter,
)
from infrastructure.maps import DesktopMapPresenter, DesktopMapPresenterConfig


def document(uri: str = "file:///tmp/roby-map.html") -> MapDocument:
    return MapDocument(uri=uri, media_type="text/html", title="Mapa de prueba")


def test_presenter_satisfies_runtime_protocol() -> None:
    assert isinstance(DesktopMapPresenter(), MapPresenter)


def test_default_config_is_immutable() -> None:
    config = DesktopMapPresenterConfig()
    with pytest.raises(FrozenInstanceError):
        config.browser_new = 1


@pytest.mark.parametrize("value", [-1, 3, 9])
def test_config_rejects_invalid_browser_new(value: int) -> None:
    with pytest.raises(ValueError, match="new value"):
        DesktopMapPresenterConfig(browser_new=value)


def test_config_normalizes_and_deduplicates_schemes() -> None:
    config = DesktopMapPresenterConfig(
        allowed_uri_schemes=(" FILE ", "https", "file")
    )
    assert config.allowed_uri_schemes == ("file", "https")


@pytest.mark.parametrize("schemes", [(), (" ",), ("file", "")])
def test_config_rejects_blank_scheme_sets(schemes: tuple[str, ...]) -> None:
    with pytest.raises(ValueError, match="schemes"):
        DesktopMapPresenterConfig(allowed_uri_schemes=schemes)


def test_system_browser_receives_uri_and_configuration() -> None:
    calls: list[tuple[str, int, bool]] = []

    def opener(uri: str, new: int, autoraise: bool) -> bool:
        calls.append((uri, new, autoraise))
        return True

    presenter = DesktopMapPresenter(
        DesktopMapPresenterConfig(browser_new=1, browser_autoraise=False),
        browser_opener=opener,
    )
    result = presenter.present(document(), mode=MapPresentationMode.SYSTEM_BROWSER)

    assert calls == [("file:///tmp/roby-map.html", 1, False)]
    assert result.status is MapPresentationStatus.PRESENTED
    assert result.presented is True
    assert result.surface == "system_browser"
    assert result.rationale == ("desktop_map_opened_in_system_browser",)


def test_present_accepts_string_mode() -> None:
    presenter = DesktopMapPresenter(browser_opener=lambda *_: True)
    result = presenter.present(document(), mode="system_browser")
    assert result.status is MapPresentationStatus.PRESENTED


def test_disabled_system_browser_is_unavailable_without_calling_opener() -> None:
    called = False

    def opener(*_args) -> bool:
        nonlocal called
        called = True
        return True

    presenter = DesktopMapPresenter(
        DesktopMapPresenterConfig(allow_system_browser=False),
        browser_opener=opener,
    )
    result = presenter.present(document(), mode=MapPresentationMode.SYSTEM_BROWSER)

    assert called is False
    assert result.status is MapPresentationStatus.UNAVAILABLE
    assert result.rationale == ("desktop_system_browser_disabled",)


def test_browser_rejection_is_reported_as_unavailable() -> None:
    presenter = DesktopMapPresenter(browser_opener=lambda *_: False)
    result = presenter.present(document(), mode=MapPresentationMode.SYSTEM_BROWSER)
    assert result.status is MapPresentationStatus.UNAVAILABLE
    assert result.rationale == ("desktop_system_browser_rejected_document",)


def test_browser_exception_is_contained_as_failed_result() -> None:
    def opener(*_args) -> bool:
        raise OSError("desktop unavailable")

    presenter = DesktopMapPresenter(browser_opener=opener)
    result = presenter.present(document(), mode=MapPresentationMode.SYSTEM_BROWSER)
    assert result.status is MapPresentationStatus.FAILED
    assert result.rationale == ("desktop_system_browser_error",)


def test_embedded_mode_requires_an_adapter() -> None:
    result = DesktopMapPresenter().present(
        document(), mode=MapPresentationMode.EMBEDDED_WINDOW
    )
    assert result.status is MapPresentationStatus.UNAVAILABLE
    assert result.rationale == ("desktop_embedded_window_adapter_missing",)


def test_disabled_embedded_mode_does_not_call_adapter() -> None:
    called = False

    def embedded(_document: MapDocument) -> bool:
        nonlocal called
        called = True
        return True

    presenter = DesktopMapPresenter(
        DesktopMapPresenterConfig(allow_embedded_window=False),
        embedded_opener=embedded,
    )
    result = presenter.present(document(), mode=MapPresentationMode.EMBEDDED_WINDOW)
    assert called is False
    assert result.status is MapPresentationStatus.UNAVAILABLE
    assert result.rationale == ("desktop_embedded_window_disabled",)


def test_embedded_adapter_receives_the_complete_document() -> None:
    received: list[MapDocument] = []
    expected = document()

    def embedded(candidate: MapDocument) -> bool:
        received.append(candidate)
        return True

    presenter = DesktopMapPresenter(embedded_opener=embedded)
    result = presenter.present(expected, mode=MapPresentationMode.EMBEDDED_WINDOW)

    assert received == [expected]
    assert result.status is MapPresentationStatus.PRESENTED
    assert result.surface == "embedded_window"
    assert result.rationale == ("desktop_map_opened_in_embedded_window",)


def test_embedded_rejection_is_reported_as_unavailable() -> None:
    presenter = DesktopMapPresenter(embedded_opener=lambda _document: False)
    result = presenter.present(document(), mode=MapPresentationMode.EMBEDDED_WINDOW)
    assert result.status is MapPresentationStatus.UNAVAILABLE
    assert result.rationale == ("desktop_embedded_window_rejected_document",)


def test_embedded_exception_is_contained_as_failed_result() -> None:
    def embedded(_document: MapDocument) -> bool:
        raise RuntimeError("window failed")

    presenter = DesktopMapPresenter(embedded_opener=embedded)
    result = presenter.present(document(), mode=MapPresentationMode.EMBEDDED_WINDOW)
    assert result.status is MapPresentationStatus.FAILED
    assert result.rationale == ("desktop_embedded_window_error",)


@pytest.mark.parametrize(
    "uri",
    [
        "file:///tmp/map.html",
        "https://example.test/map.html",
        "http://example.test/map.html",
    ],
)
def test_default_config_accepts_governed_document_schemes(uri: str) -> None:
    presenter = DesktopMapPresenter(browser_opener=lambda *_: True)
    result = presenter.present(document(uri), mode=MapPresentationMode.SYSTEM_BROWSER)
    assert result.status is MapPresentationStatus.PRESENTED


def test_missing_uri_scheme_fails_without_invoking_surface() -> None:
    called = False

    def opener(*_args) -> bool:
        nonlocal called
        called = True
        return True

    presenter = DesktopMapPresenter(browser_opener=opener)
    result = presenter.present(document("relative/map.html"), mode="system_browser")

    assert called is False
    assert result.status is MapPresentationStatus.FAILED
    assert result.rationale == ("desktop_map_document_uri_scheme_missing",)


def test_disallowed_uri_scheme_fails_without_invoking_surface() -> None:
    called = False

    def opener(*_args) -> bool:
        nonlocal called
        called = True
        return True

    presenter = DesktopMapPresenter(browser_opener=opener)
    result = presenter.present(document("javascript:alert(1)"), mode="system_browser")

    assert called is False
    assert result.status is MapPresentationStatus.FAILED
    assert result.rationale == ("desktop_map_document_uri_scheme_disallowed",)


def test_custom_scheme_policy_can_be_restricted() -> None:
    presenter = DesktopMapPresenter(
        DesktopMapPresenterConfig(allowed_uri_schemes=("file",)),
        browser_opener=lambda *_: True,
    )
    result = presenter.present(
        document("https://example.test/map.html"), mode="system_browser"
    )
    assert result.status is MapPresentationStatus.FAILED
