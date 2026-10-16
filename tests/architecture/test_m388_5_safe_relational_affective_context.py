from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    RelationalAffectiveEvidenceAdapter,
)


def _relationship(*, has_context=True):
    return SimpleNamespace(
        has_context=has_context,
        private_content="never copy this",
    )


def _profile(**changes):
    values = {
        "identity_changed": False,
        "creates_parallel_brain": False,
        "delivery_tone": "warm",
        "private_rationale": "never copy this",
    }
    values.update(changes)
    return SimpleNamespace(**values)


def _capture(*, resolved=True, relationship=None, profile=None):
    records = []
    adapter = RelationalAffectiveEvidenceAdapter()
    with adapter.capture(records.append):
        result = adapter.observe_context(
            interlocutor_resolved=resolved,
            relationship_snapshot=relationship,
            personality_profile=profile,
        )
    return records[0], result


def test_m388_5_complete_context_participates_as_simulation() -> None:
    record, result = _capture(
        relationship=_relationship(),
        profile=_profile(),
    )
    assert result is record
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert record.evidence_codes == (
        "relationship:snapshot_read",
        "relationship:confirmed_context",
        "affect:explicitly_simulated",
        "expression:profile_available",
    )


def test_m388_5_empty_relationship_snapshot_does_not_invent_context() -> None:
    record, _ = _capture(
        relationship=_relationship(has_context=False),
        profile=_profile(),
    )
    assert "relationship:no_confirmed_context" in record.evidence_codes
    assert "relationship:confirmed_context" not in record.evidence_codes


def test_m388_5_relationship_without_simulation_is_degraded() -> None:
    record, _ = _capture(relationship=_relationship())
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == (
        "relational_affective:simulation_unavailable",
    )


def test_m388_5_simulation_without_relationship_is_degraded() -> None:
    record, _ = _capture(profile=_profile())
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == (
        "relational_affective:relationship_unavailable",
    )


def test_m388_5_missing_authorities_are_explicitly_omitted() -> None:
    record, _ = _capture()
    assert record.state is CognitiveCycleNodeState.OMITTED
    assert record.reason_codes == (
        "relational_affective:authorities_unavailable",
    )


def test_m388_5_unresolved_interlocutor_omits_personalization() -> None:
    record, _ = _capture(
        resolved=False,
        relationship=_relationship(),
        profile=_profile(),
    )
    assert record.state is CognitiveCycleNodeState.OMITTED
    assert record.reason_codes == (
        "relational_affective:interlocutor_unresolved",
    )


def test_m388_5_identity_mutation_or_parallel_brain_is_blocked() -> None:
    for profile in (
        _profile(identity_changed=True),
        _profile(creates_parallel_brain=True),
    ):
        record, _ = _capture(relationship=_relationship(), profile=profile)
        assert record.state is CognitiveCycleNodeState.BLOCKED
        assert record.reason_codes == (
            "relational_affective:integrity_violation",
        )


def test_m388_5_evidence_contains_no_private_relational_content() -> None:
    record, _ = _capture(
        relationship=_relationship(),
        profile=_profile(),
    )
    assert "never copy this" not in repr(record)
    assert "warm" not in repr(record)


def test_m388_5_inactive_adapter_has_no_side_effect() -> None:
    result = RelationalAffectiveEvidenceAdapter().observe_context(
        interlocutor_resolved=True,
        relationship_snapshot=_relationship(),
        personality_profile=_profile(),
    )
    assert result is None


def test_m388_5_gateway_reads_existing_runtime_context() -> None:
    class Turn:
        response_text = "response"
        response_path = "provider"
        status = "completed"
        session_id = "session"

    class Runtime:
        relationship_memory = SimpleNamespace(last_snapshot=_relationship())
        adaptive_personality_profile = _profile()

        def converse(self, text, now=None):
            return Turn()

    gateway = OfficialConversationGateway(Runtime())
    gateway.submit("Confirmo que soy Carlos", session_id="main")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle.node("relational_affective_context").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_m388_5_adapter_has_no_memory_or_decision_authority() -> None:
    source = getsource(RelationalAffectiveEvidenceAdapter)
    forbidden = (
        "observe_turn(",
        "adapt(",
        "decide(",
        "store(",
        "persist(",
        "diagnos",
    )
    assert all(item not in source for item in forbidden)


def test_m388_5_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
