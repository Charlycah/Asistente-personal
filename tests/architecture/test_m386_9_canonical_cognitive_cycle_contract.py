from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    TARGET_COGNITIVE_ARCHITECTURE,
    CanonicalCognitiveCycle,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
    create_canonical_cognitive_cycle,
)


def _record(
    node_id: str,
    state: CognitiveCycleNodeState,
    *,
    evidence: tuple[str, ...] = (),
    reasons: tuple[str, ...] = (),
) -> CognitiveCycleNodeRecord:
    return CognitiveCycleNodeRecord(
        node_id=node_id,
        state=state,
        evidence_codes=evidence,
        reason_codes=reasons,
    )


def test_m386_9_empty_cycle_covers_every_node_without_inventing_activity() -> None:
    cycle = create_canonical_cognitive_cycle("turn:0001")
    assert tuple(node.node_id for node in cycle.nodes) == tuple(
        node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    )
    assert cycle.count(CognitiveCycleNodeState.NOT_RECORDED) == 18
    assert cycle.outcome is CognitiveCycleOutcome.UNOBSERVED


def test_m386_9_records_real_participation_with_technical_evidence() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn:0002",
        (
            _record(
                "conversation_ingress",
                CognitiveCycleNodeState.PARTICIPATED,
                evidence=("gateway:accepted",),
            ),
        ),
    )
    entry = cycle.node("conversation_ingress")
    assert entry.state is CognitiveCycleNodeState.PARTICIPATED
    assert entry.evidence_codes == ("gateway:accepted",)
    assert cycle.outcome is CognitiveCycleOutcome.PARTIAL


def test_m386_9_distinguishes_omission_from_absent_observation() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn:0003",
        (
            _record(
                "knowledge_retrieval",
                CognitiveCycleNodeState.OMITTED,
                reasons=("not_required",),
            ),
        ),
    )
    assert cycle.node("knowledge_retrieval").state is (
        CognitiveCycleNodeState.OMITTED
    )
    assert cycle.node("memory_recall").state is (
        CognitiveCycleNodeState.NOT_RECORDED
    )


def test_m386_9_degradation_requires_evidence_and_reason() -> None:
    with pytest.raises(ValueError, match="partial evidence"):
        _record(
            "memory_recall",
            CognitiveCycleNodeState.DEGRADED,
            reasons=("timeout",),
        )
    degraded = _record(
        "memory_recall",
        CognitiveCycleNodeState.DEGRADED,
        evidence=("recall:partial",),
        reasons=("timeout",),
    )
    cycle = create_canonical_cognitive_cycle("turn:0004", (degraded,))
    assert cycle.outcome is CognitiveCycleOutcome.DEGRADED


def test_m386_9_blocked_outcome_has_precedence_over_degradation() -> None:
    cycle = create_canonical_cognitive_cycle(
        "turn:0005",
        (
            _record(
                "action_gate",
                CognitiveCycleNodeState.BLOCKED,
                reasons=("permission:denied",),
            ),
            _record(
                "knowledge_retrieval",
                CognitiveCycleNodeState.DEGRADED,
                evidence=("source:local_only",),
                reasons=("network:unavailable",),
            ),
        ),
    )
    assert cycle.outcome is CognitiveCycleOutcome.BLOCKED


def test_m386_9_complete_requires_participation_of_all_graph_nodes() -> None:
    records = tuple(
        _record(
            node.node_id,
            CognitiveCycleNodeState.PARTICIPATED,
            evidence=(f"node:{node.node_id}",),
        )
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    )
    cycle = create_canonical_cognitive_cycle("turn:0006", records)
    assert cycle.count(CognitiveCycleNodeState.PARTICIPATED) == 18
    assert cycle.outcome is CognitiveCycleOutcome.COMPLETE


def test_m386_9_participation_cannot_be_claimed_without_evidence() -> None:
    with pytest.raises(ValueError, match="requires evidence"):
        _record(
            "decision",
            CognitiveCycleNodeState.PARTICIPATED,
        )


def test_m386_9_safe_codes_reject_free_form_or_private_content() -> None:
    with pytest.raises(ValueError, match="safe codes"):
        _record(
            "memory_recall",
            CognitiveCycleNodeState.PARTICIPATED,
            evidence=("Carlos dijo que...",),
        )
    with pytest.raises(ValueError, match="safe code"):
        create_canonical_cognitive_cycle("conversación privada")


def test_m386_9_rejects_unknown_or_duplicate_node_records() -> None:
    record = _record(
        "decision",
        CognitiveCycleNodeState.OMITTED,
        reasons=("not_required",),
    )
    with pytest.raises(ValueError, match="unique"):
        create_canonical_cognitive_cycle("turn:0007", (record, record))
    unknown = _record(
        "parallel_brain",
        CognitiveCycleNodeState.OMITTED,
        reasons=("not_allowed",),
    )
    with pytest.raises(ValueError, match="unknown nodes"):
        create_canonical_cognitive_cycle("turn:0008", (unknown,))


def test_m386_9_contract_is_immutable_content_free_and_advisory() -> None:
    cycle = create_canonical_cognitive_cycle("turn:0009")
    assert cycle.read_only is True
    assert cycle.grants_authority is False
    assert cycle.contains_conversation_content is False
    assert {item.name for item in fields(cycle)} == {
        "cycle_id",
        "nodes",
        "schema_version",
        "read_only",
        "grants_authority",
        "contains_conversation_content",
    }
    with pytest.raises(FrozenInstanceError):
        cycle.grants_authority = True


def test_m386_9_contract_factory_performs_no_runtime_operations() -> None:
    source = getsource(create_canonical_cognitive_cycle)
    forbidden_calls = (
        "converse(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "request(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_9_direct_contract_rejects_graph_order_drift() -> None:
    cycle = create_canonical_cognitive_cycle("turn:0010")
    with pytest.raises(ValueError, match="target graph order"):
        CanonicalCognitiveCycle(
            cycle_id="turn:0011",
            nodes=tuple(reversed(cycle.nodes)),
        )
