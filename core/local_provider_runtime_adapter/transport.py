from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LocalProviderTransportError(RuntimeError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class TransportResponse:
    status: int
    payload: dict[str, Any]


class LocalProviderTransport(Protocol):
    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None,
        timeout: float,
    ) -> TransportResponse: ...


class UrllibLocalProviderTransport:
    def request(
        self,
        *,
        method: str,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None,
        timeout: float,
    ) -> TransportResponse:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=timeout) as response:  # noqa: S310
                raw = response.read().decode("utf-8")
                data = json.loads(raw) if raw else {}
                if not isinstance(data, dict):
                    raise LocalProviderTransportError("invalid_json_shape")
                return TransportResponse(status=response.status, payload=data)
        except HTTPError as exc:
            raise LocalProviderTransportError(f"http_{exc.code}") from exc
        except URLError as exc:
            reason = getattr(exc, "reason", None)
            code = "timeout" if isinstance(reason, TimeoutError) else "unreachable"
            raise LocalProviderTransportError(code) from exc
        except TimeoutError as exc:
            raise LocalProviderTransportError("timeout") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LocalProviderTransportError("invalid_json") from exc
