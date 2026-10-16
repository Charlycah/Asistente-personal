from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from app.cognitive_operational_inventory import (
    COGNITIVE_CAPABILITY_INVENTORY,
    CognitiveAuthority,
    CognitiveCapabilityState,
    CognitiveOperationalObserver,
)
from app.official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)


class ConversationStub:
    def __init__(self, *, error: BaseException | None = None) -> None:
        self.bootstrap = object()
        self.history = ()
        self.traces = ()
        self.error = error

    def converse(self, text: str, *, now=None):
        if self.error is not None:
            raise self.error
        return SimpleNamespace(session_id="session-1", response=f"echo:{text}")


def test_inventory_declares_one_canonical_authority_per_operational_boundary():
    keys = [record.key for record in COGNITIVE_CAPABILITY_INVENTORY]

    assert len(keys) == len(set(keys))
    assert any(
        record.authority is CognitiveAuthority.DECISION and record.canonical
        for record in COGNITIVE_CAPABILITY_INVENTORY
    )
    assert any(
        record.state is CognitiveCapabilityState.SHADOW
        for record in COGNITIVE_CAPABILITY_INVENTORY
    )


def test_observer_is_deterministic_and_does_not_change_turn_result():
    gateway = OfficialConversationGateway(ConversationStub())
    now = datetime(2026, 7, 28, 20, 0, tzinfo=timezone.utc)

    result = gateway.submit(
        "hola",
        origin=ConversationOrigin.CONSOLE,
        session_id="requested-session",
        now=now,
    )

    assert result.response == "echo:hola"
    snapshot = gateway.cognitive_inventory
    assert snapshot.schema_version == "m342.1"
    assert len(snapshot.turns) == 1
    trace = snapshot.turns[0]
    assert trace.turn_id == "turn-000001"
    assert trace.completed is True
    assert trace.session_id == "requested-session"
    assert [event.stage for event in trace.events] == ["entry", "response"]


def test_observer_records_error_and_preserves_original_exception():
    expected = RuntimeError("boom")
    gateway = OfficialConversationGateway(ConversationStub(error=expected))

    with pytest.raises(RuntimeError, match="boom") as captured:
        gateway.submit("fallar", origin=ConversationOrigin.INTERNAL)

    assert captured.value is expected
    trace = gateway.cognitive_inventory.turns[0]
    assert trace.completed is False
    assert trace.events[-1].stage == "error"
    assert trace.events[-1].detail == "RuntimeError"


def test_observer_bounds_history_without_persistence_or_side_effects():
    observer = CognitiveOperationalObserver(max_turns=2)
    now = datetime(2026, 7, 28, 20, 0, tzinfo=timezone.utc)

    for index in range(3):
        turn_id = observer.begin_turn(origin="internal", session_id=None, now=now)
        observer.complete_turn(turn_id, session_id=f"session-{index}")

    assert [trace.turn_id for trace in observer.snapshot.turns] == [
        "turn-000002",
        "turn-000003",
    ]
