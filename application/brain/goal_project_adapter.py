from __future__ import annotations

from datetime import datetime

from core.household_goals import GoalStatus, HouseholdGoalRepository
from core.household_projects import HouseholdProjectRepository, ProjectStatus
from domain.brain import BrainMemory, BrainMemoryStatus, BrainMemoryType

from .service import BrainQuery


class GoalProjectBrainAdapter:
    """Read-only BRAIN view over persisted household goals and projects."""

    def __init__(
        self,
        *,
        goal_repository: HouseholdGoalRepository,
        project_repository: HouseholdProjectRepository,
        owner: str,
    ) -> None:
        self.goal_repository = goal_repository
        self.project_repository = project_repository
        self.owner = owner.strip()
        if not self.owner:
            raise ValueError("goal/project adapter owner must not be blank")

    def recall(
        self, query: BrainQuery, *, now: datetime | None = None
    ) -> tuple[BrainMemory, ...]:
        del query, now
        memories = [self._goal_memory(goal) for goal in self.goal_repository.list_all()]
        memories.extend(
            self._project_memory(project)
            for project in self.project_repository.list_all()
        )
        return tuple(memories)

    def _goal_memory(self, goal) -> BrainMemory:
        details = [goal.name]
        if goal.description:
            details.append(goal.description)
        if goal.next_step:
            details.append(f"Próximo paso: {goal.next_step}")
        status = self._status(goal.normalized_status)
        return BrainMemory(
            memory_id=f"goal:{goal.goal_id}",
            memory_type=BrainMemoryType.GOAL,
            subject=self.owner,
            content=". ".join(details),
            importance=0.8,
            confidence=1.0,
            source="household_goal",
            tags=("goal", goal.normalized_status.value),
            metadata={
                "read_only": True,
                "historical_id": goal.goal_id,
                "progress_percent": goal.progress_percent,
                "target_date": (
                    goal.target_date.isoformat() if goal.target_date else None
                ),
            },
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            status=status,
        )

    def _project_memory(self, project) -> BrainMemory:
        details = [project.name]
        if project.description:
            details.append(project.description)
        if project.next_step:
            details.append(f"Próximo paso: {project.next_step}")
        status = self._status(project.normalized_status)
        return BrainMemory(
            memory_id=f"project:{project.project_id}",
            memory_type=BrainMemoryType.GOAL,
            subject=self.owner,
            content=". ".join(details),
            importance=0.75,
            confidence=1.0,
            source="household_project",
            tags=("project", project.normalized_status.value),
            metadata={
                "read_only": True,
                "historical_id": project.project_id,
            },
            created_at=project.created_at,
            updated_at=project.updated_at,
            status=status,
        )

    @staticmethod
    def _status(status: GoalStatus | ProjectStatus) -> BrainMemoryStatus:
        if status.value == "completed":
            return BrainMemoryStatus.RESOLVED
        if status.value == "archived":
            return BrainMemoryStatus.ARCHIVED
        return BrainMemoryStatus.ACTIVE
