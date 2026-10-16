from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.official_capability_gateway import OfficialCapabilityGateway
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    ResponseActionEvidenceAdapter,
)
from core.end_to_end_local_conversation import EndToEndLocalConversation
from core.runtime_composition_root import GovernedRuntimePreparation


def _capture(call):
    records = []
    adapter = ResponseActionEvidenceAdapter()
    with adapter.capture(records.append):
        result = call(adapter)
    return {record.node_id: record for record in records}, result


def test_m387_7_completed_response_composition_participates() -> None:
    records, result = _capture(
        lambda adapter: adapter.observe_response_status("completed")
    )
    assert result is records["response_composition"]
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes == ("response_composition:completed",)


def test_m387_7_partial_response_is_explicitly_degraded() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_response_status("partial")
    )
    response = records["response_composition"]
    assert response.state is CognitiveCycleNodeState.DEGRADED
    assert response.reason_codes == (
        "response_composition:limitations_present",
    )
    withheld_records, _ = _capture(
        lambda adapter: adapter.observe_response_status("withheld")
    )
    assert (
        withheld_records["response_composition"].state
        is CognitiveCycleNodeState.BLOCKED
    )


def test_m387_7_explicit_tool_gateway_execution_participates() -> None:
    context = SimpleNamespace(status=SimpleNamespace(value="executed"))
    records, _ = _capture(
        lambda adapter: adapter.observe_tool_context(context)
    )
    action = records["action_gate"]
    assert action.state is CognitiveCycleNodeState.PARTICIPATED
    assert action.evidence_codes == ("action_gate:tool_gateway_routed",)


def test_m387_7_blocked_tool_never_claims_execution() -> None:
    context = SimpleNamespace(status=SimpleNamespace(value="blocked"))
    records, _ = _capture(
        lambda adapter: adapter.observe_tool_context(context)
    )
    action = records["action_gate"]
    assert action.state is CognitiveCycleNodeState.BLOCKED
    assert action.evidence_codes == ()


def test_m387_7_no_tool_request_is_explicitly_omitted() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_tool_context(None)
    )
    assert records["action_gate"].state is CognitiveCycleNodeState.OMITTED


def test_m387_7_external_capability_without_generic_proof_is_degraded() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_official_capability(
            external_scope=True,
            completed=True,
        )
    )
    action = records["action_gate"]
    assert action.state is CognitiveCycleNodeState.DEGRADED
    assert action.reason_codes == (
        "action_gate:generic_permission_proof_unavailable",
    )


def test_m387_7_internal_capability_claims_no_external_effect() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_official_capability(
            external_scope=False,
            completed=True,
        )
    )
    action = records["action_gate"]
    assert action.state is CognitiveCycleNodeState.OMITTED
    assert action.reason_codes == ("action_gate:no_external_effect_claimed",)


def test_m387_7_first_action_fact_cannot_be_rewritten() -> None:
    def observe(adapter):
        blocked = adapter.observe_tool_context(
            SimpleNamespace(status=SimpleNamespace(value="blocked"))
        )
        repeated = adapter.observe_tool_context(
            SimpleNamespace(status=SimpleNamespace(value="executed"))
        )
        return blocked, repeated

    records, results = _capture(observe)
    assert results[0] is records["action_gate"]
    assert results[1] is None
    assert records["action_gate"].state is CognitiveCycleNodeState.BLOCKED


def test_m387_7_productive_response_and_action_boundaries_are_observed() -> None:
    conversation = getsource(EndToEndLocalConversation.converse)
    preparation = getsource(GovernedRuntimePreparation.prepare)
    capability = getsource(OfficialCapabilityGateway.execute)
    assert "observe_response_status(" in conversation
    assert "observe_tool_context(" in preparation
    assert "observe_official_capability(" in capability


def test_m387_7_gateway_captures_and_completes_local_responses() -> None:
    source = getsource(OfficialConversationGateway.submit)
    assert "_response_action_evidence.capture(" in source
    assert "observe_response_status(" in source
    assert 'getattr(turn, "status", None)' in source


def test_m387_7_evidence_contains_no_response_or_action_payload() -> None:
    source = getsource(ResponseActionEvidenceAdapter)
    forbidden = (
        "response_text",
        "gateway_result.output",
        "invocation.payload",
        "capability_name",
        "owner",
        "session_id",
    )
    assert all(item not in source for item in forbidden)
    assert "Carlos" not in source
    assert "Cristina" not in source


def test_m387_7_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
