from __future__ import annotations

from pathlib import Path

from app.planning_foundation import PlanningFoundation
from core.personal_organization import PersonalOrganizationAuthority

ROOT = Path(__file__).resolve().parents[2]

_RETIRED = (
    "app/user_profile_model.py",
    "app/project_knowledge_model.py",
    "app/goals_objectives_model.py",
    "app/context_state_model.py",
    "app/mental_model_stabilization.py",
    "core/user_profile_model.py",
    "core/project_knowledge_model.py",
    "core/goals_objectives_model.py",
    "core/context_state_model.py",
    "core/mental_model_stabilization.py",
)


def test_m367_historical_inventory_and_diagnostic_surfaces_are_absent() -> None:
    assert all(not (ROOT / relative).exists() for relative in _RETIRED)


def test_m367_evolved_world_model_and_priority_surfaces_remain_present() -> None:
    assert (ROOT / "app/internal_world_model_foundation.py").exists()
    assert (ROOT / "app/priority_reasoning.py").exists()
    assert (ROOT / "domain/priority_reasoning.py").exists()


def test_current_planning_contract_has_no_retired_m367_source_dependencies() -> None:
    snapshot = PlanningFoundation().snapshot
    retired_names = {
        "user_profile_model",
        "project_knowledge_model",
        "goals_objectives_model",
        "context_state_model",
        "mental_model_stabilization",
    }
    assert all(
        item.parent_authority not in retired_names for item in snapshot.authorities
    )
    assert all(
        not any(name in item.implementation_path for name in retired_names)
        for item in snapshot.authorities
    )


def test_personal_organization_goals_use_existing_household_goal_owner() -> None:
    binding = PersonalOrganizationAuthority().binding_for("goals")
    assert binding.authority_name == "HouseholdGoalManager"
    assert binding.implementation_path == "core.household_goals:HouseholdGoalManager"


def test_current_python_code_does_not_import_retired_m367_modules() -> None:
    retired_module_fragments = (
        "app.user_profile_model",
        "app.project_knowledge_model",
        "app.goals_objectives_model",
        "app.context_state_model",
        "app.mental_model_stabilization",
        "core.user_profile_model",
        "core.project_knowledge_model",
        "core.goals_objectives_model",
        "core.context_state_model",
        "core.mental_model_stabilization",
    )
    roots = (
        "app",
        "core",
        "application",
        "domain",
        "infrastructure",
        "interfaces",
        "scripts",
    )
    offenders: list[str] = []
    for root_name in roots:
        for path in (ROOT / root_name).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            if any(fragment in source for fragment in retired_module_fragments):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []
