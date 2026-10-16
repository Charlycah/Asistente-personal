from __future__ import annotations

from core.dependency_tracking import (
    DependencyTaskState,
    DependencyTrackingResult,
)
from core.progress_evaluation import (
    PlanProgressState,
    ProgressEvaluationResult,
    ProgressEvaluationSnapshot,
)


class ProgressEvaluationAuthority:
    """Canonical pure authority for structural plan-progress evaluation."""

    SCHEMA_VERSION = "m368.5"
    CANONICAL_AUTHORITY = "progress_evaluation"
    PARENT_DEPENDENCY_AUTHORITY = "dependency_tracking"

    @property
    def snapshot(self) -> ProgressEvaluationSnapshot:
        return ProgressEvaluationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_dependency_authority=self.PARENT_DEPENDENCY_AUTHORITY,
            explicit_completion_required=True,
            weighted_progress_used=False,
            progress_predicted=False,
            planning_execution_authorized=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        dependency_result: DependencyTrackingResult,
    ) -> ProgressEvaluationResult:
        total = len(dependency_result.assessments)
        completed = sum(
            item.state is DependencyTaskState.COMPLETED
            for item in dependency_result.assessments
        )
        available = sum(
            item.state is DependencyTaskState.AVAILABLE
            for item in dependency_result.assessments
        )
        blocked = sum(
            item.state is DependencyTaskState.BLOCKED
            for item in dependency_result.assessments
        )

        if completed == 0:
            state = PlanProgressState.NOT_STARTED
        elif completed == total:
            state = PlanProgressState.COMPLETED
        else:
            state = PlanProgressState.IN_PROGRESS

        return ProgressEvaluationResult(
            graph_id=dependency_result.graph_id,
            goal_id=dependency_result.goal_id,
            state=state,
            total_task_count=total,
            completed_task_count=completed,
            available_task_count=available,
            blocked_task_count=blocked,
            completed_task_ids=dependency_result.completed_task_ids,
            weighted_progress_used=False,
            progress_predicted=False,
            planning_execution_authorized=False,
            persistence_added=False,
        )
