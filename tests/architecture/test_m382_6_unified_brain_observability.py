from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)
from app.unified_brain import UnifiedBrain


class Turn:
    response_text = "respuesta"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class ConversationRuntimeStub:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error

    def converse(self, text: str) -> Turn:
        if self.error is not None:
            raise self.error
        return Turn()


def _brain(runtime=None) -> UnifiedBrain:
    conversation = OfficialConversationGateway(runtime or ConversationRuntimeStub())
    return UnifiedBrain(conversation)


def test_brain_observability_starts_empty_and_uses_gateway_state() -> None:
    brain = _brain()

    assert brain.snapshot.processed_messages == 0
    assert brain.snapshot.last_origin is None
    assert brain.snapshot.last_session_id is None

    brain.process(
        "mensaje",
        origin=ConversationOrigin.DESKTOP_TEXT,
        session_id="familia",
    )

    assert brain.snapshot.processed_messages == 1
    assert brain.snapshot.last_origin is ConversationOrigin.DESKTOP_TEXT
    assert brain.snapshot.last_session_id == "familia"
    assert (
        brain.snapshot.processed_messages
        == brain.conversation.snapshot.submitted_turns
    )


def test_failed_gateway_submission_is_not_reported_as_processed() -> None:
    brain = _brain(ConversationRuntimeStub(RuntimeError("gateway failed")))

    with pytest.raises(RuntimeError):
        brain.process("mensaje")

    assert brain.snapshot.processed_messages == 0
    assert brain.snapshot.last_origin is None
    assert brain.snapshot.last_session_id is None


def test_brain_snapshot_is_immutable_and_contains_no_message_content() -> None:
    brain = _brain()
    brain.process("contenido privado")
    snapshot = brain.snapshot

    assert {item.name for item in fields(snapshot)} == {
        "processed_messages",
        "last_origin",
        "last_session_id",
    }
    assert "contenido privado" not in repr(snapshot)
    with pytest.raises(FrozenInstanceError):
        snapshot.processed_messages = 99


def test_observability_does_not_add_memory_decision_or_execution_calls() -> None:
    source = getsource(UnifiedBrain.snapshot.fget)

    forbidden_calls = (
        "remember(",
        "recall(",
        "decide(",
        "execute(",
        "intercept(",
    )

    assert all(call not in source for call in forbidden_calls)
