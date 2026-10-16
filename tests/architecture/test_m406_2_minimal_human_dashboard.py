from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from application.governed_web_panel import GovernedWebPanelReadModel
from infrastructure.web_panel_http import LocalWebPanelHttpService

NOW = datetime(2026, 8, 11, 23, 0, tzinfo=timezone.utc)


def _read_model(
    *,
    system_reader=lambda: {
        "system_status": "running",
        "runtime_ready": True,
    },
    residence_reader=lambda: {
        "residence_id": "primary-home",
        "node_status": "ready",
    },
    synchronization_reader=lambda: None,
    resources_reader=lambda: {
        "resource_count": 0,
        "resources": (),
    },
) -> GovernedWebPanelReadModel:
    return GovernedWebPanelReadModel(
        system_reader=system_reader,
        residence_reader=residence_reader,
        synchronization_reader=synchronization_reader,
        resources_reader=resources_reader,
        clock=lambda: NOW,
    )


def _request(port: int, path: str = "/", method: str = "GET"):
    request = Request(f"http://127.0.0.1:{port}{path}", method=method)
    return urlopen(request, timeout=2.0)  # noqa: S310


def test_m406_2_root_is_server_rendered_local_dashboard() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port) as response:
            html = response.read().decode("utf-8")
            assert response.status == 200
            assert response.headers["Content-Type"] == "text/html; charset=utf-8"
            assert response.headers["Cache-Control"] == "no-store"
            assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "ROBY XI.2" in html
        assert "Local Governed Status" in html
        for section in ("System", "Residence", "Synchronization", "Resources"):
            assert section in html
    finally:
        service.stop()


def test_m406_2_dashboard_uses_only_m406_1_snapshot_content() -> None:
    model = _read_model()
    expected = model.snapshot().to_dict()
    service = LocalWebPanelHttpService(model)
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port) as response:
            html = response.read().decode("utf-8")
        assert expected["system"]["payload"]["system_status"] in html
        assert expected["residence"]["payload"]["residence_id"] in html
        assert expected["system"]["classification"] in html
        assert expected["residence"]["classification"] in html
    finally:
        service.stop()


def test_m406_2_dynamic_values_are_html_escaped() -> None:
    malicious = {"system_status": "<script>alert(1)</script>"}
    service = LocalWebPanelHttpService(
        _read_model(system_reader=lambda: malicious)
    )
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port) as response:
            html = response.read().decode("utf-8")
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    finally:
        service.stop()


def test_m406_2_dashboard_has_no_javascript_polling_or_external_assets() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port) as response:
            html = response.read().decode("utf-8").casefold()
        assert "<script" not in html
        assert "setinterval" not in html
        assert "fetch(" not in html
        assert "http://" not in html
        assert "https://" not in html
        assert "refresh\" content=" not in html
    finally:
        service.stop()


def test_m406_2_dashboard_failure_is_safe_html_503() -> None:
    class BrokenReadModel:
        def snapshot(self):
            raise RuntimeError("secret internal traceback material")

    service = LocalWebPanelHttpService(BrokenReadModel())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with pytest.raises(HTTPError) as exc_info:
            _request(service.bound_port)
        response = exc_info.value
        body = response.read().decode("utf-8")
        assert response.code == 503
        assert response.headers["Content-Type"] == "text/html; charset=utf-8"
        assert "temporarily unavailable" in body
        assert "secret internal traceback material" not in body
        assert service.is_running is True
    finally:
        service.stop()


def test_m406_2_head_root_is_html_without_body() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port, method="HEAD") as response:
            assert response.status == 200
            assert response.headers["Content-Type"] == "text/html; charset=utf-8"
            assert response.read() == b""
    finally:
        service.stop()


def test_m406_2_api_status_contract_remains_json() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with _request(service.bound_port, path="/api/status") as response:
            payload = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
        assert payload["surface"] == "local_private"
        assert payload["authorizes_action"] is False
        assert payload["persists_state"] is False
    finally:
        service.stop()


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_m406_2_dashboard_mutation_methods_remain_rejected(method: str) -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with pytest.raises(HTTPError) as exc_info:
            _request(service.bound_port, method=method)
        assert exc_info.value.code == 405
    finally:
        service.stop()
