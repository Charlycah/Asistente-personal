from __future__ import annotations

from datetime import datetime, timezone
from inspect import getsource

import pytest

from app.canonical_cognitive_state_facade import CanonicalCognitiveStateFacade
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    CognitiveStateEvidenceAdapter,
)
from core.cognitive_state_contract import CognitiveState


class StateAuthority:
    def __init__(self, state: CognitiveState) -> None:
        self.state = state

    def snapshot(self) -> CognitiveState:
        return self.state

    def update(self, changes):
        return self.state

    def reset(self):
        return self.state


def _state(**changes) -> CognitiveState:
    values = {
        "active_objective": None,
        "current_focus": None,
        "confidence": 0.0,
        "last_decision": None,
        "updated_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(changes)
    return CognitiveState(**values)


def _capture(facade):
    records = []
    adapter = CognitiveStateEvidenceAdapter()
    with adapter.capture(records.append):
        result = adapter.observe_facade(facade)
    return records[0], result


def test_m388_4_bound_empty_state_participates_without_invention() -> None:
    facade = CanonicalCognitiveStateFacade(StateAuthority(_state()))
    record, result = _capture(facade)
    assert result is record
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert record.evidence_codes == (
        "cognitive_state:snapshot_read",
        "cognitive_state:empty",
    )


def test_m388_4_objective_presence_is_redacted() -> None:
    facade = CanonicalCognitiveStateFacade(
        StateAuthority(_state(active_objective="private objective"))
    )
    record, _ = _capture(facade)
    assert "cognitive_state:objective_present" in record.evidence_codes
    assert "private objective" not in repr(record)


def test_m388_4_focus_presence_is_redacted() -> None:
    facade = CanonicalCognitiveStateFacade(
        StateAuthority(_state(current_focus="private focus"))
    )
    record, _ = _capture(facade)
    assert "cognitive_state:focus_present" in record.evidence_codes
    assert "private focus" not in repr(record)


def test_m388_4_decision_and_confidence_are_metadata_only() -> None:
    facade = CanonicalCognitiveStateFacade(
        StateAuthority(_state(last_decision="private decision", confidence=0.8))
    )
    record, _ = _capture(facade)
    assert "cognitive_state:last_decision_present" in record.evidence_codes
    assert "cognitive_state:confidence_available" in record.evidence_codes
    assert "private decision" not in repr(record)


def test_m388_4_unbound_facade_is_omitted_explicitly() -> None:
    record, _ = _capture(CanonicalCognitiveStateFacade())
    assert record.state is CognitiveCycleNodeState.OMITTED
    assert record.reason_codes == ("cognitive_state:authority_unavailable",)


def test_m388_4_snapshot_failure_degrades_without_fabrication() -> None:
    class BrokenAuthority(StateAuthority):
        def snapshot(self):
            raise RuntimeError("unavailable")

    facade = CanonicalCognitiveStateFacade(BrokenAuthority(_state()))
    record, _ = _capture(facade)
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == ("cognitive_state:snapshot_unavailable",)


def test_m388_4_inactive_adapter_has_no_side_effect() -> None:
    facade = CanonicalCognitiveStateFacade(StateAuthority(_state()))
    assert CognitiveStateEvidenceAdapter().observe_facade(facade) is None


def test_m388_4_facade_can_bind_one_real_authority_once() -> None:
    facade = CanonicalCognitiveStateFacade()
    facade.bind(StateAuthority(_state()))
    assert facade.bound is True
    with pytest.raises(RuntimeError):
        facade.bind(StateAuthority(_state()))


def test_m388_4_invalid_authority_cannot_be_bound() -> None:
    facade = CanonicalCognitiveStateFacade()
    with pytest.raises(TypeError):
        facade.bind(object())


def test_m388_4_gateway_uses_runtime_authority_productively() -> None:
    class Turn:
        response_text = "response"
        response_path = "provider"
        status = "completed"
        session_id = "session"

    class Runtime:
        cognitive_state_authority = StateAuthority(_state(current_focus="turn"))

        def converse(self, text, now=None):
            return Turn()

    gateway = OfficialConversationGateway(Runtime())
    gateway.submit("Confirmo que soy Carlos", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle.node("cognitive_state").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_m388_4_adapter_has_no_update_or_storage_authority() -> None:
    source = getsource(CognitiveStateEvidenceAdapter)
    forbidden = (
        "facade.update(",
        "facade.reset(",
        "persist(",
        "store(",
        "open(",
    )
    assert all(item not in source for item in forbidden)


def test_m388_4_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
