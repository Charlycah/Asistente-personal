from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_ALLOWED_STATUS = {"activo", "inactivo", "archivado"}


@dataclass
class EmergencyContact:
    contact_id: str
    person: str
    name: str
    relationship: str = ""
    primary_phone: str = ""
    alternate_phone: str = ""
    priority: int = 1
    can_make_decisions: bool = False
    notes: str = ""
    status: str = "activo"
    archived: bool = False


@dataclass
class EmergencyCoverage:
    person: str
    provider: str = ""
    plan: str = ""
    member_number: str = ""
    emergency_phone: str = ""
    notes: str = ""


@dataclass(frozen=True)
class EmergencyContactResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingChange:
    kind: str
    value: EmergencyContact | EmergencyCoverage


class EmergencyContactRepository:
    """Stores confirmed emergency contacts and coverage atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "emergency_contacts.json"

    def load_contacts(self) -> list[EmergencyContact]:
        return [EmergencyContact(**row) for row in self._payload().get("contacts", [])]

    def load_coverages(self) -> list[EmergencyCoverage]:
        return [
            EmergencyCoverage(**row)
            for row in self._payload().get("coverages", [])
        ]

    def save(
        self,
        contacts: list[EmergencyContact],
        coverages: list[EmergencyCoverage],
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "contacts": [asdict(item) for item in contacts],
            "coverages": [asdict(item) for item in coverages],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="emergency_contacts_", suffix=".json", dir=self.path.parent
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

    def _payload(self) -> dict[str, list[dict[str, object]]]:
        if not self.path.exists():
            return {"contacts": [], "coverages": []}
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}


class EmergencyContactService:
    """Manages documented emergency contacts without placing calls."""

    _LIST = re.compile(
        r"^(?:mostrar |ver )?contactos de emergencia de (Carlos|Cristina)$",
        re.IGNORECASE,
    )
    _SUMMARY = re.compile(
        r"^(?:mostrar |ver )?(?:resumen|ficha) de emergencia de "
        r"(Carlos|Cristina)$",
        re.IGNORECASE,
    )
    _DETAIL = re.compile(
        r"^(?:mostrar |ver )?contacto de emergencia ([a-f0-9]{8})$",
        re.IGNORECASE,
    )
    _ARCHIVE = re.compile(
        r"^archivar contacto de emergencia ([a-f0-9]{8})$", re.IGNORECASE
    )

    def __init__(self, repository: EmergencyContactRepository | None = None) -> None:
        self.repository = repository or EmergencyContactRepository()
        self._pending: dict[str, _PendingChange] = {}

    def prepare(
        self, text: str, *, session_id: str | None = None
    ) -> EmergencyContactResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"
        if folded in {"confirmar emergencia", "confirmar contacto de emergencia"}:
            return self._confirm(key)
        if folded in {"cancelar emergencia", "cancelar contacto de emergencia"}:
            self._pending.pop(key, None)
            return EmergencyContactResult(True, "Cancelé el cambio pendiente.")
        for pattern, handler in (
            (self._LIST, self._list),
            (self._SUMMARY, self._summary),
            (self._DETAIL, self._detail),
        ):
            match = pattern.fullmatch(normalized)
            if match:
                return handler(match.group(1))
        match = self._ARCHIVE.fullmatch(normalized)
        if match:
            return self._prepare_archive(match.group(1), key)
        contact = self._parse_contact(normalized)
        if contact is not None:
            self._pending[key] = _PendingChange("contact", contact)
            return EmergencyContactResult(
                True,
                f"Confirmá el contacto de emergencia de {contact.person}: "
                f"{contact.name}. Decí 'confirmar emergencia'.",
            )
        coverage = self._parse_coverage(normalized)
        if coverage is not None:
            self._pending[key] = _PendingChange("coverage", coverage)
            return EmergencyContactResult(
                True,
                f"Confirmá la cobertura de emergencia de {coverage.person}: "
                f"{coverage.provider}. Decí 'confirmar emergencia'.",
            )
        return EmergencyContactResult(False)

    def _parse_contact(self, text: str) -> EmergencyContact | None:
        match = re.match(
            r"^registrar contacto de emergencia de (Carlos|Cristina):\s*(.+)$",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        name = fields.get("nombre", "")
        phone = fields.get("teléfono", fields.get("telefono", ""))
        try:
            priority = int(fields.get("prioridad", "1"))
        except ValueError:
            return None
        status = fields.get("estado", "activo").casefold()
        if not name or not phone or priority < 1 or priority > 9:
            return None
        if status not in _ALLOWED_STATUS:
            return None
        decision = fields.get("decisiones", "").casefold() in {"sí", "si", "true"}
        return EmergencyContact(
            contact_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            name=name,
            relationship=fields.get("relación", fields.get("relacion", "")),
            primary_phone=phone,
            alternate_phone=fields.get(
                "teléfono alternativo", fields.get("telefono alternativo", "")
            ),
            priority=priority,
            can_make_decisions=decision,
            notes=fields.get("notas", ""),
            status=status,
            archived=status == "archivado",
        )

    def _parse_coverage(self, text: str) -> EmergencyCoverage | None:
        match = re.match(
            r"^registrar cobertura de emergencia de (Carlos|Cristina):\s*(.+)$",
            text,
            re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        provider = fields.get("prestador", fields.get("obra social", ""))
        if not provider:
            return None
        return EmergencyCoverage(
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            provider=provider,
            plan=fields.get("plan", ""),
            member_number=fields.get("afiliado", ""),
            emergency_phone=fields.get(
                "teléfono", fields.get("telefono", "")
            ),
            notes=fields.get("notas", ""),
        )

    @staticmethod
    def _fields(raw: str) -> dict[str, str]:
        values = {}
        for part in raw.split("|"):
            if "=" in part:
                name, value = part.split("=", 1)
                values[name.strip().casefold()] = value.strip()
        return values

    def _confirm(self, key: str) -> EmergencyContactResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return EmergencyContactResult(True, "No hay cambios pendientes.")
        contacts = self.repository.load_contacts()
        coverages = self.repository.load_coverages()
        if pending.kind == "contact":
            contacts = [
                item
                for item in contacts
                if item.contact_id != pending.value.contact_id
            ]
            contacts.append(pending.value)
        else:
            coverages = [
                item for item in coverages if item.person != pending.value.person
            ]
            coverages.append(pending.value)
        self.repository.save(contacts, coverages)
        return EmergencyContactResult(
            True, "Guardé el cambio de emergencia confirmado."
        )

    def _prepare_archive(self, contact_id: str, key: str) -> EmergencyContactResult:
        contact = self._find(contact_id)
        if contact is None:
            return EmergencyContactResult(True, "No encontré ese contacto.")
        self._pending[key] = _PendingChange(
            "contact", replace(contact, status="archivado", archived=True)
        )
        return EmergencyContactResult(
            True,
            f"Confirmá archivar a {contact.name}. Decí 'confirmar emergencia'.",
        )

    def _find(self, contact_id: str) -> EmergencyContact | None:
        return next(
            (
                item
                for item in self.repository.load_contacts()
                if item.contact_id == contact_id
            ),
            None,
        )

    def _list(self, person: str) -> EmergencyContactResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        contacts = [
            item
            for item in self.repository.load_contacts()
            if item.person == canonical
            and not item.archived
            and item.status == "activo"
        ]
        contacts.sort(key=lambda item: (item.priority, item.name.casefold()))
        if not contacts:
            return EmergencyContactResult(
                True, f"{canonical} no tiene contactos activos."
            )
        rows = [
            f"- Prioridad {item.priority}: {item.name} · {item.relationship} · "
            f"{item.primary_phone} · ID {item.contact_id}"
            for item in contacts
        ]
        return EmergencyContactResult(
            True, f"Contactos de emergencia de {canonical}:\n" + "\n".join(rows)
        )

    def _detail(self, contact_id: str) -> EmergencyContactResult:
        item = self._find(contact_id)
        if item is None:
            return EmergencyContactResult(True, "No encontré ese contacto.")
        decision = "sí" if item.can_make_decisions else "no registrado"
        return EmergencyContactResult(
            True,
            f"Contacto {item.contact_id} de {item.person}: {item.name} · "
            f"relación {item.relationship or 'sin registrar'} · "
            f"teléfono {item.primary_phone} · prioridad {item.priority} · "
            f"decisiones {decision} · estado {item.status}.",
        )

    def _summary(self, person: str) -> EmergencyContactResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        contacts = [
            item
            for item in self.repository.load_contacts()
            if item.person == canonical
            and item.status == "activo"
            and not item.archived
        ]
        contacts.sort(key=lambda item: (item.priority, item.name.casefold()))
        coverage = next(
            (
                item
                for item in self.repository.load_coverages()
                if item.person == canonical
            ),
            None,
        )
        rows = [f"Ficha de emergencia de {canonical}:"]
        if contacts:
            rows.append("Contactos prioritarios:")
            rows.extend(
                f"- {item.priority}. {item.name} · {item.relationship} · "
                f"{item.primary_phone}"
                for item in contacts[:3]
            )
        else:
            rows.append("Contactos prioritarios: no hay registros activos.")
        if coverage is not None:
            rows.append(
                f"Cobertura: {coverage.provider} · plan "
                f"{coverage.plan or 'sin registrar'} "
                f"· afiliado {coverage.member_number or 'sin registrar'} · "
                f"urgencias {coverage.emergency_phone or 'sin registrar'}"
            )
        else:
            rows.append("Cobertura: no hay datos registrados.")
        rows.append(
            "ROBY organiza estos datos, pero no realiza llamadas ni reemplaza "
            "los servicios oficiales de emergencia."
        )
        return EmergencyContactResult(True, "\n".join(rows))
