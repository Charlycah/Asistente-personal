from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DependencyTaskState(StrEnum):
    AVAILABLE = "available"
    BLOCKED = "blocked"
    COMPLETED = "completed"


@dataclass(frozen=True)
class DependencyTaskAssessment:
    task_id: str
    state: DependencyTaskState
    blocker_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("dependency assessment task id must not be blank")
        if len(set(self.blocker_ids)) != len(self.blocker_ids):
            raise ValueError("dependency blockers must be unique")
        if self.task_id in self.blocker_ids:
            raise ValueError("dependency task must not block itself")
        if self.state is DependencyTaskState.BLOCKED and not self.blocker_ids:
            raise ValueError("blocked dependency task requires blockers")
        if self.state is not DependencyTaskState.BLOCKED and self.blocker_ids:
            raise ValueError("only blocked dependency tasks may have blockers")


@dataclass(frozen=True)
class DependencyTrackingResult:
    graph_id: str
    goal_id: str
    assessments: tuple[DependencyTaskAssessment, ...]
    completed_task_ids: tuple[str, ...]
    planning_execution_authorized: bool
    progress_inferred: bool
    persistence_added: bool

    def __post_init__(self) -> None:
        if not self.graph_id.strip():
            raise ValueError("dependency result graph id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("dependency result goal id must not be blank")
        task_ids = tuple(item.task_id for item in self.assessments)
        if len(set(task_ids)) != len(task_ids):
            raise ValueError("dependency assessments must be unique")
        if len(set(self.completed_task_ids)) != len(self.completed_task_ids):
            raise ValueError("completed dependency task ids must be unique")
        if not set(self.completed_task_ids).issubset(task_ids):
            raise ValueError("completed dependency task id is unknown")

    def assessment_for(self, task_id: str) -> DependencyTaskAssessment:
        for assessment in self.assessments:
            if assessment.task_id == task_id:
                return assessment
        raise KeyError(task_id)

    @property
    def available_task_ids(self) -> tuple[str, ...]:
        return tuple(
            item.task_id
            for item in self.assessments
            if item.state is DependencyTaskState.AVAILABLE
        )

    @property
    def blocked_task_ids(self) -> tuple[str, ...]:
        return tuple(
            item.task_id
            for item in self.assessments
            if item.state is DependencyTaskState.BLOCKED
        )


@dataclass(frozen=True)
class DependencyTrackingSnapshot:
    schema_version: str
    canonical_authority: str
    parent_graph_authority: str
    completion_input_required: bool
    transitive_blockers_reported: bool
    planning_execution_authorized: bool
    progress_inferred: bool
    persistence_added: bool
    runtime_behavior_changed: bool
