from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime

from .household_goals import HouseholdGoalService
from .household_projects import HouseholdProjectService

_TRUE = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ActionableFollowUpResult:
    handled: bool
    response_text: str = ""


class ActionableFollowUpService:
    """Turns explicit review follow-ups into official next-step mutations."""

    def __init__(self, *, project_db_path: str, goal_db_path: str) -> None:
        self.projects = HouseholdProjectService(project_db_path)
        self.goals = HouseholdGoalService(goal_db_path)

    def handle(self, text: str, *, now: datetime) -> ActionableFollowUpResult:
        normalized = " ".join(text.strip().split())

        project = re.match(
            r"^(?:dale|dá|da) seguimiento (?:al|a el) proyecto "
            r"(?P<name>.+?)(?::| con el próximo paso | con el proximo paso )"
            r"(?P<step>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if project:
            return self._delegate_project(
                name=project.group("name"), step=project.group("step"), now=now
            )

        goal = re.match(
            r"^(?:dale|dá|da) seguimiento (?:al|a el) "
            r"(?:objetivo|meta) (?P<name>.+?)"
            r"(?::| con el próximo paso | con el proximo paso )(?P<step>.+)$",
            normalized,
            flags=re.IGNORECASE,
        )
        if goal:
            return self._delegate_goal(
                name=goal.group("name"), step=goal.group("step"), now=now
            )

        return ActionableFollowUpResult(False)

    def _delegate_project(
        self, *, name: str, step: str, now: datetime
    ) -> ActionableFollowUpResult:
        result = self.projects.handle(
            f"El próximo paso del proyecto {name.strip(' .')} es {step.strip(' .')}",
            now=now,
        )
        return ActionableFollowUpResult(result.handled, result.response_text)

    def _delegate_goal(
        self, *, name: str, step: str, now: datetime
    ) -> ActionableFollowUpResult:
        result = self.goals.handle(
            f"El próximo paso del objetivo {name.strip(' .')} es {step.strip(' .')}",
            now=now,
        )
        return ActionableFollowUpResult(result.handled, result.response_text)


def build_actionable_follow_up_from_environment() -> ActionableFollowUpService | None:
    enabled = (
        os.getenv("ROBY_ACTIONABLE_FOLLOW_UP_ENABLED", "true").strip().casefold()
        in _TRUE
    )
    if not enabled:
        return None
    return ActionableFollowUpService(
        project_db_path=os.getenv(
            "ROBY_HOUSEHOLD_PROJECTS_DB_PATH", ".roby/household_projects.db"
        ),
        goal_db_path=os.getenv(
            "ROBY_HOUSEHOLD_GOALS_DB_PATH", ".roby/household_goals.db"
        ),
    )
