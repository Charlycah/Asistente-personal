from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass(frozen=True)
class LaboratoryResult:
    name: str
    value: str
    unit: str = ""
    reference_range: str = ""
    flag: str = ""


@dataclass
class HealthCheckup:
    record_id: str
    person: str
    study_type: str
    performed_on: str
    category: str
    institution: str = ""
    professional: str = ""
    source_file: str = ""
    report_text: str = ""
    laboratory_results: list[LaboratoryResult] = field(default_factory=list)
    archived: bool = False


@dataclass(frozen=True)
class HealthCheckupResult:
    handled: bool
    response: str = ""


class HealthCheckupRepository:
    """Stores health checkups locally using atomic JSON replacement."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "health_checkups.json"

    def load(self) -> list[HealthCheckup]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [self._decode(item) for item in payload.get("records", [])]

    def save(self, records: list[HealthCheckup]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "records": [asdict(record) for record in records],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="health_checkups_",
            suffix=".json",
            dir=self.path.parent,
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                json.dump(payload, stream, ensure_ascii=False, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)

    def _decode(self, item: dict[str, object]) -> HealthCheckup:
        results = [
            LaboratoryResult(**result)
            for result in item.get("laboratory_results", [])
        ]
        values = dict(item)
        values["laboratory_results"] = results
        return HealthCheckup(**values)


class SecureHealthCheckupService:
    """Registers confirmed checkups for Carlos or Cristina without diagnosis."""

    def __init__(self, repository: HealthCheckupRepository | None = None) -> None:
        self.repository = repository or HealthCheckupRepository()
        self._pending: dict[str, HealthCheckup] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> HealthCheckupResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in {"confirmar chequeo", "confirmá el chequeo"}:
            return self._confirm(key)
        if folded in {"cancelar chequeo", "cancelá el chequeo"}:
            self._pending.pop(key, None)
            return HealthCheckupResult(
                handled=True,
                response="Cancelé la carga pendiente y no guardé datos de salud.",
            )

        list_match = re.fullmatch(
            r"(?:mostrar|listar) chequeos de (Carlos|Cristina)",
            normalized,
            flags=re.IGNORECASE,
        )
        if list_match:
            return self._list_for(list_match.group(1))

        archive_match = re.fullmatch(
            r"archivar chequeo ([0-9a-f]{8})",
            folded,
        )
        if archive_match:
            return self._archive(archive_match.group(1))

        delete_match = re.fullmatch(
            r"eliminar chequeo ([0-9a-f]{8})",
            folded,
        )
        if delete_match:
            return self._delete(delete_match.group(1))

        draft = self._parse_registration(normalized)
        if draft is None:
            return HealthCheckupResult(handled=False)
        self._pending[key] = draft
        return HealthCheckupResult(
            handled=True,
            response=self._render_confirmation(draft),
        )

    def _parse_registration(self, text: str) -> HealthCheckup | None:
        match = re.match(
            r"^registrar chequeo de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        person = self._person(match.group(1))
        fields = self._split_fields(match.group(2))
        study_type = fields.pop("estudio", "").strip()
        performed_on = fields.pop("fecha", "").strip()
        if not study_type or not self._valid_date(performed_on):
            return None
        laboratory_text = fields.pop("resultados", "").strip()
        report_text = fields.pop("informe", "").strip()
        category = "laboratorio" if laboratory_text else "informe"
        if not laboratory_text and not report_text:
            return None
        return HealthCheckup(
            record_id=uuid4().hex[:8],
            person=person,
            study_type=study_type,
            performed_on=performed_on,
            category=category,
            institution=fields.pop("institución", fields.pop("institucion", "")),
            professional=fields.pop("profesional", ""),
            source_file=fields.pop("archivo", ""),
            report_text=report_text,
            laboratory_results=self._parse_laboratory_results(laboratory_text),
        )

    def _split_fields(self, value: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in value.split("|"):
            name, separator, content = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = content.strip()
        return fields

    def _parse_laboratory_results(self, value: str) -> list[LaboratoryResult]:
        results: list[LaboratoryResult] = []
        for item in value.split(";"):
            parts = [part.strip() for part in item.split("~")]
            if len(parts) < 2 or not parts[0] or not parts[1]:
                continue
            padded = (parts + ["", "", ""])[:5]
            results.append(
                LaboratoryResult(
                    name=padded[0],
                    value=padded[1],
                    unit=padded[2],
                    reference_range=padded[3],
                    flag=padded[4],
                )
            )
        return results

    def _confirm(self, key: str) -> HealthCheckupResult:
        draft = self._pending.pop(key, None)
        if draft is None:
            return HealthCheckupResult(
                handled=True,
                response="No hay un chequeo pendiente para confirmar.",
            )
        records = self.repository.load()
        records.append(draft)
        self.repository.save(records)
        return HealthCheckupResult(
            handled=True,
            response=(
                f"Guardé el chequeo {draft.record_id} de {draft.person} en el "
                "registro local. No realicé ninguna interpretación clínica."
            ),
        )

    def _list_for(self, person: str) -> HealthCheckupResult:
        canonical = self._person(person)
        records = [
            record
            for record in self.repository.load()
            if record.person == canonical and not record.archived
        ]
        if not records:
            return HealthCheckupResult(
                handled=True,
                response=f"No hay chequeos activos registrados para {canonical}.",
            )
        rows = "\n".join(
            f"- {record.record_id}: {record.performed_on} · {record.study_type}"
            for record in records
        )
        return HealthCheckupResult(
            handled=True,
            response=f"Chequeos activos de {canonical}:\n{rows}",
        )

    def _archive(self, record_id: str) -> HealthCheckupResult:
        records = self.repository.load()
        for record in records:
            if record.record_id == record_id:
                record.archived = True
                self.repository.save(records)
                return HealthCheckupResult(
                    handled=True,
                    response=f"Archivé el chequeo {record_id}.",
                )
        return self._not_found(record_id)

    def _delete(self, record_id: str) -> HealthCheckupResult:
        records = self.repository.load()
        remaining = [record for record in records if record.record_id != record_id]
        if len(remaining) == len(records):
            return self._not_found(record_id)
        self.repository.save(remaining)
        return HealthCheckupResult(
            handled=True,
            response=f"Eliminé definitivamente el chequeo {record_id}.",
        )

    def _render_confirmation(self, draft: HealthCheckup) -> str:
        detail = (
            f"{len(draft.laboratory_results)} resultados estructurados"
            if draft.category == "laboratorio"
            else "un informe narrativo"
        )
        return (
            f"Preparé el chequeo de {draft.person}: {draft.study_type}, "
            f"fecha {draft.performed_on}, con {detail}. "
            "Decí 'confirmar chequeo' para guardarlo localmente o "
            "'cancelar chequeo' para descartarlo."
        )

    def _person(self, value: str) -> str:
        canonical = _ALLOWED_PEOPLE.get(value.casefold())
        if canonical is None:
            raise ValueError("El registro admite únicamente a Carlos y Cristina.")
        return canonical

    def _valid_date(self, value: str) -> bool:
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    def _not_found(self, record_id: str) -> HealthCheckupResult:
        return HealthCheckupResult(
            handled=True,
            response=f"No encontré el chequeo {record_id}.",
        )
