from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from core.cognitive_state_contract import CognitiveState, CognitiveStateReader

NOW = datetime(2026, 7, 28, 12, 0, tzinfo=timezone.utc)


def test_contract_exposes_the_minimal_cognitive_state():
    state = CognitiveState(
        active_objective="Answer the user",
        current_focus="Cognitive state contract",
        confidence=0.85,
        last_decision="Keep the module isolated",
        updated_at=NOW,
    )

    assert state.active_objective == "Answer the user"
    assert state.current_focus == "Cognitive state contract"
    assert state.confidence == 0.85
    assert state.last_decision == "Keep the module isolated"
    assert state.updated_at == NOW
    assert not state.is_empty


def test_contract_is_immutable():
    state = CognitiveState.empty(updated_at=NOW)

    with pytest.raises(FrozenInstanceError):
        state.confidence = 1.0


def test_empty_state_is_explicit_and_neutral():
    state = CognitiveState.empty(updated_at=NOW)

    assert state.active_objective is None
    assert state.current_focus is None
    assert state.last_decision is None
    assert state.confidence == 0.0
    assert state.is_empty


def test_contract_normalizes_non_blank_text():
    state = CognitiveState(
        active_objective="  Answer safely  ",
        current_focus="  Current request  ",
        confidence=0.5,
        last_decision="  Do not execute  ",
        updated_at=NOW,
    )

    assert state.active_objective == "Answer safely"
    assert state.current_focus == "Current request"
    assert state.last_decision == "Do not execute"


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_contract_rejects_invalid_confidence(confidence):
    with pytest.raises(ValueError, match="confidence"):
        CognitiveState(
            active_objective=None,
            current_focus=None,
            confidence=confidence,
            last_decision=None,
            updated_at=NOW,
        )


def test_contract_requires_timezone_aware_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        CognitiveState.empty(updated_at=datetime(2026, 7, 28, 12, 0))


@pytest.mark.parametrize(
    "field_name",
    ["active_objective", "current_focus", "last_decision"],
)
def test_contract_rejects_blank_optional_text(field_name):
    values = {
        "active_objective": None,
        "current_focus": None,
        "confidence": 0.0,
        "last_decision": None,
        "updated_at": NOW,
    }
    values[field_name] = "   "

    with pytest.raises(ValueError, match=field_name):
        CognitiveState(**values)


def test_reader_protocol_is_runtime_checkable():
    class FixedReader:
        def snapshot(self):
            return CognitiveState.empty(updated_at=NOW)

    assert isinstance(FixedReader(), CognitiveStateReader)
