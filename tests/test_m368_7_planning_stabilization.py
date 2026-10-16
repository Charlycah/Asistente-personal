from pathlib import Path

from app.dependency_tracking import DependencyTrackingAuthority
from app.goal_decomposition import GoalDecompositionAuthority
from app.plan_reasoning import PlanReasoningAuthority
from app.planning_stabilization import PlanningStabilizationAudit
from app.progress_evaluation import ProgressEvaluationAuthority
from app.task_graph import TaskGraphAuthority
from core.dependency_tracking import DependencyTaskState
from core.plan_reasoning import PlanReasoningState
from core.progress_evaluation import PlanProgressState


def _closed_series_pipeline(*completed_task_ids: str):
    decomposition = GoalDecompositionAuthority().decompose(
        goal_id="goal-stable",
        goal_title="Cerrar serie M368",
        component_titles=("Auditar", "Documentar", "Validar"),
    )
    first, second, third = (
        component.component_id for component in decomposition.components
    )
    graph = TaskGraphAuthority().build(
        decomposition=decomposition,
        precedence_edges=((first, second), (second, third)),
    )
    dependencies = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=completed_task_ids,
    )
    progress = ProgressEvaluationAuthority().evaluate(
        dependency_result=dependencies
    )
    reasoning = PlanReasoningAuthority().reason(
        graph=graph,
        dependency_result=dependencies,
        progress_result=progress,
    )
    return graph, dependencies, progress, reasoning, first, second, third


def test_m368_7_certifies_exact_governed_authority_chain() -> None:
    report = PlanningStabilizationAudit().audit()

    assert report.schema_version == "m368.7"
    assert report.authority_chain == (
        "planning_foundation",
        "goal_decomposition",
        "task_graph",
        "dependency_tracking",
        "progress_evaluation",
        "plan_reasoning",
    )
    assert tuple(item.schema_version for item in report.authorities) == (
        "m368.1",
        "m368.2",
        "m368.3",
        "m368.4",
        "m368.5",
        "m368.6",
    )


def test_m368_7_certifies_side_effect_boundaries() -> None:
    report = PlanningStabilizationAudit().audit()

    assert report.authority_names_unique is True
    assert report.parent_chain_valid is True
    assert report.runtime_isolated is True
    assert report.persistence_absent is True
    assert report.execution_absent is True
    assert report.integration_invariants_verified is True
    assert report.series_closed is True


def test_m368_7_completed_task_never_remains_blocked() -> None:
    graph, _, _, _, first, _, _ = _closed_series_pipeline()
    dependencies = DependencyTrackingAuthority().evaluate(
        graph=graph,
        completed_task_ids=(first,),
    )

    assessment = dependencies.assessment_for(first)
    assert assessment.state is DependencyTaskState.COMPLETED
    assert assessment.blocker_ids == ()


def test_m368_7_recommendation_is_always_actionable() -> None:
    _, dependencies, _, reasoning, first, _, _ = _closed_series_pipeline()

    assert reasoning.state is PlanReasoningState.ACTIONABLE
    assert reasoning.recommended_task_id == first
    assert reasoning.recommended_task_id in dependencies.available_task_ids


def test_m368_7_completed_plan_has_no_pending_or_recommendation() -> None:
    _, _, _, _, first, second, third = _closed_series_pipeline()
    _, dependencies, progress, reasoning, _, _, _ = _closed_series_pipeline(
        first,
        second,
        third,
    )

    assert progress.state is PlanProgressState.COMPLETED
    assert progress.available_task_count == 0
    assert progress.blocked_task_count == 0
    assert dependencies.available_task_ids == ()
    assert dependencies.blocked_task_ids == ()
    assert reasoning.state is PlanReasoningState.COMPLETED
    assert reasoning.recommended_task_id is None


def test_m368_7_documentation_closes_series() -> None:
    root = Path(__file__).resolve().parents[1]
    stabilization = (root / "docs/M368_7_PLANNING_STABILIZATION.md").read_text(
        encoding="utf-8"
    )
    report = (root / "docs/M368_SERIES_REPORT.md").read_text(encoding="utf-8")

    assert "serie M368 queda cerrada" in stabilization
    assert "planning_foundation" in stabilization
    assert "M368.1" in report and "M368.7" in report
    assert "9002" in report
    assert "M368.7" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.7 — Planning Stabilization" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
