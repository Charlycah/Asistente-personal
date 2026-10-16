from pathlib import Path

import pytest

from app.goal_decomposition import GoalDecompositionAuthority
from app.task_graph import TaskGraphAuthority
from core.task_graph import TaskEdge, TaskGraph, TaskNode, TaskRelation


def _decomposition():
    return GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Publicar versión",
        component_titles=("Definir", "Implementar", "Validar"),
    )


def test_m368_3_declares_one_subordinate_task_graph_authority() -> None:
    snapshot = TaskGraphAuthority().snapshot

    assert snapshot.schema_version == "m368.3"
    assert snapshot.canonical_authority == "task_graph"
    assert snapshot.parent_decomposition_authority == "goal_decomposition"
    assert snapshot.relation_types == (TaskRelation.PRECEDES,)


def test_m368_3_builds_nodes_from_admitted_goal_components() -> None:
    decomposition = _decomposition()
    graph = TaskGraphAuthority().build(decomposition=decomposition)

    assert graph.goal_id == decomposition.goal_id
    assert graph.decomposition_id == decomposition.decomposition_id
    assert tuple(node.task_id for node in graph.nodes) == tuple(
        component.component_id for component in decomposition.components
    )
    assert graph.edges == ()


def test_m368_3_accepts_only_explicit_precedence_edges() -> None:
    decomposition = _decomposition()
    first, second, third = (
        component.component_id for component in decomposition.components
    )
    graph = TaskGraphAuthority().build(
        decomposition=decomposition,
        precedence_edges=((first, second), (second, third)),
    )

    assert graph.predecessors_of(second) == (graph.nodes[0],)
    assert graph.successors_of(second) == (graph.nodes[2],)
    assert graph.root_nodes == (graph.nodes[0],)
    assert graph.leaf_nodes == (graph.nodes[2],)


def test_m368_3_produces_a_stable_graph_identifier() -> None:
    decomposition = _decomposition()
    authority = TaskGraphAuthority()

    assert authority.build(decomposition=decomposition).graph_id == authority.build(
        decomposition=decomposition
    ).graph_id


def test_m368_3_rejects_unknown_duplicate_and_self_edges() -> None:
    decomposition = _decomposition()
    first, second, _ = (
        component.component_id for component in decomposition.components
    )
    authority = TaskGraphAuthority()

    with pytest.raises(ValueError, match="unknown node"):
        authority.build(
            decomposition=decomposition,
            precedence_edges=((first, "missing"),),
        )
    with pytest.raises(ValueError, match="unique"):
        authority.build(
            decomposition=decomposition,
            precedence_edges=((first, second), (first, second)),
        )
    with pytest.raises(ValueError, match="self-referential"):
        authority.build(
            decomposition=decomposition,
            precedence_edges=((first, first),),
        )


def test_m368_3_rejects_cycles() -> None:
    decomposition = _decomposition()
    first, second, third = (
        component.component_id for component in decomposition.components
    )

    with pytest.raises(ValueError, match="acyclic"):
        TaskGraphAuthority().build(
            decomposition=decomposition,
            precedence_edges=((first, second), (second, third), (third, first)),
        )


def test_m368_3_requires_a_ready_decomposition() -> None:
    decomposition = GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Objetivo",
        component_titles=("Único",),
    )

    with pytest.raises(ValueError, match="ready"):
        TaskGraphAuthority().build(decomposition=decomposition)


def test_m368_3_adds_no_execution_inference_persistence_or_runtime_change() -> None:
    snapshot = TaskGraphAuthority().snapshot
    graph = TaskGraphAuthority().build(decomposition=_decomposition())

    assert snapshot.explicit_edges_required is True
    assert snapshot.cycles_allowed is False
    assert snapshot.planning_execution_authorized is False
    assert snapshot.dependencies_inferred is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert graph.planning_execution_authorized is False
    assert graph.dependencies_inferred is False
    assert graph.persistence_added is False


def test_task_graph_contract_rejects_invalid_structures() -> None:
    node = TaskNode(task_id="task-1", goal_id="goal-1", position=1, title="Uno")
    edge = TaskEdge(predecessor_id="task-1", successor_id="missing")

    with pytest.raises(ValueError, match="unknown node"):
        TaskGraph(
            graph_id="graph-1",
            goal_id="goal-1",
            decomposition_id="decomposition-1",
            nodes=(node,),
            edges=(edge,),
            planning_execution_authorized=False,
            dependencies_inferred=False,
            persistence_added=False,
        )


def test_m368_3_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_3_TASK_GRAPH.md").read_text(encoding="utf-8")

    assert "task_graph" in document
    assert "aristas explícitas" in document
    assert "no realiza seguimiento de dependencias" in document
    assert "M368.3" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.3 — Task Graph" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
