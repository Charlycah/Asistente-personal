"""RED contracts for governed image preview transport."""

from __future__ import annotations

import io
from unittest.mock import patch

import pytest


PNG = b"\\x89PNG\\r\\n\\x1a\\n" + b"test"
JPEG = b"\\xff\\xd8\\xff" + b"test"


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        content_type: str = "image/png",
        final_url: str = "https://upload.wikimedia.org/test.png",
    ) -> None:
        self._stream = io.BytesIO(payload)
        self.headers = {"Content-Type": content_type}
        self._final_url = final_url

    def read(self, size: int = -1) -> bytes:
        return self._stream.read(size)

    def geturl(self) -> str:
        return self._final_url

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        self._stream.close()


def _fetch(
    url: str = "https://upload.wikimedia.org/test.png",
    timeout: float = 5.0,
    max_bytes: int = 1_000_000,
) -> tuple[bytes, str]:
    from app.desktop_governed_image_preview_transport import (
        fetch_governed_image_preview,
    )

    return fetch_governed_image_preview(url, timeout, max_bytes)


def test_accepts_bounded_https_image_preview() -> None:
    response = FakeResponse(PNG)

    with patch(
        "urllib.request.build_opener"
    ) as build_opener:
        opener = build_opener.return_value
        opener.open.return_value = response
        payload, content_type = _fetch()

    assert payload == PNG
    assert content_type == "image/png"


@pytest.mark.parametrize(
    "url",
    [
        "http://upload.wikimedia.org/test.png",
        "file:///C:/secret.txt",
        "https://localhost/test.png",
        "https://127.0.0.1/test.png",
        "https://192.168.1.1/test.png",
        "https://169.254.169.254/test.png",
        "https://user:password@upload.wikimedia.org/test.png",
    ],
)
def test_rejects_unsafe_preview_urls(url: str) -> None:
    with patch("urllib.request.urlopen") as opener:
        with pytest.raises(ValueError):
            _fetch(url)

    opener.assert_not_called()


def test_rejects_oversized_payload() -> None:
    response = FakeResponse(PNG + b"x" * 100)

    with patch(
        "urllib.request.urlopen",
        return_value=response,
    ):
        with pytest.raises(ValueError):
            _fetch(max_bytes=16)


def test_rejects_non_image_content_type() -> None:
    response = FakeResponse(
        b"<html>not an image</html>",
        content_type="text/html",
    )

    with patch(
        "urllib.request.urlopen",
        return_value=response,
    ):
        with pytest.raises(ValueError):
            _fetch()


def test_rejects_redirect_to_local_destination() -> None:
    response = FakeResponse(
        PNG,
        final_url="http://127.0.0.1/private.png",
    )

    with patch(
        "urllib.request.urlopen",
        return_value=response,
    ):
        with pytest.raises(ValueError):
            _fetch()


@pytest.mark.parametrize(
    "timeout,max_bytes",
    [
        (0.0, 100),
        (-1.0, 100),
        (5.0, 0),
        (5.0, -1),
    ],
)
def test_rejects_invalid_limits(
    timeout: float,
    max_bytes: int,
) -> None:
    with patch("urllib.request.urlopen") as opener:
        with pytest.raises(ValueError):
            _fetch(timeout=timeout, max_bytes=max_bytes)

    opener.assert_not_called()


def test_transport_does_not_depend_on_tkinter() -> None:
    from pathlib import Path

    path = Path(
        "app/desktop_governed_image_preview_transport.py"
    )
    source = path.read_text(encoding="utf-8")

    assert "import tkinter" not in source
    assert "from tkinter" not in source
