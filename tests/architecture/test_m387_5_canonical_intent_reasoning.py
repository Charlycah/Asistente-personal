from __future__ import annotations

from datetime import datetime, timezone
from inspect import getsource
from types import SimpleNamespace

import pytest

from app.end_to_end_conversation_runtime import (
    OfficialEndToEndConversationRuntimeGateway,
)
from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    IntentReasoningEvidenceAdapter,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _observe(*, kind, action, reasoning):
    records = []
    adapter = IntentReasoningEvidenceAdapter()
    with adapter.capture(records.append):
        result = adapter.observe(
            intent_kind=kind,
            intent_action=action,
            reasoning_status=reasoning,
        )
    return records, result


def test_m387_5_non_reasoning_route_is_canonically_completed() -> None:
    records, result = _observe(
        kind="greeting",
        action="route_to_greeting",
        reasoning=None,
    )
    assert result is records[0]
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes == (
        "intent:greeting",
        "intent:route_to_greeting",
        "reasoning:not_required",
    )


def test_m387_5_completed_governed_reasoning_participates() -> None:
    _, result = _observe(
        kind="question",
        action="route_to_reasoning",
        reasoning="completed",
    )
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes[-1] == "reasoning:completed"


def test_m387_5_cautious_reasoning_is_explicitly_degraded() -> None:
    for status in ("abstained", "review_required"):
        _, result = _observe(
            kind="question",
            action="route_to_reasoning",
            reasoning=status,
        )
        assert result.state is CognitiveCycleNodeState.DEGRADED
        assert result.reason_codes == (f"reasoning:{status}",)


def test_m387_5_blocked_reasoning_remains_blocked() -> None:
    _, result = _observe(
        kind="question",
        action="route_to_reasoning",
        reasoning="blocked",
    )
    assert result.state is CognitiveCycleNodeState.BLOCKED
    assert result.reason_codes == ("reasoning:blocked",)


def test_m387_5_missing_required_reasoning_is_not_claimed() -> None:
    _, result = _observe(
        kind="question",
        action="route_to_reasoning",
        reasoning=None,
    )
    assert result.state is CognitiveCycleNodeState.DEGRADED
    assert result.reason_codes == ("reasoning:result_missing",)


def test_m387_5_unroutable_intent_is_blocked() -> None:
    _, result = _observe(
        kind="incomplete",
        action="request_completion",
        reasoning=None,
    )
    assert result.state is CognitiveCycleNodeState.BLOCKED
    assert result.reason_codes == ("intent_reasoning:entry_not_routable",)


def test_m387_5_rejects_noncanonical_intent_or_reasoning_values() -> None:
    adapter = IntentReasoningEvidenceAdapter()
    with pytest.raises(ValueError, match="intent reasoning"):
        adapter.observe(
            intent_kind="invented",
            intent_action="route_to_reasoning",
            reasoning_status="completed",
        )
    with pytest.raises(ValueError, match="reasoning status"):
        adapter.observe(
            intent_kind="question",
            intent_action="route_to_reasoning",
            reasoning_status="invented",
        )
    result = IntentReasoningEvidenceAdapter().observe(
        intent_kind="greeting",
        intent_action="route_to_greeting",
        reasoning_status=None,
    )
    assert result is None


class EntryRuntime:
    def evaluate_text(self, text):
        return SimpleNamespace(kind="greeting", action="route_to_greeting")


class ContextRuntime:
    def enrich(self, *, conversation, inference_request):
        return inference_request


class IntelligenceRuntime:
    def evaluate_text(self, **kwargs):
        return SimpleNamespace(
            operational=SimpleNamespace(
                state=SimpleNamespace(value="stable"),
                action=SimpleNamespace(value="respond"),
            )
        )


def test_m387_5_productive_coordinator_emits_the_canonical_fact() -> None:
    runtime = OfficialEndToEndConversationRuntimeGateway(
        entry_runtime=EntryRuntime(),
        context_runtime=ContextRuntime(),
        device_runtime=object(),
        retrieval_runtime=object(),
        reasoning_runtime=object(),
        cognition_runtime=object(),
        intelligence_runtime=IntelligenceRuntime(),
    )
    records = []
    with IntentReasoningEvidenceAdapter().capture(records.append):
        runtime.evaluate_turn(
            GovernedConversationPipelineRequest(
                owner="Carlos y Cristina",
                session_id="main",
                text="Hola",
            ),
            now=datetime.now(timezone.utc),
        )
    assert records[0].node_id == "intent_and_reasoning"
    assert records[0].state is CognitiveCycleNodeState.PARTICIPATED


def test_m387_5_uses_existing_authorities_without_reclassifying_text() -> None:
    runtime_source = getsource(
        OfficialEndToEndConversationRuntimeGateway.evaluate_turn
    )
    adapter_source = getsource(IntentReasoningEvidenceAdapter)
    assert "entry_runtime.evaluate_text" in runtime_source
    assert "cognition_runtime.evaluate_text" in runtime_source
    assert "IntentReasoningEvidenceAdapter().observe" in runtime_source
    assert ".casefold()" not in runtime_source
    assert "request.text" not in adapter_source


def test_m387_5_gateway_captures_intent_reasoning_in_the_turn_dossier() -> None:
    source = getsource(OfficialConversationGateway.submit)
    assert "_intent_reasoning_evidence.capture(" in source
    assert "_conversation_entry_evidence.observe" in source


def test_m387_5_evidence_contains_no_message_identity_or_conclusion() -> None:
    records, _ = _observe(
        kind="question",
        action="route_to_reasoning",
        reasoning="abstained",
    )
    representation = repr(records[0])
    assert "Carlos" not in representation
    assert "Cristina" not in representation
    assert "conclusion" not in representation
    assert "message" not in representation


def test_m387_5_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
