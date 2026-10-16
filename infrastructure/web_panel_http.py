from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from enum import Enum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from application.governed_web_panel import WebPanelReadModelPort
from infrastructure.web_panel_html import render_governed_web_panel


class LocalWebPanelServiceStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True, slots=True)
class LocalWebPanelHttpConfig:
    host: str = "127.0.0.1"
    port: int = 0

    def __post_init__(self) -> None:
        if self.host != "127.0.0.1":
            raise ValueError("minimal web panel must bind exactly to 127.0.0.1")
        if not 0 <= self.port <= 65535:
            raise ValueError("web panel port must be between 0 and 65535")


class _LocalThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class LocalWebPanelHttpService:
    """Optional loopback-only read surface; never owns ROBY domain state."""

    def __init__(
        self,
        read_model: WebPanelReadModelPort,
        *,
        config: LocalWebPanelHttpConfig | None = None,
    ) -> None:
        self._read_model = read_model
        self._config = config or LocalWebPanelHttpConfig()
        self._server: _LocalThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._status = LocalWebPanelServiceStatus.STOPPED
        self._last_failure_code = ""

    @property
    def status(self) -> LocalWebPanelServiceStatus:
        return self._status

    @property
    def is_running(self) -> bool:
        return self._status is LocalWebPanelServiceStatus.RUNNING

    @property
    def bound_port(self) -> int | None:
        if self._server is None:
            return None
        return int(self._server.server_address[1])

    @property
    def last_failure_code(self) -> str:
        return self._last_failure_code

    def start(self) -> bool:
        if self.is_running:
            return True
        handler = _handler_factory(self._read_model)
        try:
            server = _LocalThreadingHTTPServer(
                (self._config.host, self._config.port),
                handler,
            )
        except OSError:
            self._status = LocalWebPanelServiceStatus.UNAVAILABLE
            self._last_failure_code = "bind_failed"
            return False
        thread = threading.Thread(
            target=server.serve_forever,
            name="roby-local-web-panel",
            daemon=True,
        )
        self._server = server
        self._thread = thread
        self._last_failure_code = ""
        self._status = LocalWebPanelServiceStatus.RUNNING
        thread.start()
        return True

    def stop(self) -> None:
        server = self._server
        thread = self._thread
        self._server = None
        self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None and thread.is_alive():
            thread.join(timeout=2.0)
        self._status = LocalWebPanelServiceStatus.STOPPED


def _handler_factory(
    read_model: WebPanelReadModelPort,
) -> type[BaseHTTPRequestHandler]:
    class LocalWebPanelRequestHandler(BaseHTTPRequestHandler):
        server_version = "ROBYLocalPanel/1"
        sys_version = ""

        def do_GET(self) -> None:  # noqa: N802
            path = urlsplit(self.path).path
            if path == "/api/status":
                self._serve_status_json()
                return
            if path == "/":
                self._serve_dashboard_html()
                return
            self._send_json(404, {"error": "not_found"})

        def do_HEAD(self) -> None:  # noqa: N802
            path = urlsplit(self.path).path
            if path == "/api/status":
                self._send_headers(
                    200,
                    0,
                    content_type="application/json; charset=utf-8",
                )
                return
            if path == "/":
                self._send_headers(
                    200,
                    0,
                    content_type="text/html; charset=utf-8",
                )
                return
            self._send_headers(
                404,
                0,
                content_type="application/json; charset=utf-8",
            )

        def do_POST(self) -> None:  # noqa: N802
            self._method_not_allowed()

        def do_PUT(self) -> None:  # noqa: N802
            self._method_not_allowed()

        def do_PATCH(self) -> None:  # noqa: N802
            self._method_not_allowed()

        def do_DELETE(self) -> None:  # noqa: N802
            self._method_not_allowed()

        def log_message(self, format: str, *args: object) -> None:
            return None

        def _serve_status_json(self) -> None:
            try:
                payload = read_model.snapshot().to_dict()
            except Exception:
                self._send_json(503, {"error": "read_model_unavailable"})
                return
            self._send_json(200, payload)

        def _serve_dashboard_html(self) -> None:
            try:
                page = render_governed_web_panel(read_model.snapshot())
            except Exception:
                self._send_html(
                    503,
                    "<h1>ROBY status temporarily unavailable.</h1>",
                )
                return
            self._send_html(200, page)

        def _method_not_allowed(self) -> None:
            self._send_json(405, {"error": "method_not_allowed"})

        def _send_json(self, status: int, payload: dict[str, object]) -> None:
            body = json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
            self._send_headers(
                status,
                len(body),
                content_type="application/json; charset=utf-8",
            )
            self.wfile.write(body)

        def _send_html(self, status: int, page: str) -> None:
            body = page.encode("utf-8")
            self._send_headers(
                status,
                len(body),
                content_type="text/html; charset=utf-8",
            )
            self.wfile.write(body)

        def _send_headers(
            self,
            status: int,
            content_length: int,
            *,
            content_type: str,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(content_length))
            self.end_headers()

    return LocalWebPanelRequestHandler
