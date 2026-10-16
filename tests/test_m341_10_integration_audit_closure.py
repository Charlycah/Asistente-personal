from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from app.desktop_ui import DesktopConversationController
from app.m341_stage_closure import M341StageClosureService


class StubAdapter:
    def submit_text(self, text: str, session_id: str | None = None):
        raise AssertionError("No debe llegar al adaptador general.")


class VoiceAdapter:
    def submit_text(self, text: str, session_id: str | None = None):
        raise AssertionError("No debe llegar al adaptador general.")

    def submit_voice(self, text: str, session_id: str | None = None):
        raise AssertionError("No debe llegar al adaptador de voz.")


class FixedVoiceInput:
    def __init__(self, text: str) -> None:
        self.text = text

    def transcribe(self) -> str:
        return self.text


def fixed_clock() -> datetime:
    return datetime(2026, 7, 28, 18, 30, 0)


def test_ignores_unrelated_request() -> None:
    result = M341StageClosureService().prepare("hola roby")
    assert result.handled is False


def test_reports_all_stage_capabilities() -> None:
    result = M341StageClosureService(clock=fixed_clock).prepare(
        "estado de integración M341"
    )
    assert result.handled is True
    assert "9/9" in result.response
    assert "M341.1" in result.response
    assert "M341.9" in result.response


def test_audit_is_closed_when_every_component_is_integrated() -> None:
    report = M341StageClosureService(clock=fixed_clock).audit()
    assert report.status == "cerrada"
    assert all(check.passed for check in report.checks)


def test_audit_detects_missing_component() -> None:
    service = M341StageClosureService(clock=fixed_clock)
    integrations = {
        capability.component: True
        for capability in service.CAPABILITIES
    }
    integrations["DeviceArchitectureService"] = False
    report = service.audit(integrations=integrations)
    assert report.status == "incompleta"
    assert report.checks[-1].passed is False


def test_exports_json_closure_report(tmp_path: Path) -> None:
    service = M341StageClosureService(
        output_dir=tmp_path,
        clock=fixed_clock,
    )
    result = service.prepare("generar informe de cierre M341")
    assert result.report_path == tmp_path / "cierre_m341_20260728_183000.json"
    payload = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert payload["status"] == "cerrada"
    assert len(payload["capabilities"]) == 9


def test_export_records_safety_boundaries(tmp_path: Path) -> None:
    service = M341StageClosureService(
        output_dir=tmp_path,
        clock=fixed_clock,
    )
    result = service.prepare("exportar auditoría M341")
    payload = json.loads(result.report_path.read_text(encoding="utf-8"))
    assert payload["safety"]["clinical_actions_executed"] is False
    assert payload["safety"]["hardware_activated"] is False


def test_desktop_routes_stage_audit() -> None:
    controller = DesktopConversationController(StubAdapter())
    messages = controller.submit("auditar etapa M341")
    assert len(messages) == 2
    assert "Auditoría de integración" in messages[1].text


def test_voice_routes_stage_audit() -> None:
    controller = DesktopConversationController(
        VoiceAdapter(),
        voice_input=FixedVoiceInput("auditar etapa M341"),
    )
    messages = controller.submit_voice()
    assert len(messages) == 2
    assert "9/9" in messages[1].text


def test_voice_routes_device_architecture() -> None:
    controller = DesktopConversationController(
        VoiceAdapter(),
        voice_input=FixedVoiceInput("dispositivos disponibles"),
    )
    messages = controller.submit_voice()
    assert len(messages) == 2
    assert "arquitectura para dispositivos" in messages[1].text


def test_closure_preserves_default_no_side_effect_audit(tmp_path: Path) -> None:
    service = M341StageClosureService(
        output_dir=tmp_path,
        clock=fixed_clock,
    )
    result = service.prepare("cierre de etapa M341")
    assert result.handled is True
    assert result.report_path is None
    assert list(tmp_path.iterdir()) == []
