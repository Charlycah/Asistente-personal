"""R-VISUAL-01C-04C: isolated transport security contract."""

from unittest.mock import patch

import pytest

from app.desktop_governed_image_preview_transport import (
    _SafeRedirectHandler,
    fetch_governed_image_preview,
)


PUBLIC_URL = "https://upload.wikimedia.org/test.png"
PRIVATE_URL = "https://127.0.0.1/private.png"
PNG = b"\\x89PNG\\r\\n\\x1a\\n" + b"data"


class FakeResponse:
    def __init__(
        self,
        payload: bytes,
        content_type: str = "image/png",
        final_url: str = PUBLIC_URL,
    ) -> None:
        self.payload = payload
        self.position = 0
        self.headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(payload)),
        }
        self.final_url = final_url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.final_url

    def read(self, size=-1):
        if size < 0:
            raise AssertionError("Unbounded read forbidden")
        chunk = self.payload[self.position:self.position + size]
        self.position += len(chunk)
        return chunk


def public_dns(*args, **kwargs):
    return [
        (2, 1, 6, "", ("208.80.154.224", 443)),
    ]


def private_dns(*args, **kwargs):
    return [
        (2, 1, 6, "", ("127.0.0.1", 443)),
    ]


def test_bounded_image_response_without_network():
    response = FakeResponse(PNG)

    with patch("socket.getaddrinfo", side_effect=public_dns):
        with patch("urllib.request.build_opener") as factory:
            factory.return_value.open.return_value = response
            result = fetch_governed_image_preview(PUBLIC_URL)

    assert result == (PNG, "image/png")
    factory.return_value.open.assert_called_once()


def test_private_dns_rejected_before_open():
    with patch("socket.getaddrinfo", side_effect=private_dns):
        with patch("urllib.request.build_opener") as factory:
            with pytest.raises(ValueError):
                fetch_governed_image_preview(PUBLIC_URL)

    factory.return_value.open.assert_not_called()


def test_private_redirect_rejected():
    handler = _SafeRedirectHandler()

    with patch("socket.getaddrinfo", side_effect=public_dns):
        with pytest.raises(ValueError):
            handler.redirect_request(
                None,
                None,
                302,
                "Found",
                {},
                PRIVATE_URL,
            )


def test_non_image_content_type_rejected():
    response = FakeResponse(PNG, content_type="text/html")

    with patch("socket.getaddrinfo", side_effect=public_dns):
        with patch("urllib.request.build_opener") as factory:
            factory.return_value.open.return_value = response
            with pytest.raises(ValueError):
                fetch_governed_image_preview(PUBLIC_URL)


def test_oversized_stream_rejected():
    response = FakeResponse(PNG + b"x" * 128)

    with patch("socket.getaddrinfo", side_effect=public_dns):
        with patch("urllib.request.build_opener") as factory:
            factory.return_value.open.return_value = response
            with pytest.raises(ValueError):
                fetch_governed_image_preview(
                    PUBLIC_URL,
                    max_bytes=16,
                )


def test_dns_rebinding_cannot_reach_private_address():
    """A second DNS answer must not reach a private connection."""
    import socket

    original_getaddrinfo = socket.getaddrinfo
    calls = []
    attempted_private_connection = []

    def changing_dns(host, port, *args, **kwargs):
        if host != "upload.wikimedia.org":
            return original_getaddrinfo(
                host, port, *args, **kwargs
            )

        calls.append(host)

        if len(calls) == 1:
            address = "208.80.154.224"
        else:
            address = "127.0.0.1"

        return [
            (
                socket.AF_INET,
                socket.SOCK_STREAM,
                socket.IPPROTO_TCP,
                "",
                (address, port),
            ),
        ]

    def guarded_connect(address, *args, **kwargs):
        host = address[0]

        if host == "127.0.0.1":
            attempted_private_connection.append(address)

        raise OSError("Simulated connection blocked")

    with patch(
        "socket.getaddrinfo",
        side_effect=changing_dns,
    ):
        with patch(
            "socket.socket.connect",
            side_effect=guarded_connect,
        ):
            with pytest.raises(ValueError):
                fetch_governed_image_preview(PUBLIC_URL)

    assert not attempted_private_connection, (
        "DNS rebinding reached a private connection attempt"
    )
