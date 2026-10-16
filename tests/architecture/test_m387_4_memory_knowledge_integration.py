from __future__ import annotations

from inspect import getsource
from types import SimpleNamespace

from app.official_conversation_gateway import OfficialConversationGateway
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    MemoryKnowledgeEvidenceAdapter,
)
from core.end_to_end_local_conversation import EndToEndLocalConversation
from core.runtime_composition_root import GovernedRuntimePreparation


def _capture(call):
    records = []
    adapter = MemoryKnowledgeEvidenceAdapter()
    with adapter.capture(records.append):
        result = call(adapter)
    return records, result


def test_m387_4_completed_memory_recall_without_items_participates() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_memory(
            runtime_available=True,
            access_allowed=True,
            recall_completed=True,
        )
    )
    record = records[0]
    assert record.node_id == "memory_recall"
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert record.evidence_codes == (
        "memory_recall:completed",
        "memory_recall:no_relevant_items",
    )


def test_m387_4_included_memory_context_is_redacted_evidence() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_memory(
            runtime_available=True,
            access_allowed=True,
            recall_completed=True,
            context_included=True,
        )
    )
    assert records[0].evidence_codes[-1] == "memory_recall:context_included"
    assert "Carlos" not in repr(records[0])
    assert "Cristina" not in repr(records[0])


def test_m387_4_identity_denial_blocks_memory_recall() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_memory(
            runtime_available=True,
            access_allowed=False,
            recall_completed=False,
        )
    )
    assert records[0].state is CognitiveCycleNodeState.BLOCKED
    assert records[0].reason_codes == (
        "memory_recall:private_context_denied",
    )


def test_m387_4_missing_memory_runtime_is_explicitly_omitted() -> None:
    records, _ = _capture(
        lambda adapter: adapter.observe_memory(
            runtime_available=False,
            access_allowed=True,
            recall_completed=False,
        )
    )
    assert records[0].state is CognitiveCycleNodeState.OMITTED
    assert records[0].reason_codes == ("memory_recall:runtime_unavailable",)


def test_m387_4_completed_knowledge_execution_participates() -> None:
    def observe(adapter):
        adapter.observe_knowledge_plan("local_planned")
        return adapter.observe_knowledge_execution(
            SimpleNamespace(
                status=SimpleNamespace(value="completed"),
                retrieval_performed=True,
            )
        )

    records, result = _capture(observe)
    assert result is records[0]
    assert result.node_id == "knowledge_retrieval"
    assert result.state is CognitiveCycleNodeState.PARTICIPATED
    assert result.evidence_codes == ("knowledge_retrieval:completed",)


def test_m387_4_plan_alone_never_claims_knowledge_retrieval() -> None:
    def observe(adapter):
        adapter.observe_knowledge_plan("local_planned")
        return adapter.observe_knowledge_execution(None)

    records, result = _capture(observe)
    assert result is records[0]
    assert result.state is CognitiveCycleNodeState.DEGRADED
    assert result.evidence_codes == ("knowledge_retrieval:planned",)
    assert result.reason_codes == (
        "knowledge_retrieval:execution_missing",
    )


def test_m387_4_not_applicable_knowledge_is_omitted() -> None:
    def observe(adapter):
        adapter.observe_knowledge_plan("not_applicable")
        return adapter.observe_knowledge_execution(None)

    records, result = _capture(observe)
    assert result is records[0]
    assert result.state is CognitiveCycleNodeState.OMITTED
    assert result.reason_codes == ("knowledge_retrieval:not_applicable",)


def test_m387_4_withheld_knowledge_is_blocked() -> None:
    def observe(adapter):
        adapter.observe_knowledge_plan("withheld")
        return adapter.observe_knowledge_execution(None)

    records, result = _capture(observe)
    assert result is records[0]
    assert result.state is CognitiveCycleNodeState.BLOCKED
    assert result.reason_codes == ("knowledge_retrieval:withheld",)


def test_m387_4_partial_knowledge_is_degraded_not_completed() -> None:
    def observe(adapter):
        adapter.observe_knowledge_plan("verification_planned")
        return adapter.observe_knowledge_execution(
            SimpleNamespace(
                status=SimpleNamespace(value="partial"),
                retrieval_performed=True,
            )
        )

    _, result = _capture(observe)
    assert result.state is CognitiveCycleNodeState.DEGRADED
    assert result.evidence_codes == ("knowledge_retrieval:partial_result",)
    assert result.reason_codes == ("knowledge_retrieval:partial",)


def test_m387_4_productive_runtime_emits_both_node_facts() -> None:
    preparation = getsource(GovernedRuntimePreparation.prepare)
    conversation = getsource(EndToEndLocalConversation.converse)
    gateway = getsource(OfficialConversationGateway.submit)
    assert "observe_memory(" in preparation
    assert "observe_knowledge_plan(" in preparation
    assert "observe_knowledge_execution(" in conversation
    assert "_memory_knowledge_evidence.capture(" in gateway


def test_m387_4_evidence_schema_contains_no_private_content() -> None:
    method_source = getsource(MemoryKnowledgeEvidenceAdapter)
    forbidden = ("artifact.content", "request.text", "owner", "session_id")
    assert all(item not in method_source for item in forbidden)
    assert "Carlos" not in method_source
    assert "Cristina" not in method_source


def test_m387_4_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
