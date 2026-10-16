from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from uuid import uuid4

from app.secure_medication_registry import MedicationRegistryRepository
from app.structured_symptom_registry import SymptomRepository
from app.vital_sign_history import VitalSignHistoryService, VitalSignRepository

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_ALLOWED_STATUS = {"activa", "controlada", "en estudio", "resuelta", "archivada"}


@dataclass
class ChronicConditionRecord:
    condition_id: str
    person: str
    name: str
    diagnosed_on: str = ""
    status: str = "activa"
    professional: str = ""
    health_center: str = ""
    related_medications: tuple[str, ...] = ()
    monitoring_metrics: tuple[str, ...] = ()
    followups: tuple[str, ...] = ()
    professional_goals: tuple[str, ...] = ()
    notes: str = ""
    archived: bool = False


@dataclass(frozen=True)
class ChronicConditionResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingConditionChange:
    kind: str
    value: ChronicConditionRecord


class ChronicConditionRepository:
    """Stores confirmed chronic conditions atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "chronic_conditions.json"

    def load(self) -> list[ChronicConditionRecord]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        rows = payload.get("conditions", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            return []
        records = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            normalized = dict(row)
            for field in (
                "related_medications",
                "monitoring_metrics",
                "followups",
                "professional_goals",
            ):
                normalized[field] = tuple(normalized.get(field, ()))
            records.append(ChronicConditionRecord(**normalized))
        return records

    def save(self, records: list[ChronicConditionRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "conditions": [asdict(item) for item in records],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="chronic_conditions_",
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


class ChronicConditionRegistryService:
    """Tracks documented conditions without diagnosing or changing treatment."""

    _LIST = re.compile(
        r"^(?:mostrar |ver )?(?:enfermedades crónicas|condiciones crónicas) de "
        r"(Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )
    _DETAIL = re.compile(
        r"^(?:mostrar |ver )?(?:condición|enfermedad) ([a-f0-9]{8})$",
        flags=re.IGNORECASE,
    )
    _ARCHIVE = re.compile(
        r"^archivar (?:condición|enfermedad) ([a-f0-9]{8})$",
        flags=re.IGNORECASE,
    )
    _STATUS = re.compile(
        r"^actualizar (?:condición|enfermedad) ([a-f0-9]{8}):\s*estado=(.+)$",
        flags=re.IGNORECASE,
    )
    _FOLLOWUP = re.compile(
        r"^(?:seguimiento|resumen) de (.+) de (Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        repository: ChronicConditionRepository | None = None,
        medication_repository: MedicationRegistryRepository | None = None,
        vital_repository: VitalSignRepository | None = None,
        symptom_repository: SymptomRepository | None = None,
    ) -> None:
        self.repository = repository or ChronicConditionRepository()
        self.medication_repository = (
            medication_repository or MedicationRegistryRepository()
        )
        self.vital_repository = vital_repository or VitalSignRepository()
        self.symptom_repository = symptom_repository or SymptomRepository()
        self._pending: dict[str, _PendingConditionChange] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> ChronicConditionResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"
        if folded in {"confirmar condición", "confirmá condición"}:
            return self._confirm(key)
        if folded in {"cancelar condición", "cancelá condición"}:
            self._pending.pop(key, None)
            return ChronicConditionResult(True, "Cancelé el cambio pendiente.")

        match = self._LIST.fullmatch(normalized)
        if match:
            return self._list(match.group(1))
        match = self._DETAIL.fullmatch(normalized)
        if match:
            return self._detail(match.group(1))
        match = self._ARCHIVE.fullmatch(normalized)
        if match:
            return self._prepare_archive(match.group(1), key)
        match = self._STATUS.fullmatch(normalized)
        if match:
            return self._prepare_status(match.group(1), match.group(2), key)
        match = self._FOLLOWUP.fullmatch(normalized)
        if match:
            return self._followup(match.group(1), match.group(2))

        record = self._parse_registration(normalized)
        if record is None:
            return ChronicConditionResult(False)
        self._pending[key] = _PendingConditionChange("create", record)
        return ChronicConditionResult(
            True,
            f"Confirmá la condición de {record.person}: {record.name} · "
            f"estado {record.status}. Decí 'confirmar condición' para guardarla.",
        )

    def _parse_registration(self, text: str) -> ChronicConditionRecord | None:
        match = re.match(
            r"^registrar (?:condición|enfermedad crónica) de "
            r"(Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        name = fields.get("nombre", fields.get("condición", ""))
        status = fields.get("estado", "activa").casefold()
        if not name or status not in _ALLOWED_STATUS:
            return None
        return ChronicConditionRecord(
            condition_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            name=name,
            diagnosed_on=fields.get("diagnóstico", fields.get("diagnostico", "")),
            status=status,
            professional=fields.get("profesional", ""),
            health_center=fields.get("centro", ""),
            related_medications=self._items(fields.get("medicación", "")),
            monitoring_metrics=self._items(fields.get("seguimiento", "")),
            followups=self._items(fields.get("controles", "")),
            professional_goals=self._items(fields.get("objetivos", "")),
            notes=fields.get("notas", ""),
            archived=status == "archivada",
        )

    @staticmethod
    def _fields(raw: str) -> dict[str, str]:
        values = {}
        for part in raw.split("|"):
            if "=" not in part:
                continue
            name, value = part.split("=", 1)
            values[name.strip().casefold()] = value.strip()
        return values

    @staticmethod
    def _items(raw: str) -> tuple[str, ...]:
        return tuple(item.strip() for item in raw.split(",") if item.strip())

    def _confirm(self, key: str) -> ChronicConditionResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return ChronicConditionResult(True, "No hay cambios pendientes.")
        records = self.repository.load()
        if pending.kind == "create":
            records.append(pending.value)
            message = "Guardé la condición crónica confirmada."
        else:
            records = [
                pending.value
                if item.condition_id == pending.value.condition_id
                else item
                for item in records
            ]
            message = "Actualicé la condición crónica confirmada."
        self.repository.save(records)
        return ChronicConditionResult(True, message)

    def _prepare_archive(self, condition_id: str, key: str) -> ChronicConditionResult:
        record = self._find(condition_id)
        if record is None:
            return ChronicConditionResult(True, "No encontré esa condición.")
        self._pending[key] = _PendingConditionChange(
            "update",
            replace(record, status="archivada", archived=True),
        )
        return ChronicConditionResult(
            True,
            f"Confirmá el archivo de la condición {condition_id}. "
            "Decí 'confirmar condición' para aplicarlo.",
        )

    def _prepare_status(
        self,
        condition_id: str,
        raw_status: str,
        key: str,
    ) -> ChronicConditionResult:
        status = raw_status.strip().casefold()
        if status not in _ALLOWED_STATUS:
            return ChronicConditionResult(False)
        record = self._find(condition_id)
        if record is None:
            return ChronicConditionResult(True, "No encontré esa condición.")
        self._pending[key] = _PendingConditionChange(
            "update",
            replace(record, status=status, archived=status == "archivada"),
        )
        return ChronicConditionResult(
            True,
            f"Confirmá el estado {status} para {condition_id}. "
            "Decí 'confirmar condición' para aplicarlo.",
        )

    def _find(self, condition_id: str) -> ChronicConditionRecord | None:
        return next(
            (
                item
                for item in self.repository.load()
                if item.condition_id == condition_id
            ),
            None,
        )

    def _list(self, person: str) -> ChronicConditionResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = [
            item
            for item in self.repository.load()
            if item.person == canonical and not item.archived
        ]
        if not records:
            return ChronicConditionResult(
                True,
                f"{canonical} no tiene condiciones crónicas activas registradas.",
            )
        rows = [
            f"- {item.name} · estado {item.status} · ID {item.condition_id}"
            for item in sorted(records, key=lambda row: row.name.casefold())
        ]
        return ChronicConditionResult(
            True,
            f"Condiciones crónicas de {canonical}:\n" + "\n".join(rows),
        )

    def _detail(self, condition_id: str) -> ChronicConditionResult:
        item = self._find(condition_id)
        if item is None:
            return ChronicConditionResult(True, "No encontré esa condición.")
        details = [
            f"Condición {item.condition_id} de {item.person}: {item.name}",
            f"Estado registrado: {item.status}",
        ]
        if item.diagnosed_on:
            details.append(f"Diagnóstico documentado: {item.diagnosed_on}")
        if item.professional:
            details.append(f"Profesional: {item.professional}")
        if item.health_center:
            details.append(f"Centro: {item.health_center}")
        if item.monitoring_metrics:
            details.append("Seguimiento: " + ", ".join(item.monitoring_metrics))
        return ChronicConditionResult(True, "\n".join(details))

    def _followup(self, raw_name: str, person: str) -> ChronicConditionResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        target = raw_name.strip().casefold()
        record = next(
            (
                item
                for item in self.repository.load()
                if item.person == canonical
                and item.name.casefold() == target
                and not item.archived
            ),
            None,
        )
        if record is None:
            return ChronicConditionResult(
                True,
                f"No encontré {raw_name.strip()} registrada para {canonical}.",
            )
        sections = [
            f"Seguimiento documentado de {record.name} para {canonical}:",
            f"- Estado registrado: {record.status}",
        ]
        if record.professional:
            sections.append(f"- Profesional: {record.professional}")
        if record.health_center:
            sections.append(f"- Centro: {record.health_center}")
        if record.professional_goals:
            sections.append(
                "- Objetivos profesionales: "
                + ", ".join(record.professional_goals)
            )
        medications = self._related_medications(record)
        sections.append("- Medicación relacionada: " + medications)
        sections.append("- Últimos signos: " + self._latest_vitals(record))
        sections.append("- Síntomas activos: " + self._active_symptoms(canonical))
        if record.followups:
            sections.append("- Controles registrados: " + ", ".join(record.followups))
        sections.append(
            "Resumen descriptivo de datos confirmados. No determina si la "
            "condición está clínicamente controlada y no modifica tratamientos."
        )
        return ChronicConditionResult(True, "\n".join(sections))

    def _related_medications(self, record: ChronicConditionRecord) -> str:
        configured = {item.casefold() for item in record.related_medications}
        records = [
            item
            for item in self.medication_repository.load()
            if item.person == record.person
            and item.status == "activo"
            and not item.archived
            and item.name.casefold() in configured
        ]
        if not records:
            return "sin coincidencias activas"
        return ", ".join(
            f"{item.name} ({item.dosage})"
            for item in sorted(records, key=lambda row: row.name.casefold())
        )

    def _latest_vitals(self, record: ChronicConditionRecord) -> str:
        rows = [
            item
            for item in self.vital_repository.load()
            if item.person == record.person and not item.archived
        ]
        if not rows:
            return "sin registros"
        latest = max(rows, key=lambda item: item.measured_at)
        return f"{latest.measured_at} · {VitalSignHistoryService.render_values(latest)}"

    def _active_symptoms(self, person: str) -> str:
        rows = [
            item
            for item in self.symptom_repository.load()
            if item.person == person
            and item.status == "activo"
            and not item.archived
        ]
        if not rows:
            return "sin episodios activos"
        return ", ".join(
            item.symptom
            for item in sorted(rows, key=lambda row: row.started_at, reverse=True)[:5]
        )
