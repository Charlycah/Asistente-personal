import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_ALLOWED_STATUSES = {
    "activo": "activo",
    "activa": "activo",
    "pausado": "pausado",
    "pausada": "pausado",
    "finalizado": "finalizado",
    "finalizada": "finalizado",
}
_ALLOWED_MOMENTS = {"mañana", "mediodía", "tarde", "noche"}
_ALLOWED_FOOD_RELATIONS = {
    "antes de comer",
    "con comida",
    "después de comer",
    "indistinto",
    "sin especificar",
}


@dataclass
class MedicationRecord:
    record_id: str
    person: str
    name: str
    dosage: str
    schedules: list[str]
    presentation: str = ""
    moments: list[str] | None = None
    food_relation: str = "sin especificar"
    instructions: str = ""
    indication: str = ""
    professional: str = ""
    source: str = ""
    start_date: str = ""
    end_date: str = ""
    missed_dose_instruction: str = ""
    status: str = "activo"
    reviewed_on: str = ""
    archived: bool = False

    def __post_init__(self) -> None:
        if self.moments is None:
            self.moments = []


@dataclass
class MedicationIntake:
    intake_id: str
    medication_id: str
    person: str
    scheduled_date: str
    scheduled_time: str
    status: str
    recorded_at: str
    due_at: str = ""


@dataclass(frozen=True)
class MedicationRegistryResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingMedicationChange:
    action: str
    record: MedicationRecord


