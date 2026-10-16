from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.canonical_cognitive_state_facade import (
    CanonicalCognitiveStateFacade,
    CanonicalCognitiveStateOperation,
    CanonicalCognitiveStateRole,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_state_contract import CognitiveState, CognitiveStateUpdate


class RecordingStateAuthority:
    def __init__(self):
        self.calls = []
        self.state = CognitiveState.empty(
            updated_at=datetime(2026, 7, 28, tzinfo=timezone.utc)
        )

    def snapshot(self):
        self.calls.append(("snapshot", None))
        return self.state

    def update(self, changes):
        self.calls.append(("update", changes))
        return self.state

    def reset(self):
        self.calls.append(("reset", None))
        return self.state


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_cognitive_state_facade_declares_one_official_primary():
    snapshot = CanonicalCognitiveStateFacade().snapshot
    primaries = [
        component
        for component in snapshot.components
        if component.role is CanonicalCognitiveStateRole.PRIMARY
    ]

    assert snapshot.schema_version == "m342.8"
    assert snapshot.primary == "cognitive_state_contract"
    assert [component.key for component in primaries] == [
        "cognitive_state_contract"
    ]


def test_primary_is_the_only_writable_state_component():
    snapshot = CanonicalCognitiveStateFacade().snapshot
    writable = [component for component in snapshot.components if component.writable]

    assert [component.key for component in writable] == [
        "cognitive_state_contract"
    ]
    assert writable[0].operations == (
        CanonicalCognitiveStateOperation.READ,
        CanonicalCognitiveStateOperation.UPDATE,
        CanonicalCognitiveStateOperation.RESET,
    )


def test_derived_and_observational_states_remain_subordinate():
    snapshot = CanonicalCognitiveStateFacade().snapshot
    global_state = snapshot.component_for("global_cognitive_state")
    resident_state = snapshot.component_for("continuous_cognitive_loop_state")

    assert global_state.role is CanonicalCognitiveStateRole.SPECIALIZED
    assert global_state.operations == (CanonicalCognitiveStateOperation.DERIVE,)
    assert resident_state.role is CanonicalCognitiveStateRole.OBSERVER
    assert resident_state.operations == (CanonicalCognitiveStateOperation.OBSERVE,)
    assert resident_state.writable is False


def test_unbound_facade_is_observable_but_not_operational():
    facade = CanonicalCognitiveStateFacade()

    assert facade.bound is False
    with pytest.raises(RuntimeError, match="not bound"):
        facade.current()


def test_bound_facade_delegates_without_changing_state_semantics():
    authority = RecordingStateAuthority()
    facade = CanonicalCognitiveStateFacade(authority=authority)
    changes = CognitiveStateUpdate(current_focus="consolidar estado")

    assert facade.current() is authority.state
    assert facade.update(changes) is authority.state
    assert facade.reset() is authority.state
    assert authority.calls == [
        ("snapshot", None),
        ("update", changes),
        ("reset", None),
    ]


def test_gateway_exposes_state_consolidation_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_cognitive_state
    result = gateway.converse("hola")
    after = gateway.canonical_cognitive_state

    assert result.response == "echo:hola"
    assert before == after
    assert before.primary == "cognitive_state_contract"
