from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PresentationMode(StrEnum):
    CONVERSATION = "conversation"
    SOURCE_ONLY = "source_only"
    LINK_ONLY = "link_only"


@dataclass(frozen=True)
class ResponsePresentation:
    """Structured response data before it reaches text or voice surfaces."""

    body: str = ""
    source: str = ""
    link: str = ""


class ResponsePresenter:
    """Render structured capability output without exposing internal metadata."""

    _HIDDEN_PREFIXES = (
        "enlace:",
        "url:",
        "rss:",
        "provider:",
        "proveedor:",
        "request_id:",
        "session_id:",
    )

    def present(
        self,
        response: ResponsePresentation,
        *,
        mode: PresentationMode = PresentationMode.CONVERSATION,
    ) -> str:
        if mode is PresentationMode.LINK_ONLY:
            return response.link.strip()
        if mode is PresentationMode.SOURCE_ONLY:
            return response.source.strip()

        lines = []
        for raw_line in response.body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.casefold().startswith(self._HIDDEN_PREFIXES):
                continue
            if line.startswith(("http://", "https://")):
                continue
            lines.append(line)
        return "\n".join(lines)