class MedicationRegistryRepository:
    """Stores medication records locally using atomic JSON replacement."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "medications.json"

    def _load_payload(self) -> dict[str, object]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def load(self) -> list[MedicationRecord]:
        payload = self._load_payload()
        records = payload.get("records", [])
        if not isinstance(records, list):
            return []
        return [MedicationRecord(**item) for item in records if isinstance(item, dict)]

    def load_intakes(self) -> list[MedicationIntake]:
        payload = self._load_payload()
        intakes = payload.get("intakes", [])
        if not isinstance(intakes, list):
            return []
        return [MedicationIntake(**item) for item in intakes if isinstance(item, dict)]

    def save(
        self,
        records: list[MedicationRecord],
        intakes: list[MedicationIntake] | None = None,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if intakes is None:
            intakes = self.load_intakes()
        payload = {
            "schema_version": 1,
            "records": [asdict(record) for record in records],
            "intakes": [asdict(intake) for intake in intakes],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="medications_",
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


class SecureMedicationRegistryService:
    """Maintains confirmed medication instructions without clinical inference."""

    def __init__(
        self,
        repository: MedicationRegistryRepository | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository or MedicationRegistryRepository()
        self._now = now or datetime.now
        self._pending: dict[str, _PendingMedicationChange] = {}

    def prepare(
        self,
        text: str,
        *,
        session_id: str | None = None,
    ) -> MedicationRegistryResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in {"confirmar medicamento", "confirmá el medicamento"}:
            return self._confirm(key)
        if folded in {"cancelar medicamento", "cancelá el medicamento"}:
            self._pending.pop(key, None)
            return MedicationRegistryResult(
                handled=True,
                response=(
                    "Cancelé el cambio pendiente y no guardé datos de medicación."
                ),
            )

        agenda_match = re.fullmatch(
            r"(?:mostrar |ver )?agenda de medicaci[oó]n de "
            r"(Carlos|Cristina)(?: hoy)?",
            normalized,
            flags=re.IGNORECASE,
        )
        if agenda_match:
            return self._agenda_for(agenda_match.group(1))

        history_match = re.fullmatch(
            r"(?:mostrar |ver )?historial de medicaci[oó]n de "
            r"(Carlos|Cristina)(?: hoy)?",
            normalized,
            flags=re.IGNORECASE,
        )
        if history_match:
            return self._history_for(history_match.group(1))

        taken_match = re.fullmatch(
            r"(?:marcar |registrar )?toma ([0-9a-f]{8}) (\d{2}:\d{2}) "
            r"como tomad[oa]",
            folded,
        )
        if taken_match:
            return self._record_intake(
                taken_match.group(1),
                taken_match.group(2),
                "tomado",
            )

        omitted_match = re.fullmatch(
            r"(?:marcar )?toma ([0-9a-f]{8}) (\d{2}:\d{2}) "
            r"como omitid[oa]",
            folded,
        )
        if omitted_match:
            return self._record_intake(
                omitted_match.group(1),
                omitted_match.group(2),
                "omitido",
            )

        postpone_match = re.fullmatch(
            r"postergar toma ([0-9a-f]{8}) (\d{2}:\d{2}) "
            r"(\d{1,3}) minutos",
            folded,
        )
        if postpone_match:
            return self._postpone_intake(
                postpone_match.group(1),
                postpone_match.group(2),
                int(postpone_match.group(3)),
            )

        state_match = re.fullmatch(
            r"estado de toma ([0-9a-f]{8}) (\d{2}:\d{2})",
            folded,
        )
        if state_match:
            return self._intake_state(
                state_match.group(1),
                state_match.group(2),
            )

        list_match = re.fullmatch(
            r"(?:mostrar|listar) medicamentos(?: activos)? de "
            r"(Carlos|Cristina)",
            normalized,
            flags=re.IGNORECASE,
        )
        if list_match:
            return self._list_for(list_match.group(1))

        detail_match = re.fullmatch(
            r"(?:mostrar|ver) medicamento ([0-9a-f]{8})",
            folded,
        )
        if detail_match:
            return self._show(detail_match.group(1))

        status_match = re.fullmatch(
            r"(?:marcar|poner) medicamento ([0-9a-f]{8}) como "
            r"(activo|activa|pausado|pausada|finalizado|finalizada)",
            folded,
        )
        if status_match:
            return self._prepare_status(
                key,
                status_match.group(1),
                status_match.group(2),
            )

        archive_match = re.fullmatch(
            r"archivar medicamento ([0-9a-f]{8})",
            folded,
        )
        if archive_match:
            return self._prepare_archive(key, archive_match.group(1))

        update_match = re.match(
            r"^actualizar medicamento ([0-9a-fA-F]{8}):\s*(.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if update_match:
            return self._prepare_update(
                key,
                update_match.group(1),
                update_match.group(2),
            )

        draft = self._parse_registration(normalized)
        if draft is None:
            return MedicationRegistryResult(handled=False)
        self._pending[key] = _PendingMedicationChange("registrar", draft)
        return MedicationRegistryResult(
            handled=True,
            response=self._render_confirmation("registrar", draft),
        )

    def _parse_registration(self, text: str) -> MedicationRecord | None:
        match = re.match(
            r"^registrar medicamento de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            return None

        fields = self._split_fields(match.group(2))
        person = self._person(match.group(1))
        name = self._pop_alternative(fields, "medicamento", "nombre").strip()
        dosage = fields.pop("dosis", "").strip()
        schedule_value = self._pop_alternative(
            fields,
            "horarios",
            "horario",
        )
        schedules = self._parse_schedules(schedule_value)
        if not name or not dosage or not schedules:
            return None

        moment_value = self._pop_alternative(
            fields,
            "momentos",
            "momento",
        )
        moments = self._parse_moments(moment_value)
        food_relation = (
            fields.pop(
                "comidas",
                "sin especificar",
            )
            .casefold()
            .strip()
        )
        if food_relation not in _ALLOWED_FOOD_RELATIONS:
            food_relation = "sin especificar"

        start_date = fields.pop("inicio", "").strip()
        end_date = fields.pop("fin", "").strip()
        if not self._valid_date_range(start_date, end_date):
            return None

        return MedicationRecord(
            record_id=uuid4().hex[:8],
            person=person,
            name=name,
            dosage=dosage,
            schedules=schedules,
            presentation=self._pop_alternative(
                fields,
                "presentación",
                "presentacion",
            ),
            moments=moments,
            food_relation=food_relation,
            instructions=fields.pop("instrucciones", ""),
            indication=self._pop_alternative(
                fields,
                "indicación",
                "indicacion",
            ),
            professional=fields.pop("profesional", ""),
            source=fields.pop("fuente", ""),
            start_date=start_date,
            end_date=end_date,
            missed_dose_instruction=self._pop_alternative(
                fields,
                "olvido",
                "dosis olvidada",
            ),
            reviewed_on=self._now().date().isoformat(),
        )

    def _prepare_update(
        self,
        key: str,
        record_id: str,
        raw_fields: str,
    ) -> MedicationRegistryResult:
        record = self._find(record_id.casefold())
        if record is None:
            return self._not_found(record_id)

        fields = self._split_fields(raw_fields)
        if not fields:
            return MedicationRegistryResult(
                handled=True,
                response="No encontré campos válidos para actualizar.",
            )

        candidate = MedicationRecord(**asdict(record))
        if "medicamento" in fields or "nombre" in fields:
            candidate.name = self._get_alternative(
                fields,
                "medicamento",
                "nombre",
            ).strip()
        if "dosis" in fields:
            candidate.dosage = fields["dosis"].strip()
        if "horarios" in fields or "horario" in fields:
            parsed = self._parse_schedules(
                self._get_alternative(
                    fields,
                    "horarios",
                    "horario",
                )
            )
            if not parsed:
                return MedicationRegistryResult(
                    handled=True,
                    response="Los horarios deben usar formato HH:MM.",
                )
            candidate.schedules = parsed
        if "momentos" in fields or "momento" in fields:
            candidate.moments = self._parse_moments(
                self._get_alternative(
                    fields,
                    "momentos",
                    "momento",
                )
            )

        for field_name, attribute in (
            ("presentación", "presentation"),
            ("presentacion", "presentation"),
            ("instrucciones", "instructions"),
            ("indicación", "indication"),
            ("indicacion", "indication"),
            ("profesional", "professional"),
            ("fuente", "source"),
            ("olvido", "missed_dose_instruction"),
            ("dosis olvidada", "missed_dose_instruction"),
        ):
            if field_name in fields:
                setattr(candidate, attribute, fields[field_name].strip())

        if "comidas" in fields:
            relation = fields["comidas"].casefold().strip()
            if relation not in _ALLOWED_FOOD_RELATIONS:
                return MedicationRegistryResult(
                    handled=True,
                    response="La relación con comidas no es válida.",
                )
            candidate.food_relation = relation

        for field_name, attribute in (
            ("inicio", "start_date"),
            ("fin", "end_date"),
        ):
            if field_name in fields:
                value = fields[field_name].strip()
                if value and not self._valid_date(value):
                    return MedicationRegistryResult(
                        handled=True,
                        response=(f"La fecha de {field_name} debe usar AAAA-MM-DD."),
                    )
                setattr(candidate, attribute, value)

        if not self._valid_date_range(
            candidate.start_date,
            candidate.end_date,
        ):
            return MedicationRegistryResult(
                handled=True,
                response=(
                    "La fecha de finalización no puede ser anterior "
                    "a la fecha de inicio."
                ),
            )

        if not candidate.name or not candidate.dosage or not candidate.schedules:
            return MedicationRegistryResult(
                handled=True,
                response="Nombre, dosis y horarios no pueden quedar vacíos.",
            )

        candidate.reviewed_on = self._now().date().isoformat()
        self._pending[key] = _PendingMedicationChange(
            "actualizar",
            candidate,
        )
        return MedicationRegistryResult(
            handled=True,
            response=self._render_confirmation("actualizar", candidate),
        )

    def _prepare_status(
        self,
        key: str,
        record_id: str,
        status: str,
    ) -> MedicationRegistryResult:
        record = self._find(record_id)
        if record is None:
            return self._not_found(record_id)
        candidate = MedicationRecord(**asdict(record))
        candidate.status = _ALLOWED_STATUSES[status]
        candidate.reviewed_on = self._now().date().isoformat()
        self._pending[key] = _PendingMedicationChange(
            "cambiar estado",
            candidate,
        )
        return MedicationRegistryResult(
            handled=True,
            response=self._render_confirmation(
                "cambiar estado",
                candidate,
            ),
        )

    def _prepare_archive(
        self,
        key: str,
        record_id: str,
    ) -> MedicationRegistryResult:
        record = self._find(record_id)
        if record is None:
            return self._not_found(record_id)
        candidate = MedicationRecord(**asdict(record))
        candidate.archived = True
        candidate.reviewed_on = self._now().date().isoformat()
        self._pending[key] = _PendingMedicationChange(
            "archivar",
            candidate,
        )
        return MedicationRegistryResult(
            handled=True,
            response=self._render_confirmation("archivar", candidate),
        )

    def _confirm(self, key: str) -> MedicationRegistryResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return MedicationRegistryResult(
                handled=True,
                response=("No hay un cambio de medicación pendiente para confirmar."),
            )

        records = self.repository.load()
        if pending.action == "registrar":
            records.append(pending.record)
        else:
            records = [
                pending.record if item.record_id == pending.record.record_id else item
                for item in records
            ]

        self.repository.save(records)
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Confirmé el cambio del medicamento "
                f"{pending.record.record_id} de {pending.record.person}. "
                "Guardé exactamente la indicación informada; no validé ni "
                "modifiqué la prescripción médica."
            ),
        )

    def _agenda_for(self, person: str) -> MedicationRegistryResult:
        canonical = self._person(person)
        today = self._now().date()
        records = [
            record
            for record in self.repository.load()
            if self._is_scheduled_on(record, today) and record.person == canonical
        ]
        if not records:
            return MedicationRegistryResult(
                handled=True,
                response=(f"No hay tomas activas programadas hoy para {canonical}."),
            )

        intake_index = {
            (
                intake.medication_id,
                intake.scheduled_date,
                intake.scheduled_time,
            ): intake
            for intake in self.repository.load_intakes()
        }
        today_key = today.isoformat()

        rows: list[str] = []
        for record in records:
            for schedule in record.schedules:
                intake = intake_index.get((record.record_id, today_key, schedule))
                state = self._agenda_state(
                    intake,
                    schedule,
                    today,
                )
                rows.append(
                    f"- {schedule} · {record.name} · {record.dosage} · "
                    f"{state} · ID {record.record_id}"
                )

        rows.sort()
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Agenda de medicación de {canonical} para "
                f"{today.isoformat()}:\n"
                + "\n".join(rows)
                + "\nLos estados registran cumplimiento; no cambian la "
                "indicación médica."
            ),
        )

    def _history_for(self, person: str) -> MedicationRegistryResult:
        canonical = self._person(person)
        today = self._now().date().isoformat()
        names = {record.record_id: record.name for record in self.repository.load()}
        entries = [
            intake
            for intake in self.repository.load_intakes()
            if intake.person == canonical and intake.scheduled_date == today
        ]
        if not entries:
            return MedicationRegistryResult(
                handled=True,
                response=f"No hay tomas registradas hoy para {canonical}.",
            )

        entries.sort(
            key=lambda item: (
                item.scheduled_time,
                item.recorded_at,
            )
        )
        rows = [
            f"- {item.scheduled_time} · "
            f"{names.get(item.medication_id, item.medication_id)} · "
            f"{item.status} · registrado {item.recorded_at}"
            for item in entries
        ]
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Historial de medicación de {canonical} hoy:\n" + "\n".join(rows)
            ),
        )

    def _record_intake(
        self,
        record_id: str,
        schedule: str,
        status: str,
    ) -> MedicationRegistryResult:
        record = self._find(record_id)
        validation = self._validate_occurrence(
            record,
            record_id,
            schedule,
        )
        if validation is not None:
            return validation

        assert record is not None
        now = self._now()
        intake = MedicationIntake(
            intake_id=uuid4().hex[:8],
            medication_id=record.record_id,
            person=record.person,
            scheduled_date=now.date().isoformat(),
            scheduled_time=schedule,
            status=status,
            recorded_at=now.isoformat(timespec="seconds"),
        )
        self._save_intake(intake)
        wording = "tomada" if status == "tomado" else "omitida"
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Registré como {wording} la toma de {record.name} de "
                f"{record.person} prevista para las {schedule}. "
                "No modifiqué la indicación médica."
            ),
        )

    def _postpone_intake(
        self,
        record_id: str,
        schedule: str,
        minutes: int,
    ) -> MedicationRegistryResult:
        record = self._find(record_id)
        validation = self._validate_occurrence(
            record,
            record_id,
            schedule,
        )
        if validation is not None:
            return validation
        if not 1 <= minutes <= 180:
            return MedicationRegistryResult(
                handled=True,
                response="La postergación debe ser de 1 a 180 minutos.",
            )

        assert record is not None
        now = self._now()
        due_at = now + timedelta(minutes=minutes)
        intake = MedicationIntake(
            intake_id=uuid4().hex[:8],
            medication_id=record.record_id,
            person=record.person,
            scheduled_date=now.date().isoformat(),
            scheduled_time=schedule,
            status="postergado",
            recorded_at=now.isoformat(timespec="seconds"),
            due_at=due_at.isoformat(timespec="seconds"),
        )
        self._save_intake(intake)
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Postergué el aviso de {record.name} de {record.person} "
                f"hasta las {due_at.strftime('%H:%M')}. El horario indicado "
                f"sigue siendo {schedule}."
            ),
        )

    def _intake_state(
        self,
        record_id: str,
        schedule: str,
    ) -> MedicationRegistryResult:
        record = self._find(record_id)
        validation = self._validate_occurrence(
            record,
            record_id,
            schedule,
        )
        if validation is not None:
            return validation

        assert record is not None
        today = self._now().date()
        intake = self._find_intake(
            record.record_id,
            schedule,
            today,
        )
        state = self._agenda_state(
            intake,
            schedule,
            today,
        )
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"La toma de {record.name} de {record.person} de las "
                f"{schedule} figura como {state}."
            ),
        )

    def _validate_occurrence(
        self,
        record: MedicationRecord | None,
        record_id: str,
        schedule: str,
    ) -> MedicationRegistryResult | None:
        if record is None:
            return self._not_found(record_id)
        if schedule not in record.schedules:
            return MedicationRegistryResult(
                handled=True,
                response=(
                    f"El horario {schedule} no está registrado para "
                    f"{record.name}. No hice cambios."
                ),
            )
        if not self._is_scheduled_on(record, self._now().date()):
            return MedicationRegistryResult(
                handled=True,
                response=("Ese medicamento no está activo para la fecha de hoy."),
            )
        return None

    def _save_intake(self, intake: MedicationIntake) -> None:
        records = self.repository.load()
        intakes = [
            item
            for item in self.repository.load_intakes()
            if not (
                item.medication_id == intake.medication_id
                and item.scheduled_date == intake.scheduled_date
                and item.scheduled_time == intake.scheduled_time
            )
        ]
        intakes.append(intake)
        self.repository.save(records, intakes)

    def _find_intake(
        self,
        record_id: str,
        schedule: str,
        scheduled_date: date,
    ) -> MedicationIntake | None:
        scheduled_date_key = scheduled_date.isoformat()
        return next(
            (
                item
                for item in self.repository.load_intakes()
                if item.medication_id == record_id
                and item.scheduled_date == scheduled_date_key
                and item.scheduled_time == schedule
            ),
            None,
        )

    def _agenda_state(
        self,
        intake: MedicationIntake | None,
        schedule: str,
        scheduled_date: date,
    ) -> str:
        if intake is not None:
            if intake.status == "postergado" and intake.due_at:
                due_at = datetime.fromisoformat(intake.due_at)
                if self._now() > due_at:
                    return f"postergación vencida desde {due_at:%H:%M}"
                return f"postergado hasta {due_at:%H:%M}"
            return intake.status

        scheduled = datetime.combine(
            scheduled_date,
            datetime.strptime(schedule, "%H:%M").time(),
        )
        return "pendiente" if self._now() <= scheduled else "sin confirmar"

    def _is_scheduled_on(
        self,
        record: MedicationRecord,
        target: date,
    ) -> bool:
        if record.archived or record.status != "activo":
            return False
        if record.start_date and date.fromisoformat(record.start_date) > target:
            return False
        if record.end_date and date.fromisoformat(record.end_date) < target:
            return False
        return True

    def _list_for(self, person: str) -> MedicationRegistryResult:
        canonical = self._person(person)
        records = [
            record
            for record in self.repository.load()
            if record.person == canonical and not record.archived
        ]
        if not records:
            return MedicationRegistryResult(
                handled=True,
                response=(f"No hay medicamentos registrados para {canonical}."),
            )

        rows = "\n".join(
            f"- {record.record_id}: {record.name} · "
            f"{record.dosage} · {', '.join(record.schedules)} · "
            f"{record.status}"
            for record in records
        )
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Medicamentos registrados de {canonical}:\n{rows}\n"
                "Esta lista reproduce datos confirmados y no reemplaza "
                "la receta."
            ),
        )

    def _show(self, record_id: str) -> MedicationRegistryResult:
        record = self._find(record_id)
        if record is None:
            return self._not_found(record_id)

        moments = ", ".join(record.moments or []) or "sin especificar"
        presentation = record.presentation or "sin especificar"
        instructions = record.instructions or "sin especificar"
        reviewed_on = record.reviewed_on or "sin especificar"
        return MedicationRegistryResult(
            handled=True,
            response=(
                f"Medicamento {record.record_id} de {record.person}:\n"
                f"- Nombre: {record.name}\n"
                f"- Presentación: {presentation}\n"
                f"- Dosis informada: {record.dosage}\n"
                f"- Horarios: {', '.join(record.schedules)}\n"
                f"- Momentos: {moments}\n"
                f"- Comidas: {record.food_relation}\n"
                f"- Instrucciones: {instructions}\n"
                f"- Estado: {record.status}\n"
                f"- Última revisión: {reviewed_on}\n"
                "No interpreto ni ajusto esta indicación."
            ),
        )

    def _render_confirmation(
        self,
        action: str,
        record: MedicationRecord,
    ) -> str:
        moments = ", ".join(record.moments or []) or "sin especificar"
        presentation = record.presentation or "sin especificar"
        return (
            f"Preparé el cambio para {action} el medicamento de "
            f"{record.person}:\n"
            f"- Nombre: {record.name}\n"
            f"- Presentación: {presentation}\n"
            f"- Dosis informada: {record.dosage}\n"
            f"- Horarios: {', '.join(record.schedules)}\n"
            f"- Momentos: {moments}\n"
            f"- Comidas: {record.food_relation}\n"
            f"- Estado: {record.status}\n"
            "Decí 'confirmar medicamento' para guardarlo o "
            "'cancelar medicamento' para descartarlo. "
            "No ajustaré la indicación."
        )

    def _find(self, record_id: str) -> MedicationRecord | None:
        normalized_id = record_id.casefold()
        return next(
            (
                record
                for record in self.repository.load()
                if record.record_id == normalized_id
            ),
            None,
        )

    def _split_fields(self, value: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in value.split("|"):
            name, separator, content = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = content.strip()
        return fields

    def _parse_schedules(self, value: str) -> list[str]:
        schedules: list[str] = []
        for item in re.split(r"[;,]", value):
            candidate = item.strip()
            try:
                parsed = datetime.strptime(candidate, "%H:%M")
            except ValueError:
                continue
            normalized = parsed.strftime("%H:%M")
            if normalized not in schedules:
                schedules.append(normalized)
        return schedules

    def _parse_moments(self, value: str) -> list[str]:
        moments: list[str] = []
        for item in re.split(r"[;,]", value.casefold()):
            candidate = item.strip()
            if candidate in _ALLOWED_MOMENTS and candidate not in moments:
                moments.append(candidate)
        return moments

    def _person(self, value: str) -> str:
        canonical = _ALLOWED_PEOPLE.get(value.casefold())
        if canonical is None:
            raise ValueError("El registro admite únicamente a Carlos y Cristina.")
        return canonical

    def _valid_date(self, value: str) -> bool:
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True

    def _valid_date_range(
        self,
        start_date: str,
        end_date: str,
    ) -> bool:
        if start_date and not self._valid_date(start_date):
            return False
        if end_date and not self._valid_date(end_date):
            return False
        if start_date and end_date:
            return date.fromisoformat(start_date) <= date.fromisoformat(end_date)
        return True

    def _pop_alternative(
        self,
        fields: dict[str, str],
        primary: str,
        fallback: str,
    ) -> str:
        if primary in fields:
            return fields.pop(primary)
        return fields.pop(fallback, "")

    def _get_alternative(
        self,
        fields: dict[str, str],
        primary: str,
        fallback: str,
    ) -> str:
        if primary in fields:
            return fields[primary]
        return fields.get(fallback, "")

    def _not_found(self, record_id: str) -> MedicationRegistryResult:
        return MedicationRegistryResult(
            handled=True,
            response=f"No encontré el medicamento {record_id}.",
        )
