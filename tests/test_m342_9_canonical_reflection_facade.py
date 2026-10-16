from types import SimpleNamespace

import pytest

from app.canonical_reflection_facade import (
    CanonicalReflectionFacade,
    CanonicalReflectionOperation,
    CanonicalReflectionRole,
)
from app.official_conversation_gateway import OfficialConversationGateway


class RecordingReflectionAuthority:
    def __init__(self):
        self.calls = []

    def reflect(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return "reflection-result"


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_reflection_facade_declares_one_official_primary():
    snapshot = CanonicalReflectionFacade().snapshot
    primaries = [
        component
        for component in snapshot.components
        if component.role is CanonicalReflectionRole.PRIMARY
    ]

    assert snapshot.schema_version == "m342.9"
    assert snapshot.primary == "cognitive_core_resident"
    assert [component.key for component in primaries] == [
        "cognitive_core_resident"
    ]


def test_adaptive_cognition_remains_a_consultative_collaborator():
    component = CanonicalReflectionFacade().snapshot.component_for(
        "adaptive_cognition"
    )

    assert component.role is CanonicalReflectionRole.COLLABORATOR
    assert component.operations == (CanonicalReflectionOperation.CONTRIBUTE,)
    assert component.operational is True


def test_specialized_reflection_engines_remain_subordinate():
    snapshot = CanonicalReflectionFacade().snapshot
    resident = snapshot.component_for("resident_reflection_engine")
    metacognitive = snapshot.component_for("metacognitive_reflection_engine")

    assert resident.role is CanonicalReflectionRole.SPECIALIZED
    assert metacognitive.role is CanonicalReflectionRole.SPECIALIZED
    assert resident.operational is False
    assert metacognitive.operational is False


def test_runtime_contributor_is_observational_only():
    contributor = CanonicalReflectionFacade().snapshot.component_for(
        "reflection_runtime_contributor"
    )

    assert contributor.role is CanonicalReflectionRole.OBSERVER
    assert contributor.operations == (CanonicalReflectionOperation.OBSERVE,)
    assert contributor.operational is False


def test_unbound_facade_is_observable_but_not_operational():
    facade = CanonicalReflectionFacade()

    assert facade.bound is False
    with pytest.raises(RuntimeError, match="not bound"):
        facade.reflect("subject")


def test_bound_facade_delegates_without_changing_reflection_semantics():
    authority = RecordingReflectionAuthority()
    facade = CanonicalReflectionFacade(authority=authority)

    result = facade.reflect("subject", focus="behavior")

    assert result == "reflection-result"
    assert authority.calls == [(('subject',), {"focus": "behavior"})]


def test_gateway_exposes_reflection_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_reflection
    result = gateway.converse("hola")
    after = gateway.canonical_reflection

    assert result.response == "echo:hola"
    assert before == after
    assert before.primary == "cognitive_core_resident"
