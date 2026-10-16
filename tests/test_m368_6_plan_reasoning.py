from pathlib import Path

import pytest

from app.dependency_tracking import DependencyTrackingAuthority
from app.goal_decomposition import GoalDecompositionAuthority
from app.plan_reasoning import PlanReasoningAuthority
from app.progress_evaluation import ProgressEvaluationAuthority
from app.task_graph import TaskGraphAuthority
from core.plan_reasoning import PlanReasoningState


def _planning_state(*completed_task_ids: str):
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
        precedence_edges=((first, third), (second, third)),
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
    return reasoning, graph, dependencies, progress, first, second, third


def test_m368_6_declares_one_subordinate_reasoning_authority() -> None:
    snapshot = PlanReasoningAuthority().snapshot

    assert snapshot.schema_version == "m368.6"
    assert snapshot.canonical_authority == "plan_reasoning"
    assert snapshot.parent_progress_authority == "progress_evaluation"


def test_m368_6_recommends_first_actionable_task_in_graph_order() -> None:
    reasoning, _, _, _, first, second, third = _planning_state()

    assert reasoning.state is PlanReasoningState.ACTIONABLE
    assert reasoning.actionable_task_ids == (first, second)
    assert reasoning.recommended_task_id == first
    assert reasoning.blocked_task_ids == (third,)
    assert reasoning.direct_blocker_ids == (first, second)


def test_m368_6_updates_recommendation_from_explicit_completion() -> None:
    initial, _, _, _, first, second, _ = _planning_state()
    reasoning, _, _, _, _, _, _ = _planning_state(first)

    assert initial.recommended_task_id == first
    assert reasoning.actionable_task_ids == (second,)
    assert reasoning.recommended_task_id == second


def test_m368_6_reports_completed_without_recommendation() -> None:
    _, _, _, _, first, second, third = _planning_state()
    reasoning, _, _, _, _, _, _ = _planning_state(first, second, third)

    assert reasoning.state is PlanReasoningState.COMPLETED
    assert reasoning.recommended_task_id is None
    assert reasoning.actionable_task_ids == ()
    assert reasoning.rationale_codes == ("plan_completed",)


def test_m368_6_rejects_mismatched_governed_inputs() -> None:
    _, graph, dependencies, progress, _, _, _ = _planning_state()
    other = GoalDecompositionAuthority().decompose(
        goal_id="goal-2",
        goal_title="Otro objetivo",
        component_titles=("Uno", "Dos"),
    )
    other_graph = TaskGraphAuthority().build(decomposition=other)

    with pytest.raises(ValueError, match="does not match task graph"):
        PlanReasoningAuthority().reason(
            graph=other_graph,
            dependency_result=dependencies,
            progress_result=progress,
        )
    assert graph.graph_id != other_graph.graph_id


def test_m368_6_does_not_infer_priority_reorder_replan_or_execute() -> None:
    reasoning, _, _, _, _, _, _ = _planning_state()
    snapshot = PlanReasoningAuthority().snapshot

    assert snapshot.graph_order_preserved is True
    assert snapshot.explicit_state_required is True
    assert snapshot.priority_inferred is False
    assert snapshot.plan_reordered is False
    assert snapshot.replanning_authorized is False
    assert snapshot.planning_execution_authorized is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert reasoning.priority_inferred is False
    assert reasoning.plan_reordered is False
    assert reasoning.replanning_authorized is False
    assert reasoning.planning_execution_authorized is False
    assert reasoning.persistence_added is False


def test_m368_6_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_6_PLAN_REASONING.md").read_text(
        encoding="utf-8"
    )

    assert "plan_reasoning" in document
    assert "orden del grafo" in document
    assert "no replantea" in document
    assert "M368.6" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.6 — Plan Reasoning" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
