from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from app.web_panel_sources import ExternalResourcesWebPanelSource
from application.governed_web_panel import (
    GovernedWebPanelReadModel,
    GovernedWebPanelSnapshot,
    WebPanelSection,
    WebPanelSectionStatus,
    WebPanelSurface,
)
from core.external_resource_registry import (
    ExternalResourceConnectivityState,
    ExternalResourceKind,
    ExternalResourceRegistration,
    ExternalResourceRegistryAuthority,
)
from domain.information_classification import InformationClassification
from infrastructure.web_panel_http import (
    LocalWebPanelHttpConfig,
    LocalWebPanelHttpService,
    LocalWebPanelServiceStatus,
)

NOW = datetime(2026, 8, 11, 22, 0, tzinfo=timezone.utc)


def _read_model(
    *,
    system_reader=lambda: {"system_status": "running", "runtime_ready": True},
    residence_reader=lambda: {"residence_id": "primary-home", "node_status": "ready"},
    synchronization_reader=lambda: None,
    resources_reader=lambda: {"resource_count": 0, "resources": ()},
) -> GovernedWebPanelReadModel:
    return GovernedWebPanelReadModel(
        system_reader=system_reader,
        residence_reader=residence_reader,
        synchronization_reader=synchronization_reader,
        resources_reader=resources_reader,
        clock=lambda: NOW,
    )


def _request(port: int, path: str = "/api/status", method: str = "GET"):
    request = Request(f"http://127.0.0.1:{port}{path}", method=method)
    return urlopen(request, timeout=2.0)  # noqa: S310


def test_m406_1_snapshot_is_local_read_only_and_non_persistent() -> None:
    snapshot = _read_model().snapshot()
    assert isinstance(snapshot, GovernedWebPanelSnapshot)
    assert snapshot.surface is WebPanelSurface.LOCAL_PRIVATE
    assert snapshot.authorizes_action is False
    assert snapshot.persists_state is False
    assert snapshot.generated_at == NOW


def test_m406_1_sections_have_explicit_conservative_classification() -> None:
    snapshot = _read_model().snapshot()
    assert snapshot.system.classification is InformationClassification.PERSONAL
    assert snapshot.residence.classification is InformationClassification.PRIVATE
    assert snapshot.synchronization.classification is InformationClassification.PRIVATE
    assert snapshot.resources.classification is InformationClassification.PRIVATE


def test_m406_1_sensitive_or_unclassified_sections_cannot_be_exposed() -> None:
    with pytest.raises(ValueError, match="classification"):
        WebPanelSection(
            section_id="system",
            status=WebPanelSectionStatus.AVAILABLE,
            classification=InformationClassification.SENSITIVE,
            payload={"status": "running"},
        )
    with pytest.raises(ValueError, match="classification"):
        WebPanelSection(
            section_id="system",
            status=WebPanelSectionStatus.AVAILABLE,
            classification=InformationClassification.UNCLASSIFIED,
            payload={"status": "running"},
        )


def test_m406_1_unavailable_source_degrades_only_its_section() -> None:
    def unavailable():
        raise RuntimeError("source failed")

    snapshot = _read_model(residence_reader=unavailable).snapshot()
    assert snapshot.system.status is WebPanelSectionStatus.AVAILABLE
    assert snapshot.residence.status is WebPanelSectionStatus.UNAVAILABLE
    assert snapshot.residence.payload == {}
    assert snapshot.resources.status is WebPanelSectionStatus.AVAILABLE


def test_m406_1_missing_source_is_explicit_no_data() -> None:
    snapshot = _read_model(synchronization_reader=lambda: None).snapshot()
    assert snapshot.synchronization.status is WebPanelSectionStatus.NO_DATA
    assert snapshot.synchronization.payload == {}



def test_m406_1_resource_source_excludes_endpoint_metadata_and_external_ref() -> None:
    registry = ExternalResourceRegistryAuthority()
    registry.register(
        ExternalResourceRegistration(
            resource_id="camera-living",
            label="Living camera",
            kind=ExternalResourceKind.CAMERA,
            source_authority="owner",
            external_ref="rtsp://user:secret@example.invalid/live",
            capabilities=("image_frame",),
            metadata={"token": "do-not-expose"},
        )
    )
    registry.declare_connectivity(
        "camera-living",
        state=ExternalResourceConnectivityState.CONFIGURED,
        transport_type="rtsp",
        endpoint_reference="rtsp://user:secret@example.invalid/live",
        source="owner",
        declared_at=NOW.isoformat(),
    )
    payload = ExternalResourcesWebPanelSource(registry).read()
    serialized = json.dumps(payload)
    assert "camera-living" in serialized
    assert "image_frame" in serialized
    assert "secret" not in serialized
    assert "endpoint" not in serialized
    assert "token" not in serialized


def test_m406_1_http_config_is_strictly_ipv4_loopback() -> None:
    assert LocalWebPanelHttpConfig().host == "127.0.0.1"
    for host in ("localhost", "0.0.0.0", "::1", "192.168.1.10"):
        with pytest.raises(ValueError, match="127.0.0.1"):
            LocalWebPanelHttpConfig(host=host, port=0)


def test_m406_1_http_status_route_is_read_only_json_with_no_store() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.status is LocalWebPanelServiceStatus.RUNNING
        assert service.bound_port is not None
        with _request(service.bound_port) as response:
            body = json.loads(response.read().decode("utf-8"))
            assert response.status == 200
            assert response.headers["Content-Type"] == "application/json; charset=utf-8"
            assert response.headers["Cache-Control"] == "no-store"
            assert response.headers["X-Content-Type-Options"] == "nosniff"
            assert response.headers.get("Access-Control-Allow-Origin") is None
        assert body["surface"] == "local_private"
        assert body["authorizes_action"] is False
        assert body["persists_state"] is False
    finally:
        service.stop()


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_m406_1_mutation_methods_are_rejected(method: str) -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with pytest.raises(HTTPError) as exc_info:
            _request(service.bound_port, method=method)
        assert exc_info.value.code == 405
    finally:
        service.stop()


def test_m406_1_unknown_route_is_404() -> None:
    service = LocalWebPanelHttpService(_read_model())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with pytest.raises(HTTPError) as exc_info:
            _request(service.bound_port, path="/not-a-route")
        assert exc_info.value.code == 404
    finally:
        service.stop()


def test_m406_1_http_read_model_failure_is_503_not_server_crash() -> None:
    class BrokenReadModel:
        def snapshot(self):
            raise RuntimeError("broken")

    service = LocalWebPanelHttpService(BrokenReadModel())
    try:
        assert service.start() is True
        assert service.bound_port is not None
        with pytest.raises(HTTPError) as exc_info:
            _request(service.bound_port)
        assert exc_info.value.code == 503
        assert service.is_running is True
    finally:
        service.stop()


def test_m406_1_bind_failure_is_local_panel_failure_only() -> None:
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]
    try:
        service = LocalWebPanelHttpService(
            _read_model(),
            config=LocalWebPanelHttpConfig(port=port),
        )
        assert service.start() is False
        assert service.status is LocalWebPanelServiceStatus.UNAVAILABLE
        assert service.last_failure_code == "bind_failed"
        assert service.bound_port is None
    finally:
        blocker.close()


def test_m406_1_service_start_stop_is_idempotent() -> None:
    service = LocalWebPanelHttpService(_read_model())
    assert service.start() is True
    first_port = service.bound_port
    assert service.start() is True
    assert service.bound_port == first_port
    service.stop()
    service.stop()
    assert service.status is LocalWebPanelServiceStatus.STOPPED
    assert service.is_running is False
