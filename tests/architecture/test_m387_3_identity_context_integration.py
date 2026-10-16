from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CanonicalInterlocutorResolver,
    ControlledConversationalIdentificationFlow,
    IdentityContextAccessDecision,
    IdentityContextAccessGate,
)
from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
)
from core.runtime_composition_root import GovernedRuntimePreparation


def _resolved(session_id: str = "main"):
    result = ControlledConversationalIdentificationFlow().process(
        "Confirmo que soy Carlos",
        session_id=session_id,
    )
    assert result.resolution is not None
    return result.resolution


class Turn:
    response_text = "respuesta normal"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False
    response_path = "interceptor"
    degradation_reason = "not_applicable"


class RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def __init__(self) -> None:
        self.access_decisions = []

    def converse(self, text: str) -> Turn:
        self.access_decisions.append(IdentityContextAccessGate.current())
        return Turn()


def test_m387_3_direct_internal_runtime_keeps_compatibility() -> None:
    decision = IdentityContextAccessGate.current()
    assert decision.governed_entry is False
    assert decision.shared_conversation_context_allowed is True
    assert decision.private_context_allowed is True
    assert decision.reason_code == "identity_context:unmanaged_compatibility"


def test_m387_3_resolved_matching_session_allows_private_context() -> None:
    with IdentityContextAccessGate.activate(
        _resolved(),
        session_id="main",
    ) as decision:
        assert decision.governed_entry is True
        assert decision.identity_resolved is True
        assert decision.session_scoped is True
        assert decision.shared_conversation_context_allowed is True
        assert decision.private_context_allowed is True


def test_m387_3_unknown_identity_closes_private_context() -> None:
    unknown = CanonicalInterlocutorResolver().unresolved("main")
    with IdentityContextAccessGate.activate(
        unknown,
        session_id="main",
    ) as decision:
        assert decision.identity_resolved is False
        assert decision.shared_conversation_context_allowed is True
        assert decision.private_context_allowed is False
        assert decision.reason_code == "identity_context:identity_not_resolved"
        assert decision.shared_conversation_reason_code == (
            "identity_context:shared_conversation_allowed"
        )


def test_m387_3_session_mismatch_closes_private_context() -> None:
    with IdentityContextAccessGate.activate(
        _resolved("session-one"),
        session_id="session-one",
        context_session_id="session-two",
    ) as decision:
        assert decision.identity_resolved is True
        assert decision.session_scoped is False
        assert decision.shared_conversation_context_allowed is False
        assert decision.private_context_allowed is False
        assert decision.reason_code == "identity_context:session_mismatch"
        assert decision.shared_conversation_reason_code == (
            "identity_context:shared_conversation_session_mismatch"
        )


def test_m387_3_access_context_is_nested_and_ephemeral() -> None:
    initial = IdentityContextAccessGate.current()
    unknown = CanonicalInterlocutorResolver().unresolved("main")
    with IdentityContextAccessGate.activate(unknown, session_id="main"):
        assert IdentityContextAccessGate.current().private_context_allowed is False
        with IdentityContextAccessGate.activate(_resolved(), session_id="main"):
            assert IdentityContextAccessGate.current().private_context_allowed is True
        assert IdentityContextAccessGate.current().private_context_allowed is False
    assert IdentityContextAccessGate.current() is initial


def test_m387_3_official_entry_denies_unidentified_normal_turn() -> None:
    runtime = RuntimeStub()
    UnifiedBrain(OfficialConversationGateway(runtime)).process(
        "mensaje normal",
        session_id="main",
    )
    assert len(runtime.access_decisions) == 1
    assert runtime.access_decisions[0].private_context_allowed is False


def test_m387_3_confirmed_identity_reaches_following_normal_turn() -> None:
    runtime = RuntimeStub()
    brain = UnifiedBrain(OfficialConversationGateway(runtime))
    brain.process("Confirmo que soy Cristina", session_id="main")
    brain.process("mensaje normal", session_id="main")
    assert len(runtime.access_decisions) == 1
    decision = runtime.access_decisions[0]
    assert decision.identity_resolved is True
    assert decision.private_context_allowed is True


