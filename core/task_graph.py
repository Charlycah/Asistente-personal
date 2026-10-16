from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TaskRelation(StrEnum):
    PRECEDES = "precedes"


@dataclass(frozen=True)
class TaskNode:
    task_id: str
    goal_id: str
    position: int
    title: str

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("goal id must not be blank")
        if self.position < 1:
            raise ValueError("task position must be positive")
        if not self.title.strip():
            raise ValueError("task title must not be blank")


@dataclass(frozen=True)
class TaskEdge:
    predecessor_id: str
    successor_id: str
    relation: TaskRelation = TaskRelation.PRECEDES

    def __post_init__(self) -> None:
        if not self.predecessor_id.strip() or not self.successor_id.strip():
            raise ValueError("task edge endpoints must not be blank")
        if self.predecessor_id == self.successor_id:
            raise ValueError("task edge must not be self-referential")


@dataclass(frozen=True)
class TaskGraph:
    graph_id: str
    goal_id: str
    decomposition_id: str
    nodes: tuple[TaskNode, ...]
    edges: tuple[TaskEdge, ...]
    planning_execution_authorized: bool
    dependencies_inferred: bool
    persistence_added: bool

    def __post_init__(self) -> None:
        if not self.graph_id.strip():
            raise ValueError("graph id must not be blank")
        if not self.goal_id.strip():
            raise ValueError("goal id must not be blank")
        if not self.decomposition_id.strip():
            raise ValueError("decomposition id must not be blank")
        node_ids = tuple(node.task_id for node in self.nodes)
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("task graph node ids must be unique")
        edge_keys = tuple(
            (edge.predecessor_id, edge.successor_id, edge.relation)
            for edge in self.edges
        )
        if len(set(edge_keys)) != len(edge_keys):
            raise ValueError("task graph edges must be unique")
        known = set(node_ids)
        if any(
            edge.predecessor_id not in known or edge.successor_id not in known
            for edge in self.edges
        ):
            raise ValueError("task graph edge references an unknown node")

    def predecessors_of(self, task_id: str) -> tuple[TaskNode, ...]:
        ids = {
            edge.predecessor_id
            for edge in self.edges
            if edge.successor_id == task_id
        }
        return tuple(node for node in self.nodes if node.task_id in ids)

    def successors_of(self, task_id: str) -> tuple[TaskNode, ...]:
        ids = {
            edge.successor_id
            for edge in self.edges
            if edge.predecessor_id == task_id
        }
        return tuple(node for node in self.nodes if node.task_id in ids)

    @property
    def root_nodes(self) -> tuple[TaskNode, ...]:
        successors = {edge.successor_id for edge in self.edges}
        return tuple(node for node in self.nodes if node.task_id not in successors)

    @property
    def leaf_nodes(self) -> tuple[TaskNode, ...]:
        predecessors = {edge.predecessor_id for edge in self.edges}
        return tuple(node for node in self.nodes if node.task_id not in predecessors)


@dataclass(frozen=True)
class TaskGraphSnapshot:
    schema_version: str
    canonical_authority: str
    parent_decomposition_authority: str
    relation_types: tuple[TaskRelation, ...]
    explicit_edges_required: bool
    cycles_allowed: bool
    planning_execution_authorized: bool
    dependencies_inferred: bool
    persistence_added: bool
    runtime_behavior_changed: bool
