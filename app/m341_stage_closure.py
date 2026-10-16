from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class StageCapability:
    version: str
    name: str
    component: str


@dataclass(frozen=True)
class StageAuditCheck:
    check_id: str
    description: str
    passed: bool


@dataclass(frozen=True)
class StageAuditReport:
    stage: str
    generated_at: str
    status: str
    capabilities: tuple[StageCapability, ...]
    checks: tuple[StageAuditCheck, ...]


@dataclass(frozen=True)
class StageClosureResponse:
    handled: bool
    response: str
    report_path: Path | None = None


class M341StageClosureService:
    _STATUS_PATTERNS = (
        r"\bestado de integración m341\b",
        r"\bresumen de etapa m341\b",
        r"\bcierre de etapa m341\b",
    )
    _AUDIT_PATTERNS = (
        r"\bauditar etapa m341\b",
        r"\bauditá etapa m341\b",
        r"\bauditoria de etapa m341\b",
        r"\bauditoría de etapa m341\b",
    )
    _EXPORT_PATTERNS = (
        r"\bgenerar informe de cierre m341\b",
        r"\bexportar auditoria m341\b",
        r"\bexportar auditoría m341\b",
    )

    CAPABILITIES = (
        StageCapability(
            "M341.1",
            "Registro estructurado de síntomas",
            "StructuredSymptomService",
        ),
        StageCapability(
            "M341.2",
            "Alergias como entidades de primera clase",
            "AllergyRegistryService",
        ),
        StageCapability(
            "M341.3",
            "Seguimiento de condiciones crónicas",
            "ChronicConditionRegistryService",
        ),
        StageCapability(
            "M341.4",
            "Profesionales y centros de salud",
            "HealthcareDirectoryService",
        ),
        StageCapability(
            "M341.5",
            "Contactos y cobertura de emergencia",
            "EmergencyContactService",
        ),
        StageCapability(
            "M341.6",
            "Orquestador integral de salud",
            "HealthOrchestratorService",
        ),
        StageCapability(
            "M341.7",
            "Guía conversacional de salud",
            "ConversationalHealthGuidanceService",
        ),
        StageCapability(
            "M341.8",
            "Exportación médica en PDF",
            "MedicalPdfExportService",
        ),
        StageCapability(
            "M341.9",
            "Arquitectura para dispositivos",
            "DeviceArchitectureService",
        ),
    )

    def __init__(
        self,
        *,
        output_dir: Path | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.output_dir = output_dir or Path(".roby/audits")
        self.clock = clock or datetime.now

    def prepare(
        self,
        text: str,
        *,
        integrations: dict[str, bool] | None = None,
    ) -> StageClosureResponse:
        normalized = " ".join(text.strip().casefold().split())
        export_requested = self._matches(self._EXPORT_PATTERNS, normalized)
        audit_requested = self._matches(self._AUDIT_PATTERNS, normalized)
        status_requested = self._matches(self._STATUS_PATTERNS, normalized)
        if not (export_requested or audit_requested or status_requested):
            return StageClosureResponse(False, "")

        report = self.audit(integrations=integrations)
        response = self._render(report)
        if not export_requested:
            return StageClosureResponse(True, response)

        path = self._write_report(report)
        return StageClosureResponse(
            True,
            f"{response}\nInforme de cierre guardado en: {path}",
            path,
        )

    def audit(
        self,
        *,
        integrations: dict[str, bool] | None = None,
    ) -> StageAuditReport:
        integration_state = integrations or {
            capability.component: True for capability in self.CAPABILITIES
        }
        checks = tuple(
            StageAuditCheck(
                check_id=f"integration-{capability.version.casefold()}",
                description=(
                    f"{capability.version}: {capability.name} integrada"
                ),
                passed=bool(integration_state.get(capability.component, False)),
            )
            for capability in self.CAPABILITIES
        )
        status = "cerrada" if all(check.passed for check in checks) else "incompleta"
        return StageAuditReport(
            stage="M341",
            generated_at=self.clock().isoformat(timespec="seconds"),
            status=status,
            capabilities=self.CAPABILITIES,
            checks=checks,
        )

    @staticmethod
    def _matches(patterns: tuple[str, ...], text: str) -> bool:
        return any(re.search(pattern, text) for pattern in patterns)

    @staticmethod
    def _render(report: StageAuditReport) -> str:
        passed = sum(check.passed for check in report.checks)
        lines = [
            "Auditoría de integración de la etapa M341",
            f"Estado: {report.status}.",
            f"Componentes integrados: {passed}/{len(report.checks)}.",
        ]
        for check in report.checks:
            marker = "OK" if check.passed else "PENDIENTE"
            lines.append(f"- [{marker}] {check.description}")
        lines.extend(
            (
                "La auditoría no ejecuta acciones clínicas ni activa hardware.",
                "La validación técnica definitiva requiere Ruff y pytest.",
            )
        )
        return "\n".join(lines)

    def _write_report(self, report: StageAuditReport) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = self.clock().strftime("%Y%m%d_%H%M%S")
        path = self.output_dir / f"cierre_m341_{timestamp}.json"
        payload = {
            "stage": report.stage,
            "generated_at": report.generated_at,
            "status": report.status,
            "capabilities": [
                asdict(capability) for capability in report.capabilities
            ],
            "checks": [asdict(check) for check in report.checks],
            "safety": {
                "clinical_actions_executed": False,
                "hardware_activated": False,
            },
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path
