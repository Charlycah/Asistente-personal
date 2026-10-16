from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime

from .household_goals import HouseholdGoalService
from .household_projects import HouseholdProjectService

_TRUE = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ProgressCheckInResult:
    handled: bool
    response_text: str = ""


class ProgressCheckInService:
    """Records explicit progress through the official project and goal mutations."""

    def __init__(self, *, project_db_path: str, goal_db_path: str) -> None:
        self.projects = HouseholdProjectService(project_db_path)
        self.goals = HouseholdGoalService(goal_db_path)

    def handle(self, text: str, *, now: datetime) -> ProgressCheckInResult:
        normalized = " ".join(text.strip().split())

        project = re.match(
            r"^(?:registrá|registra|anotá|anota) (?:el )?avance "
            r"(?:del|de el) proyecto (?P<name>.+?): (?P<note>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if project:
            return self._delegate_project(
                name=project.group("name"), note=project.group("note"), now=now
            )

        goal = re.match(
            r"^(?:registrá|registra|actualizá|actualiza) (?:el )?avance "
            r"(?:del|de el|de la) (?:objetivo|meta) (?P<name>.+?):? "
            r"(?P<progress>\d{1,3})%$",
            normalized,
            flags=re.IGNORECASE,
        )
        if goal:
            return self._delegate_goal(
                name=goal.group("name"),
                progress=goal.group("progress"),
                now=now,
            )

        return ProgressCheckInResult(False)

    def _delegate_project(
        self, *, name: str, note: str, now: datetime
    ) -> ProgressCheckInResult:
        result = self.projects.handle(
            f"Agregá una nota al proyecto {name.strip(' .')}: {note.strip(' .')}",
            now=now,
        )
        return ProgressCheckInResult(result.handled, result.response_text)

    def _delegate_goal(
        self, *, name: str, progress: str, now: datetime
    ) -> ProgressCheckInResult:
        result = self.goals.handle(
            f"El objetivo {name.strip(' .')} va en {progress}%",
            now=now,
        )
        return ProgressCheckInResult(result.handled, result.response_text)


def build_progress_check_in_from_environment() -> ProgressCheckInService | None:
    enabled = (
        os.getenv("ROBY_PROGRESS_CHECK_IN_ENABLED", "true").strip().casefold() in _TRUE
    )
    if not enabled:
        return None
    return ProgressCheckInService(
        project_db_path=os.getenv(
            "ROBY_HOUSEHOLD_PROJECTS_DB_PATH", ".roby/household_projects.db"
        ),
        goal_db_path=os.getenv(
            "ROBY_HOUSEHOLD_GOALS_DB_PATH", ".roby/household_goals.db"
        ),
    )
