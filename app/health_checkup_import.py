from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from uuid import uuid4

from app.document_reading import DocumentReadingService
from app.secure_health_checkups import (
    HealthCheckup,
    HealthCheckupRepository,
    LaboratoryResult,
)

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass(frozen=True)
class HealthCheckupImportResult:
    handled: bool
    response: str = ""


@dataclass
class _PendingImport:
    checkup: HealthCheckup
    warnings: list[str]


class AssistedHealthCheckupImportService:
    """Extracts a reviewable health-checkup draft from a local document."""

    _REQUEST = re.compile(
        r"^importar chequeo de (Carlos|Cristina):\s*(.+)$",
        flags=re.IGNORECASE,
    )
    _LAB_LINE = re.compile(
        r"^\s*(?P<name>[^|;\t:]+?)\s*(?:\||\t|:)\s*"
        r"(?P<value>[^|;\t]+?)"
        r"(?:\s*(?:\||\t)\s*(?P<unit>[^|;\t]*))?"
        r"(?:\s*(?:\||\t)\s*(?P<range>[^|;\t]*))?"
        r"(?:\s*(?:\||\t)\s*(?P<flag>[^|;\t]*))?\s*$"
    )

    def __init__(
        self,
        repository: HealthCheckupRepository | None = None,
        reader: DocumentReadingService | None = None,
    ) -> None:
        self.repository = repository or HealthCheckupRepository()
        self.reader = reader or DocumentReadingService()
        self._pending: dict[str, _PendingImport] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> HealthCheckupImportResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in {
            "confirmar importación",
            "confirmar importacion",
            "confirmá la importación",
        }:
            return self._confirm(key)
        if folded in {
            "cancelar importación",
            "cancelar importacion",
            "cancelá la importación",
        }:
            self._pending.pop(key, None)
            return HealthCheckupImportResult(
                handled=True,
                response="Cancelé la importación y no guardé datos de salud.",
            )

        match = self._REQUEST.match(normalized)
        if match is None:
            return HealthCheckupImportResult(handled=False)
        try:
            pending = self._build_pending(match.group(1), match.group(2))
        except (OSError, ValueError) as exc:
            return HealthCheckupImportResult(True, str(exc))
        self._pending[key] = pending
        return HealthCheckupImportResult(
            handled=True,
            response=self._render_review(pending),
        )

    def _build_pending(self, person: str, raw_fields: str) -> _PendingImport:
        fields = self._split_fields(raw_fields)
        source = fields.get("archivo", "").strip().strip('"\'“”')
        study = fields.get("estudio", "").strip()
        performed_on = fields.get("fecha", "").strip()
        kind = fields.get("tipo", "").strip().casefold()
        if not source or not study or not self._valid_date(performed_on):
            raise ValueError(
                "Indicá archivo, estudio y una fecha válida con formato AAAA-MM-DD."
            )
        if kind not in {"laboratorio", "informe"}:
            raise ValueError("El tipo debe ser laboratorio o informe.")
        path = Path(source).expanduser()
        content = self.reader.read_text(path)
        warnings: list[str] = []
        results: list[LaboratoryResult] = []
        report_text = ""
        if kind == "laboratorio":
            results, warnings = self._extract_laboratory(content)
            if not results:
                raise ValueError(
                    "No pude extraer resultados estructurados. "
                    "Usá líneas separadas con nombre | valor | unidad | rango | marca."
                )
        else:
            report_text = content
        checkup = HealthCheckup(
            record_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[person.casefold()],
            study_type=study,
            performed_on=performed_on,
            category=kind,
            institution=fields.get("institución", fields.get("institucion", "")),
            professional=fields.get("profesional", ""),
            source_file=str(path.resolve()),
            report_text=report_text,
            laboratory_results=results,
        )
        return _PendingImport(checkup, warnings)

    def _extract_laboratory(
        self,
        content: str,
    ) -> tuple[list[LaboratoryResult], list[str]]:
        results: list[LaboratoryResult] = []
        warnings: list[str] = []
        for number, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            match = self._LAB_LINE.match(stripped)
            if match is None:
                warnings.append(f"línea {number} no reconocida")
                continue
            values = {
                key: (value or "").strip()
                for key, value in match.groupdict().items()
            }
            if not values["name"] or not values["value"]:
                warnings.append(f"línea {number} incompleta")
                continue
            results.append(
                LaboratoryResult(
                    name=values["name"],
                    value=values["value"],
                    unit=values["unit"],
                    reference_range=values["range"],
                    flag=values["flag"],
                )
            )
        return results, warnings

    def _confirm(self, key: str) -> HealthCheckupImportResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return HealthCheckupImportResult(
                handled=True,
                response="No hay una importación pendiente para confirmar.",
            )
        records = self.repository.load()
        records.append(pending.checkup)
        self.repository.save(records)
        return HealthCheckupImportResult(
            handled=True,
            response=(
                f"Guardé la importación {pending.checkup.record_id} de "
                f"{pending.checkup.person}. No realicé interpretación clínica."
            ),
        )

    def _render_review(self, pending: _PendingImport) -> str:
        checkup = pending.checkup
        if checkup.category == "laboratorio":
            detail = f"{len(checkup.laboratory_results)} resultados detectados"
        else:
            detail = f"informe narrativo de {len(checkup.report_text)} caracteres"
        warning = ""
        if pending.warnings:
            warning = (
                f" Advertencias: {len(pending.warnings)} líneas requieren revisión."
            )
        return (
            f"Preparé una importación para {checkup.person}: "
            f"{checkup.study_type}, fecha {checkup.performed_on}, {detail}."
            f"{warning} Revisá el archivo y decí 'confirmar importación' para "
            "guardar o 'cancelar importación' para descartar."
        )

    def _split_fields(self, value: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in value.split("|"):
            name, separator, content = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = content.strip()
        return fields

    def _valid_date(self, value: str) -> bool:
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True
