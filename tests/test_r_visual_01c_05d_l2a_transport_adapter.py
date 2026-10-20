from __future__ import annotations

from unittest.mock import patch

from app.desktop_governed_image_preview_fetch_adapter import (
    fetch_desktop_governed_preview,
)


def test_adapter_preserves_named_transport_limits():
    expected = (b"preview", "image/png")

    with patch(
        "app.desktop_governed_image_preview_fetch_adapter."
        "fetch_governed_image_preview",
        return_value=expected,
    ) as transport:
        result = fetch_desktop_governed_preview(
            "https://example.org/preview.png",
            5.0,
            1_000_000,
        )

    assert result == expected
    transport.assert_called_once_with(
        "https://example.org/preview.png",
        timeout=5.0,
        max_bytes=1_000_000,
    )
