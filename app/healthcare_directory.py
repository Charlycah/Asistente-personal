from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_ALLOWED_PROFESSIONAL_STATUS = {"activo", "inactivo", "archivado"}
_ALLOWED_CENTER_STATUS = {"activo", "inactivo", "archivado"}


@dataclass
class HealthcareProfessional:
    professional_id: str
    person: str
    name: str
    specialty: str = ""
    registration: str = ""
    phone: str = ""
    email: str = ""
    center_ids: tuple[str, ...] = ()
    notes: str = ""
    status: str = "activo"
    archived: bool = False


@dataclass
class HealthCenter:
    center_id: str
    person: str
    name: str
    center_type: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    notes: str = ""
    status: str = "activo"
    archived: bool = False


@dataclass(frozen=True)
class HealthcareDirectoryResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingDirectoryChange:
    entity: str
    kind: str
    value: HealthcareProfessional | HealthCenter


class HealthcareDirectoryRepository:
    """Stores confirmed healthcare professionals and centers atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "healthcare_directory.json"

    def load_professionals(self) -> list[HealthcareProfessional]:
        payload = self._load_payload()
        records = []
        for row in payload.get("professionals", []):
            if not isinstance(row, dict):
                continue
            normalized = dict(row)
            normalized["center_ids"] = tuple(normalized.get("center_ids", ()))
            records.append(HealthcareProfessional(**normalized))
        return records

    def load_centers(self) -> list[HealthCenter]:
        payload = self._load_payload()
        return [
            HealthCenter(**row)
            for row in payload.get("centers", [])
            if isinstance(row, dict)
        ]

    def save(
        self,
        professionals: list[HealthcareProfessional],
        centers: list[HealthCenter],
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "professionals": [asdict(item) for item in professionals],
            "centers": [asdict(item) for item in centers],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="healthcare_directory_",
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

    def _load_payload(self) -> dict[str, object]:
        if not self.path.exists():
            return {"professionals": [], "centers": []}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}


class HealthcareDirectoryService:
    """Manages documented care contacts without verifying credentials."""

    _LIST_PROFESSIONALS = re.compile(
        r"^(?:mostrar |ver )?(?:profesionales|médicos|medicos) de "
        r"(Carlos|Cristina)$",
        re.IGNORECASE,
    )
    _LIST_CENTERS = re.compile(
        r"^(?:mostrar |ver )?(?:centros de salud|instituciones) de "
        r"(Carlos|Cristina)$",
        re.IGNORECASE,
    )
    _DETAIL_PROFESSIONAL = re.compile(
        r"^(?:mostrar |ver )?profesional ([a-f0-9]{8})$", re.IGNORECASE
    )
    _DETAIL_CENTER = re.compile(
        r"^(?:mostrar |ver )?centro ([a-f0-9]{8})$", re.IGNORECASE
    )
    _ARCHIVE = re.compile(
        r"^archivar (profesional|centro) ([a-f0-9]{8})$", re.IGNORECASE
    )
    _LINK = re.compile(
        r"^vincular profesional ([a-f0-9]{8}) con centro ([a-f0-9]{8})$",
        re.IGNORECASE,
    )

    def __init__(self, repository: HealthcareDirectoryRepository | None = None) -> None:
        self.repository = repository or HealthcareDirectoryRepository()
        self._pending: dict[str, _PendingDirectoryChange] = {}

    def prepare(
        self, text: str, *, session_id: str | None = None
    ) -> HealthcareDirectoryResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"
        if folded in {"confirmar directorio médico", "confirmar directorio medico"}:
            return self._confirm(key)
        if folded in {"cancelar directorio médico", "cancelar directorio medico"}:
            self._pending.pop(key, None)
            return HealthcareDirectoryResult(True, "Cancelé el cambio pendiente.")

        for pattern, handler in (
            (self._LIST_PROFESSIONALS, self._list_professionals),
            (self._LIST_CENTERS, self._list_centers),
            (self._DETAIL_PROFESSIONAL, self._detail_professional),
            (self._DETAIL_CENTER, self._detail_center),
        ):
            match = pattern.fullmatch(normalized)
            if match:
                return handler(match.group(1))
        match = self._ARCHIVE.fullmatch(normalized)
        if match:
            return self._prepare_archive(match.group(1), match.group(2), key)
        match = self._LINK.fullmatch(normalized)
        if match:
            return self._prepare_link(match.group(1), match.group(2), key)

        professional = self._parse_professional(normalized)
        if professional is not None:
            self._pending[key] = _PendingDirectoryChange(
                "professional", "create", professional
            )
            return HealthcareDirectoryResult(
                True,
                f"Confirmá el profesional de {professional.person}: "
                f"{professional.name}. Decí 'confirmar directorio médico'.",
            )
        center = self._parse_center(normalized)
        if center is not None:
            self._pending[key] = _PendingDirectoryChange("center", "create", center)
            return HealthcareDirectoryResult(
                True,
                f"Confirmá el centro de {center.person}: {center.name}. "
                "Decí 'confirmar directorio médico'.",
            )
        return HealthcareDirectoryResult(False)

    def _parse_professional(self, text: str) -> HealthcareProfessional | None:
        match = re.match(
            r"^registrar profesional de (Carlos|Cristina):\s*(.+)$",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        name = fields.get("nombre", "")
        status = fields.get("estado", "activo").casefold()
        if not name or status not in _ALLOWED_PROFESSIONAL_STATUS:
            return None
        return HealthcareProfessional(
            professional_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            name=name,
            specialty=fields.get("especialidad", ""),
            registration=fields.get("matrícula", fields.get("matricula", "")),
            phone=fields.get("teléfono", fields.get("telefono", "")),
            email=fields.get("email", ""),
            notes=fields.get("notas", ""),
            status=status,
            archived=status == "archivado",
        )

    def _parse_center(self, text: str) -> HealthCenter | None:
        match = re.match(
            r"^registrar centro de salud de (Carlos|Cristina):\s*(.+)$",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        name = fields.get("nombre", "")
        status = fields.get("estado", "activo").casefold()
        if not name or status not in _ALLOWED_CENTER_STATUS:
            return None
        return HealthCenter(
            center_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            name=name,
            center_type=fields.get("tipo", ""),
            address=fields.get("dirección", fields.get("direccion", "")),
            phone=fields.get("teléfono", fields.get("telefono", "")),
            email=fields.get("email", ""),
            website=fields.get("web", ""),
            notes=fields.get("notas", ""),
            status=status,
            archived=status == "archivado",
        )

    @staticmethod
    def _fields(raw: str) -> dict[str, str]:
        values = {}
        for part in raw.split("|"):
            if "=" in part:
                name, value = part.split("=", 1)
                values[name.strip().casefold()] = value.strip()
        return values

    def _confirm(self, key: str) -> HealthcareDirectoryResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return HealthcareDirectoryResult(True, "No hay cambios pendientes.")
        professionals = self.repository.load_professionals()
        centers = self.repository.load_centers()
        if pending.entity == "professional":
            value = pending.value
            assert isinstance(value, HealthcareProfessional)
            professionals = self._upsert_professional(professionals, value)
        else:
            value = pending.value
            assert isinstance(value, HealthCenter)
            centers = self._upsert_center(centers, value)
        self.repository.save(professionals, centers)
        return HealthcareDirectoryResult(True, "Guardé el cambio confirmado.")

    @staticmethod
    def _upsert_professional(
        records: list[HealthcareProfessional], value: HealthcareProfessional
    ) -> list[HealthcareProfessional]:
        if any(item.professional_id == value.professional_id for item in records):
            return [
                value if item.professional_id == value.professional_id else item
                for item in records
            ]
        return [*records, value]

    @staticmethod
    def _upsert_center(
        records: list[HealthCenter],
        value: HealthCenter,
    ) -> list[HealthCenter]:
        if any(item.center_id == value.center_id for item in records):
            return [
                value if item.center_id == value.center_id else item
                for item in records
            ]
        return [*records, value]

    def _prepare_archive(
        self, entity: str, record_id: str, key: str
    ) -> HealthcareDirectoryResult:
        if entity.casefold() == "profesional":
            record = next(
                (item for item in self.repository.load_professionals()
                 if item.professional_id == record_id),
                None,
            )
            if record is None:
                return HealthcareDirectoryResult(True, "No encontré ese profesional.")
            value = replace(record, status="archivado", archived=True)
            self._pending[key] = _PendingDirectoryChange(
                "professional",
                "update",
                value,
            )
        else:
            record = next(
                (item for item in self.repository.load_centers()
                 if item.center_id == record_id),
                None,
            )
            if record is None:
                return HealthcareDirectoryResult(True, "No encontré ese centro.")
            value = replace(record, status="archivado", archived=True)
            self._pending[key] = _PendingDirectoryChange("center", "update", value)
        return HealthcareDirectoryResult(
            True, "El archivado quedó pendiente de confirmación."
        )

    def _prepare_link(
        self, professional_id: str, center_id: str, key: str
    ) -> HealthcareDirectoryResult:
        professional = next(
            (item for item in self.repository.load_professionals()
             if item.professional_id == professional_id),
            None,
        )
        center = next(
            (item for item in self.repository.load_centers()
             if item.center_id == center_id),
            None,
        )
        if professional is None or center is None:
            return HealthcareDirectoryResult(True, "No encontré ambos registros.")
        if professional.person != center.person:
            return HealthcareDirectoryResult(
                True, "No puedo vincular registros de personas diferentes."
            )
        ids = tuple(dict.fromkeys((*professional.center_ids, center.center_id)))
        self._pending[key] = _PendingDirectoryChange(
            "professional", "update", replace(professional, center_ids=ids)
        )
        return HealthcareDirectoryResult(
            True, "El vínculo quedó pendiente de confirmación."
        )

    def _list_professionals(self, person: str) -> HealthcareDirectoryResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = [
            item for item in self.repository.load_professionals()
            if item.person == canonical and not item.archived
        ]
        if not records:
            return HealthcareDirectoryResult(
                True, f"Profesionales de {canonical}: no hay registros activos."
            )
        rows = [
            f"- {item.name} · {item.specialty or 'sin especialidad'} · "
            f"ID {item.professional_id}"
            for item in sorted(records, key=lambda value: value.name.casefold())
        ]
        return HealthcareDirectoryResult(
            True, f"Profesionales de {canonical}:\n" + "\n".join(rows)
        )

    def _list_centers(self, person: str) -> HealthcareDirectoryResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        records = [
            item for item in self.repository.load_centers()
            if item.person == canonical and not item.archived
        ]
        if not records:
            return HealthcareDirectoryResult(
                True, f"Centros de salud de {canonical}: no hay registros activos."
            )
        rows = [
            f"- {item.name} · {item.center_type or 'sin tipo'} · ID {item.center_id}"
            for item in sorted(records, key=lambda value: value.name.casefold())
        ]
        return HealthcareDirectoryResult(
            True, f"Centros de salud de {canonical}:\n" + "\n".join(rows)
        )

    def _detail_professional(self, record_id: str) -> HealthcareDirectoryResult:
        item = next(
            (row for row in self.repository.load_professionals()
             if row.professional_id == record_id),
            None,
        )
        if item is None:
            return HealthcareDirectoryResult(True, "No encontré ese profesional.")
        centers = {row.center_id: row.name for row in self.repository.load_centers()}
        linked = ", ".join(centers.get(value, value) for value in item.center_ids)
        return HealthcareDirectoryResult(
            True,
            f"Profesional {item.name} · especialidad {item.specialty or 'sin dato'} · "
            f"matrícula {item.registration or 'sin dato'} · teléfono "
            f"{item.phone or 'sin dato'} · centros {linked or 'sin vínculos'}.",
        )

    def _detail_center(self, record_id: str) -> HealthcareDirectoryResult:
        item = next(
            (
                row
                for row in self.repository.load_centers()
                if row.center_id == record_id
            ),
            None,
        )
        if item is None:
            return HealthcareDirectoryResult(True, "No encontré ese centro.")
        return HealthcareDirectoryResult(
            True,
            f"Centro {item.name} · tipo {item.center_type or 'sin dato'} · "
            f"dirección {item.address or 'sin dato'} · teléfono "
            f"{item.phone or 'sin dato'}.",
        )
