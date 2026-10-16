from pathlib import Path

import pytest

from app.planning_foundation import PlanningFoundation
from core.planning_foundation import (
    PlanningAuthority,
    PlanningDomain,
    PlanningRole,
)


def test_m368_1_declares_canonical_planning_foundation() -> None:
    snapshot = PlanningFoundation().snapshot

    assert snapshot.schema_version == "m368.1"
    assert snapshot.canonical_authority == "planning_foundation"
    assert snapshot.parent_world_authority == "internal_world_model"


def test_m368_1_covers_every_foundational_planning_domain() -> None:
    snapshot = PlanningFoundation().snapshot

    assert snapshot.supported_domains == tuple(PlanningDomain)
    assert tuple(item.domain for item in snapshot.authorities) == tuple(PlanningDomain)


def test_m368_1_preserves_one_authority_and_uses_current_goal_owner() -> None:
    snapshot = PlanningFoundation().snapshot

    assert {item.authority_key for item in snapshot.authorities} == {
        "planning_foundation"
    }
    goals = snapshot.authority_for(PlanningDomain.GOALS)
    assert goals.implementation_path == "core.cognitive_goals.manager:GoalManager"
    assert goals.parent_authority == "cognitive_goals"


def test_m368_1_maps_context_priority_and_progress_to_existing_authorities() -> None:
    snapshot = PlanningFoundation().snapshot

    assert snapshot.authority_for("priorities").parent_authority == (
        "priority_reasoning"
    )
    context = snapshot.authority_for("context")
    assert context.parent_authority == "global_context_fusion"
    assert context.implementation_path == (
        "core.global_context_fusion:GlobalContextFusionEngine"
    )
    assert snapshot.authority_for("tasks").parent_authority == "task_intelligence"
    assert snapshot.authority_for("progress").parent_authority == "goal_project_review"
    assert snapshot.authority_for("constraints").implementation_path == (
        "core.scope_guard:ScopeGuardManager"
    )


def test_m368_1_is_read_only_and_non_executing() -> None:
    snapshot = PlanningFoundation().snapshot

    assert snapshot.read_only is True
    assert snapshot.planning_execution_authorized is False
    assert snapshot.automatic_goal_creation is False
    assert snapshot.automatic_decomposition is False
    assert snapshot.automatic_replanning is False
    assert snapshot.persistence_added is False
    assert snapshot.runtime_behavior_changed is False
    assert all(not item.runtime_connected for item in snapshot.authorities)


def test_planning_authority_rejects_invalid_contracts() -> None:
    common = dict(
        domain=PlanningDomain.GOALS,
        role=PlanningRole.DESCRIBE,
        authority_key="planning_foundation",
        implementation_path="core.cognitive_goals.manager:GoalManager",
        purpose="Representar objetivos gobernados.",
        parent_authority="cognitive_goals",
        runtime_connected=False,
        persistent=False,
    )

    with pytest.raises(ValueError, match="authority key"):
        PlanningAuthority(**{**common, "authority_key": " "})
    with pytest.raises(ValueError, match="module:Symbol"):
        PlanningAuthority(**{**common, "implementation_path": "invalid"})
    with pytest.raises(ValueError, match="parent authority"):
        PlanningAuthority(**{**common, "parent_authority": " "})


def test_m368_1_documentation_records_foundation_scope() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (root / "docs/M368_1_PLANNING_FOUNDATION.md").read_text(
        encoding="utf-8"
    )

    assert "planning_foundation" in document
    assert "no ejecuta planes" in document
    assert "M368.1" in (root / "README.md").read_text(encoding="utf-8")
    assert "## M368.1 — Planning Foundation" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
