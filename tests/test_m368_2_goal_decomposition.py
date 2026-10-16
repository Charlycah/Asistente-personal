from pathlib import Path

import pytest

from app.goal_decomposition import GoalDecompositionAuthority
from core.goal_decomposition import (
    DecompositionAdmissionMode,
    DecompositionStatus,
    GoalComponent,
    GoalDecomposition,
)


def test_m368_2_declares_one_subordinate_decomposition_authority() -> None:
    snapshot = GoalDecompositionAuthority().snapshot

    assert snapshot.schema_version == "m368.2"
    assert snapshot.canonical_authority == "goal_decomposition"
    assert snapshot.parent_planning_authority == "planning_foundation"
    assert snapshot.admission_mode is DecompositionAdmissionMode.EXPLICIT_COMPONENTS


def test_m368_2_decomposes_only_explicit_ordered_components() -> None:
    result = GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Preparar la próxima versión",
        component_titles=("Definir alcance", "Implementar", "Validar"),
    )

    assert result.status is DecompositionStatus.READY
    assert tuple(item.title for item in result.components) == (
        "Definir alcance",
        "Implementar",
        "Validar",
    )
    assert tuple(item.position for item in result.components) == (1, 2, 3)
    assert {item.parent_goal_id for item in result.components} == {"goal-1"}


def test_m368_2_produces_stable_traceable_identifiers() -> None:
    authority = GoalDecompositionAuthority()
    kwargs = dict(
        goal_id="goal-1",
        goal_title="Objetivo",
        component_titles=("Primero", "Segundo"),
    )

    first = authority.decompose(**kwargs)
    second = authority.decompose(**kwargs)

    assert first.decomposition_id == second.decomposition_id
    assert tuple(item.component_id for item in first.components) == tuple(
        item.component_id for item in second.components
    )


def test_m368_2_requests_clarification_without_enough_components() -> None:
    result = GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Objetivo",
        component_titles=("Único paso",),
    )

    assert result.status is DecompositionStatus.CLARIFICATION_REQUIRED
    assert result.components == ()
    assert "dos componentes explícitos" in (result.clarification_reason or "")


def test_m368_2_rejects_duplicate_or_excessive_components() -> None:
    authority = GoalDecompositionAuthority()

    with pytest.raises(ValueError, match="unique"):
        authority.decompose(
            goal_id="goal-1",
            goal_title="Objetivo",
            component_titles=("Repetido", "Repetido"),
        )
    with pytest.raises(ValueError, match="too many"):
        authority.decompose(
            goal_id="goal-1",
            goal_title="Objetivo",
            component_titles=(str(index) for index in range(21)),
        )


def test_m368_2_adds_no_execution_graph_dependencies_or_persistence() -> None:
    snapshot = GoalDecompositionAuthority().snapshot
    result = GoalDecompositionAuthority().decompose(
        goal_id="goal-1",
        goal_title="Objetivo",
        component_titles=("Uno", "Dos"),
    )

    assert snapshot.explicit_input_required is True
    assert snapshot.automatic_inference is False
    assert snapshot.planning_execution_authorized is False
    assert snapshot.task_graph_created is False
    assert snapshot.dependencies_inferred is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert result.planning_execution_authorized is False
    assert result.task_graph_created is False
    assert result.dependencies_inferred is False
    assert result.persistence_added is False


def test_goal_decomposition_contract_rejects_invalid_structures() -> None:
    component = GoalComponent(
        component_id="component-1",
        parent_goal_id="goal-1",
        position=1,
        title="Primero",
    )

    with pytest.raises(ValueError, match="at least two"):
        GoalDecomposition(
            decomposition_id="decomposition-1",
            goal_id="goal-1",
            goal_title="Objetivo",
            components=(component,),
            status=DecompositionStatus.READY,
            admission_mode=DecompositionAdmissionMode.EXPLICIT_COMPONENTS,
            clarification_reason=None,
            planning_execution_authorized=False,
            task_graph_created=False,
            dependencies_inferred=False,
            persistence_added=False,
        )


def test_m368_2_documentation_records_governed_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_2_GOAL_DECOMPOSITION.md").read_text(
        encoding="utf-8"
    )

    assert "goal_decomposition" in document
    assert "componentes explícitos" in document
    assert "no crea un grafo de tareas" in document
    assert "M368.2" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.2 — Goal Decomposition" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
