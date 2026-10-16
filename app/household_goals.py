from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime

from core.household_goals import GoalStatus, HouseholdGoalManager
from infrastructure.repositories.sqlite_household_goal_repository import (
    SQLiteHouseholdGoalRepository,
)


@dataclass(frozen=True)
class HouseholdGoalResult:
    handled: bool
    response_text: str = ""


class HouseholdGoalService:
    def __init__(self, db_path: str) -> None:
        self.manager = HouseholdGoalManager(SQLiteHouseholdGoalRepository(db_path))

    def handle(self, text: str, *, now: datetime) -> HouseholdGoalResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()

        create = re.match(
            r"^(?:creá|crea|iniciá|inicia|definí|define) "
            r"(?:el |la )?(?:objetivo|meta) (?P<name>.+?)"
            r"(?: para (?P<description>.+))?$",
            normalized,
            flags=re.IGNORECASE,
        )
        if create:
            name = create.group("name").strip(" .")
            description = (create.group("description") or "").strip(" .")
            goal = self.manager.create(name, description=description, now=now)
            return HouseholdGoalResult(True, f"Creé el objetivo: {goal.name}.")

        if folded in {
            "qué objetivos tenemos",
            "que objetivos tenemos",
            "lista de objetivos",
            "nuestras metas",
            "mis objetivos",
        }:
            goals = self.manager.list()
            if not goals:
                return HouseholdGoalResult(True, "No hay objetivos activos.")
            lines = ["Objetivos del hogar:"]
            for goal in goals:
                detail = f" — próximo paso: {goal.next_step}" if goal.next_step else ""
                lines.append(
                    f"- {goal.name} [{goal.normalized_status.value}] "
                    f"{goal.progress_percent}%{detail}"
                )
            return HouseholdGoalResult(True, "\n".join(lines))

        progress = re.match(
            r"^(?:el |la )?(?:objetivo|meta) (?P<name>.+?) (?:va|está|esta) "
            r"(?:en )?(?P<progress>\d{1,3})%$",
            normalized,
            flags=re.IGNORECASE,
        )
        if progress:
            value = int(progress.group("progress"))
            if value > 100:
                return HouseholdGoalResult(
                    True, "El progreso debe estar entre 0 y 100%."
                )
            goal = self.manager.find(progress.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            updated = self.manager.set_progress(goal.goal_id, value, now=now)
            return HouseholdGoalResult(
                True, f"Actualicé {updated.name} al {updated.progress_percent}%."
            )

        next_step = re.match(
            r"^(?:el )?próximo paso (?:del )?(?:objetivo|meta) "
            r"(?P<name>.+?) es (?P<step>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if next_step:
            goal = self.manager.find(next_step.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            updated = self.manager.set_next_step(
                goal.goal_id, next_step.group("step"), now=now
            )
            return HouseholdGoalResult(
                True, f"Actualicé el próximo paso de {updated.name}."
            )

        link_patterns = (
            (
                r"^(?:vinculá|vincula) (?:el |la )?(?:objetivo|meta) (?P<name>.+?) "
                r"(?:con|al) (?:el )?proyecto (?P<link>.+)$",
                "project",
            ),
            (
                r"^(?:vinculá|vincula) (?:el |la )?(?:objetivo|meta) (?P<name>.+?) "
                r"(?:con|a) (?:la )?rutina (?P<link>.+)$",
                "routine",
            ),
        )
        for pattern, kind in link_patterns:
            match = re.match(pattern, normalized, flags=re.IGNORECASE)
            if not match:
                continue
            goal = self.manager.find(match.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            if kind == "project":
                updated = self.manager.link_project(
                    goal.goal_id, match.group("link"), now=now
                )
                label = "proyecto"
            else:
                updated = self.manager.link_routine(
                    goal.goal_id, match.group("link"), now=now
                )
                label = "rutina"
            return HouseholdGoalResult(
                True, f"Vinculé {updated.name} con el {label} indicado."
            )

        note = re.match(
            r"^(?:agregá|agrega|anotá|anota) (?:una )?nota "
            r"(?:al|en el) (?:objetivo|meta) (?P<name>.+?): (?P<note>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if note:
            goal = self.manager.find(note.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            updated = self.manager.add_note(goal.goal_id, note.group("note"), now=now)
            return HouseholdGoalResult(True, f"Agregué una nota a {updated.name}.")

        status_patterns = (
            (
                r"^(?:pausá|pausa) (?:el |la )?(?:objetivo|meta) "
                r"(?P<name>.+)$",
                GoalStatus.PAUSED,
                "Pausé",
            ),
            (
                r"^(?:reanuda|reanudá) (?:el |la )?(?:objetivo|meta) "
                r"(?P<name>.+)$",
                GoalStatus.ACTIVE,
                "Reanudé",
            ),
            (
                r"^(?:completá|completa|terminá|termina) "
                r"(?:el |la )?(?:objetivo|meta) (?P<name>.+)$",
                GoalStatus.COMPLETED,
                "Completé",
            ),
            (
                r"^(?:archivá|archiva) (?:el |la )?(?:objetivo|meta) "
                r"(?P<name>.+)$",
                GoalStatus.ARCHIVED,
                "Archivé",
            ),
        )
        for pattern, status, verb in status_patterns:
            match = re.match(pattern, normalized, flags=re.IGNORECASE)
            if not match:
                continue
            goal = self.manager.find(match.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            updated = self.manager.change_status(goal.goal_id, status, now=now)
            return HouseholdGoalResult(True, f"{verb} el objetivo {updated.name}.")

        detail = re.match(
            r"^(?:estado|detalle|detalles) (?:del )?(?:objetivo|meta) (?P<name>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if detail:
            goal = self.manager.find(detail.group("name"))
            if goal is None:
                return HouseholdGoalResult(True, "No encontré ese objetivo.")
            return HouseholdGoalResult(True, self._render_detail(goal))

        return HouseholdGoalResult(False)

    @staticmethod
    def _render_detail(goal) -> str:
        lines = [
            f"Objetivo {goal.name}:",
            f"- Estado: {goal.normalized_status.value}",
            f"- Progreso: {goal.progress_percent}%",
        ]
        if goal.description:
            lines.append(f"- Descripción: {goal.description}")
        if goal.target_date:
            lines.append(f"- Fecha objetivo: {date.isoformat(goal.target_date)}")
        if goal.next_step:
            lines.append(f"- Próximo paso: {goal.next_step}")
        if goal.linked_project:
            lines.append(f"- Proyecto vinculado: {goal.linked_project}")
        if goal.linked_routine:
            lines.append(f"- Rutina vinculada: {goal.linked_routine}")
        if goal.notes:
            lines.append("- Notas:")
            lines.extend(f"  - {item}" for item in goal.notes[-10:])
        return "\n".join(lines)
