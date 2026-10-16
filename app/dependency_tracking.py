from __future__ import annotations

from typing import Iterable

from core.dependency_tracking import (
    DependencyTaskAssessment,
    DependencyTaskState,
    DependencyTrackingResult,
    DependencyTrackingSnapshot,
)
from core.task_graph import TaskGraph


class DependencyTrackingAuthority:
    """Canonical pure authority for evaluating explicit task dependencies."""

    SCHEMA_VERSION = "m368.4"
    CANONICAL_AUTHORITY = "dependency_tracking"
    PARENT_GRAPH_AUTHORITY = "task_graph"

    @property
    def snapshot(self) -> DependencyTrackingSnapshot:
        return DependencyTrackingSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_graph_authority=self.PARENT_GRAPH_AUTHORITY,
            completion_input_required=True,
            transitive_blockers_reported=False,
            planning_execution_authorized=False,
            progress_inferred=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        graph: TaskGraph,
        completed_task_ids: Iterable[str] = (),
    ) -> DependencyTrackingResult:
        completed = tuple(completed_task_ids)
        if len(set(completed)) != len(completed):
            raise ValueError("completed task ids must be unique")

        known = {node.task_id for node in graph.nodes}
        unknown = tuple(task_id for task_id in completed if task_id not in known)
        if unknown:
            raise ValueError("completed task id is unknown")

        completed_set = set(completed)
        assessments = tuple(
            self._assess_task(
                graph=graph,
                task_id=node.task_id,
                completed_task_ids=completed_set,
            )
            for node in graph.nodes
        )
        return DependencyTrackingResult(
            graph_id=graph.graph_id,
            goal_id=graph.goal_id,
            assessments=assessments,
            completed_task_ids=completed,
            planning_execution_authorized=False,
            progress_inferred=False,
            persistence_added=False,
        )

    @staticmethod
    def _assess_task(
        *,
        graph: TaskGraph,
        task_id: str,
        completed_task_ids: set[str],
    ) -> DependencyTaskAssessment:
        if task_id in completed_task_ids:
            return DependencyTaskAssessment(
                task_id=task_id,
                state=DependencyTaskState.COMPLETED,
                blocker_ids=(),
            )

        blockers = tuple(
            node.task_id
            for node in graph.predecessors_of(task_id)
            if node.task_id not in completed_task_ids
        )
        state = (
            DependencyTaskState.BLOCKED
            if blockers
            else DependencyTaskState.AVAILABLE
        )
        return DependencyTaskAssessment(
            task_id=task_id,
            state=state,
            blocker_ids=blockers,
        )
