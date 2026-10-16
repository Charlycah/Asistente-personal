from __future__ import annotations

from core.dependency_tracking import (
    DependencyTaskState,
    DependencyTrackingResult,
)
from core.plan_reasoning import (
    PlanReasoningResult,
    PlanReasoningSnapshot,
    PlanReasoningState,
)
from core.progress_evaluation import (
    PlanProgressState,
    ProgressEvaluationResult,
)
from core.task_graph import TaskGraph


class PlanReasoningAuthority:
    """Canonical pure authority for deterministic plan-state reasoning."""

    SCHEMA_VERSION = "m368.6"
    CANONICAL_AUTHORITY = "plan_reasoning"
    PARENT_PROGRESS_AUTHORITY = "progress_evaluation"

    @property
    def snapshot(self) -> PlanReasoningSnapshot:
        return PlanReasoningSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_progress_authority=self.PARENT_PROGRESS_AUTHORITY,
            graph_order_preserved=True,
            explicit_state_required=True,
            priority_inferred=False,
            plan_reordered=False,
            replanning_authorized=False,
            planning_execution_authorized=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def reason(
        self,
        *,
        graph: TaskGraph,
        dependency_result: DependencyTrackingResult,
        progress_result: ProgressEvaluationResult,
    ) -> PlanReasoningResult:
        self._validate_traceability(
            graph=graph,
            dependency_result=dependency_result,
            progress_result=progress_result,
        )

        assessments = {
            item.task_id: item for item in dependency_result.assessments
        }
        actionable = tuple(
            node.task_id
            for node in graph.nodes
            if assessments[node.task_id].state is DependencyTaskState.AVAILABLE
        )
        blocked = tuple(
            node.task_id
            for node in graph.nodes
            if assessments[node.task_id].state is DependencyTaskState.BLOCKED
        )
        direct_blockers = tuple(
            node.task_id
            for node in graph.nodes
            if any(
                node.task_id in assessment.blocker_ids
                for assessment in dependency_result.assessments
            )
        )

        if progress_result.state is PlanProgressState.COMPLETED:
            state = PlanReasoningState.COMPLETED
            recommended = None
            rationale = ("plan_completed",)
        elif actionable:
            state = PlanReasoningState.ACTIONABLE
            recommended = actionable[0]
            rationale = (
                "explicit_dependencies_satisfied",
                "graph_order_preserved",
            )
        else:
            state = PlanReasoningState.STALLED
            recommended = None
            rationale = ("no_actionable_task", "direct_blockers_present")

        return PlanReasoningResult(
            graph_id=graph.graph_id,
            goal_id=graph.goal_id,
            state=state,
            progress_state=progress_result.state,
            recommended_task_id=recommended,
            actionable_task_ids=actionable,
            blocked_task_ids=blocked,
            direct_blocker_ids=direct_blockers,
            rationale_codes=rationale,
            priority_inferred=False,
            plan_reordered=False,
            replanning_authorized=False,
            planning_execution_authorized=False,
            persistence_added=False,
        )

    @staticmethod
    def _validate_traceability(
        *,
        graph: TaskGraph,
        dependency_result: DependencyTrackingResult,
        progress_result: ProgressEvaluationResult,
    ) -> None:
        expected = (graph.graph_id, graph.goal_id)
        if (dependency_result.graph_id, dependency_result.goal_id) != expected:
            raise ValueError("dependency result does not match task graph")
        if (progress_result.graph_id, progress_result.goal_id) != expected:
            raise ValueError("progress result does not match task graph")
        if progress_result.completed_task_ids != dependency_result.completed_task_ids:
            raise ValueError("progress and dependency completion differ")
