from __future__ import annotations

import json
import os
import re
import tempfile
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_VALID_EVOLUTION = {"comenzó", "mejoró", "empeoró", "igual", "desapareció"}


@dataclass
class SymptomEpisode:
    episode_id: str
    person: str
    symptom: str
    started_at: str
    intensity: int | None = None
    body_area: str = ""
    duration: str = ""
    frequency: str = ""
    evolution: str = "comenzó"
    aggravating_factors: str = ""
    relieving_factors: str = ""
    accompanying_symptoms: str = ""
    related_vital_signs: str = ""
    medication_taken: str = ""
    notes: str = ""
    status: str = "activo"
    closed_at: str = ""
    archived: bool = False


@dataclass(frozen=True)
class SymptomResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _PendingSymptomChange:
    action: str
    episode: SymptomEpisode


class SymptomRepository:
    """Stores confirmed symptom episodes atomically."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".roby") / "symptoms.json"

    def load(self) -> list[SymptomEpisode]:
        if not self.path.exists():
            return []
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        rows = payload.get("episodes", []) if isinstance(payload, dict) else []
        if not isinstance(rows, list):
            return []
        return [SymptomEpisode(**row) for row in rows if isinstance(row, dict)]

    def save(self, episodes: list[SymptomEpisode]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": 1,
            "episodes": [asdict(item) for item in episodes],
        }
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="symptoms_",
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


class StructuredSymptomService:
    """Registers and summarizes symptoms without diagnosis or treatment advice."""

    def __init__(
        self,
        repository: SymptomRepository | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository or SymptomRepository()
        self._now = now or datetime.now
        self._pending: dict[str, _PendingSymptomChange] = {}

    def prepare(self, text: str, *, session_id: str | None = None) -> SymptomResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()
        key = session_id or "default"

        if folded in {"confirmar síntoma", "confirmar sintoma"}:
            return self._confirm(key)
        if folded in {"cancelar síntoma", "cancelar sintoma"}:
            self._pending.pop(key, None)
            return SymptomResult(True, "Cancelé el cambio de síntomas pendiente.")

        draft = self._parse_registration(normalized)
        if draft is not None:
            self._pending[key] = _PendingSymptomChange("create", draft)
            return SymptomResult(True, self._confirmation(draft))

        update = self._parse_update(normalized)
        if update is not None:
            self._pending[key] = _PendingSymptomChange("update", update)
            return SymptomResult(
                True,
                f"Confirmá la evolución del episodio {update.episode_id}: "
                f"{update.evolution}. Decí 'confirmar síntoma' para guardarla.",
            )

        close = self._parse_close(normalized)
        if close is not None:
            self._pending[key] = _PendingSymptomChange("update", close)
            return SymptomResult(
                True,
                f"Confirmá el cierre del episodio {close.episode_id}. "
                "Decí 'confirmar síntoma' para guardarlo.",
            )

        archive = self._parse_archive(normalized)
        if archive is not None:
            self._pending[key] = _PendingSymptomChange("update", archive)
            return SymptomResult(
                True,
                f"Confirmá el archivado del episodio {archive.episode_id}. "
                "Decí 'confirmar síntoma' para guardarlo.",
            )

        active = re.fullmatch(
            r"(?:mostrar |ver )?síntomas activos de (Carlos|Cristina)",
            normalized,
            flags=re.IGNORECASE,
        )
        if active:
            return self._active(active.group(1))

        history = re.fullmatch(
            r"historial de síntomas de (Carlos|Cristina)"
            r"(?: de los últimos (\d+) días)?",
            normalized,
            flags=re.IGNORECASE,
        )
        if history:
            return self._history(history.group(1), int(history.group(2) or 30))

        detail = re.fullmatch(
            r"(?:mostrar |ver )?episodio de síntoma ([a-f0-9]{8})",
            normalized,
            flags=re.IGNORECASE,
        )
        if detail:
            return self._detail(detail.group(1))
        return SymptomResult(False)

    def _parse_registration(self, text: str) -> SymptomEpisode | None:
        match = re.match(
            r"^registrar síntoma de (Carlos|Cristina):\s*(.+)$",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            match = re.match(
                r"^registrar sintoma de (Carlos|Cristina):\s*(.+)$",
                text,
                flags=re.IGNORECASE,
            )
        if match is None:
            return None
        fields = self._fields(match.group(2))
        symptom = fields.get("síntoma", fields.get("sintoma", ""))
        if not symptom:
            return None
        started_at = fields.get("inicio", self._now().isoformat(timespec="minutes"))
        try:
            datetime.fromisoformat(started_at)
        except ValueError:
            return None
        intensity = self._intensity(fields.get("intensidad", ""))
        if fields.get("intensidad") and intensity is None:
            return None
        evolution = fields.get("evolución", fields.get("evolucion", "comenzó"))
        evolution = evolution.casefold()
        if evolution not in _VALID_EVOLUTION:
            return None
        return SymptomEpisode(
            episode_id=uuid4().hex[:8],
            person=_ALLOWED_PEOPLE[match.group(1).casefold()],
            symptom=symptom,
            started_at=started_at,
            intensity=intensity,
            body_area=fields.get("zona", ""),
            duration=fields.get("duración", fields.get("duracion", "")),
            frequency=fields.get("frecuencia", ""),
            evolution=evolution,
            aggravating_factors=fields.get("agravantes", ""),
            relieving_factors=fields.get("alivio", ""),
            accompanying_symptoms=fields.get("acompañantes", ""),
            related_vital_signs=fields.get("signos", ""),
            medication_taken=fields.get("medicación", fields.get("medicacion", "")),
            notes=fields.get("notas", ""),
        )

    def _parse_update(self, text: str) -> SymptomEpisode | None:
        match = re.fullmatch(
            r"actualizar síntoma ([a-f0-9]{8}):\s*evolución=(.+)",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            match = re.fullmatch(
                r"actualizar sintoma ([a-f0-9]{8}):\s*evolucion=(.+)",
                text,
                flags=re.IGNORECASE,
            )
        if match is None:
            return None
        episode = self._find(match.group(1))
        evolution = match.group(2).strip().casefold()
        if episode is None or evolution not in _VALID_EVOLUTION:
            return None
        episode.evolution = evolution
        if evolution == "desapareció":
            episode.status = "cerrado"
            episode.closed_at = self._now().isoformat(timespec="minutes")
        return episode

    def _parse_close(self, text: str) -> SymptomEpisode | None:
        match = re.fullmatch(
            r"cerrar episodio de síntoma ([a-f0-9]{8})",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            match = re.fullmatch(
                r"cerrar episodio de sintoma ([a-f0-9]{8})",
                text,
                flags=re.IGNORECASE,
            )
        episode = self._find(match.group(1)) if match else None
        if episode is None:
            return None
        episode.status = "cerrado"
        episode.evolution = "desapareció"
        episode.closed_at = self._now().isoformat(timespec="minutes")
        return episode

    def _parse_archive(self, text: str) -> SymptomEpisode | None:
        match = re.fullmatch(
            r"archivar episodio de síntoma ([a-f0-9]{8})",
            text,
            flags=re.IGNORECASE,
        )
        if match is None:
            match = re.fullmatch(
                r"archivar episodio de sintoma ([a-f0-9]{8})",
                text,
                flags=re.IGNORECASE,
            )
        episode = self._find(match.group(1)) if match else None
        if episode is None:
            return None
        episode.archived = True
        return episode

    @staticmethod
    def _fields(raw: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in raw.split("|"):
            name, separator, value = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = value.strip()
        return fields

    @staticmethod
    def _intensity(raw: str) -> int | None:
        if not raw:
            return None
        try:
            value = int(raw)
        except ValueError:
            return None
        return value if 0 <= value <= 10 else None

    def _find(self, episode_id: str) -> SymptomEpisode | None:
        return next(
            (
                item
                for item in self.repository.load()
                if item.episode_id.casefold() == episode_id.casefold()
            ),
            None,
        )

    def _confirm(self, key: str) -> SymptomResult:
        pending = self._pending.pop(key, None)
        if pending is None:
            return SymptomResult(True, "No hay cambios de síntomas pendientes.")
        episodes = self.repository.load()
        if pending.action == "create":
            episodes.append(pending.episode)
            message = (
                f"Guardé el episodio {pending.episode.episode_id} de "
                f"{pending.episode.person}."
            )
        else:
            episodes = [
                pending.episode
                if item.episode_id == pending.episode.episode_id
                else item
                for item in episodes
            ]
            message = f"Actualicé el episodio {pending.episode.episode_id}."
        self.repository.save(episodes)
        return SymptomResult(True, message + " " + self._safety_notice(pending.episode))

    def _confirmation(self, episode: SymptomEpisode) -> str:
        details = [episode.symptom, f"inicio {episode.started_at}"]
        if episode.intensity is not None:
            details.append(f"intensidad {episode.intensity}/10")
        if episode.body_area:
            details.append(f"zona {episode.body_area}")
        return (
            f"Confirmá el síntoma de {episode.person}: "
            + " · ".join(details)
            + ". Decí 'confirmar síntoma' para guardarlo. "
            + self._safety_notice(episode)
        )

    def _active(self, person: str) -> SymptomResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        episodes = [
            item
            for item in self.repository.load()
            if item.person == canonical
            and item.status == "activo"
            and not item.archived
        ]
        if not episodes:
            return SymptomResult(True, f"No hay síntomas activos de {canonical}.")
        rows = "\n".join(self.render_episode(item) for item in episodes)
        return SymptomResult(
            True,
            f"Síntomas activos de {canonical}:\n{rows}\n"
            "Resumen descriptivo; no constituye un diagnóstico.",
        )

    def _history(self, person: str, days: int) -> SymptomResult:
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        cutoff = self._now() - timedelta(days=max(1, days))
        episodes = [
            item
            for item in self.repository.load()
            if item.person == canonical
            and not item.archived
            and datetime.fromisoformat(item.started_at) >= cutoff
        ]
        episodes.sort(key=lambda item: item.started_at, reverse=True)
        if not episodes:
            return SymptomResult(
                True,
                f"No hay síntomas registrados para {canonical} en ese período.",
            )
        rows = "\n".join(self.render_episode(item) for item in episodes)
        return SymptomResult(
            True,
            f"Historial de síntomas de {canonical} ({days} días):\n{rows}\n"
            "La evolución se muestra sin interpretación clínica.",
        )

    def _detail(self, episode_id: str) -> SymptomResult:
        episode = self._find(episode_id)
        if episode is None or episode.archived:
            return SymptomResult(True, "No encontré ese episodio activo.")
        fields = [
            f"Episodio {episode.episode_id} de {episode.person}",
            f"síntoma: {episode.symptom}",
            f"inicio: {episode.started_at}",
            f"estado: {episode.status}",
            f"evolución: {episode.evolution}",
        ]
        optional = {
            "intensidad": (
                f"{episode.intensity}/10" if episode.intensity is not None else ""
            ),
            "zona": episode.body_area,
            "duración": episode.duration,
            "frecuencia": episode.frequency,
            "agravantes": episode.aggravating_factors,
            "alivio": episode.relieving_factors,
            "acompañantes": episode.accompanying_symptoms,
            "signos relacionados": episode.related_vital_signs,
            "medicación tomada": episode.medication_taken,
            "notas": episode.notes,
        }
        fields.extend(f"{name}: {value}" for name, value in optional.items() if value)
        return SymptomResult(True, "\n".join(fields))

    @staticmethod
    def render_episode(episode: SymptomEpisode) -> str:
        intensity = (
            f" · intensidad {episode.intensity}/10"
            if episode.intensity is not None
            else ""
        )
        return (
            f"- {episode.started_at} · {episode.symptom}{intensity} · "
            f"{episode.evolution} · {episode.status} · ID {episode.episode_id}"
        )

    @staticmethod
    def _safety_notice(episode: SymptomEpisode) -> str:
        text = " ".join(
            [episode.symptom, episode.accompanying_symptoms, episode.notes]
        ).casefold()
        urgent_patterns = (
            ("dolor de pecho", "falta de aire"),
            ("dolor de pecho", "desmayo"),
            ("debilidad", "confusión"),
            ("debilidad", "confusion"),
        )
        urgent = any(
            all(term in text for term in pattern)
            for pattern in urgent_patterns
        )
        urgent = urgent or any(
            term in text
            for term in (
                "sangrado abundante",
                "dificultad para respirar",
                "pérdida de conocimiento",
                "perdida de conocimiento",
            )
        )
        if urgent:
            return (
                "La combinación registrada contiene una señal de alarma. "
                "Buscá asistencia médica inmediata o llamá al servicio local de "
                "emergencias; no esperes a completar registros en ROBY."
            )
        return (
            "ROBY registra y organiza la información, pero no diagnostica ni "
            "indica cambios de tratamiento."
        )
