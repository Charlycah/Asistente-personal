from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime

from app.allergy_registry import AllergyRepository
from app.chronic_condition_registry import ChronicConditionRepository
from app.emergency_contacts import EmergencyContactRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.structured_symptom_registry import SymptomRepository

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_URGENT_TERMS = (
    "dolor de pecho",
    "dificultad para respirar",
    "falta de aire",
    "pérdida de conocimiento",
    "perdida de conocimiento",
    "desmayo",
    "sangrado abundante",
    "confusión",
    "confusion",
)


@dataclass(frozen=True)
class ConversationalHealthGuidanceResult:
    handled: bool
    response: str = ""


class ConversationalHealthGuidanceService:
    """Offers descriptive next-step guidance from confirmed local health data."""

    _REQUEST = re.compile(
        r"^(?:guía|guia|orientación|orientacion)(?: conversacional)? de salud de "
        r"(Carlos|Cristina)$|^(?:orientame|oriéntame) sobre la salud de "
        r"(Carlos|Cristina)$|^qué debería revisar de salud de (Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        medication_repository: MedicationRegistryRepository | None = None,
        symptom_repository: SymptomRepository | None = None,
        allergy_repository: AllergyRepository | None = None,
        chronic_repository: ChronicConditionRepository | None = None,
        emergency_repository: EmergencyContactRepository | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.medication_repository = (
            medication_repository or MedicationRegistryRepository()
        )
        self.symptom_repository = symptom_repository or SymptomRepository()
        self.allergy_repository = allergy_repository or AllergyRepository()
        self.chronic_repository = chronic_repository or ChronicConditionRepository()
        self.emergency_repository = emergency_repository or EmergencyContactRepository()
        self._now = now or datetime.now

    def prepare(self, text: str) -> ConversationalHealthGuidanceResult:
        normalized = " ".join(text.strip().split())
        match = self._REQUEST.fullmatch(normalized)
        if match is None:
            return ConversationalHealthGuidanceResult(handled=False)
        person = next(group for group in match.groups() if group is not None)
        return self._guide_for(_ALLOWED_PEOPLE[person.casefold()])

    def _guide_for(self, person: str) -> ConversationalHealthGuidanceResult:
        symptoms = [
            item
            for item in self.symptom_repository.load()
            if item.person == person and item.status == "activo" and not item.archived
        ]
        allergies = [
            item
            for item in self.allergy_repository.load()
            if item.person == person and item.status == "activa" and not item.archived
        ]
        conditions = [
            item
            for item in self.chronic_repository.load()
            if item.person == person and not item.archived
        ]
        urgent = [
            item
            for item in symptoms
            if self._contains_urgent_term(item.symptom, item.accompanying_symptoms)
        ]
        precaution = [
            item
            for item in symptoms
            if item not in urgent and item.intensity is not None and item.intensity >= 7
        ]
        severe_allergies = [
            item
            for item in allergies
            if item.severity.casefold() in {"alta", "grave", "severa"}
        ]
        pending = self._pending_medication_count(person, self._now().date())

        sections: list[str] = []
        if urgent:
            sections.append(
                "Urgente: hay síntomas registrados que coinciden con señales de "
                "alarma explícitas. Buscá asistencia médica inmediata o contactá "
                "los servicios oficiales de emergencia de tu zona."
            )
        if precaution or severe_allergies:
            details = []
            if precaution:
                details.append(
                    f"{len(precaution)} síntoma(s) con intensidad registrada de 7/10 "
                    "o más"
                )
            if severe_allergies:
                details.append(
                    f"{len(severe_allergies)} alergia(s) con gravedad alta o grave"
                )
            sections.append(
                "Precaución: " + " y ".join(details) + ". Revisá la evolución y "
                "consultá a un profesional según el contexto."
            )
        followups = []
        if pending:
            followups.append(f"confirmar {pending} toma(s) de medicación de hoy")
        nonurgent_symptoms = [item for item in symptoms if item not in urgent]
        if nonurgent_symptoms:
            followups.append(
                "actualizar la evolución de "
                f"{len(nonurgent_symptoms)} síntoma(s) activo(s)"
            )
        if conditions:
            followups.append(
                f"revisar el seguimiento documentado de {len(conditions)} condición(es)"
            )
        if followups:
            sections.append("Seguimiento: " + "; ".join(followups) + ".")
        if not sections:
            sections.append(
                "Informativo: no aparecen prioridades conversacionales a partir de "
                "los registros confirmados. Podés mantener actualizados síntomas, "
                "medicación, alergias y controles."
            )
        emergency_contacts = self.emergency_repository.load_contacts()
        coverage = self.emergency_repository.load_coverages()
        has_emergency = any(
            item.person == person and item.status == "activo" and not item.archived
            for item in emergency_contacts
        ) or any(item.person == person for item in coverage)
        if not has_emergency:
            sections.append(
                "Preventiva: no hay contactos ni cobertura de emergencia registrados."
            )
        return ConversationalHealthGuidanceResult(
            handled=True,
            response=(
                f"Guía conversacional de salud de {person}:\n- "
                + "\n- ".join(sections)
                + "\nEsta guía organiza datos confirmados. No diagnostica, "
                "no reemplaza "
                "una consulta profesional y no indica iniciar, suspender o modificar "
                "tratamientos."
            ),
        )

    @staticmethod
    def _contains_urgent_term(*values: str) -> bool:
        text = " ".join(values).casefold()
        return any(term in text for term in _URGENT_TERMS)

    def _pending_medication_count(self, person: str, today: date) -> int:
        records = [
            record
            for record in self.medication_repository.load()
            if record.person == person and self._active_on(record, today)
        ]
        intakes = {
            (item.medication_id, item.scheduled_date, item.scheduled_time)
            for item in self.medication_repository.load_intakes()
        }
        today_key = today.isoformat()
        return sum(
            (record.record_id, today_key, schedule) not in intakes
            for record in records
            for schedule in record.schedules
        )

    @staticmethod
    def _active_on(record: object, today: date) -> bool:
        if getattr(record, "archived", False):
            return False
        if getattr(record, "status", "activo") != "activo":
            return False
        start_date = getattr(record, "start_date", "")
        end_date = getattr(record, "end_date", "")
        if start_date and date.fromisoformat(start_date) > today:
            return False
        return not (end_date and date.fromisoformat(end_date) < today)
