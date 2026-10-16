from types import SimpleNamespace

from app.canonical_cognitive_cycle import (
    CanonicalCognitiveCycle,
    CognitiveCycleParticipation,
    CognitiveCyclePhase,
)
from app.cognitive_operational_inventory import CognitiveAuthority
from app.official_conversation_gateway import OfficialConversationGateway


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_cycle_is_ordered_from_entry_to_response():
    snapshot = CanonicalCognitiveCycle().snapshot

    assert snapshot.schema_version == "m342.3"
    assert snapshot.stages[0].phase is CognitiveCyclePhase.ENTRY
    assert snapshot.stages[-1].phase is CognitiveCyclePhase.RESPONSE
    assert tuple(stage.sequence for stage in snapshot.stages) == tuple(
        range(1, len(snapshot.stages) + 1)
    )


def test_cycle_covers_every_official_authority():
    snapshot = CanonicalCognitiveCycle().snapshot

    assert {stage.authority for stage in snapshot.stages} == set(
        CognitiveAuthority
    )


def test_cycle_uses_primary_components_from_authority_map():
    snapshot = CanonicalCognitiveCycle().snapshot

    assert snapshot.stage_for(CognitiveCyclePhase.ENTRY).primary == (
        "conversation_entry"
    )
    assert snapshot.stage_for(CognitiveCyclePhase.PLANNING).primary == (
        "executive_planning"
    )
    assert snapshot.stage_for(CognitiveCyclePhase.DECISION).primary == (
        "unified_cognitive_coordination"
    )
    assert snapshot.stage_for(CognitiveCyclePhase.EXECUTION).primary == (
        "capability_orchestrator"
    )


def test_cycle_marks_optional_and_observational_participation():
    snapshot = CanonicalCognitiveCycle().snapshot

    assert snapshot.stage_for(CognitiveCyclePhase.MEMORY).participation is (
        CognitiveCycleParticipation.CONDITIONAL
    )
    assert snapshot.stage_for(CognitiveCyclePhase.EXECUTION).participation is (
        CognitiveCycleParticipation.CONDITIONAL
    )
    assert snapshot.stage_for(CognitiveCyclePhase.OBSERVABILITY).participation is (
        CognitiveCycleParticipation.OBSERVATIONAL
    )


def test_response_returns_through_same_official_boundary():
    snapshot = CanonicalCognitiveCycle().snapshot
    entry = snapshot.stage_for(CognitiveCyclePhase.ENTRY)
    response = snapshot.stage_for(CognitiveCyclePhase.RESPONSE)

    assert response.authority is entry.authority
    assert response.primary == entry.primary


def test_gateway_exposes_cycle_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_cognitive_cycle
    result = gateway.converse("hola")
    after = gateway.canonical_cognitive_cycle

    assert result.response == "echo:hola"
    assert before == after
    assert after.stage_for(CognitiveCyclePhase.RESPONSE).primary == (
        "conversation_entry"
    )
