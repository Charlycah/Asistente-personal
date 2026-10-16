from __future__ import annotations

from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    UnifiedCoordinationEvidenceAdapter,
)


class Turn:
    response_text = "respuesta"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def converse(self, text: str) -> Turn:
        if self.error is not None:
            raise self.error
        return Turn()


def test_m386_12_direct_gateway_records_entry_perception_and_response() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    gateway.submit("contenido privado")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 3
    assert cycle.node("unified_coordination").state is (
        CognitiveCycleNodeState.NOT_RECORDED
    )


def test_m386_12_unified_brain_records_exactly_six_real_nodes() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("contenido privado")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("conversation_ingress").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    coordination = cycle.node("unified_coordination")
    assert coordination.state is CognitiveCycleNodeState.PARTICIPATED
    assert coordination.evidence_codes == ("unified_brain:delegated",)
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 6
    assert cycle.count(CognitiveCycleNodeState.OMITTED) == 3
    assert cycle.node("cognitive_state").state is CognitiveCycleNodeState.OMITTED
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 9
    assert cycle.node("relational_affective_context").state is (
        CognitiveCycleNodeState.OMITTED
    )


def test_m386_12_coordinated_cycle_remains_partial() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.outcome is CognitiveCycleOutcome.PARTIAL


def test_m386_12_runtime_failure_preserves_two_pre_runtime_facts() -> None:
    gateway = OfficialConversationGateway(RuntimeStub(RuntimeError("failure")))
    brain = UnifiedBrain(gateway)
    with pytest.raises(RuntimeError, match="failure"):
        brain.process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 3
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 14
    assert cycle.node("cognitive_state").state is CognitiveCycleNodeState.OMITTED
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_m386_12_coordination_scope_is_closed_after_success() -> None:
    adapter = UnifiedCoordinationEvidenceAdapter()
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("mensaje")
    assert adapter.current_record() is None
    gateway.submit("mensaje directo")
    latest = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert latest is not None
    assert latest.node("unified_coordination").state is (
        CognitiveCycleNodeState.NOT_RECORDED
    )


def test_m386_12_coordination_scope_is_closed_after_failure() -> None:
    adapter = UnifiedCoordinationEvidenceAdapter()
    brain = UnifiedBrain(
        OfficialConversationGateway(RuntimeStub(RuntimeError("failure")))
    )
    with pytest.raises(RuntimeError):
        brain.process("mensaje")
    assert adapter.current_record() is None


def test_m386_12_adapter_is_inactive_by_default() -> None:
    adapter = UnifiedCoordinationEvidenceAdapter()
    assert adapter.current_record() is None


def test_m386_12_adapter_emits_only_safe_technical_metadata() -> None:
    adapter = UnifiedCoordinationEvidenceAdapter()
    with adapter.activate():
        record = adapter.current_record()
    assert record is not None
    assert record.node_id == "unified_coordination"
    assert record.evidence_codes == ("unified_brain:delegated",)
    assert record.reason_codes == ()


def test_m386_12_nested_coordination_scopes_restore_correctly() -> None:
    adapter = UnifiedCoordinationEvidenceAdapter()
    with adapter.activate():
        assert adapter.current_record() is not None
        with adapter.activate():
            assert adapter.current_record() is not None
        assert adapter.current_record() is not None
    assert adapter.current_record() is None


def test_m386_12_legacy_gateway_compatibility_is_preserved() -> None:
    class LegacyGateway:
        def submit(self, message, *, origin, session_id, now):
            return Turn()

    result = UnifiedBrain(LegacyGateway()).process("mensaje")
    assert result is not None


def test_m386_12_adapter_has_no_domain_or_execution_authority() -> None:
    source = getsource(UnifiedCoordinationEvidenceAdapter)
    forbidden_calls = (
        "converse(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "respond(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_12_no_downstream_node_is_claimed() -> None:
    gateway = OfficialConversationGateway(RuntimeStub())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    for node_id in (
        "identity_and_context",
        "memory_recall",
        "intent_and_reasoning",
        "planning",
        "decision",
        "action_gate",
    ):
        assert cycle.node(node_id).state is CognitiveCycleNodeState.NOT_RECORDED
    learning = cycle.node("learning_candidate")
    assert learning.state is CognitiveCycleNodeState.OMITTED
    assert learning.reason_codes == ("learning_candidate:none_proposed",)
    assert cycle.node("unified_diagnostics").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
