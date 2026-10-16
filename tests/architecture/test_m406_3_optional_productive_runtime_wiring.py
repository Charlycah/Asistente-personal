from __future__ import annotations

from app.resident_component_registry import ResidentCriticality
from app.web_panel_runtime import (
    DEFAULT_WEB_PANEL_PORT,
    build_local_web_panel_service,
    web_panel_enabled_from_environment,
)
from infrastructure.web_panel_http import LocalWebPanelServiceStatus


class _Operational:
    status = type("Value", (), {"value": "running"})()
    health = type("Value", (), {"value": "healthy"})()
    generated_at = type(
        "Stamp",
        (),
        {"isoformat": lambda self: "2026-08-11T23:00:00+00:00"},
    )()


class _Readiness:
    ready = True


class _Runtime:
    def snapshot(self):
        return _Operational()

    def readiness(self):
        return _Readiness()


def test_m406_3_web_panel_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("ROBY_WEB_PANEL_ENABLED", raising=False)
    assert web_panel_enabled_from_environment() is False


def test_m406_3_web_panel_requires_explicit_opt_in(monkeypatch) -> None:
    monkeypatch.setenv("ROBY_WEB_PANEL_ENABLED", "true")
    assert web_panel_enabled_from_environment() is True


def test_m406_3_default_productive_port_is_fixed_and_local(monkeypatch) -> None:
    monkeypatch.delenv("ROBY_WEB_PANEL_PORT", raising=False)
    service = build_local_web_panel_service(_Runtime())
    assert service.service.status is LocalWebPanelServiceStatus.STOPPED
    assert service.service._config.host == "127.0.0.1"
    assert service.service._config.port == DEFAULT_WEB_PANEL_PORT


def test_m406_3_environment_port_is_validated(monkeypatch) -> None:
    monkeypatch.setenv("ROBY_WEB_PANEL_PORT", "8766")
    service = build_local_web_panel_service(_Runtime())
    assert service.service._config.port == 8766


def test_m406_3_missing_domain_sources_remain_explicit_no_data() -> None:
    service = build_local_web_panel_service(_Runtime(), port=0)
    snapshot = service.service._read_model.snapshot()
    assert snapshot.system.status.value == "available"
    assert snapshot.residence.status.value == "no_data"
    assert snapshot.synchronization.status.value == "no_data"
    assert snapshot.resources.status.value == "no_data"


def test_m406_3_desktop_registers_panel_as_optional_resident() -> None:
    source = open("app/desktop_bootstrap.py", encoding="utf-8").read()
    assert 'component_id="web_panel_local"' in source
    assert "criticality=ResidentCriticality.OPTIONAL" in source
    assert "build_local_web_panel_service(personal_runtime)" in source
    assert "web_panel_enabled_from_environment()" in source


def test_m406_3_does_not_use_residential_runtime_or_conversation_gateway() -> None:
    source = open("app/web_panel_runtime.py", encoding="utf-8").read()
    assert "ResidentRuntimeService" not in source
    assert "OfficialConversationGateway" not in source
    assert "RuntimeCompositionRoot" not in source


def test_m406_3_registration_criticality_remains_optional() -> None:
    assert ResidentCriticality.OPTIONAL.value == "optional"


def test_m406_3_resident_reports_http_bind_failure() -> None:
    class FailingService:
        last_failure_code = "bind_failed"

        def start(self):
            return False

        def stop(self):
            return None

    from app.web_panel_runtime import ProductiveWebPanelResident

    resident = ProductiveWebPanelResident(FailingService())
    import pytest

    with pytest.raises(RuntimeError, match="bind_failed"):
        resident.start()
