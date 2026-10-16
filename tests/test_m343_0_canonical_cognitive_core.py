from __future__ import annotations

from types import SimpleNamespace

from app.canonical_cognitive_core import (
    CanonicalCognitiveCore,
    CanonicalCognitiveCoreDomain,
)
from app.canonical_cognitive_state_facade import CanonicalCognitiveStateFacade
from app.canonical_decision_facade import CanonicalDecisionFacade
from app.canonical_memory_facade import CanonicalMemoryFacade
from app.canonical_planning_facade import CanonicalPlanningFacade
from app.canonical_reflection_facade import CanonicalReflectionFacade
from app.official_conversation_gateway import OfficialConversationGateway


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def _core() -> CanonicalCognitiveCore:
    return CanonicalCognitiveCore(
        memory=CanonicalMemoryFacade(),
        planning=CanonicalPlanningFacade(),
        decision=CanonicalDecisionFacade(),
        state=CanonicalCognitiveStateFacade(),
        reflection=CanonicalReflectionFacade(),
    )


def test_core_exposes_exactly_five_canonical_domains():
    snapshot = _core().snapshot

    assert tuple(component.domain for component in snapshot.components) == tuple(
        CanonicalCognitiveCoreDomain
    )


def test_core_preserves_each_domain_primary_authority():
    snapshot = _core().snapshot

    assert snapshot.component_for(CanonicalCognitiveCoreDomain.MEMORY).primary == (
        "memory_gateway"
    )
    assert snapshot.component_for(CanonicalCognitiveCoreDomain.PLANNING).primary == (
        "executive_planning"
    )
    assert snapshot.component_for(CanonicalCognitiveCoreDomain.DECISION).primary == (
        "unified_cognitive_coordination"
    )
    assert snapshot.component_for(CanonicalCognitiveCoreDomain.STATE).primary == (
        "cognitive_state_contract"
    )
    assert snapshot.component_for(CanonicalCognitiveCoreDomain.REFLECTION).primary == (
        "cognitive_core_resident"
    )


def test_core_does_not_bind_unbound_domain_facades():
    snapshot = _core().snapshot

    assert all(component.bound is False for component in snapshot.components)


def test_core_returns_original_facade_instances():
    memory = CanonicalMemoryFacade()
    core = CanonicalCognitiveCore(
        memory=memory,
        planning=CanonicalPlanningFacade(),
        decision=CanonicalDecisionFacade(),
        state=CanonicalCognitiveStateFacade(),
        reflection=CanonicalReflectionFacade(),
    )

    assert core.facade_for(CanonicalCognitiveCoreDomain.MEMORY) is memory


def test_core_snapshot_is_serializable():
    payload = _core().snapshot.as_dict()

    assert payload["schema_version"] == "m343.0"
    assert len(payload["components"]) == 5


def test_gateway_exposes_canonical_core_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_cognitive_core
    result = gateway.converse("hola")
    after = gateway.canonical_cognitive_core

    assert result.response == "echo:hola"
    assert before == after
    assert before.schema_version == "m343.0"
    assert len(before.components) == 5
