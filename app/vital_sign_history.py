from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_FIELDS = {
    "presión": ("blood_pressure", "mmHg"),
    "presion": ("blood_pressure", "mmHg"),
    "glucemia": ("glucose", "mg/dL"),
    "peso": ("weight", "kg"),
    "saturación": ("oxygen_saturation", "%"),
    "saturacion": ("oxygen_saturation", "%"),
    "temperatura": ("temperature", "°C"),
    "pulso": ("heart_rate", "lpm"),
    "frecuencia cardíaca": ("heart_rate", "lpm"),
    "frecuencia cardiaca": ("heart_rate", "lpm"),
}
_LABELS = {
    "blood_pressure": "presión",
    "glucose": "glucemia",
    "weight": "peso",
    "oxygen_saturation": "saturación",
    "temperature": "temperatura",
    "heart_rate": "frecuencia cardíaca",
}
_UNITS = {
    "blood_pressure": "mmHg",
    "glucose": "mg/dL",
    "weight": "kg",
    "oxygen_saturation": "%",
    "temperature": "°C",
    "heart_rate": "lpm",
}


@dataclass
class VitalSignRecord:
    record_id: str
    person: str
    measured_at: str
    blood_pressure: str = ""
    glucose: float | None = None
    weight: float | None = None
    oxygen_saturation: float | None = None
    temperature: float | None = None
    heart_rate: float | None = None
    notes: str = ""
    archived: bool = False


@dataclass(frozen=True)
class VitalSignResult:
    handled: bool
    response: str = ""


