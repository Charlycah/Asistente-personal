from __future__ import annotations

from types import SimpleNamespace

from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    IdentityContextEvidenceAdapter,
    ReflectionLearningEvidenceAdapter,
    TextPerceptionEvidenceAdapter,
)


def _capture(adapter, call):
    records = []
    with adapter.capture(records.append):
        call(adapter)
    return {item.node_id: item for item in records}


def test_m388_5_5_unresolved_identity_degrades_explicitly() -> None:
    records = _capture(
        IdentityContextEvidenceAdapter(),
        lambda adapter: adapter.observe_resolution(
            coownership_scoped=True,
            session_scoped=True,
            context_bounded=True,
            interlocutor_resolved=False,
        ),
    )
    node = records["identity_and_context"]
    assert node.state is CognitiveCycleNodeState.DEGRADED
    assert node.reason_codes


def test_m388_5_5_absent_learning_candidate_is_explicitly_omitted() -> None:
    records = _capture(
        ReflectionLearningEvidenceAdapter(),
        lambda adapter: adapter.observe_learning_candidate(None),
    )
    node = records["learning_candidate"]
    assert node.state is CognitiveCycleNodeState.OMITTED
    assert node.reason_codes == ("learning_candidate:none_proposed",)


def test_m388_5_5_missing_reflection_is_explicitly_omitted() -> None:
    records = _capture(
        ReflectionLearningEvidenceAdapter(),
        lambda adapter: adapter.observe_reflection(None),
    )
    assert records["post_turn_reflection"].state is CognitiveCycleNodeState.OMITTED


def test_m388_5_5_text_perception_does_not_claim_unavailable_channels() -> None:
    adapter = TextPerceptionEvidenceAdapter()
    record = adapter.observe_input(
        text="mensaje", origin=SimpleNamespace(value="internal")
    )
    representation = repr(record).casefold()
    assert "camera" not in representation
    assert "microphone" not in representation
    assert "sensor" not in representation
