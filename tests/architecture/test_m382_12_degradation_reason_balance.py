from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from app.unified_brain import DegradationReasonBalance, UnifiedBrain
from core.governed_operational_conversation_pipeline import (
    ConversationDegradationReason,
    ConversationResponsePath,
)


class Turn:
    status = "failed"
    session_id = "familia"
    response_path = ConversationResponsePath.DEGRADED
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False

    def __init__(self, reason: ConversationDegradationReason | str) -> None:
        self.degradation_reason = reason


class ConversationGatewayStub:
    def __init__(self, *reasons: ConversationDegradationReason | str) -> None:
        self._turns = [Turn(reason) for reason in reasons]

    def submit(self, text: str, **kwargs) -> Turn:
        return self._turns.pop(0)


def test_each_degradation_cause_is_counted_explicitly() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationDegradationReason.PIPELINE_DISABLED,
            ConversationDegradationReason.INPUT_LIMIT_EXCEEDED,
            ConversationDegradationReason.TURN_FAILED_SAFELY,
            ConversationDegradationReason.PROVIDER_RESPONSE_UNAVAILABLE,
            ConversationDegradationReason.UNKNOWN,
        )
    )

    for _ in range(5):
        brain.process("contenido privado")

    balance = brain.reflection_snapshot.degradation_reasons
    assert balance == DegradationReasonBalance(
        pipeline_disabled=1,
        input_limit_exceeded=1,
        turn_failed_safely=1,
        provider_response_unavailable=1,
        unknown=1,
    )


def test_reason_balance_matches_the_total_degraded_responses() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(
            ConversationDegradationReason.TURN_FAILED_SAFELY,
            ConversationDegradationReason.TURN_FAILED_SAFELY,
            ConversationDegradationReason.PROVIDER_RESPONSE_UNAVAILABLE,
        )
    )

    for _ in range(3):
        brain.process("mensaje")

    snapshot = brain.reflection_snapshot
    balance = snapshot.degradation_reasons
    assert sum(getattr(balance, item.name) for item in fields(balance)) == 3
    assert snapshot.degraded_responses == 3


@pytest.mark.parametrize(
    "legacy_reason",
    ("unexpected_legacy_reason", ConversationDegradationReason.NOT_APPLICABLE),
)
def test_invalid_legacy_reason_is_counted_as_unknown(legacy_reason: object) -> None:
    brain = UnifiedBrain(ConversationGatewayStub(legacy_reason))

    brain.process("mensaje histórico")

    assert brain.reflection_snapshot.degradation_reasons.unknown == 1


def test_reason_balance_is_immutable_and_contains_no_message_content() -> None:
    brain = UnifiedBrain(
        ConversationGatewayStub(ConversationDegradationReason.PIPELINE_DISABLED)
    )
    brain.process("dato familiar reservado")
    balance = brain.reflection_snapshot.degradation_reasons

    assert "dato familiar reservado" not in repr(balance)
    with pytest.raises(FrozenInstanceError):
        balance.pipeline_disabled = 99


def test_reason_balance_has_no_operational_authority() -> None:
    source = getsource(DegradationReasonBalance)

    for method in ("alert", "decide", "execute", "persist", "remember", "retry"):
        assert f"def {method}" not in source
