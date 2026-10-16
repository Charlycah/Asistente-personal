from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from core.progress_evaluation import PlanProgressState


class PlanReasoningState(StrEnum):
    ACTIONABLE = "actionable"
    STALLED = "stalled"
    COMPLETED = "completed"


@dataclass(frozen=True)
class PlanReasoningResult:
    graph_id: str
    goal_id: str
    state: PlanReasoningState
    progress_state: PlanProgressState
    recommended_task_id: str | None
    actionable_task_ids: tuple[str, ...]
    blocked_task_ids: tuple[str, ...]
    direct_blocker_ids: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    priority_inferred: bool
    plan_reordered: bool
    replanning_authorized: bool
    planning_execution_authorized: bool
    persistence_added: bool

    def __post_init__(self) -> None:
        if not self.graph_id.strip():
            raise ValueError("plan reasoning graph id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("plan reasoning goal id must not be blank")
        for values in (
            self.actionable_task_ids,
            self.blocked_task_ids,
            self.direct_blocker_ids,
            self.rationale_codes,
        ):
            if len(set(values)) != len(values):
                raise ValueError("plan reasoning collections must be unique")
        if self.recommended_task_id is not None:
            if self.recommended_task_id not in self.actionable_task_ids:
                raise ValueError("recommended task must be actionable")
        if self.state is PlanReasoningState.COMPLETED:
            if self.progress_state is not PlanProgressState.COMPLETED:
                raise ValueError("completed reasoning requires completed progress")
            if self.recommended_task_id is not None or self.actionable_task_ids:
                raise ValueError("completed reasoning must not recommend tasks")
        if self.state is PlanReasoningState.ACTIONABLE:
            if not self.actionable_task_ids or self.recommended_task_id is None:
                raise ValueError("actionable reasoning requires a recommendation")
        if self.state is PlanReasoningState.STALLED:
            if self.actionable_task_ids or self.recommended_task_id is not None:
                raise ValueError("stalled reasoning must not recommend tasks")


@dataclass(frozen=True)
class PlanReasoningSnapshot:
    schema_version: str
    canonical_authority: str
    parent_progress_authority: str
    graph_order_preserved: bool
    explicit_state_required: bool
    priority_inferred: bool
    plan_reordered: bool
    replanning_authorized: bool
    planning_execution_authorized: bool
    persistence_added: bool
    runtime_behavior_changed: bool
