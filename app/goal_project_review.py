from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from core.household_goals import GoalStatus, HouseholdGoalManager
from core.household_projects import HouseholdProjectManager, ProjectStatus
from infrastructure.repositories.sqlite_household_goal_repository import (
    SQLiteHouseholdGoalRepository,
)
from infrastructure.repositories.sqlite_household_project_repository import (
    SQLiteHouseholdProjectRepository,
)

_TRUE = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class GoalProjectReviewConfig:
    enabled: bool = True
    stale_days: int = 14
    max_items: int = 8
    include_in_briefing: bool = True


@dataclass(frozen=True)
class GoalProjectReviewResult:
    handled: bool
    response_text: str = ""


class ReviewItem(Protocol):
    name: str
    updated_at: datetime
    next_step: str


class GoalProjectReviewService:
    """Produces a deterministic household review over official goals and projects."""

    def __init__(
        self,
        *,
        project_db_path: str,
        goal_db_path: str,
        config: GoalProjectReviewConfig | None = None,
    ) -> None:
        self.projects = HouseholdProjectManager(
            SQLiteHouseholdProjectRepository(project_db_path)
        )
        self.goals = HouseholdGoalManager(SQLiteHouseholdGoalRepository(goal_db_path))
        self.config = config or GoalProjectReviewConfig()

    def handle(self, text: str, *, now: datetime) -> GoalProjectReviewResult:
        normalized = " ".join(text.strip().split()).casefold().rstrip("?.!")
        if normalized not in {
            "revisión de objetivos y proyectos",
            "revision de objetivos y proyectos",
            "revisemos objetivos y proyectos",
            "revisión semanal",
            "revision semanal",
            "qué está estancado",
            "que esta estancado",
        }:
            return GoalProjectReviewResult(False)
        return GoalProjectReviewResult(True, self.generate(now=now))

    def generate(self, *, now: datetime) -> str:
        if not self.config.enabled:
            return ""
        findings = self._findings(now=now)
        if not findings:
            return (
                "Revisión de objetivos y proyectos:\n"
                "- Todo lo activo tiene un próximo paso y movimiento reciente."
            )
        lines = ["Revisión de objetivos y proyectos:"]
        lines.extend(f"- {finding}" for finding in findings[: self.config.max_items])
        return "\n".join(lines)

    def briefing_lines(self, *, now: datetime) -> tuple[str, ...]:
        if not self.config.enabled or not self.config.include_in_briefing:
            return ()
        return tuple(self._findings(now=now)[: self.config.max_items])

    def _findings(self, *, now: datetime) -> list[str]:
        cutoff = now - timedelta(days=max(1, self.config.stale_days))
        findings: list[tuple[int, datetime, str]] = []

        for project in self.projects.list():
            if project.normalized_status is not ProjectStatus.ACTIVE:
                continue
            if not project.next_step:
                findings.append(
                    (
                        0,
                        project.updated_at,
                        f"Proyecto {project.name}: falta definir el próximo paso.",
                    )
                )
            elif project.updated_at <= cutoff:
                findings.append(
                    (
                        1,
                        project.updated_at,
                        f"Proyecto {project.name}: sin movimiento desde hace "
                        f"{self._days(now, project.updated_at)} días.",
                    )
                )

        for goal in self.goals.list():
            if goal.normalized_status is not GoalStatus.ACTIVE:
                continue
            if not goal.next_step:
                findings.append(
                    (
                        0,
                        goal.updated_at,
                        f"Objetivo {goal.name}: falta definir el próximo paso.",
                    )
                )
            elif goal.updated_at <= cutoff:
                findings.append(
                    (
                        1,
                        goal.updated_at,
                        f"Objetivo {goal.name}: progreso en {goal.progress_percent}% y "
                        f"sin movimiento desde hace "
                        f"{self._days(now, goal.updated_at)} días.",
                    )
                )

        findings.sort(key=lambda item: (item[0], item[1], item[2].casefold()))
        return [text for _, _, text in findings]

    @staticmethod
    def _days(now: datetime, updated_at: datetime) -> int:
        return max(0, (now.date() - updated_at.astimezone(now.tzinfo).date()).days)


def build_goal_project_review_from_environment() -> GoalProjectReviewService | None:
    enabled = (
        os.getenv("ROBY_GOAL_PROJECT_REVIEW_ENABLED", "true").strip().casefold()
        in _TRUE
    )
    if not enabled:
        return None
    return GoalProjectReviewService(
        project_db_path=os.getenv(
            "ROBY_HOUSEHOLD_PROJECTS_DB_PATH", ".roby/household_projects.db"
        ),
        goal_db_path=os.getenv(
            "ROBY_HOUSEHOLD_GOALS_DB_PATH", ".roby/household_goals.db"
        ),
        config=GoalProjectReviewConfig(
            enabled=True,
            stale_days=int(os.getenv("ROBY_GOAL_PROJECT_REVIEW_STALE_DAYS", "14")),
            max_items=int(os.getenv("ROBY_GOAL_PROJECT_REVIEW_MAX_ITEMS", "8")),
            include_in_briefing=(
                os.getenv("ROBY_GOAL_PROJECT_REVIEW_INCLUDE_IN_BRIEFING", "true")
                .strip()
                .casefold()
                in _TRUE
            ),
        ),
    )
