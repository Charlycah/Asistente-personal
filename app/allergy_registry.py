from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_ALLOWED_TYPES = {
    "medicamento",
    "alimento",
    "sustancia",
    "ambiental",
    "material",
    "otra",
}
_ALLOWED_STATUS = {"activa", "descartada", "pendiente", "archivada"}


@dataclass
class AllergyRecord:
    allergy_id: str
    person: str
    allergen: str
    allergy_type: str
    reaction: str = ""
    severity: str = ""
    episode_date: str = ""
    professional_confirmed: bool = False
    professional: str = ""
    institution: str = ""
    notes: str = ""
    status: str = "activa"
    archived: bool = False


@dataclass(frozen=True)
class AllergyResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingAllergyChange:
    kind: str
    value: AllergyRecord


class AllergyRepository:
    """Stores confirmed allergy records atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "allergies.json"

    def load(self) -> list[AllergyRecord]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        rows = payload.get("allergies", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            return []
        return [AllergyRecord(**row) for row in rows if isinstance(row, dict)]

    def save(self, records: list[AllergyRecord]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "allergies": [asdict(item) for item in records],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="allergies_",
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


class AllergyRegistryService:
    """Registers factual allergies without inferring drug families."""

    _LIST = re.compile(
        r"^(?:mostrar |ver )?(?:alergias|alergias activas) de "
        r"(Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )
    _DETAIL = re.compile(
        r"^(?:mostrar |ver )?alergia ([a-f0-9]{8})$",
        flags=re.IGNORECASE,
    )
    _ARCHIVE = re.compile(
        r"^archivar alergia ([a-f0-9]{8})$",
        flags=re.IGNORECASE,
    )
    _STATUS = re.compile(
        r"^actualizar alergia ([a-f0-9]{8}):\s*estado=(.+)$",
        flags=re.IGNORECASE,
    )

    def __init__(self, repository: AllergyRepository | None = None) -> None:
        self.repository = repository or AllergyRepository()
        self._pending: dict[str, _PendingAllergyChange] = {}

    def prepare(self, text: str, *, session_id: str | None = None) -> AllergyResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"
        if folded in {"confirmar alergia", "confirmá alergia"}:
            return self._confirm(key)
        if folded in {"cancelar alergia", "cancelá alergia"}:
            self._pending.pop(key, None)
            return AllergyResult(True, "Cancelé el cambio de alergia pendiente.")

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

        record = self._parse_registration(normalized)
        if record is None:
            return AllergyResult(False)
        self._pending[key] = _PendingAllergyChange("create", record)
        confirmation = (
            f"Confirmá la alergia de {record.person}: {record.allergen} · "
            f"tipo {record.allergy_type} · estado {record.status}"
        )
        if record.reaction:
            confirmation += f" · reacción {record.reaction}"
        confirmation += ". Decí 'confirmar alergia' para guardarla."
        return AllergyResult(True, confirmation)

    def _parse_registration(self, text: str) -> AllergyRecord | None:
        match = re.match(
            r"^registrar alergia de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        allergen = fields.get("alérgeno", fields.get("alergeno", ""))
        allergy_type = fields.get("tipo", "otra").casefold()
        status = fields.get("estado", "activa").casefold()
        if not allergen or allergy_type not in _ALLOWED_TYPES:
            return None
        if status not in _ALLOWED_STATUS:
            return None
        confirmed = fields.get("confirmada", "no").casefold() in {
            "sí",
            "si",
            "true",
            "1",
        }
        return AllergyRecord(
            allergy_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            allergen=allergen,
            allergy_type=allergy_type,
            reaction=fields.get("reacción", fields.get("reaccion", "")),
            severity=fields.get("gravedad", ""),
            episode_date=fields.get("fecha", ""),
            professional_confirmed=confirmed,
            professional=fields.get("profesional", ""),
            institution=fields.get("institución", fields.get("institucion", "")),
            notes=fields.get("notas", ""),
            status=status,
            archived=status == "archivada",
        )

    @staticmethod
    def _fields(raw: str) -> dict[str, str]:
        values: dict[str, str] = {}
        for part in raw.split("|"):
            if "=" not in part:
                continue
            name, value = part.split("=", 1)
            values[name.strip().casefold()] = value.strip()
        return values

    def _confirm(self, key: str) -> AllergyResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return AllergyResult(True, "No hay cambios de alergia pendientes.")
        records = self.repository.load()
        if pending.kind == "create":
            records.append(pending.value)
            message = "Guardé la alergia confirmada en el perfil correspondiente."
        else:
            records = [
                pending.value if item.allergy_id == pending.value.allergy_id else item
                for item in records
            ]
            message = "Actualicé la alergia confirmada."
        self.repository.save(records)
        return AllergyResult(True, message)

    def _prepare_archive(self, allergy_id: str, key: str) -> AllergyResult:
        record = self._find(allergy_id)
        if record is None:
            return AllergyResult(True, "No encontré esa alergia.")
        updated = replace(record, status="archivada", archived=True)
        self._pending[key] = _PendingAllergyChange("update", updated)
        return AllergyResult(
            True,
            f"Confirmá el archivo de la alergia {allergy_id}. "
            "Decí 'confirmar alergia' para aplicarlo.",
        )

    def _prepare_status(
        self,
        allergy_id: str,
        raw_status: str,
        key: str,
    ) -> AllergyResult:
        status = raw_status.strip().casefold()
        if status not in _ALLOWED_STATUS:
            return AllergyResult(False)
        record = self._find(allergy_id)
        if record is None:
            return AllergyResult(True, "No encontré esa alergia.")
        updated = replace(record, status=status, archived=status == "archivada")
        self._pending[key] = _PendingAllergyChange("update", updated)
        return AllergyResult(
            True,
            f"Confirmá el estado {status} para la alergia {allergy_id}. "
            "Decí 'confirmar alergia' para aplicarlo.",
        )

    def _find(self, allergy_id: str) -> AllergyRecord | None:
        return next(
            (item for item in self.repository.load() if item.allergy_id == allergy_id),
            None,
        )

    def _list(self, person: str) -> AllergyResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = [
            item
            for item in self.repository.load()
            if item.person == canonical
            and item.status == "activa"
            and not item.archived
        ]
        records.sort(key=lambda item: item.allergen.casefold())
        if not records:
            return AllergyResult(
                True,
                f"Alergias activas de {canonical}: sin registros.",
            )
        rows = [self._render(item) for item in records]
        return AllergyResult(
            True,
            f"Alergias activas de {canonical}:\n" + "\n".join(rows),
        )

    def _detail(self, allergy_id: str) -> AllergyResult:
        record = self._find(allergy_id)
        if record is None:
            return AllergyResult(True, "No encontré esa alergia.")
        return AllergyResult(True, self._render(record, detailed=True))

    @staticmethod
    def _render(record: AllergyRecord, *, detailed: bool = False) -> str:
        row = (
            f"- {record.allergen} · tipo {record.allergy_type} · "
            f"estado {record.status} · ID {record.allergy_id}"
        )
        if record.reaction:
            row += f" · reacción {record.reaction}"
        if record.severity:
            row += f" · gravedad {record.severity}"
        if detailed and record.professional_confirmed:
            row += " · confirmada por profesional"
        if detailed and record.professional:
            row += f" · {record.professional}"
        return row

    @staticmethod
    def medication_matches(record: AllergyRecord, medication_name: str) -> bool:
        return (
            record.allergy_type == "medicamento"
            and record.status == "activa"
            and not record.archived
            and record.allergen.strip().casefold() == medication_name.strip().casefold()
        )
