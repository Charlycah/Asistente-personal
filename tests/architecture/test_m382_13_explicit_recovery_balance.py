from __future__ import annotations

from dataclasses import FrozenInstanceError
from inspect import getsource

import pytest

from app.unified_brain import RecoveryBalance, UnifiedBrain
from core.governed_operational_conversation_pipeline import (
    ConversationDegradationReason,
    ConversationResponsePath,
)


class Turn:
    status = "completed"
    session_id = "familia"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False

    def __init__(self, path: ConversationResponsePath | str) -> None:
        self.response_path = path
        self.degradation_reason = (
            ConversationDegradationReason.PROVIDER_RESPONSE_UNAVAILABLE
            if path is ConversationResponsePath.DEGRADED
            else ConversationDegradationReason.NOT_APPLICABLE
        )


class ConversationGatewayStub:
    def __init__(self, *paths: ConversationResponsePath | str) -> None:
        self._turns = [Turn(path) for path in paths]

    def submit(self, text: str, **kwargs) -> Turn:
        return self._turns.pop(0)


@pytest.mark.parametrize(
    ("recovery_path", "expected"),
    (
        (
            ConversationResponsePath.PROVIDER,
            RecoveryBalance(provider_recoveries=1, interceptor_recoveries=0),
        ),
        (
            ConversationResponsePath.INTERCEPTOR,
            RecoveryBalance(provider_recoveries=0, interceptor_recoveries=1),
        ),
    ),
)
def test_recovery_is_counted_after_a_degraded_sequence(
    recovery_path: ConversationResponsePath,
    expected: RecoveryBalance,
) -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.DEGRADED,
            recovery_path,
        )
    )

    for _ in range(3):
        brain.process("contenido privado")

    assert brain.reflection_snapshot.recoveries == expected
    assert brain.reflection_snapshot.consecutive_degraded_responses == 0


def test_normal_responses_without_prior_degradation_are_not_recoveries() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.PROVIDER,
            ConversationResponsePath.INTERCEPTOR,
            ConversationResponsePath.PROVIDER,
        )
    )

    for _ in range(3):
        brain.process("mensaje")

    assert brain.reflection_snapshot.recoveries == RecoveryBalance(0, 0)


def test_only_first_normal_response_closes_a_degraded_sequence() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.PROVIDER,
            ConversationResponsePath.PROVIDER,
        )
    )

    for _ in range(3):
        brain.process("mensaje")

    assert brain.reflection_snapshot.recoveries.provider_recoveries == 1


def test_recovery_balance_is_immutable_and_contains_no_message() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationResponsePath.DEGRADED,
            ConversationResponsePath.INTERCEPTOR,
        )
    )
    brain.process("dato familiar reservado")
    brain.process("segundo dato reservado")
    recoveries = brain.reflection_snapshot.recoveries

    assert "dato familiar reservado" not in repr(recoveries)
    assert "segundo dato reservado" not in repr(recoveries)
    with pytest.raises(FrozenInstanceError):
        recoveries.interceptor_recoveries = 99


def test_recovery_balance_has_no_operational_authority() -> None:
    source = getsource(RecoveryBalance)

    for method in ("alert", "decide", "execute", "persist", "remember", "retry"):
        assert f"def {method}" not in source
