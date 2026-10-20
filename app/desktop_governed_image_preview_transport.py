"""Bounded HTTPS transport for governed image previews."""

from __future__ import annotations

import http.client
import ipaddress
import math
import socket
import urllib.error
import urllib.request
from urllib.parse import urlsplit


_DEFAULT_TIMEOUT = 5.0
_DEFAULT_MAX_BYTES = 1_000_000
_CHUNK_SIZE = 64 * 1024


def _validate_url(url: str) -> None:
    if not isinstance(url, str) or not url:
        raise ValueError("A non-empty HTTPS URL is required")

    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Invalid image preview URL") from exc

    if parsed.scheme.casefold() != "https":
        raise ValueError("Image previews require HTTPS")

    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Invalid image preview authority")

    if port not in (None, 443):
        raise ValueError("Unsupported image preview port")

    host = parsed.hostname.rstrip(".").casefold()

    if host == "localhost" or host.endswith(".localhost"):
        raise ValueError("Local image preview destinations are forbidden")

    if host.endswith((".local", ".internal", ".test", ".invalid")):
        raise ValueError("Non-public image preview destinations are forbidden")

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None

    if address is not None and not address.is_global:
        raise ValueError("Non-public image preview addresses are forbidden")


def _validate_public_resolution(url: str) -> None:
    host = urlsplit(url).hostname
    if host is None:
        raise ValueError("Missing image preview hostname")

    try:
        addresses = socket.getaddrinfo(
            host,
            443,
            type=socket.SOCK_STREAM,
        )
    except OSError as exc:
        raise ValueError("Image preview hostname could not be resolved") from exc

    if not addresses:
        raise ValueError("Image preview hostname has no addresses")

    for address in addresses:
        resolved = ipaddress.ip_address(address[4][0])

        if not resolved.is_global:
            raise ValueError(
                "Image preview hostname resolves to a non-public address"
            )


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect only to DNS addresses validated as public."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._create_connection = self._connect_public_address

    def _connect_public_address(
        self,
        address: tuple[str, int],
        timeout: float,
        source_address: tuple[str, int] | None = None,
    ) -> socket.socket:
        host, port = address

        try:
            candidates = socket.getaddrinfo(
                host,
                port,
                type=socket.SOCK_STREAM,
            )
        except OSError as exc:
            raise ValueError("HTTPS destination resolution failed") from exc

        if not candidates:
            raise ValueError("HTTPS destination has no addresses")

        for candidate in candidates:
            resolved = ipaddress.ip_address(candidate[4][0])
            if not resolved.is_global:
                raise ValueError("HTTPS destination is not public")

        last_error: OSError | None = None

        for candidate in candidates:
            family, socktype, protocol, _, sockaddr = candidate
            sock = socket.socket(family, socktype, protocol)

            try:
                sock.settimeout(timeout)

                if source_address is not None:
                    sock.bind(source_address)

                sock.connect(sockaddr)
                return sock
            except OSError as exc:
                last_error = exc
                sock.close()

        raise OSError("Public HTTPS connection failed") from last_error


class _PinnedHTTPSHandler(urllib.request.HTTPSHandler):
    """Use the pinned connection while retaining normal TLS checks."""

    def https_open(
        self,
        request: urllib.request.Request,
    ) -> object:
        return self.do_open(
            _PinnedHTTPSConnection,
            request,
            context=self._context,
            check_hostname=self._check_hostname,
        )


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        response: object,
        code: int,
        message: str,
        headers: object,
        new_url: str,
    ) -> urllib.request.Request:
        _validate_url(new_url)
        _validate_public_resolution(new_url)

        return super().redirect_request(
            request,
            response,
            code,
            message,
            headers,
            new_url,
        )


def fetch_governed_image_preview(
    url: str,
    timeout: float = _DEFAULT_TIMEOUT,
    max_bytes: int = _DEFAULT_MAX_BYTES,
) -> tuple[bytes, str]:
    """Fetch a bounded image response from a public HTTPS destination."""
    if (
        isinstance(timeout, bool)
        or not isinstance(timeout, (int, float))
        or not math.isfinite(timeout)
        or timeout <= 0
    ):
        raise ValueError("Timeout must be a finite positive number")

    if (
        isinstance(max_bytes, bool)
        or not isinstance(max_bytes, int)
        or max_bytes <= 0
    ):
        raise ValueError("Maximum response size must be positive")

    _validate_url(url)
    _validate_public_resolution(url)

    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        _SafeRedirectHandler(),
        _PinnedHTTPSHandler(),
    )
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ROBY-Governed-Image-Preview/1.0"},
    )

    try:
        response = opener.open(request, timeout=timeout)
    except (OSError, urllib.error.URLError) as exc:
        raise ValueError("Image preview request failed") from exc

    with response:
        final_url = response.geturl()
        _validate_url(final_url)
        _validate_public_resolution(final_url)

        content_type = (
            response.headers.get("Content-Type", "")
            .split(";", 1)[0]
            .strip()
            .casefold()
        )

        if not content_type.startswith("image/"):
            raise ValueError("Response is not an image")

        declared_size = response.headers.get("Content-Length")

        if declared_size is not None:
            try:
                if int(declared_size) > max_bytes:
                    raise ValueError("Image preview exceeds size limit")
            except ValueError as exc:
                raise ValueError("Invalid image response size") from exc

        chunks: list[bytes] = []
        total = 0

        while True:
            chunk = response.read(
                min(_CHUNK_SIZE, max_bytes + 1 - total)
            )

            if not chunk:
                break

            total += len(chunk)

            if total > max_bytes:
                raise ValueError("Image preview exceeds size limit")

            chunks.append(chunk)

        if not chunks:
            raise ValueError("Image preview response is empty")

        return b"".join(chunks), content_type
