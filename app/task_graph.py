from __future__ import annotations

from hashlib import sha256
from typing import Iterable

from core.goal_decomposition import DecompositionStatus, GoalDecomposition
from core.task_graph import (
    TaskEdge,
    TaskGraph,
    TaskGraphSnapshot,
    TaskNode,
    TaskRelation,
)


class TaskGraphAuthority:
    """Canonical pure authority for explicit acyclic task structure."""

    SCHEMA_VERSION = "m368.3"
    CANONICAL_AUTHORITY = "task_graph"
    PARENT_DECOMPOSITION_AUTHORITY = "goal_decomposition"

    @property
    def snapshot(self) -> TaskGraphSnapshot:
        return TaskGraphSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_decomposition_authority=self.PARENT_DECOMPOSITION_AUTHORITY,
            relation_types=(TaskRelation.PRECEDES,),
            explicit_edges_required=True,
            cycles_allowed=False,
            planning_execution_authorized=False,
            dependencies_inferred=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def build(
        self,
        *,
        decomposition: GoalDecomposition,
        precedence_edges: Iterable[tuple[str, str]] = (),
    ) -> TaskGraph:
        if decomposition.status is not DecompositionStatus.READY:
            raise ValueError("task graph requires a ready goal decomposition")

        nodes = tuple(
            TaskNode(
                task_id=component.component_id,
                goal_id=decomposition.goal_id,
                position=component.position,
                title=component.title,
            )
            for component in decomposition.components
        )
        edges = tuple(
            TaskEdge(predecessor_id=predecessor, successor_id=successor)
            for predecessor, successor in precedence_edges
        )
        graph = TaskGraph(
            graph_id=self._stable_id("task-graph", decomposition.decomposition_id),
            goal_id=decomposition.goal_id,
            decomposition_id=decomposition.decomposition_id,
            nodes=nodes,
            edges=edges,
            planning_execution_authorized=False,
            dependencies_inferred=False,
            persistence_added=False,
        )
        self._assert_acyclic(graph)
        return graph

    @staticmethod
    def _assert_acyclic(graph: TaskGraph) -> None:
        successors: dict[str, set[str]] = {node.task_id: set() for node in graph.nodes}
        indegree = {node.task_id: 0 for node in graph.nodes}
        for edge in graph.edges:
            successors[edge.predecessor_id].add(edge.successor_id)
            indegree[edge.successor_id] += 1

        ready = [task_id for task_id, count in indegree.items() if count == 0]
        visited = 0
        while ready:
            task_id = ready.pop()
            visited += 1
            for successor in successors[task_id]:
                indegree[successor] -= 1
                if indegree[successor] == 0:
                    ready.append(successor)
        if visited != len(graph.nodes):
            raise ValueError("task graph must be acyclic")

    @staticmethod
    def _stable_id(prefix: str, *parts: str) -> str:
        payload = "\x1f".join(parts).encode("utf-8")
        return f"{prefix}-{sha256(payload).hexdigest()[:16]}"
