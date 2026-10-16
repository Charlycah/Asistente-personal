from __future__ import annotations

from dataclasses import FrozenInstanceError
from inspect import getsource

import pytest

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


def test_consecutive_degraded_responses_are_observed_factually() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.DEGRADED,
        )
    )

    brain.process("primer mensaje privado")
    assert brain.reflection_snapshot.consecutive_degraded_responses == 1

    brain.process("segundo mensaje privado")
    snapshot = brain.reflection_snapshot
    assert snapshot.consecutive_degraded_responses == 2
    assert snapshot.degraded_responses == 2
    assert snapshot.observed_turns == 2


@pytest.mark.parametrize(
    "recovery_path",
    (
        ConversationResponsePath.PROVIDER,
        ConversationResponsePath.INTERCEPTOR,
    ),
)
def test_non_degraded_response_resets_the_signal(
    recovery_path: ConversationResponsePath,
) -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.DEGRADED,
            recovery_path,
        )
    )

    for _ in range(3):
        brain.process("mensaje")

    snapshot = brain.reflection_snapshot
    assert snapshot.consecutive_degraded_responses == 0
    assert snapshot.degraded_responses == 2
    assert snapshot.observed_turns == 3


def test_degradation_signal_is_immutable_and_contains_no_message() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(ConversationResponsePath.DEGRADED)
    )
    brain.process("contenido familiar reservado")
    snapshot = brain.reflection_snapshot

    assert "contenido familiar reservado" not in repr(snapshot)
    with pytest.raises(FrozenInstanceError):
        snapshot.consecutive_degraded_responses = 99


def test_degradation_signal_has_no_policy_or_operational_authority() -> None:
    source = getsource(PostTurnReflectionObserver)
    forbidden_calls = (
        "alert(",
        "decide(",
        "execute(",
        "persist(",
        "remember(",
        "retry(",
    )

    assert all(call not in source for call in forbidden_calls)
