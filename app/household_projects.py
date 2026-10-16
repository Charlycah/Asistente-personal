from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from core.household_projects import HouseholdProjectManager, ProjectStatus
from infrastructure.repositories.sqlite_household_project_repository import (
    SQLiteHouseholdProjectRepository,
)


@dataclass(frozen=True)
class HouseholdProjectResult:
    handled: bool
    response_text: str = ""


class HouseholdProjectService:
    def __init__(self, db_path: str) -> None:
        self.manager = HouseholdProjectManager(
            SQLiteHouseholdProjectRepository(db_path)
        )

    def handle(self, text: str, *, now: datetime) -> HouseholdProjectResult:
        normalized = " ".join(text.strip().split())
        folded = normalized.casefold()

        create = re.match(
            r"^(?:creá|crea|iniciá|inicia) (?:el )?proyecto (?P<name>.+?)"
            r"(?: para (?P<description>.+))?$",
            normalized,
            flags=re.IGNORECASE,
        )
        if create:
            name = create.group("name").strip(" .")
            description = (create.group("description") or "").strip(" .")
            project = self.manager.create(name, description=description, now=now)
            return HouseholdProjectResult(True, f"Creé el proyecto: {project.name}.")

        if folded in {
            "qué proyectos tenemos",
            "que proyectos tenemos",
            "lista de proyectos",
            "mis proyectos",
        }:
            projects = self.manager.list()
            if not projects:
                return HouseholdProjectResult(True, "No hay proyectos activos.")
            lines = ["Proyectos del hogar:"]
            for project in projects:
                detail = (
                    f" — próximo paso: {project.next_step}" if project.next_step else ""
                )
                lines.append(
                    f"- {project.name} [{project.normalized_status.value}]{detail}"
                )
            return HouseholdProjectResult(True, "\n".join(lines))

        next_step = re.match(
            r"^(?:el )?próximo paso (?:del proyecto )?(?P<name>.+?) es (?P<step>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if next_step:
            project = self.manager.find(next_step.group("name"))
            if project is None:
                return HouseholdProjectResult(True, "No encontré ese proyecto.")
            updated = self.manager.set_next_step(
                project.project_id, next_step.group("step"), now=now
            )
            return HouseholdProjectResult(
                True, f"Actualicé el próximo paso de {updated.name}."
            )

        note = re.match(
            r"^(?:agregá|agrega|anotá|anota) (?:una )?nota "
            r"(?:al|en el) proyecto (?P<name>.+?): (?P<note>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if note:
            project = self.manager.find(note.group("name"))
            if project is None:
                return HouseholdProjectResult(True, "No encontré ese proyecto.")
            updated = self.manager.add_note(
                project.project_id, note.group("note"), now=now
            )
            return HouseholdProjectResult(True, f"Agregué una nota a {updated.name}.")

        status_patterns = (
            (
                r"^(?:pausá|pausa) (?:el )?proyecto (?P<name>.+)$",
                ProjectStatus.PAUSED,
                "Pausé",
            ),
            (
                r"^(?:reanuda|reanudá) (?:el )?proyecto (?P<name>.+)$",
                ProjectStatus.ACTIVE,
                "Reanudé",
            ),
            (
                r"^(?:completá|completa|terminá|termina) "
                r"(?:el )?proyecto (?P<name>.+)$",
                ProjectStatus.COMPLETED,
                "Completé",
            ),
            (
                r"^(?:archivá|archiva) (?:el )?proyecto (?P<name>.+)$",
                ProjectStatus.ARCHIVED,
                "Archivé",
            ),
        )
        for pattern, status, verb in status_patterns:
            match = re.match(pattern, normalized, flags=re.IGNORECASE)
            if match:
                project = self.manager.find(match.group("name"))
                if project is None:
                    return HouseholdProjectResult(True, "No encontré ese proyecto.")
                updated = self.manager.change_status(
                    project.project_id, status, now=now
                )
                return HouseholdProjectResult(
                    True, f"{verb} el proyecto {updated.name}."
                )

        detail = re.match(
            r"^(?:estado|detalle|detalles) (?:del )?proyecto (?P<name>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if detail:
            project = self.manager.find(detail.group("name"))
            if project is None:
                return HouseholdProjectResult(True, "No encontré ese proyecto.")
            lines = [
                f"Proyecto {project.name}:",
                f"- Estado: {project.normalized_status.value}",
            ]
            if project.description:
                lines.append(f"- Descripción: {project.description}")
            if project.next_step:
                lines.append(f"- Próximo paso: {project.next_step}")
            if project.notes:
                lines.append("- Notas:")
                lines.extend(f"  - {item}" for item in project.notes[-10:])
            return HouseholdProjectResult(True, "\n".join(lines))

        return HouseholdProjectResult(False)
