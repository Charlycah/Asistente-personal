from __future__ import annotations

import re
from dataclasses import dataclass

from domain.reminders import Reminder

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_MEDICAL_TERMS = (
    "turno",
    "consulta",
    "control",
)
_CARE_TERMS = (
    "médic",
    "medic",
    "doctor",
    "doctora",
    "dr ",
    "dra ",
    "cardió",
    "cardio",
    "odont",
    "dent",
    "traumat",
    "dermat",
    "oftalm",
    "ginec",
    "urolog",
    "neur",
    "pediatr",
    "clínic",
    "clinic",
    "hospital",
    "sanatorio",
)


@dataclass(frozen=True, slots=True)
class MedicalAppointmentCue:
    person: str
    reminder_id: str


class MedicalAppointmentConsultationOffer:
    """Recognize a bounded medical reminder and append an opt-in preparation offer."""

    def recognize(self, reminder: Reminder) -> MedicalAppointmentCue | None:
        text = " ".join(
            value.strip()
            for value in (reminder.title, reminder.description or "")
            if value and value.strip()
        )
        normalized = text.casefold()
        if not any(term in normalized for term in _MEDICAL_TERMS):
            return None
        if not any(term in normalized for term in _CARE_TERMS):
            return None

        people = {
            canonical
            for key, canonical in _ALLOWED_PEOPLE.items()
            if re.search(rf"\b{re.escape(key)}\b", normalized)
        }
        if len(people) != 1:
            return None
        return MedicalAppointmentCue(
            person=people.pop(),
            reminder_id=str(reminder.id),
        )

    def enhance(self, reminder: Reminder, message: str) -> str:
        cue = self.recognize(reminder)
        if cue is None:
            return message
        return (
            f"{message}\n"
            f"Si querés, puedo preparar el resumen preconsulta de {cue.person}."
        )
