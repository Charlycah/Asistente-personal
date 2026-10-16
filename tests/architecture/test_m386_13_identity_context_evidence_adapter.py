from __future__ import annotations

from inspect import getsource
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    IdentityContextEvidenceAdapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Turn:
    response_text = "respuesta"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class IdentityAwareRuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(
        self,
        *,
        joint: bool = True,
        interlocutor: bool = False,
        error: Exception | None = None,
    ) -> None:
        self.joint = joint
        self.interlocutor = interlocutor
        self.error = error

    def converse(self, text: str) -> Turn:
        IdentityContextEvidenceAdapter().observe_resolution(
            coownership_scoped=self.joint,
            session_scoped=True,
            context_bounded=True,
            interlocutor_resolved=self.interlocutor,
        )
        if self.error is not None:
            raise self.error
        return Turn()


def test_m386_13_current_realistic_resolution_is_degraded_not_complete() -> None:
    gateway = OfficialConversationGateway(IdentityAwareRuntimeStub())
    UnifiedBrain(gateway).process("contenido privado")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    identity = cycle.node("identity_and_context")
    assert identity.state is CognitiveCycleNodeState.DEGRADED
    assert identity.evidence_codes == (
        "identity_context:joint_coownership",
        "identity_context:session_scoped",
        "identity_context:bounded_history",
    )
    assert identity.reason_codes == ("interlocutor:not_resolved",)


def test_m386_13_degraded_identity_makes_the_cycle_degraded() -> None:
    gateway = OfficialConversationGateway(IdentityAwareRuntimeStub())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 6
    assert cycle.count(CognitiveCycleNodeState.DEGRADED) == 1
    assert cycle.count(CognitiveCycleNodeState.OMITTED) == 3
    assert cycle.node("cognitive_state").state is CognitiveCycleNodeState.OMITTED
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 8
    assert cycle.node("relational_affective_context").state is (
        CognitiveCycleNodeState.OMITTED
    )
    assert cycle.outcome is CognitiveCycleOutcome.DEGRADED


def test_m386_13_full_participation_requires_all_four_checks() -> None:
    gateway = OfficialConversationGateway(
        IdentityAwareRuntimeStub(interlocutor=True)
    )
    UnifiedBrain(gateway).process("mensaje")
    identity = gateway.target_cognitive_cycle_evidence.latest_cycle.node(
        "identity_and_context"
    )
    assert identity.state is CognitiveCycleNodeState.PARTICIPATED
    assert identity.reason_codes == ()


def test_m386_13_noncanonical_owner_is_an_explicit_additional_gap() -> None:
    gateway = OfficialConversationGateway(
        IdentityAwareRuntimeStub(joint=False)
    )
    UnifiedBrain(gateway).process("mensaje")
    identity = gateway.target_cognitive_cycle_evidence.latest_cycle.node(
        "identity_and_context"
    )
    assert identity.state is CognitiveCycleNodeState.DEGRADED
    assert identity.reason_codes == (
        "coownership:not_canonical",
        "interlocutor:not_resolved",
    )


def test_m386_13_runtime_failure_preserves_resolution_evidence() -> None:
    gateway = OfficialConversationGateway(
        IdentityAwareRuntimeStub(error=RuntimeError("failure"))
    )
    with pytest.raises(RuntimeError, match="failure"):
        UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("identity_and_context").state is (
        CognitiveCycleNodeState.DEGRADED
    )
    assert gateway.target_cognitive_cycle_evidence.active_cycle_ids == ()


def test_m386_13_absent_runtime_signal_does_not_invent_identity() -> None:
    class UnobservedRuntime:
        bootstrap = object()
        history = ()
        traces = ()

        def converse(self, text: str) -> Turn:
            return Turn()

    gateway = OfficialConversationGateway(UnobservedRuntime())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("identity_and_context").state is (
        CognitiveCycleNodeState.NOT_RECORDED
    )


def test_m386_13_adapter_is_inactive_outside_the_gateway_scope() -> None:
    adapter = IdentityContextEvidenceAdapter()
    record = adapter.observe_resolution(
        coownership_scoped=True,
        session_scoped=True,
        context_bounded=True,
        interlocutor_resolved=False,
    )
    assert record is None


def test_m386_13_capture_scope_closes_after_failure() -> None:
    adapter = IdentityContextEvidenceAdapter()

    def fail(record):
        raise RuntimeError(record.node_id)

    with pytest.raises(RuntimeError):
        with adapter.capture(fail):
            adapter.observe_resolution(
                coownership_scoped=True,
                session_scoped=True,
                context_bounded=True,
                interlocutor_resolved=False,
            )
    assert adapter.observe_resolution(
        coownership_scoped=True,
        session_scoped=True,
        context_bounded=True,
        interlocutor_resolved=False,
    ) is None


def test_m386_13_evidence_contains_no_identity_or_context_content() -> None:
    captured = []
    adapter = IdentityContextEvidenceAdapter()
    with adapter.capture(captured.append):
        adapter.observe_resolution(
            coownership_scoped=True,
            session_scoped=True,
            context_bounded=True,
            interlocutor_resolved=False,
        )
    representation = repr(captured[0])
    assert "Carlos" not in representation
    assert "Cristina" not in representation
    assert "runtime-session" not in representation
    assert "private-session" not in representation
    assert "contenido" not in representation


def test_m386_13_production_runtime_declares_unresolved_interlocutor() -> None:
    source = (
        PROJECT_ROOT / "core" / "end_to_end_local_conversation" / "runtime.py"
    ).read_text(encoding="utf-8")
    assert "IdentityContextEvidenceAdapter" in source
    assert "current_interlocutor_resolved()" in source
    assert 'request.owner.casefold() == "carlos y cristina"' in source


def test_m386_13_adapter_has_no_domain_or_execution_authority() -> None:
    source = getsource(IdentityContextEvidenceAdapter)
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


def test_m386_13_no_unrelated_downstream_node_is_claimed() -> None:
    gateway = OfficialConversationGateway(IdentityAwareRuntimeStub())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    for node_id in (
        "memory_recall",
        "knowledge_retrieval",
        "intent_and_reasoning",
        "planning",
        "decision",
        "action_gate",
    ):
        assert cycle.node(node_id).state is CognitiveCycleNodeState.NOT_RECORDED
    assert cycle.node("perception_and_evidence").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
