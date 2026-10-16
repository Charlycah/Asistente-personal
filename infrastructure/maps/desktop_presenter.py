from __future__ import annotations

import webbrowser
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

from core.map_display import (
    MapDocument,
    MapPresentationMode,
    MapPresentationResult,
    MapPresenter,
)

BrowserOpener = Callable[[str, int, bool], bool]
EmbeddedOpener = Callable[[MapDocument], bool]


@dataclass(frozen=True)
class DesktopMapPresenterConfig:
    allow_system_browser: bool = True
    allow_embedded_window: bool = True
    browser_new: int = 2
    browser_autoraise: bool = True
    allowed_uri_schemes: tuple[str, ...] = ("file", "http", "https")

    def __post_init__(self) -> None:
        if self.browser_new not in (0, 1, 2):
            raise ValueError("desktop map browser new value must be 0, 1, or 2")
        normalized_schemes = tuple(
            dict.fromkeys(item.strip().casefold() for item in self.allowed_uri_schemes)
        )
        if not normalized_schemes or any(not item for item in normalized_schemes):
            raise ValueError("desktop map URI schemes must not be blank")
        object.__setattr__(self, "allowed_uri_schemes", normalized_schemes)


class DesktopMapPresenter:
    """Presents rendered map documents on an explicitly selected desktop surface."""

    def __init__(
        self,
        config: DesktopMapPresenterConfig | None = None,
        *,
        browser_opener: BrowserOpener | None = None,
        embedded_opener: EmbeddedOpener | None = None,
    ) -> None:
        self._config = config or DesktopMapPresenterConfig()
        self._browser_opener = browser_opener or self._open_in_system_browser
        self._embedded_opener = embedded_opener

    def present(
        self,
        document: MapDocument,
        *,
        mode: MapPresentationMode,
    ) -> MapPresentationResult:
        selected_mode = MapPresentationMode(mode)
        invalid_reason = self._validate_document(document)
        if invalid_reason is not None:
            return self._failed(invalid_reason)
        if selected_mode is MapPresentationMode.SYSTEM_BROWSER:
            return self._present_in_system_browser(document)
        return self._present_in_embedded_window(document)

    def _present_in_system_browser(
        self, document: MapDocument
    ) -> MapPresentationResult:
        if not self._config.allow_system_browser:
            return self._unavailable("desktop_system_browser_disabled")
        try:
            opened = self._browser_opener(
                document.uri,
                self._config.browser_new,
                self._config.browser_autoraise,
            )
        except Exception:
            return self._failed("desktop_system_browser_error")
        if not opened:
            return self._unavailable("desktop_system_browser_rejected_document")
        return MapPresentationResult(
            status="presented",
            presented=True,
            surface="system_browser",
            rationale=("desktop_map_opened_in_system_browser",),
        )

    def _present_in_embedded_window(
        self, document: MapDocument
    ) -> MapPresentationResult:
        if not self._config.allow_embedded_window:
            return self._unavailable("desktop_embedded_window_disabled")
        if self._embedded_opener is None:
            return self._unavailable("desktop_embedded_window_adapter_missing")
        try:
            opened = self._embedded_opener(document)
        except Exception:
            return self._failed("desktop_embedded_window_error")
        if not opened:
            return self._unavailable("desktop_embedded_window_rejected_document")
        return MapPresentationResult(
            status="presented",
            presented=True,
            surface="embedded_window",
            rationale=("desktop_map_opened_in_embedded_window",),
        )

    def _validate_document(self, document: MapDocument) -> str | None:
        scheme = urlparse(document.uri).scheme.casefold()
        if not scheme:
            return "desktop_map_document_uri_scheme_missing"
        if scheme not in self._config.allowed_uri_schemes:
            return "desktop_map_document_uri_scheme_disallowed"
        return None

    @staticmethod
    def _open_in_system_browser(uri: str, new: int, autoraise: bool) -> bool:
        return webbrowser.open(uri, new=new, autoraise=autoraise)

    @staticmethod
    def _unavailable(reason: str) -> MapPresentationResult:
        return MapPresentationResult(
            status="unavailable",
            presented=False,
            surface=None,
            rationale=(reason,),
        )

    @staticmethod
    def _failed(reason: str) -> MapPresentationResult:
        return MapPresentationResult(
            status="failed",
            presented=False,
            surface=None,
            rationale=(reason,),
        )


assert isinstance(DesktopMapPresenter(), MapPresenter)
