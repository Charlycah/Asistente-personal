from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    ReflectionLearningEvidenceAdapter,
)


def _capture(call):
    records = []
    adapter = ReflectionLearningEvidenceAdapter()
    with adapter.capture(records.append):
        result = call(adapter)
    return {record.node_id: record for record in records}, result


def test_m387_8_observed_reflection_participates() -> None:
    reflection = SimpleNamespace(response_path="provider")
    records, result = _capture(
        lambda adapter: adapter.observe_reflection(reflection)
    )
    assert result is records["post_turn_reflection"]
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes == ("post_turn_reflection:metadata_observed",)


def test_m387_8_degraded_response_is_explicitly_assessed() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_reflection(
            SimpleNamespace(response_path="degraded")
        )
    )
    assert records["post_turn_reflection"].evidence_codes == (
        "post_turn_reflection:metadata_observed",
        "post_turn_reflection:degradation_assessed",
    )


def test_m387_8_missing_reflection_is_omitted() -> None:
    records, _ = _capture(lambda adapter: adapter.observe_reflection(None))
    assert records["post_turn_reflection"].state is CognitiveCycleNodeState.OMITTED


def test_m387_8_review_only_learning_candidate_participates() -> None:
    candidate = SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=False,
        persistence_authorized=False,
    )
    records, _ = _capture(
        lambda adapter: adapter.observe_learning_candidate(candidate)
    )
    learning = records["learning_candidate"]
    assert learning.state is CognitiveCycleNodeState.PARTICIPATED
    assert learning.evidence_codes == ("learning_candidate:review_required",)


def test_m387_8_absent_learning_candidate_is_omitted() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_learning_candidate(None)
    )
    learning = records["learning_candidate"]
    assert learning.state is CognitiveCycleNodeState.OMITTED
    assert learning.reason_codes == ("learning_candidate:none_proposed",)


def test_m387_8_automatic_acceptance_is_blocked() -> None:
    candidate = SimpleNamespace(
        disposition="review_required",
        accepted_as_knowledge=True,
        persistence_authorized=True,
    )
    records, _ = _capture(
        lambda adapter: adapter.observe_learning_candidate(candidate)
    )
    learning = records["learning_candidate"]
    assert learning.state is CognitiveCycleNodeState.BLOCKED
    assert learning.reason_codes == ("learning_candidate:governance_violation",)


def test_m387_8_first_learning_fact_cannot_be_rewritten() -> None:
    def observe(adapter):
        first = adapter.observe_learning_candidate(None)
        second = adapter.observe_learning_candidate(
            SimpleNamespace(
                disposition="review_required",
                accepted_as_knowledge=False,
                persistence_authorized=False,
            )
        )
        return first, second

    records, results = _capture(observe)
    assert results[0] is records["learning_candidate"]
    assert results[1] is None
    assert records["learning_candidate"].state is CognitiveCycleNodeState.OMITTED


def test_m387_8_official_brain_closes_reflection_inside_the_turn() -> None:
    class Turn:
        response_text = "respuesta"
        response_path = "provider"
        status = "completed"
        session_id = "runtime-session"

    class Runtime:
        def converse(self, text, now=None):
            return Turn()

    gateway = OfficialConversationGateway(Runtime())
    UnifiedBrain(gateway).process("mensaje")
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("post_turn_reflection").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )
    assert cycle.node("learning_candidate").state is CognitiveCycleNodeState.OMITTED


def test_m387_8_legacy_gateway_keeps_post_turn_observation() -> None:
    turn = SimpleNamespace(
        status="completed",
        session_id="legacy",
        response_path="provider",
    )

    class LegacyGateway:
        def submit(self, message, *, origin, session_id, now):
            return turn

    brain = UnifiedBrain(LegacyGateway())
    assert brain.process("mensaje") is turn
    assert brain.reflection_snapshot.observed_turns == 1


def test_m387_8_reflection_occurs_before_cycle_sealing() -> None:
    source = getsource(OfficialConversationGateway.submit)
    reflection_index = source.index("observe_reflection(")
    seal_index = source.index("_conversation_entry_evidence.seal(")
    assert reflection_index < seal_index
    assert "submit_observed" in getsource(UnifiedBrain.process)


def test_m387_8_evidence_never_changes_learning_or_copies_content() -> None:
    source = getsource(ReflectionLearningEvidenceAdapter)
    forbidden = (
        "statement",
        "proposed_value",
        "response_text",
        "candidate_id",
        "store",
        "accept(",
    )
    assert all(item not in source for item in forbidden)


def test_m387_8_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
