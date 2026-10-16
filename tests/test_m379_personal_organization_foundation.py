import pytest

from core.personal_organization import (
    PersonalOrganizationAuthority,
    PersonalOrganizationBinding,
    PersonalOrganizationCapability,
    PersonalOrganizationReadiness,
    PersonalOrganizationSnapshot,
)


def test_authority_covers_every_personal_organization_capability_once() -> None:
    snapshot = PersonalOrganizationAuthority().snapshot()
    assert {binding.normalized_capability for binding in snapshot.bindings} == set(
        PersonalOrganizationCapability
    )
    assert len(snapshot.bindings) == len(PersonalOrganizationCapability)


def test_foundation_reuses_existing_authorities_instead_of_replacing_them() -> None:
    snapshot = PersonalOrganizationAuthority().snapshot()
    assert snapshot.unified_core is True
    assert snapshot.replaces_existing_authorities is False
    assert snapshot.runtime_changed is False
    assert all(binding.authority_name for binding in snapshot.bindings)


def test_notes_reuse_existing_m74_personal_knowledge_authority() -> None:
    binding = PersonalOrganizationAuthority().binding_for("notes")
    assert binding.normalized_readiness is PersonalOrganizationReadiness.EXISTING
    assert binding.authority_name == "PersonalKnowledgeBaseManager"
    assert "KnowledgeKind.NOTE" in binding.notes[0]


def test_existing_capabilities_are_inventory_items() -> None:
    authority = PersonalOrganizationAuthority()
    for capability in ("agenda", "tasks", "reminders", "prioritization"):
        binding = authority.binding_for(capability)
        assert binding.normalized_readiness is PersonalOrganizationReadiness.EXISTING


def test_goals_reuse_existing_household_goal_owner() -> None:
    binding = PersonalOrganizationAuthority().binding_for("goals")
    assert binding.normalized_readiness is PersonalOrganizationReadiness.EXISTING
    assert binding.authority_name == "HouseholdGoalManager"
    assert binding.implementation_path == "core.household_goals:HouseholdGoalManager"
    assert "cognitive goals remain separate" in binding.notes[0]


def test_snapshot_rejects_missing_or_duplicate_capabilities() -> None:
    binding = PersonalOrganizationBinding(
        "agenda", "Agenda", "module:Agenda", "existing"
    )
    with pytest.raises(ValueError):
        PersonalOrganizationSnapshot((binding,))
    with pytest.raises(ValueError):
        PersonalOrganizationSnapshot((binding,) * len(PersonalOrganizationCapability))


def test_snapshot_rejects_parallel_brain_or_authority_replacement() -> None:
    bindings = PersonalOrganizationAuthority().snapshot().bindings
    with pytest.raises(ValueError):
        PersonalOrganizationSnapshot(bindings, creates_parallel_brain=True)
    with pytest.raises(ValueError):
        PersonalOrganizationSnapshot(bindings, replaces_existing_authorities=True)


def test_binding_requires_traceable_authority_and_implementation() -> None:
    with pytest.raises(ValueError):
        PersonalOrganizationBinding("agenda", "", "module:Agenda", "existing")
    with pytest.raises(ValueError):
        PersonalOrganizationBinding("agenda", "Agenda", "", "existing")


def test_authority_has_no_crud_execution_memory_or_agent_api() -> None:
    authority = PersonalOrganizationAuthority()
    for name in (
        "create_task",
        "delete_note",
        "execute_reminder",
        "write_memory",
        "spawn_agent",
        "call_llm",
    ):
        assert not hasattr(authority, name)