class VitalSignRepository:
    """Stores confirmed vital-sign records with atomic JSON replacement."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "vital_signs.json"

    def load(self) -> list[VitalSignRecord]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [VitalSignRecord(**item) for item in payload.get("records", [])]

    def save(self, records: list[VitalSignRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "records": [asdict(record) for record in records],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="vital_signs_", suffix=".json", dir=self.path.parent
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


class VitalSignHistoryService:
    """Registers and summarizes longitudinal vital signs without diagnosis."""

    def __init__(
        self,
        repository: VitalSignRepository | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository or VitalSignRepository()
        self._now = now or datetime.now
        self._pending: dict[str, VitalSignRecord] = {}

    def prepare(self, text: str, *, session_id: str | None = None) -> VitalSignResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"
        if folded in {"confirmar signos", "confirmar control"}:
            return self._confirm(key)
        if folded in {"cancelar signos", "cancelar control"}:
            self._pending.pop(key, None)
            return VitalSignResult(
                True, "Cancelé el control pendiente sin guardar datos."
            )

        draft = self._parse_registration(normalized)
        if draft is not None:
            self._pending[key] = draft
            return VitalSignResult(True, self._render_confirmation(draft))

        history = re.fullmatch(
            r"historial de signos de (Carlos|Cristina)(?: de los últimos (\d+) días)?",
            normalized,
            flags=re.IGNORECASE,
        )
        if history:
            days = int(history.group(2) or 30)
            return self._history(history.group(1), days)

        trend = re.fullmatch(
            r"tendencia de "
            r"(presión|presion|glucemia|peso|saturación|saturacion|"
            r"temperatura|pulso|frecuencia cardíaca|frecuencia cardiaca) "
            r"de (Carlos|Cristina)(?: de los últimos (\d+) días)?",
            normalized,
            flags=re.IGNORECASE,
        )
        if trend:
            field = _FIELDS[trend.group(1).casefold()][0]
            return self._trend(trend.group(2), field, int(trend.group(3) or 30))

        summary = re.fullmatch(
            r"resumen (semanal|mensual) de signos de (Carlos|Cristina)",
            normalized,
            flags=re.IGNORECASE,
        )
        if summary:
            days = 7 if summary.group(1).casefold() == "semanal" else 30
            return self._period_summary(summary.group(2), days)
        return VitalSignResult(False)

    def _parse_registration(self, text: str) -> VitalSignRecord | None:
        match = re.match(
            r"^registrar signos de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._split_fields(match.group(2))
        measured_at = fields.pop("fecha", self._now().isoformat(timespec="minutes"))
        try:
            datetime.fromisoformat(measured_at)
        except ValueError:
            return None
        values: dict[str, object] = {}
        for label, (name, _) in _FIELDS.items():
            raw = fields.pop(label, "")
            if not raw or name in values:
                continue
            if name == "blood_pressure":
                if not re.fullmatch(r"\d{2,3}/\d{2,3}", raw):
                    return None
                values[name] = raw
            else:
                try:
                    values[name] = float(raw.replace(",", "."))
                except ValueError:
                    return None
        if not values:
            return None
        return VitalSignRecord(
            record_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            measured_at=measured_at,
            notes=fields.pop("notas", ""),
            **values,
        )

    def _split_fields(self, value: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in value.split("|"):
            name, separator, content = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = content.strip()
        return fields

    def _confirm(self, key: str) -> VitalSignResult:
        draft = self._pending.pop(key, None)
        if draft is None:
            return VitalSignResult(True, "No hay un control de signos pendiente.")
        records = self.repository.load()
        records.append(draft)
        self.repository.save(records)
        return VitalSignResult(
            True,
            f"Guardé el control {draft.record_id} de {draft.person}. "
            "El registro es descriptivo y no constituye una evaluación clínica.",
        )

    def _history(self, person: str, days: int) -> VitalSignResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = self._records(canonical, days)
        if not records:
            return VitalSignResult(
                True,
                f"No hay signos registrados para {canonical} en ese período.",
            )
        rows = "\n".join(
            f"- {item.measured_at}: {self.render_values(item)}" for item in records
        )
        return VitalSignResult(
            True, f"Historial de signos de {canonical} ({days} días):\n{rows}"
        )

    def _trend(self, person: str, field: str, days: int) -> VitalSignResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        points = self._field_points(canonical, field, days)
        if len(points) < 2:
            return VitalSignResult(
                True,
                f"No hay suficientes registros de {_LABELS[field]} "
                "para calcular una tendencia.",
            )
        first_date, first = points[0]
        last_date, last = points[-1]
        if field == "blood_pressure":
            first_sys, first_dia = self._pressure(first)
            last_sys, last_dia = self._pressure(last)
            variation = f"{last_sys - first_sys:+.0f}/{last_dia - first_dia:+.0f}"
            detail = f"{first} a {last} (variación {variation} mmHg)"
        else:
            change = float(last) - float(first)
            detail = (
                f"{self._number(first)} a {self._number(last)} "
                f"{_UNITS[field]} (variación {change:+.1f})"
            )
        return VitalSignResult(
            True,
            f"Tendencia descriptiva de {_LABELS[field]} de {canonical}: {detail}, "
            f"entre {first_date} y {last_date}. Se usaron {len(points)} registros. "
            "La variación no se interpreta clínicamente.",
        )

    def _period_summary(self, person: str, days: int) -> VitalSignResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = self._records(canonical, days)
        if not records:
            return VitalSignResult(
                True,
                f"No hay signos registrados para {canonical} "
                f"en los últimos {days} días.",
            )
        rows: list[str] = []
        for field in _LABELS:
            points = self._field_points(canonical, field, days)
            if not points:
                continue
            values = [value for _, value in points]
            if field == "blood_pressure":
                systolic = [self._pressure(value)[0] for value in values]
                diastolic = [self._pressure(value)[1] for value in values]
                average = f"promedio {mean(systolic):.0f}/{mean(diastolic):.0f} mmHg"
            else:
                numeric_mean = mean(float(value) for value in values)
                average = f"promedio {numeric_mean:.1f} {_UNITS[field]}"
            rows.append(f"- {_LABELS[field]}: {average}; {len(values)} registros")
        return VitalSignResult(
            True,
            f"Resumen de signos de {canonical} de los últimos {days} días:\n"
            + "\n".join(rows)
            + "\nEs un resumen descriptivo de datos confirmados, "
            "sin diagnóstico ni alertas clínicas.",
        )

    def _records(self, person: str, days: int) -> list[VitalSignRecord]:
        cutoff = self._now() - timedelta(days=max(1, days))
        records = [
            item
            for item in self.repository.load()
            if item.person == person
            and not item.archived
            and datetime.fromisoformat(item.measured_at) >= cutoff
        ]
        return sorted(records, key=lambda item: item.measured_at)

    def _field_points(
        self, person: str, field: str, days: int
    ) -> list[tuple[str, object]]:
        return [
            (record.measured_at, value)
            for record in self._records(person, days)
            if (value := getattr(record, field)) not in {None, ""}
        ]

    @staticmethod
    def _pressure(value: object) -> tuple[float, float]:
        systolic, diastolic = str(value).split("/", maxsplit=1)
        return float(systolic), float(diastolic)

    @staticmethod
    def _number(value: object) -> str:
        return f"{float(value):g}"

    @classmethod
    def render_values(cls, record: VitalSignRecord) -> str:
        values: list[str] = []
        for field, label in _LABELS.items():
            value = getattr(record, field)
            if value in {None, ""}:
                continue
            rendered = str(value) if field == "blood_pressure" else cls._number(value)
            values.append(f"{label} {rendered} {_UNITS[field]}")
        return "; ".join(values)

    def _render_confirmation(self, draft: VitalSignRecord) -> str:
        return (
            f"Preparé un control de signos para {draft.person}, "
            f"fecha {draft.measured_at}: "
            f"{self.render_values(draft)}. Decí 'confirmar signos' para guardarlo "
            "o 'cancelar signos' para descartarlo."
        )
