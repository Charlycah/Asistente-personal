from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from app.allergy_registry import AllergyRepository
from app.chronic_condition_registry import ChronicConditionRepository
from app.emergency_contacts import EmergencyContactRepository
from app.healthcare_directory import HealthcareDirectoryRepository
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.vital_sign_history import VitalSignHistoryService, VitalSignRepository

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass(frozen=True)
class MedicalConsultationPreparationResult:
    handled: bool
    response: str = ""


class MedicalConsultationPreparationService:
    """Builds a factual pre-consultation summary from confirmed local data."""

    _COMMAND = re.compile(
        r"^(?:preparar|preparame|prepará|generar|mostrar) "
        r"(?:un )?(?:resumen|informe) (?:para (?:la )?consulta|preconsulta) "
        r"de (Carlos|Cristina)(?: con (?:el|la) (.+))?$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        medication_repository: MedicationRegistryRepository | None = None,
        checkup_repository: HealthCheckupRepository | None = None,
        vital_repository: VitalSignRepository | None = None,
        now: Callable[[], datetime] | None = None,
        allergy_repository: AllergyRepository | None = None,
        chronic_repository: ChronicConditionRepository | None = None,
        directory_repository: HealthcareDirectoryRepository | None = None,
        emergency_repository: EmergencyContactRepository | None = None,
    ) -> None:
        self.medication_repository = (
            medication_repository or MedicationRegistryRepository()
        )
        self.checkup_repository = checkup_repository or HealthCheckupRepository()
        self.vital_repository = vital_repository or VitalSignRepository()
        self._now = now or datetime.now
        self.allergy_repository = allergy_repository or AllergyRepository()
        self.chronic_repository = chronic_repository or ChronicConditionRepository()
        self.directory_repository = (
            directory_repository or HealthcareDirectoryRepository()
        )
        self.emergency_repository = (
            emergency_repository or EmergencyContactRepository()
        )

    def prepare(self, text: str) -> MedicalConsultationPreparationResult:
        normalized = " ".join(text.strip().split())
        match = self._COMMAND.fullmatch(normalized)
        if match is None:
            return MedicalConsultationPreparationResult(False)
        person = _ALLOWED_PEOPLE[match.group(1).casefold()]
        professional = (match.group(2) or "").strip()
        return self._build(person, professional)

    def _build(
        self,
        person: str,
        professional: str,
    ) -> MedicalConsultationPreparationResult:
        today = self._now().date()
        heading = f"Resumen preconsulta de {person} · {today.isoformat()}"
        if professional:
            heading += f" · para {professional}"
        sections = [
            heading,
            self._allergies(person),
            self._chronic_conditions(person),
            self._care_directory(person, professional),
            self._emergency_contacts(person),
            self._medications(person, today),
            self._recent_medication_changes(person, today),
            self._recent_adherence(person, today),
            self._vital_signs(person, today),
            self._checkups(person),
            (
                "Síntomas registrados: no existe aún un registro estructurado "
                "de síntomas para incluir automáticamente."
            ),
            (
                "Estudios pendientes: no hay vencimientos ni órdenes pendientes "
                "estructuradas en el registro actual."
            ),
            (
                "Puntos para revisar con el profesional:\n"
                "- Confirmar que la lista de medicación siga vigente.\n"
                "- Comentar cambios recientes en signos o cumplimiento.\n"
                "- Llevar los estudios originales mencionados en este resumen."
            ),
            (
                "Documento descriptivo basado en datos locales confirmados. "
                "No diagnostica, no interpreta resultados y no reemplaza la "
                "evaluación profesional."
            ),
        ]
        return MedicalConsultationPreparationResult(True, "\n\n".join(sections))

    def _allergies(self, person: str) -> str:
        records = [
            item
            for item in self.allergy_repository.load()
            if item.person == person
            and item.status == "activa"
            and not item.archived
        ]
        records.sort(key=lambda item: item.allergen.casefold())
        if not records:
            return "Alergias activas: no hay registros activos."
        rows = []
        for item in records:
            detail = f"- {item.allergen} · tipo {item.allergy_type}"
            if item.reaction:
                detail += f" · reacción {item.reaction}"
            if item.severity:
                detail += f" · gravedad {item.severity}"
            rows.append(detail)
        return "Alergias activas:\n" + "\n".join(rows)

    def _chronic_conditions(self, person: str) -> str:
        records = [
            item
            for item in self.chronic_repository.load()
            if item.person == person and not item.archived
        ]
        records.sort(key=lambda item: item.name.casefold())
        if not records:
            return "Condiciones crónicas: no hay registros activos."
        rows = []
        for item in records:
            detail = f"- {item.name} · estado registrado {item.status}"
            if item.professional:
                detail += f" · profesional {item.professional}"
            if item.health_center:
                detail += f" · centro {item.health_center}"
            rows.append(detail)
        return "Condiciones crónicas:\n" + "\n".join(rows)

    def _care_directory(self, person: str, requested: str) -> str:
        professionals = [
            item for item in self.directory_repository.load_professionals()
            if item.person == person and not item.archived
        ]
        centers = {
            item.center_id: item
            for item in self.directory_repository.load_centers()
            if item.person == person and not item.archived
        }
        rows = []
        for item in sorted(professionals, key=lambda value: value.name.casefold()):
            detail = f"- {item.name} · {item.specialty or 'sin especialidad'}"
            linked = [
                centers[value].name
                for value in item.center_ids
                if value in centers
            ]
            if linked:
                detail += f" · centros {', '.join(linked)}"
            if requested and requested.casefold() in item.name.casefold():
                detail += " · profesional indicado para esta preconsulta"
            rows.append(detail)
        if not rows:
            return "Profesionales tratantes: no hay registros activos."
        return "Profesionales tratantes:\n" + "\n".join(rows)

    def _emergency_contacts(self, person: str) -> str:
        contacts = [
            item
            for item in self.emergency_repository.load_contacts()
            if item.person == person and item.status == "activo" and not item.archived
        ]
        contacts.sort(key=lambda item: (item.priority, item.name.casefold()))
        if not contacts:
            return "Contactos de emergencia: no hay registros activos."
        rows = [
            f"- {item.name} · {item.relationship} · {item.primary_phone}"
            for item in contacts[:3]
        ]
        return "Contactos de emergencia:\n" + "\n".join(rows)

    def _medications(self, person: str, today: date) -> str:
        records = [
            record
            for record in self.medication_repository.load()
            if record.person == person and self._active_on(record, today)
        ]
        if not records:
            return "Medicación actual: no hay medicamentos activos registrados."
        rows = []
        for record in sorted(records, key=lambda item: item.name.casefold()):
            schedules = ", ".join(record.schedules) or "sin horario"
            detail = f"- {record.name} · {record.dosage} · {schedules}"
            if record.professional:
                detail += f" · indicado por {record.professional}"
            if record.instructions:
                detail += f" · {record.instructions}"
            rows.append(detail)
        return "Medicación actual:\n" + "\n".join(rows)

    def _recent_medication_changes(self, person: str, today: date) -> str:
        cutoff = today - timedelta(days=30)
        rows: list[str] = []
        for record in self.medication_repository.load():
            if record.person != person or record.archived:
                continue
            dates = [
                ("inicio", record.start_date),
                ("revisión", record.reviewed_on),
                ("finalización", record.end_date),
            ]
            for label, value in dates:
                parsed = self._safe_date(value)
                if parsed is not None and cutoff <= parsed <= today:
                    rows.append(
                        f"- {parsed.isoformat()} · {record.name} · {label} "
                        f"documentada · estado {record.status}"
                    )
        if not rows:
            return "Cambios recientes de medicación: ninguno documentado en 30 días."
        return "Cambios recientes de medicación:\n" + "\n".join(sorted(rows))

    def _recent_adherence(self, person: str, today: date) -> str:
        cutoff = today - timedelta(days=7)
        intakes = [
            item
            for item in self.medication_repository.load_intakes()
            if item.person == person
            and cutoff <= date.fromisoformat(item.scheduled_date) <= today
        ]
        if not intakes:
            return "Cumplimiento reciente: no hay tomas registradas en 7 días."
        counts: dict[str, int] = {}
        for intake in intakes:
            counts[intake.status] = counts.get(intake.status, 0) + 1
        details = ", ".join(
            f"{status}: {count}" for status, count in sorted(counts.items())
        )
        return f"Cumplimiento reciente (7 días): {details}."

    def _vital_signs(self, person: str, today: date) -> str:
        cutoff = datetime.combine(today - timedelta(days=30), datetime.min.time())
        records = [
            record
            for record in self.vital_repository.load()
            if record.person == person
            and not record.archived
            and datetime.fromisoformat(record.measured_at) >= cutoff
        ]
        records.sort(key=lambda item: item.measured_at)
        if not records:
            return "Signos vitales: no hay controles activos en los últimos 30 días."
        first = records[0]
        latest = records[-1]
        section = (
            f"Signos vitales (30 días): {len(records)} control(es).\n"
            f"- Último: {latest.measured_at} · "
            f"{VitalSignHistoryService.render_values(latest)}"
        )
        if len(records) > 1:
            section += (
                f"\n- Primer control del período: {first.measured_at} · "
                f"{VitalSignHistoryService.render_values(first)}"
            )
        return section

    def _checkups(self, person: str) -> str:
        records = [
            record
            for record in self.checkup_repository.load()
            if record.person == person and not record.archived
        ]
        records.sort(key=lambda item: item.performed_on, reverse=True)
        if not records:
            return "Estudios recientes: no hay estudios activos registrados."
        rows = []
        for record in records[:5]:
            detail = (
                f"- {record.performed_on} · {record.study_type} · "
                f"ID {record.record_id}"
            )
            if record.institution:
                detail += f" · {record.institution}"
            if record.professional:
                detail += f" · {record.professional}"
            rows.append(detail)
        return "Estudios recientes:\n" + "\n".join(rows)

    @staticmethod
    def _safe_date(value: str) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    @staticmethod
    def _active_on(record: object, target: date) -> bool:
        if getattr(record, "archived") or getattr(record, "status") != "activo":
            return False
        start_date = getattr(record, "start_date")
        end_date = getattr(record, "end_date")
        if start_date and date.fromisoformat(start_date) > target:
            return False
        return not (end_date and date.fromisoformat(end_date) < target)
