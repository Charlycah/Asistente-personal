"""Positional adapter for the governed HTTPS preview transport."""

from __future__ import annotations

from app.desktop_governed_image_preview_transport import (
    fetch_governed_image_preview,
)


def fetch_desktop_governed_preview(
    url: str,
    timeout: float,
    max_bytes: int,
) -> tuple[bytes, str]:
    """Preserve coordinator compatibility and named transport limits."""
    return fetch_governed_image_preview(
        url,
        timeout=timeout,
        max_bytes=max_bytes,
    )
