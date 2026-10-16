from pathlib import Path

import pytest

from app.procedural_memory_foundation import ProceduralMemoryFoundation
from core.procedural_memory_foundation import (
    ProceduralAdmissionMode,
    ProceduralMemoryAuthority,
    ProceduralMemoryLayer,
)


def test_m366_4_declares_existing_procedural_layers_once() -> None:
    snapshot = ProceduralMemoryFoundation().snapshot

    assert snapshot.schema_version == "m366.4"
    assert tuple(item.layer for item in snapshot.authorities) == tuple(
        ProceduralMemoryLayer
    )


def test_m366_4_preserves_one_canonical_procedural_authority() -> None:
    snapshot = ProceduralMemoryFoundation().snapshot

    assert snapshot.canonical_authority == "memory_gateway"
    assert {item.authority_key for item in snapshot.authorities} == {
        "memory_gateway"
    }


def test_governed_plans_reuse_existing_model() -> None:
    authority = ProceduralMemoryFoundation().snapshot.authority_for("governed_plans")

    assert authority.implementation_path == "domain.governed_plan:GovernedPlanModel"
    assert authority.admission_mode is ProceduralAdmissionMode.EXPLICIT_ACCEPTANCE


def test_routines_reuse_existing_manager() -> None:
    authority = ProceduralMemoryFoundation().snapshot.authority_for("routines_habits")

    assert authority.implementation_path == "core.routines_habits:RoutineHabitManager"
    assert authority.admission_mode is ProceduralAdmissionMode.SUPERVISED_OBSERVATION


def test_tasks_reuse_existing_intelligence_manager() -> None:
    authority = ProceduralMemoryFoundation().snapshot.authority_for("task_procedures")

    assert authority.implementation_path == (
        "core.task_intelligence:TaskIntelligenceManager"
    )
    assert authority.admission_mode is (
        ProceduralAdmissionMode.GOVERNED_TASK_DEFINITION
    )


def test_remembered_procedure_does_not_authorize_execution() -> None:
    snapshot = ProceduralMemoryFoundation().snapshot

    assert snapshot.remembered_procedure_authorizes_execution is False
    assert all(item.execution_authority is False for item in snapshot.authorities)


def test_m366_4_adds_no_persistence_learning_or_runtime_behavior() -> None:
    snapshot = ProceduralMemoryFoundation().snapshot

    assert snapshot.persistence_added is False
    assert snapshot.automatic_learning_added is False
    assert snapshot.runtime_behavior_changed is False
    assert all(item.automatic_promotion is False for item in snapshot.authorities)


def test_authority_rejects_execution_and_automatic_promotion() -> None:
    with pytest.raises(ValueError, match="cannot grant"):
        ProceduralMemoryAuthority(
            layer=ProceduralMemoryLayer.GOVERNED_PLANS,
            authority_key="memory_gateway",
            implementation_path="module:Symbol",
            purpose="test",
            admission_mode=ProceduralAdmissionMode.EXPLICIT_ACCEPTANCE,
            persistent=False,
            runtime_connected=False,
            execution_authority=True,
        )

    with pytest.raises(ValueError, match="cannot enable automatic"):
        ProceduralMemoryAuthority(
            layer=ProceduralMemoryLayer.GOVERNED_PLANS,
            authority_key="memory_gateway",
            implementation_path="module:Symbol",
            purpose="test",
            admission_mode=ProceduralAdmissionMode.EXPLICIT_ACCEPTANCE,
            persistent=False,
            runtime_connected=False,
            automatic_promotion=True,
        )


def test_existing_procedural_implementations_remain_available() -> None:
    root = Path(__file__).resolve().parents[1]

    assert (root / "domain/governed_plan.py").exists()
    assert (root / "core/routines_habits.py").exists()
    assert (root / "core/task_intelligence.py").exists()


def test_m366_4_documentation_and_root_register_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M366_4_PROCEDURAL_MEMORY.md").read_text(
        encoding="utf-8"
    )

    assert "GovernedPlanModel" in document
    assert "RoutineHabitManager" in document
    assert "TaskIntelligenceManager" in document
    assert "recordar un procedimiento no autoriza su ejecución" in document
    assert "M366.4" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M366.4 — Procedural Memory" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
