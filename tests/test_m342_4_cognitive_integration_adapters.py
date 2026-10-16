from types import SimpleNamespace

from app.cognitive_integration_adapters import (
    CognitiveAdapterKind,
    CognitiveAdapterMode,
    CognitiveIntegrationAdapters,
    CognitiveIntegrationRequest,
)
from app.cognitive_operational_inventory import CognitiveAuthority
from app.official_conversation_gateway import OfficialConversationGateway


class ConversationStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str, *, now=None):
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_adapters_cover_declared_integration_boundaries():
    snapshot = CognitiveIntegrationAdapters().snapshot

    assert snapshot.schema_version == "m342.4"
    assert {adapter.kind for adapter in snapshot.adapters} == set(
        CognitiveAdapterKind
    )


def test_adapters_use_official_primary_authorities():
    snapshot = CognitiveIntegrationAdapters().snapshot

    assert snapshot.adapter_for(CognitiveAdapterKind.MEMORY).primary == (
        "memory_gateway"
    )
    assert snapshot.adapter_for(CognitiveAdapterKind.PLANNING).primary == (
        "executive_planning"
    )
    assert snapshot.adapter_for(CognitiveAdapterKind.DECISION).primary == (
        "unified_cognitive_coordination"
    )


def test_adapters_preserve_read_only_and_observational_roles():
    snapshot = CognitiveIntegrationAdapters().snapshot

    assert snapshot.adapter_for(CognitiveAdapterKind.REFLECTION).mode is (
        CognitiveAdapterMode.READ_ONLY
    )
    assert snapshot.adapter_for(CognitiveAdapterKind.OBSERVABILITY).mode is (
        CognitiveAdapterMode.OBSERVATIONAL
    )


def test_request_description_does_not_invoke_runtime():
    adapters = CognitiveIntegrationAdapters()
    request = CognitiveIntegrationRequest(
        adapter=CognitiveAdapterKind.DECISION,
        turn_id="turn-1",
        payload={"options": ("a", "b")},
    )

    result = adapters.describe_request(request)

    assert result.accepted is True
    assert result.authority is CognitiveAuthority.DECISION
    assert result.primary == "unified_cognitive_coordination"
    assert result.payload == {"options": ("a", "b")}


def test_gateway_exposes_adapters_without_changing_conversation():
    gateway = OfficialConversationGateway(ConversationStub())

    before = gateway.cognitive_integration_adapters
    result = gateway.converse("hola")
    after = gateway.cognitive_integration_adapters

    assert result.response == "echo:hola"
    assert before == after


def test_adapter_snapshot_is_serializable():
    payload = CognitiveIntegrationAdapters().snapshot.as_dict()

    assert payload["schema_version"] == "m342.4"
    assert len(payload["adapters"]) == len(CognitiveAdapterKind)
