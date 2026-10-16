from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PlanProgressState(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ProgressEvaluationResult:
    graph_id: str
    goal_id: str
    state: PlanProgressState
    total_task_count: int
    completed_task_count: int
    available_task_count: int
    blocked_task_count: int
    completed_task_ids: tuple[str, ...]
    weighted_progress_used: bool
    progress_predicted: bool
    planning_execution_authorized: bool
    persistence_added: bool

    def __post_init__(self) -> None:
        if not self.graph_id.strip():
            raise ValueError("progress result graph id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("progress result goal id must not be blank")
        counts = (
            self.total_task_count,
            self.completed_task_count,
            self.available_task_count,
            self.blocked_task_count,
        )
        if any(count < 0 for count in counts):
            raise ValueError("progress counts must not be negative")
        if self.total_task_count < 1:
            raise ValueError("progress evaluation requires at least one task")
        if sum(counts[1:]) != self.total_task_count:
            raise ValueError("progress task-state counts must cover all tasks")
        if len(set(self.completed_task_ids)) != len(self.completed_task_ids):
            raise ValueError("completed progress task ids must be unique")
        if len(self.completed_task_ids) != self.completed_task_count:
            raise ValueError("completed progress ids must match completed count")
        expected_state = self._expected_state()
        if self.state is not expected_state:
            raise ValueError("progress state does not match completed task count")

    def _expected_state(self) -> PlanProgressState:
        if self.completed_task_count == 0:
            return PlanProgressState.NOT_STARTED
        if self.completed_task_count == self.total_task_count:
            return PlanProgressState.COMPLETED
        return PlanProgressState.IN_PROGRESS

    @property
    def completion_fraction(self) -> tuple[int, int]:
        return self.completed_task_count, self.total_task_count

    @property
    def completion_percentage(self) -> float:
        return round(
            (self.completed_task_count / self.total_task_count) * 100,
            2,
        )


@dataclass(frozen=True)
class ProgressEvaluationSnapshot:
    schema_version: str
    canonical_authority: str
    parent_dependency_authority: str
    explicit_completion_required: bool
    weighted_progress_used: bool
    progress_predicted: bool
    planning_execution_authorized: bool
    persistence_added: bool
    runtime_behavior_changed: bool
