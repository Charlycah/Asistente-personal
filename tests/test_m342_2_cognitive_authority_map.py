from types import SimpleNamespace

import pytest

from app.cognitive_authority_map import (
    COGNITIVE_AUTHORITY_ASSIGNMENTS,
    CognitiveAuthorityAssignment,
    CognitiveAuthorityMap,
)
from app.cognitive_operational_inventory import (
    CognitiveAuthority,
    CognitiveCapabilityState,
)
from app.official_conversation_gateway import OfficialConversationGateway


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_map_assigns_exactly_one_primary_to_every_authority():
    snapshot = CognitiveAuthorityMap().snapshot

    assert snapshot.schema_version == "m342.2"
    assert {item.authority for item in snapshot.assignments} == set(
        CognitiveAuthority
    )
    assert len(snapshot.assignments) == len(CognitiveAuthority)
    assert all(item.primary for item in snapshot.assignments)


def test_map_declares_secondary_roles_without_competing_authority():
    snapshot = CognitiveAuthorityMap().snapshot

    decision = snapshot.authority_for(CognitiveAuthority.DECISION)
    planning = snapshot.authority_for(CognitiveAuthority.PLANNING)
    reflection = snapshot.authority_for(CognitiveAuthority.REFLECTION)

    assert decision.primary == "unified_cognitive_coordination"
    assert decision.collaborators == ("executive_director",)
    assert planning.primary == "executive_planning"
    assert planning.shadow == ("cognitive_planner_shadow",)
    assert reflection.primary == "cognitive_core_resident"
    assert reflection.collaborators == ("adaptive_cognition",)


def test_map_rejects_duplicate_or_missing_authority_assignments():
    duplicated = COGNITIVE_AUTHORITY_ASSIGNMENTS + (
        COGNITIVE_AUTHORITY_ASSIGNMENTS[0],
    )

    with pytest.raises(ValueError, match="one assignment"):
        CognitiveAuthorityMap(assignments=duplicated)

    with pytest.raises(ValueError, match="all cognitive authorities"):
        CognitiveAuthorityMap(assignments=COGNITIVE_AUTHORITY_ASSIGNMENTS[:-1])


def test_map_rejects_promoting_shadow_component_to_primary():
    invalid = tuple(
        CognitiveAuthorityAssignment(
            authority=item.authority,
            primary=(
                "cognitive_planner_shadow"
                if item.authority is CognitiveAuthority.PLANNING
                else item.primary
            ),
            collaborators=item.collaborators,
            observers=item.observers,
            shadow=(),
            rationale=item.rationale,
        )
        for item in COGNITIVE_AUTHORITY_ASSIGNMENTS
    )

    with pytest.raises(ValueError, match="must be canonical"):
        CognitiveAuthorityMap(assignments=invalid)


def test_gateway_exposes_read_only_map_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.cognitive_authority_map
    result = gateway.converse("hola")
    after = gateway.cognitive_authority_map

    assert result.response == "echo:hola"
    assert before == after
    assert after.authority_for(CognitiveAuthority.EXECUTION).primary == (
        "capability_orchestrator"
    )
    assert (
        after.authority_for(CognitiveAuthority.PLANNING).shadow
        == ("cognitive_planner_shadow",)
    )


def test_declared_shadow_role_matches_inventory_state():
    snapshot = CognitiveAuthorityMap().snapshot
    planning = snapshot.authority_for(CognitiveAuthority.PLANNING)

    assert planning.shadow == ("cognitive_planner_shadow",)
    assert CognitiveCapabilityState.SHADOW.value == "shadow"
