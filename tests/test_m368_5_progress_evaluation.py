from pathlib import Path

from app.dependency_tracking import DependencyTrackingAuthority
from app.goal_decomposition import GoalDecompositionAuthority
from app.progress_evaluation import ProgressEvaluationAuthority
from app.task_graph import TaskGraphAuthority
from core.progress_evaluation import PlanProgressState


def _graph_and_tasks():
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


def _progress(*completed_task_ids: str):
    graph, first, second, third = _graph_and_tasks()
    dependencies = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=completed_task_ids,
    )
    progress = ProgressEvaluationAuthority().evaluate(
        dependency_result=dependencies
    )
    return progress, first, second, third


def test_m368_5_declares_one_subordinate_progress_authority() -> None:
    snapshot = ProgressEvaluationAuthority().snapshot

    assert snapshot.schema_version == "m368.5"
    assert snapshot.canonical_authority == "progress_evaluation"
    assert snapshot.parent_dependency_authority == "dependency_tracking"


def test_m368_5_reports_not_started_from_explicit_empty_completion() -> None:
    progress, _, _, _ = _progress()

    assert progress.state is PlanProgressState.NOT_STARTED
    assert progress.completion_fraction == (0, 3)
    assert progress.completion_percentage == 0.0
    assert progress.available_task_count == 1
    assert progress.blocked_task_count == 2


def test_m368_5_reports_structural_progress_from_completed_tasks() -> None:
    _, first, _, _ = _progress()
    progress, _, second, _ = _progress(first)

    assert progress.state is PlanProgressState.IN_PROGRESS
    assert progress.completed_task_ids == (first,)
    assert progress.completion_fraction == (1, 3)
    assert progress.completion_percentage == 33.33
    assert progress.available_task_count == 1
    assert progress.blocked_task_count == 1
    assert second not in progress.completed_task_ids


def test_m368_5_reports_completed_only_when_every_task_is_completed() -> None:
    _, first, second, third = _progress()
    progress, _, _, _ = _progress(first, second, third)

    assert progress.state is PlanProgressState.COMPLETED
    assert progress.completion_fraction == (3, 3)
    assert progress.completion_percentage == 100.0
    assert progress.available_task_count == 0
    assert progress.blocked_task_count == 0


def test_m368_5_preserves_graph_and_goal_traceability() -> None:
    graph, first, _, _ = _graph_and_tasks()
    dependencies = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=(first,),
    )
    progress = ProgressEvaluationAuthority().evaluate(
        dependency_result=dependencies
    )

    assert progress.graph_id == graph.graph_id
    assert progress.goal_id == graph.goal_id


def test_m368_5_does_not_weight_predict_execute_or_persist() -> None:
    progress, _, _, _ = _progress()
    snapshot = ProgressEvaluationAuthority().snapshot

    assert snapshot.explicit_completion_required is True
    assert snapshot.weighted_progress_used is False
    assert snapshot.progress_predicted is False
    assert snapshot.planning_execution_authorized is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert progress.weighted_progress_used is False
    assert progress.progress_predicted is False
    assert progress.planning_execution_authorized is False
    assert progress.persistence_added is False


def test_m368_5_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_5_PROGRESS_EVALUATION.md").read_text(
        encoding="utf-8"
    )

    assert "progress_evaluation" in document
    assert "completitud explícita" in document
    assert "no pondera tareas" in document
    assert "M368.5" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.5 — Progress Evaluation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
