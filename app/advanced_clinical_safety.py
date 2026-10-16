from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from app.allergy_registry import AllergyRegistryService, AllergyRepository
from app.secure_medication_registry import MedicationRegistryRepository

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass
class InteractionRule:
    rule_id: str
    medication_a: str
    medication_b: str
    note: str
    source: str
    archived: bool = False


@dataclass
class StudyControlPlan:
    plan_id: str
    person: str
    study_type: str
    due_on: str
    professional: str = ""
    source: str = ""
    archived: bool = False


@dataclass(frozen=True)
class ClinicalSafetyResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingSafetyChange:
    kind: str
    value: InteractionRule | StudyControlPlan


class ClinicalSafetyRepository:
    """Stores confirmed safety rules and control deadlines atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "clinical_safety.json"

    def _load_payload(self) -> dict[str, object]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def load_interactions(self) -> list[InteractionRule]:
        rows = self._load_payload().get("interaction_rules", [])
        if not isinstance(rows, list):
            return []
        return [InteractionRule(**row) for row in rows if isinstance(row, dict)]

    def load_controls(self) -> list[StudyControlPlan]:
        rows = self._load_payload().get("study_controls", [])
        if not isinstance(rows, list):
            return []
        return [StudyControlPlan(**row) for row in rows if isinstance(row, dict)]

    def save(
        self,
        interactions: list[InteractionRule],
        controls: list[StudyControlPlan],
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "interaction_rules": [asdict(item) for item in interactions],
            "study_controls": [asdict(item) for item in controls],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="clinical_safety_",
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


class AdvancedClinicalSafetyService:
    """Reports factual medication and control risks without clinical inference."""

    _REPORT = re.compile(
        r"^(?:mostrar |ver )?(?:seguridad clínica|control de seguridad) de "
        r"(Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        medication_repository: MedicationRegistryRepository | None = None,
        repository: ClinicalSafetyRepository | None = None,
        now: Callable[[], datetime] | None = None,
        allergy_repository: AllergyRepository | None = None,
    ) -> None:
        self.medication_repository = (
            medication_repository or MedicationRegistryRepository()
        )
        self.repository = repository or ClinicalSafetyRepository()
        self._now = now or datetime.now
        self.allergy_repository = allergy_repository or AllergyRepository()
        self._pending: dict[str, _PendingSafetyChange] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> ClinicalSafetyResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in {"confirmar seguridad", "confirmá seguridad"}:
            return self._confirm(key)
        if folded in {"cancelar seguridad", "cancelá seguridad"}:
            self._pending.pop(key, None)
            return ClinicalSafetyResult(
                True,
                "Cancelé el cambio de seguridad pendiente.",
            )

        match = self._REPORT.fullmatch(normalized)
        if match:
            return self._report(match.group(1))

        interaction = self._parse_interaction(normalized)
        if interaction is not None:
            self._pending[key] = _PendingSafetyChange("interaction", interaction)
            return ClinicalSafetyResult(
                True,
                "Confirmá la regla de interacción potencial: "
                f"{interaction.medication_a} + {interaction.medication_b} · "
                f"{interaction.note} · fuente: {interaction.source}. "
                "Decí 'confirmar seguridad' para guardarla.",
            )

        control = self._parse_control(normalized)
        if control is not None:
            self._pending[key] = _PendingSafetyChange("control", control)
            return ClinicalSafetyResult(
                True,
                "Confirmá el control programado: "
                f"{control.person} · {control.study_type} · vence "
                f"{control.due_on}. Decí 'confirmar seguridad' para guardarlo.",
            )
        return ClinicalSafetyResult(False)

    def _parse_interaction(self, text: str) -> InteractionRule | None:
        match = re.match(
            r"^registrar interacción potencial:\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(1))
        required = {"medicamento a", "medicamento b", "nota", "fuente"}
        if not required.issubset(fields):
            return None
        return InteractionRule(
            uuid4().hex[:8],
            fields["medicamento a"],
            fields["medicamento b"],
            fields["nota"],
            fields["fuente"],
        )

    def _parse_control(self, text: str) -> StudyControlPlan | None:
        match = re.match(
            r"^registrar control de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        if not {"estudio", "vence"}.issubset(fields):
            return None
        try:
            date.fromisoformat(fields["vence"])
        except ValueError:
            return None
        return StudyControlPlan(
            uuid4().hex[:8],
            _ALLOWED_PEOPLE[match.group(1).casefold()],
            fields["estudio"],
            fields["vence"],
            fields.get("profesional", ""),
            fields.get("fuente", ""),
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

    def _confirm(self, key: str) -> ClinicalSafetyResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return ClinicalSafetyResult(True, "No hay cambios de seguridad pendientes.")
        interactions = self.repository.load_interactions()
        controls = self.repository.load_controls()
        if pending.kind == "interaction":
            interactions.append(pending.value)  # type: ignore[arg-type]
            message = "Guardé la regla documentada de interacción potencial."
        else:
            controls.append(pending.value)  # type: ignore[arg-type]
            message = "Guardé la fecha documentada del control médico."
        self.repository.save(interactions, controls)
        return ClinicalSafetyResult(True, message)

    def _report(self, person: str) -> ClinicalSafetyResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        today = self._now().date()
        active = [
            item
            for item in self.medication_repository.load()
            if item.person == canonical and self._active_on(item, today)
        ]
        duplicates = self._duplicates(active)
        expired = self._expired_active(canonical, today)
        renewals = self._renewals(active, today)
        interactions = self._interactions(active)
        allergy_matches = self._allergy_matches(canonical, active)
        controls = self._controls(canonical, today)
        sections = [
            f"Seguridad clínica de {canonical} · {today.isoformat()}",
            self._section("Posibles duplicidades", duplicates),
            self._section("Medicaciones activas vencidas", expired),
            self._section("Renovaciones próximas", renewals),
            self._section("Interacciones documentadas para revisar", interactions),
            self._allergy_section(allergy_matches),
            self._section("Controles médicos vencidos o próximos", controls),
            (
                "Revisión descriptiva basada en registros locales. No suspendas, "
                "dupliques ni cambies medicación sin consultar al profesional."
            ),
        ]
        return ClinicalSafetyResult(True, "\n\n".join(sections))

    def _allergy_matches(self, person: str, records: list[object]) -> list[str]:
        allergies = [
            item
            for item in self.allergy_repository.load()
            if item.person == person
        ]
        rows = []
        for medication in records:
            name = getattr(medication, "name")
            for allergy in allergies:
                if AllergyRegistryService.medication_matches(allergy, name):
                    rows.append(
                        f"- {name} coincide exactamente con la alergia "
                        f"{allergy.allergen} · revisar con profesional"
                    )
        return sorted(set(rows))

    @staticmethod
    def _allergy_section(rows: list[str]) -> str:
        title = "Coincidencias con alergias registradas"
        return f"{title}:\n" + (
            "\n".join(rows) if rows else "- sin coincidencias exactas"
        )

    @staticmethod
    def _section(title: str, rows: list[str]) -> str:
        return f"{title}:\n" + ("\n".join(rows) if rows else "- sin hallazgos")

    @staticmethod
    def _duplicates(records: list[object]) -> list[str]:
        groups: dict[str, list[object]] = {}
        for record in records:
            key = getattr(record, "name").strip().casefold()
            groups.setdefault(key, []).append(record)
        rows = []
        for items in groups.values():
            if len(items) > 1:
                ids = ", ".join(getattr(item, "record_id") for item in items)
                rows.append(f"- {getattr(items[0], 'name')} · registros {ids}")
        return rows

    def _expired_active(self, person: str, today: date) -> list[str]:
        rows = []
        for record in self.medication_repository.load():
            if record.person != person or record.archived or record.status != "activo":
                continue
            if record.end_date and date.fromisoformat(record.end_date) < today:
                rows.append(f"- {record.name} · finalizó {record.end_date}")
        return rows

    @staticmethod
    def _renewals(records: list[object], today: date) -> list[str]:
        limit = today + timedelta(days=30)
        rows = []
        for record in records:
            end_date = getattr(record, "end_date")
            if end_date and today <= date.fromisoformat(end_date) <= limit:
                rows.append(f"- {getattr(record, 'name')} · finaliza {end_date}")
        return rows

    def _interactions(self, records: list[object]) -> list[str]:
        names = {getattr(record, "name").strip().casefold() for record in records}
        rows = []
        for rule in self.repository.load_interactions():
            if rule.archived:
                continue
            both_active = (
                rule.medication_a.casefold() in names
                and rule.medication_b.casefold() in names
            )
            if both_active:
                rows.append(
                    f"- {rule.medication_a} + {rule.medication_b} · "
                    f"{rule.note} · fuente: {rule.source}"
                )
        return rows

    def _controls(self, person: str, today: date) -> list[str]:
        limit = today + timedelta(days=30)
        rows = []
        for plan in self.repository.load_controls():
            if plan.person != person or plan.archived:
                continue
            due = date.fromisoformat(plan.due_on)
            if due <= limit:
                state = "vencido" if due < today else "próximo"
                detail = f"- {plan.study_type} · {state} · {plan.due_on}"
                if plan.professional:
                    detail += f" · {plan.professional}"
                rows.append(detail)
        return rows

    @staticmethod
    def _active_on(record: object, target: date) -> bool:
        if getattr(record, "archived") or getattr(record, "status") != "activo":
            return False
        start_date = getattr(record, "start_date")
        end_date = getattr(record, "end_date")
        if start_date and date.fromisoformat(start_date) > target:
            return False
        return not (end_date and date.fromisoformat(end_date) < target)