def test_m387_3_recent_history_is_available_for_unresolved_matching_session() -> None:
    runtime = object.__new__(EndToEndLocalConversation)
    runtime.config = EndToEndLocalConversationConfig()
    runtime.bootstrap = type(
        "Bootstrap",
        (),
        {"config": type("Config", (), {"owner": "x", "session_id": "main"})()},
    )()
    runtime.journal = type(
        "Journal",
        (),
        {"list_for_session": lambda self, owner, session_id: (_turn_with_text(),)},
    )()
    unknown = CanonicalInterlocutorResolver().unresolved("main")
    with IdentityContextAccessGate.activate(unknown, session_id="main") as decision:
        assert decision.shared_conversation_context_allowed is True
        assert decision.private_context_allowed is False
        recent = runtime._recent_context()
    assert len(recent) == 1
    assert recent[0].user_text == "dato compartido"
    assert recent[0].assistant_text == "respuesta"


def test_m387_3_recent_history_is_closed_for_session_mismatch() -> None:
    runtime = object.__new__(EndToEndLocalConversation)
    runtime.config = EndToEndLocalConversationConfig()
    runtime.bootstrap = type(
        "Bootstrap",
        (),
        {"config": type("Config", (), {"owner": "x", "session_id": "main"})()},
    )()
    runtime.journal = type(
        "Journal",
        (),
        {"list_for_session": lambda self, owner, session_id: (_turn_with_text(),)},
    )()
    unknown = CanonicalInterlocutorResolver().unresolved("main")
    with IdentityContextAccessGate.activate(
        unknown,
        session_id="main",
        context_session_id="other",
    ):
        assert runtime._recent_context() == ()


def _turn_with_text():
    return type(
        "StoredTurn",
        (),
        {"user_text": "dato compartido", "response_text": "respuesta"},
    )()


def test_m387_3_memory_recall_and_learning_use_the_same_gate() -> None:
    preparation = getsource(GovernedRuntimePreparation.prepare)
    conversation = getsource(EndToEndLocalConversation.converse)
    assert "IdentityContextAccessGate.current().private_context_allowed" in (
        preparation
    )
    assert "memory_runtime.enrich" in preparation
    assert "IdentityContextAccessGate.current().private_context_allowed" in (
        conversation
    )
    assert "memory_runtime.record" in conversation
    recent_context = getsource(EndToEndLocalConversation._recent_context)
    assert "shared_conversation_context_allowed" in recent_context
    assert "private_context_allowed" not in recent_context


def test_m387_3_split_decision_preserves_private_boundary() -> None:
    unknown = CanonicalInterlocutorResolver().unresolved("main")
    decision = IdentityContextAccessGate.decide(unknown, session_id="main")

    assert decision.session_scoped is True
    assert decision.shared_conversation_context_allowed is True
    assert decision.private_context_allowed is False


def test_m387_3_access_decision_contains_no_identity_or_content() -> None:
    names = {item.name for item in fields(IdentityContextAccessDecision)}
    forbidden = {
        "message",
        "response",
        "owner",
        "speaker",
        "interlocutor",
        "session_id",
        "memory",
    }
    assert names.isdisjoint(forbidden)
    decision = IdentityContextAccessGate.decide(_resolved(), session_id="main")
    assert "Carlos" not in repr(decision)
    assert "Cristina" not in repr(decision)


def test_m387_3_access_decision_is_immutable_and_non_authoritative() -> None:
    decision = IdentityContextAccessGate.decide(_resolved(), session_id="main")
    assert decision.equal_coowner_authority is True
    assert decision.grants_action_authority is False
    assert decision.inferred_identity_used is False
    assert decision.persisted is False
    with pytest.raises(FrozenInstanceError):
        decision.private_context_allowed = False


def test_m387_3_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
