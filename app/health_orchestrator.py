from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from app.allergy_registry import AllergyRepository
from app.chronic_condition_registry import ChronicConditionRepository
from app.emergency_contacts import EmergencyContactRepository
from app.healthcare_directory import HealthcareDirectoryRepository
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.structured_symptom_registry import SymptomRepository
from app.vital_sign_history import VitalSignHistoryService, VitalSignRepository

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass(frozen=True)
class HealthOrchestratorResult:
    handled: bool
    response: str = ""


class HealthOrchestratorService:
    """Builds a unified, descriptive health snapshot from confirmed local data."""

    _INTEGRAL = re.compile(
        r"^(?:mostrar |ver )?(?:orquestador integral(?: de salud)?|"
        r"panorama integral|prioridades de salud) de (Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )
    _SUMMARY = re.compile(
        r"^(?:mostrar |ver )?(?:resumen|estado) de salud de "
        r"(Carlos|Cristina)(?: hoy)?$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        medication_repository: MedicationRegistryRepository | None = None,
        checkup_repository: HealthCheckupRepository | None = None,
        now: Callable[[], datetime] | None = None,
        vital_repository: VitalSignRepository | None = None,
        symptom_repository: SymptomRepository | None = None,
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
        self.symptom_repository = symptom_repository or SymptomRepository()
        self.allergy_repository = allergy_repository or AllergyRepository()
        self.chronic_repository = chronic_repository or ChronicConditionRepository()
        self.directory_repository = (
            directory_repository or HealthcareDirectoryRepository()
        )
        self.emergency_repository = emergency_repository or EmergencyContactRepository()
        self._now = now or datetime.now

    def prepare(self, text: str) -> HealthOrchestratorResult:
        normalized = " ".join(text.strip().split())
        integral = self._INTEGRAL.fullmatch(normalized)
        if integral is not None:
            return self._integral_for(integral.group(1))
        match = self._SUMMARY.fullmatch(normalized)
        if match is None:
            return HealthOrchestratorResult(handled=False)
        return self._summary_for(match.group(1))

    def _integral_for(self, person: str) -> HealthOrchestratorResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        today = self._now().date()
        medications = self._medication_rows(canonical, today)
        symptoms = self._active_symptoms(canonical)
        allergies = self._active_allergies(canonical)
        conditions = self._active_conditions(canonical)
        checkups = self._checkup_rows(canonical)
        vitals = self._vital_rows(canonical)
        care = self._care_rows(canonical)
        emergency = self._emergency_rows(canonical)

        priorities: list[str] = []
        high_intensity = [
            item
            for item in symptoms
            if item.intensity is not None and item.intensity >= 7
        ]
        if high_intensity:
            priorities.append(
                f"Alta: {len(high_intensity)} síntoma(s) activo(s) con intensidad "
                "registrada de 7/10 o más; revisar evolución y buscar orientación "
                "profesional según el contexto."
            )
        severe_allergies = [
            item
            for item in allergies
            if item.severity.casefold() in {"grave", "severa", "alta"}
        ]
        if severe_allergies:
            priorities.append(
                f"Alta: {len(severe_allergies)} alergia(s) activa(s) con gravedad "
                "registrada alta o grave."
            )
        pending_medication = [row for row in medications if "pendiente" in row]
        if pending_medication:
            priorities.append(
                f"Seguimiento: {len(pending_medication)} toma(s) de hoy pendientes "
                "de confirmar."
            )
        if symptoms and not high_intensity:
            priorities.append(
                f"Seguimiento: {len(symptoms)} episodio(s) de síntomas activos."
            )
        if conditions:
            priorities.append(
                f"Seguimiento: {len(conditions)} condición(es) crónica(s) "
                "registrada(s)."
            )
        if not emergency:
            priorities.append(
                "Preventiva: no hay contactos ni cobertura de emergencia registrados."
            )
        if not priorities:
            priorities.append(
                "Sin prioridades detectadas a partir de los registros confirmados."
            )

        sections = [
            self._integral_section("Prioridades registradas", priorities),
            self._integral_section("Medicación de hoy", medications),
            self._integral_section("Síntomas activos", self._symptom_rows(canonical)),
            self._integral_section("Alergias activas", self._allergy_rows(canonical)),
            self._integral_section(
                "Condiciones crónicas", self._chronic_rows(canonical)
            ),
            self._integral_section("Último control de signos", vitals),
            self._integral_section("Últimos chequeos", checkups),
            self._integral_section("Equipo y centros de salud", care),
            self._integral_section("Emergencia", emergency),
        ]
        return HealthOrchestratorResult(
            handled=True,
            response=(
                f"Orquestador integral de salud de {canonical} para "
                f"{today.isoformat()}:\n"
                + "\n".join(sections)
                + "\nLas prioridades se basan únicamente en datos confirmados y reglas "
                "descriptivas. ROBY no diagnostica, no determina urgencia clínica "
                "por sí solo y no modifica tratamientos."
            ),
        )

    @staticmethod
    def _integral_section(title: str, rows: list[str]) -> str:
        if not rows:
            return f"{title}: sin registros activos."
        normalized = [row if row.startswith("-") else f"- {row}" for row in rows]
        return f"{title}:\n" + "\n".join(normalized)

    def _active_symptoms(self, person: str) -> list[object]:
        return [
            item
            for item in self.symptom_repository.load()
            if item.person == person and item.status == "activo" and not item.archived
        ]

    def _active_allergies(self, person: str) -> list[object]:
        return [
            item
            for item in self.allergy_repository.load()
            if item.person == person and item.status == "activa" and not item.archived
        ]

    def _active_conditions(self, person: str) -> list[object]:
        return [
            item
            for item in self.chronic_repository.load()
            if item.person == person and not item.archived
        ]

    def _summary_for(self, person: str) -> HealthOrchestratorResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        today = self._now().date()
        medication_rows = self._medication_rows(canonical, today)
        checkup_rows = self._checkup_rows(canonical)
        vital_rows = self._vital_rows(canonical)
        symptom_rows = self._symptom_rows(canonical)
        allergy_rows = self._allergy_rows(canonical)
        chronic_rows = self._chronic_rows(canonical)
        care_rows = self._care_rows(canonical)
        emergency_rows = self._emergency_rows(canonical)

        medication_section = (
            "Medicación de hoy:\n" + "\n".join(medication_rows)
            if medication_rows
            else "Medicación de hoy: no hay tomas activas programadas."
        )
        checkup_section = (
            "Últimos chequeos:\n" + "\n".join(checkup_rows)
            if checkup_rows
            else "Últimos chequeos: no hay registros activos."
        )
        symptom_section = (
            "Síntomas activos:\n" + "\n".join(symptom_rows)
            if symptom_rows
            else "Síntomas activos: no hay episodios activos."
        )
        allergy_section = (
            "Alergias activas:\n" + "\n".join(allergy_rows)
            if allergy_rows
            else "Alergias activas: no hay registros activos."
        )
        chronic_section = (
            "Condiciones crónicas:\n" + "\n".join(chronic_rows)
            if chronic_rows
            else "Condiciones crónicas: no hay registros activos."
        )
        care_section = (
            "Equipo y centros de salud:\n" + "\n".join(care_rows)
            if care_rows
            else "Equipo y centros de salud: no hay registros activos."
        )
        emergency_section = (
            "Emergencia:\n" + "\n".join(emergency_rows)
            if emergency_rows
            else "Emergencia: no hay contactos ni cobertura registrados."
        )
        vital_section = (
            "Último control de signos:\n" + "\n".join(vital_rows)
            if vital_rows
            else "Último control de signos: no hay registros activos."
        )
        return HealthOrchestratorResult(
            handled=True,
            response=(
                f"Resumen de salud de {canonical} para {today.isoformat()}:\n"
                f"{medication_section}\n{allergy_section}\n"
                f"{chronic_section}\n{care_section}\n{emergency_section}\n"
                f"{symptom_section}\n"
                f"{vital_section}\n{checkup_section}\n"
                "Este resumen reúne datos confirmados del registro local. "
                "No interpreta síntomas, no modifica indicaciones y no reemplaza "
                "la consulta profesional."
            ),
        )

    def _medication_rows(self, person: str, today: date) -> list[str]:
        records = [
            record
            for record in self.medication_repository.load()
            if record.person == person and self._active_on(record, today)
        ]
        intakes = {
            (item.medication_id, item.scheduled_date, item.scheduled_time): item
            for item in self.medication_repository.load_intakes()
        }
        today_key = today.isoformat()
        rows: list[str] = []
        for record in records:
            for schedule in record.schedules:
                intake = intakes.get((record.record_id, today_key, schedule))
                state = (
                    intake.status if intake is not None else "pendiente de confirmar"
                )
                if (
                    intake is not None
                    and intake.status == "postergado"
                    and intake.due_at
                ):
                    due_at = datetime.fromisoformat(intake.due_at)
                    state = f"postergado hasta {due_at:%H:%M}"
                rows.append(f"- {schedule} · {record.name} · {record.dosage} · {state}")
        return sorted(rows)

    def _vital_rows(self, person: str) -> list[str]:
        records = [
            record
            for record in self.vital_repository.load()
            if record.person == person and not record.archived
        ]
        if not records:
            return []
        latest = max(records, key=lambda record: record.measured_at)
        values = VitalSignHistoryService.render_values(latest)
        return [f"- {latest.measured_at} · {values}"]

    def _symptom_rows(self, person: str) -> list[str]:
        episodes = [
            item
            for item in self.symptom_repository.load()
            if item.person == person and item.status == "activo" and not item.archived
        ]
        episodes.sort(key=lambda item: item.started_at, reverse=True)
        rows = []
        for episode in episodes[:5]:
            intensity = (
                f" · intensidad {episode.intensity}/10"
                if episode.intensity is not None
                else ""
            )
            rows.append(
                f"- {episode.started_at} · {episode.symptom}{intensity} · "
                f"{episode.evolution} · ID {episode.episode_id}"
            )
        return rows

    def _allergy_rows(self, person: str) -> list[str]:
        records = [
            item
            for item in self.allergy_repository.load()
            if item.person == person and item.status == "activa" and not item.archived
        ]
        records.sort(key=lambda item: item.allergen.casefold())
        rows = []
        for item in records:
            detail = f"- {item.allergen} · {item.allergy_type}"
            if item.reaction:
                detail += f" · reacción {item.reaction}"
            rows.append(detail)
        return rows

    def _chronic_rows(self, person: str) -> list[str]:
        records = [
            item
            for item in self.chronic_repository.load()
            if item.person == person and not item.archived
        ]
        records.sort(key=lambda item: item.name.casefold())
        return [
            f"- {item.name} · estado registrado {item.status} · ID {item.condition_id}"
            for item in records
        ]

    def _emergency_rows(self, person: str) -> list[str]:
        contacts = [
            item
            for item in self.emergency_repository.load_contacts()
            if item.person == person and item.status == "activo" and not item.archived
        ]
        contacts.sort(key=lambda item: (item.priority, item.name.casefold()))
        rows = [
            f"- Contacto {item.priority}: {item.name} · {item.relationship} · "
            f"{item.primary_phone}"
            for item in contacts[:3]
        ]
        coverage = next(
            (
                item
                for item in self.emergency_repository.load_coverages()
                if item.person == person
            ),
            None,
        )
        if coverage is not None:
            rows.append(
                f"- Cobertura: {coverage.provider} · "
                f"urgencias {coverage.emergency_phone or 'sin registrar'}"
            )
        return rows

    def _checkup_rows(self, person: str) -> list[str]:
        records = [
            record
            for record in self.checkup_repository.load()
            if record.person == person and not record.archived
        ]
        records.sort(key=lambda record: record.performed_on, reverse=True)
        return [
            f"- {record.performed_on} · {record.study_type} · ID {record.record_id}"
            for record in records[:3]
        ]

    def _active_on(self, record: object, target: date) -> bool:
        if getattr(record, "archived") or getattr(record, "status") != "activo":
            return False
        start_date = getattr(record, "start_date")
        end_date = getattr(record, "end_date")
        if start_date and date.fromisoformat(start_date) > target:
            return False
        return not (end_date and date.fromisoformat(end_date) < target)

    def _care_rows(self, person: str) -> list[str]:
        professionals = [
            item
            for item in self.directory_repository.load_professionals()
            if item.person == person and not item.archived
        ]
        centers = [
            item
            for item in self.directory_repository.load_centers()
            if item.person == person and not item.archived
        ]
        rows = [
            f"- Profesional: {item.name} · {item.specialty or 'sin especialidad'}"
            for item in sorted(professionals, key=lambda value: value.name.casefold())
        ]
        rows.extend(
            f"- Centro: {item.name} · {item.center_type or 'sin tipo'}"
            for item in sorted(centers, key=lambda value: value.name.casefold())
        )
        return rows[:8]
