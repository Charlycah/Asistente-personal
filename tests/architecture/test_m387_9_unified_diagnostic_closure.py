from __future__ import annotations

from inspect import getsource

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


def _official_brain() -> UnifiedBrain:
    class Turn:
        response_text = "respuesta"
        response_path = "provider"
        status = "completed"
        session_id = "runtime-session"

    class Runtime:
        def converse(self, text, now=None):
            return Turn()

    return UnifiedBrain(OfficialConversationGateway(Runtime()))


def test_m387_9_complete_diagnostic_closure_participates() -> None:
    records, result = _capture(
        lambda adapter: adapter.observe_diagnostics(
            reflection_observed=True,
            learning_assessed=True,
        )
    )
    assert result is records["unified_diagnostics"]
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes == (
        "unified_diagnostics:turn_closure_observed",
    )


def test_m387_9_missing_reflection_degrades_closure() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_diagnostics(
            reflection_observed=False,
            learning_assessed=True,
        )
    )
    diagnostic = records["unified_diagnostics"]
    assert diagnostic.state is CognitiveCycleNodeState.DEGRADED
    assert diagnostic.reason_codes == (
        "unified_diagnostics:incomplete_observation",
    )


def test_m387_9_missing_learning_assessment_degrades_closure() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_diagnostics(
            reflection_observed=True,
            learning_assessed=False,
        )
    )
    assert records["unified_diagnostics"].state is (
        CognitiveCycleNodeState.DEGRADED
    )


def test_m387_9_unobserved_closure_is_omitted() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_diagnostics(
            reflection_observed=False,
            learning_assessed=False,
        )
    )
    diagnostic = records["unified_diagnostics"]
    assert diagnostic.state is CognitiveCycleNodeState.OMITTED
    assert diagnostic.reason_codes == ("unified_diagnostics:not_observed",)


def test_m387_9_first_diagnostic_fact_cannot_be_rewritten() -> None:
    def observe(adapter):
        first = adapter.observe_diagnostics(
            reflection_observed=False,
            learning_assessed=True,
        )
        second = adapter.observe_diagnostics(
            reflection_observed=True,
            learning_assessed=True,
        )
        return first, second

    records, results = _capture(observe)
    assert results[0] is records["unified_diagnostics"]
    assert results[1] is None
    assert records["unified_diagnostics"].state is CognitiveCycleNodeState.DEGRADED


def test_m387_9_official_turn_records_diagnostic_closure() -> None:
    brain = _official_brain()
    brain.process("mensaje")
    cycle = brain.conversation.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    diagnostic = cycle.node("unified_diagnostics")
    assert diagnostic.state is CognitiveCycleNodeState.PARTICIPATED
    assert diagnostic.evidence_codes == (
        "unified_diagnostics:turn_closure_observed",
    )


def test_m387_9_existing_unified_view_remains_balanced() -> None:
    brain = _official_brain()
    brain.process("mensaje")
    diagnostic = brain.diagnostics
    assert diagnostic.fully_observed is True
    assert diagnostic.observation_gap == 0
    assert diagnostic.conversation.processed_messages == 1
    assert diagnostic.reflection.observed_turns == 1


def test_m387_9_diagnostic_does_not_hide_earlier_graph_gaps() -> None:
    brain = _official_brain()
    brain.process("mensaje")
    diagnostic = brain.conversation.operational_cycle_diagnostic
    assert diagnostic.latest_first_interruption_node_id == "identity_and_context"
    assert diagnostic.node("unified_diagnostics").participated_turns == 1


def test_m387_9_closure_is_observed_before_cycle_sealing() -> None:
    source = getsource(OfficialConversationGateway.submit)
    diagnostic_index = source.index("observe_diagnostics(")
    seal_index = source.index("_conversation_entry_evidence.seal(")
    assert diagnostic_index < seal_index


def test_m387_9_diagnostics_remain_advisory_and_content_free() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_diagnostics(
            reflection_observed=True,
            learning_assessed=True,
        )
    )
    diagnostic = records["unified_diagnostics"]
    assert diagnostic.evidence_codes
    assert "mensaje" not in repr(diagnostic)
    assert "respuesta" not in repr(diagnostic)


def test_m387_9_adapter_has_no_operational_authority() -> None:
    source = getsource(ReflectionLearningEvidenceAdapter.observe_diagnostics)
    forbidden = (
        "execute(",
        "persist(",
        "remember(",
        "decide(",
        "retry(",
        "alert(",
    )
    assert all(item not in source for item in forbidden)


def test_m387_9_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
