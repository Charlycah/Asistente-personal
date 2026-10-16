from types import SimpleNamespace

import pytest

from app.canonical_memory_facade import (
    CanonicalMemoryFacade,
    CanonicalMemoryOperation,
    CanonicalMemoryRole,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.memory import MemoryItem, MemoryQuery


class RecordingMemoryGateway:
    def __init__(self):
        self.remembered = []
        self.queries = []

    def remember(self, item):
        self.remembered.append(item)

    def recall(self, query):
        self.queries.append(query)
        return [MemoryItem(content="Carlos prefiere mate", metadata={})]

    def status(self):
        return SimpleNamespace(owner="Carlos", stored_count=1, persistent=True)

    def intercept(self, request, *, now):
        return (request, now)


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_memory_facade_declares_one_official_primary():
    snapshot = CanonicalMemoryFacade().snapshot

    primaries = [
        component
        for component in snapshot.components
        if component.role is CanonicalMemoryRole.PRIMARY
    ]

    assert snapshot.schema_version == "m342.5"
    assert snapshot.primary == "memory_gateway"
    assert [component.key for component in primaries] == ["memory_gateway"]


def test_specialized_memories_remain_subordinate():
    snapshot = CanonicalMemoryFacade().snapshot

    assert snapshot.component_for("episodic_memory").role is (
        CanonicalMemoryRole.SPECIALIZED
    )
    assert snapshot.component_for("executive_working_memory").role is (
        CanonicalMemoryRole.SPECIALIZED
    )
    assert snapshot.component_for("cognitive_memory_integration").role is (
        CanonicalMemoryRole.LEGACY
    )


def test_brain_adapter_is_read_only():
    adapter = CanonicalMemoryFacade().snapshot.component_for("brain_memory_adapter")

    assert adapter.writable is False
    assert adapter.operations == (CanonicalMemoryOperation.RECALL,)


def test_unbound_facade_is_observable_but_not_operational():
    facade = CanonicalMemoryFacade()

    assert facade.bound is False
    with pytest.raises(RuntimeError, match="not bound"):
        facade.recall(MemoryQuery(text="Carlos"))


def test_bound_facade_delegates_without_changing_memory_semantics():
    gateway = RecordingMemoryGateway()
    facade = CanonicalMemoryFacade(gateway=gateway)
    item = MemoryItem(content="Carlos prefiere mate", metadata={})
    query = MemoryQuery(text="mate")

    facade.remember(item)
    recalled = facade.recall(query)

    assert facade.bound is True
    assert gateway.remembered == [item]
    assert gateway.queries == [query]
    assert recalled == [MemoryItem(content="Carlos prefiere mate", metadata={})]
    assert facade.status().stored_count == 1


def test_gateway_exposes_memory_consolidation_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.canonical_memory
    result = gateway.converse("hola")
    after = gateway.canonical_memory

    assert result.response == "echo:hola"
    assert before == after
    assert before.primary == "memory_gateway"
