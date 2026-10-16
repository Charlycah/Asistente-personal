from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DecompositionStatus(StrEnum):
    READY = "ready"
    CLARIFICATION_REQUIRED = "clarification_required"


class DecompositionAdmissionMode(StrEnum):
    EXPLICIT_COMPONENTS = "explicit_components"


@dataclass(frozen=True)
class GoalComponent:
    component_id: str
    parent_goal_id: str
    position: int
    title: str

    def __post_init__(self) -> None:
        if not self.component_id.strip():
            raise ValueError("component id must not be blank")
        if not self.parent_goal_id.strip():
            raise ValueError("parent goal id must not be blank")
        if self.position < 1:
            raise ValueError("component position must be positive")
        if not self.title.strip():
            raise ValueError("component title must not be blank")


@dataclass(frozen=True)
class GoalDecomposition:
    decomposition_id: str
    goal_id: str
    goal_title: str
    components: tuple[GoalComponent, ...]
    status: DecompositionStatus
    admission_mode: DecompositionAdmissionMode
    clarification_reason: str | None
    planning_execution_authorized: bool
    task_graph_created: bool
    dependencies_inferred: bool
    persistence_added: bool

    def __post_init__(self) -> None:
        if not self.decomposition_id.strip():
            raise ValueError("decomposition id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("goal id must not be blank")
        if not self.goal_title.strip():
            raise ValueError("goal title must not be blank")
        positions = tuple(component.position for component in self.components)
        if positions != tuple(range(1, len(self.components) + 1)):
            raise ValueError("component positions must be contiguous")
        if self.status is DecompositionStatus.READY and len(self.components) < 2:
            raise ValueError("ready decomposition requires at least two components")
        if (
            self.status is DecompositionStatus.CLARIFICATION_REQUIRED
            and not (self.clarification_reason or "").strip()
        ):
            raise ValueError("clarification reason is required")


@dataclass(frozen=True)
class GoalDecompositionSnapshot:
    schema_version: str
    canonical_authority: str
    parent_planning_authority: str
    admission_mode: DecompositionAdmissionMode
    minimum_components: int
    maximum_components: int
    explicit_input_required: bool
    automatic_inference: bool
    planning_execution_authorized: bool
    task_graph_created: bool
    dependencies_inferred: bool
    persistence_added: bool
    runtime_behavior_changed: bool
