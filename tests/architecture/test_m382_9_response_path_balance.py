from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.official_conversation_gateway import ConversationOrigin
from app.unified_brain import PostTurnReflectionObserver, UnifiedBrain
from core.governed_operational_conversation_pipeline import ConversationResponsePath


class Turn:
    status = "completed"
    session_id = "familia"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False

    def __init__(self, response_path: ConversationResponsePath) -> None:
        self.response_path = response_path


class ConversationGatewayStub:
    def __init__(self, *paths: ConversationResponsePath) -> None:
        self._turns = [Turn(path) for path in paths]

    def submit(self, text: str, **kwargs) -> Turn:
        return self._turns.pop(0)


def test_response_paths_are_counted_after_successful_turns() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.PROVIDER,
            ConversationResponsePath.INTERCEPTOR,
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.PROVIDER,
        )
    )

    for _ in range(4):
        brain.process("contenido privado", origin=ConversationOrigin.DESKTOP_TEXT)

    snapshot = brain.reflection_snapshot
    assert snapshot.observed_turns == 4
    assert snapshot.provider_responses == 2
    assert snapshot.interceptor_responses == 1
    assert snapshot.degraded_responses == 1
    assert (
        snapshot.provider_responses
        + snapshot.interceptor_responses
        + snapshot.degraded_responses
        == snapshot.observed_turns
    )


def test_response_balance_is_immutable_and_contains_no_message_content() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(ConversationResponsePath.DEGRADED)
    )
    brain.process("información familiar privada")
    snapshot = brain.reflection_snapshot

    assert {item.name for item in fields(snapshot)} == {
        "observed_turns",
        "provider_responses",
        "interceptor_responses",
        "degraded_responses",
        "consecutive_degraded_responses",
        "degradation_reasons",
        "recoveries",
        "last_reflection",
    }
    assert "información familiar privada" not in repr(snapshot)
    with pytest.raises(FrozenInstanceError):
        snapshot.degraded_responses = 99


def test_each_observer_owns_only_its_ephemeral_balance() -> None:
    first = PostTurnReflectionObserver()
    second = PostTurnReflectionObserver()
    turn = Turn(ConversationResponsePath.INTERCEPTOR)

    first.observe(
        turn,
        origin=ConversationOrigin.INTERNAL,
        session_id=None,
    )

    assert first.snapshot.interceptor_responses == 1
    assert second.snapshot.observed_turns == 0
    assert second.snapshot.interceptor_responses == 0


def test_balance_adds_no_memory_decision_persistence_or_execution() -> None:
    source = getsource(PostTurnReflectionObserver)
    forbidden_calls = (
        "remember(",
        "recall(",
        "decide(",
        "execute(",
        "persist(",
        "intercept(",
    )

    assert all(call not in source for call in forbidden_calls)
