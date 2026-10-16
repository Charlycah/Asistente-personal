from pathlib import Path

import pytest

from app.dependency_tracking import DependencyTrackingAuthority
from app.goal_decomposition import GoalDecompositionAuthority
from app.task_graph import TaskGraphAuthority
from core.dependency_tracking import DependencyTaskState


def _graph():
    decomposition = GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Publicar versión",
        component_titles=("Definir", "Implementar", "Validar"),
    )
    first, second, third = (
        component.component_id for component in decomposition.components
    )
    graph = TaskGraphAuthority().build(
        decomposition=decomposition,
        precedence_edges=((first, second), (second, third)),
    )
    return graph, first, second, third


def test_m368_4_declares_one_subordinate_dependency_authority() -> None:
    snapshot = DependencyTrackingAuthority().snapshot

    assert snapshot.schema_version == "m368.4"
    assert snapshot.canonical_authority == "dependency_tracking"
    assert snapshot.parent_graph_authority == "task_graph"


def test_m368_4_marks_roots_available_and_dependents_blocked() -> None:
    graph, first, second, third = _graph()
    result = DependencyTrackingAuthority().evaluate(graph=graph)

    assert result.assessment_for(first).state is DependencyTaskState.AVAILABLE
    assert result.assessment_for(second).state is DependencyTaskState.BLOCKED
    assert result.assessment_for(second).blocker_ids == (first,)
    assert result.assessment_for(third).blocker_ids == (second,)


def test_m368_4_releases_only_tasks_with_completed_predecessors() -> None:
    graph, first, second, third = _graph()
    result = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=(first,),
    )

    assert result.assessment_for(first).state is DependencyTaskState.COMPLETED
    assert result.assessment_for(second).state is DependencyTaskState.AVAILABLE
    assert result.assessment_for(third).state is DependencyTaskState.BLOCKED
    assert result.available_task_ids == (second,)
    assert result.blocked_task_ids == (third,)


def test_m368_4_does_not_treat_completion_as_execution_or_progress_inference() -> None:
    graph, first, _, _ = _graph()
    result = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=(first,),
    )
    snapshot = DependencyTrackingAuthority().snapshot

    assert snapshot.completion_input_required is True
    assert snapshot.transitive_blockers_reported is False
    assert snapshot.planning_execution_authorized is False
    assert snapshot.progress_inferred is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert result.planning_execution_authorized is False
    assert result.progress_inferred is False
    assert result.persistence_added is False


def test_m368_4_rejects_unknown_and_duplicate_completion_input() -> None:
    graph, first, _, _ = _graph()
    authority = DependencyTrackingAuthority()

    with pytest.raises(ValueError, match="unknown"):
        authority.evaluate(graph=graph, completed_task_ids=("missing",))
    with pytest.raises(ValueError, match="unique"):
        authority.evaluate(graph=graph, completed_task_ids=(first, first))


def test_m368_4_preserves_graph_order_in_assessments() -> None:
    graph, _, _, _ = _graph()
    result = DependencyTrackingAuthority().evaluate(graph=graph)

    assert tuple(item.task_id for item in result.assessments) == tuple(
        node.task_id for node in graph.nodes
    )


def test_m368_4_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_4_DEPENDENCY_TRACKING.md").read_text(
        encoding="utf-8"
    )

    assert "dependency_tracking" in document
    assert "predecesores incompletos" in document
    assert "no ejecuta tareas" in document
    assert "M368.4" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.4 — Dependency Tracking" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
