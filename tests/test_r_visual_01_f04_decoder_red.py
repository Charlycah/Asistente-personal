"""R-VISUAL-01-F04: governed JPEG decoder RED."""

from __future__ import annotations

import base64

from app.desktop_governed_image_preview_decoder import (
    decode_governed_jpeg_preview,
)

JPEG_BASE64 = (
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYI"
    "DAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkF"
    "BQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQU"
    "FBQUFBT/wAARCAACAAIDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQF"
    "BgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEI"
    "I0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNk"
    "ZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLD"
    "xMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEB"
    "AQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJB"
    "UQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZH"
    "SElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaan"
    "qKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oA"
    "DAMBAAIRAxEAPwD7V/Z2+C3w91v9n74ZajqPgTwzf6heeF9MuLm7utHt5JZ5XtImd3dk"
    "JZmJJJJySSTRRRXyOL/3ip/if5nwmO/3qr/il+bP/9k="
)


def jpeg_payload():
    return base64.b64decode(JPEG_BASE64, validate=True)


def test_valid_jpeg_returns_png():
    payload = jpeg_payload()

    assert payload.startswith(bytes.fromhex("ffd8"))
    assert payload.endswith(bytes.fromhex("ffd9"))

    result = decode_governed_jpeg_preview(
        payload,
        "image/jpeg",
    )

    assert isinstance(result, bytes)
    assert result.startswith(b"\x89PNG\r\n\x1a\n")


def test_corrupt_jpeg_is_rejected():
    result = decode_governed_jpeg_preview(
        b"not-a-jpeg",
        "image/jpeg",
    )

    assert result is None


def test_wrong_mime_is_rejected():
    result = decode_governed_jpeg_preview(
        jpeg_payload(),
        "text/plain",
    )

    assert result is None


def test_oversized_dimension_is_rejected():
    result = decode_governed_jpeg_preview(
        jpeg_payload(),
        "image/jpeg",
        max_dimension=0,
    )

    assert result is None
