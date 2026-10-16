from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    STANDARD_TARGET_EVIDENCE,
    TARGET_COGNITIVE_ARCHITECTURE,
    TARGET_COGNITIVE_COVERAGE,
    CognitiveMaturityEvidence,
    CognitiveNodeStatus,
    diagnose_target_cognitive_coverage,
)


def test_m386_8_coverage_matches_every_target_graph_node() -> None:
    target_ids = {
        node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    }
    coverage_ids = {node.node_id for node in TARGET_COGNITIVE_COVERAGE.nodes}
    assert coverage_ids == target_ids
    assert TARGET_COGNITIVE_COVERAGE.total_nodes == 18


def test_m386_8_reports_the_certified_m386_7_status_baseline() -> None:
    diagnostic = TARGET_COGNITIVE_COVERAGE
    assert diagnostic.operational_nodes == 10
    assert diagnostic.partial_nodes == 7
    assert diagnostic.contract_only_nodes == 1
    assert diagnostic.operational_coverage_ratio == pytest.approx(10 / 18)
    assert diagnostic.complete is False


def test_m386_8_operational_does_not_mean_diagnostically_observed() -> None:
    diagnostic = TARGET_COGNITIVE_COVERAGE
    assert diagnostic.runtime_integrated_nodes == 10
    assert diagnostic.diagnostically_observed_nodes == 0
    assert diagnostic.runtime_integration_ratio == pytest.approx(10 / 18)
    assert diagnostic.diagnostic_observation_ratio == 0.0


def test_m386_8_every_node_declares_evidence_and_concrete_gaps() -> None:
    for node in TARGET_COGNITIVE_COVERAGE.nodes:
        assert node.required_evidence == STANDARD_TARGET_EVIDENCE
        assert node.missing_evidence == (
            node.required_evidence - node.demonstrated_evidence
        )
        assert node.maturity_gaps
        assert all(item.strip() for item in node.maturity_gaps)


def test_m386_8_operational_nodes_still_lack_live_diagnostics() -> None:
    memory = TARGET_COGNITIVE_COVERAGE.node("memory_recall")
    assert memory.declared_status is CognitiveNodeStatus.OPERATIONAL
    assert CognitiveMaturityEvidence.RUNTIME_INTEGRATION in (
        memory.demonstrated_evidence
    )
    assert CognitiveMaturityEvidence.OPERATIONAL_DIAGNOSTIC in (
        memory.missing_evidence
    )
    assert memory.diagnostically_observed is False


def test_m386_8_epistemic_classification_is_the_first_priority_gap() -> None:
    diagnostic = TARGET_COGNITIVE_COVERAGE
    epistemic = diagnostic.node("epistemic_classification")
    assert diagnostic.priority_gaps[0] == epistemic.node_id
    assert epistemic.declared_status is CognitiveNodeStatus.CONTRACT_ONLY
    assert CognitiveMaturityEvidence.RUNTIME_INTEGRATION in (
        epistemic.missing_evidence
    )


def test_m386_8_partial_nodes_follow_the_contract_only_priority() -> None:
    diagnostic = TARGET_COGNITIVE_COVERAGE
    partial_ids = tuple(
        node.node_id
        for node in diagnostic.nodes
        if node.declared_status is CognitiveNodeStatus.PARTIAL
    )
    assert diagnostic.priority_gaps[1:] == partial_ids


def test_m386_8_only_action_gate_exposes_external_effect_metadata() -> None:
    external = [
        node
        for node in TARGET_COGNITIVE_COVERAGE.nodes
        if node.may_produce_external_effect
    ]
    assert [node.node_id for node in external] == ["action_gate"]
    assert external[0].declared_status is CognitiveNodeStatus.PARTIAL


def test_m386_8_diagnostic_contains_no_conversation_or_identity_content() -> None:
    field_names = {
        item.name for item in fields(TARGET_COGNITIVE_COVERAGE)
    }
    forbidden = {"message", "response", "owner", "speaker", "memory"}
    assert field_names.isdisjoint(forbidden)
    assert "Carlos" not in repr(TARGET_COGNITIVE_COVERAGE)
    assert "Cristina" not in repr(TARGET_COGNITIVE_COVERAGE)


def test_m386_8_diagnostic_is_immutable_read_only_and_advisory() -> None:
    diagnostic = TARGET_COGNITIVE_COVERAGE
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False
    with pytest.raises(FrozenInstanceError):
        diagnostic.complete = True
    with pytest.raises(FrozenInstanceError):
        diagnostic.node("action_gate").runtime_integrated = True


def test_m386_8_diagnostic_performs_no_runtime_or_external_calls() -> None:
    source = getsource(diagnose_target_cognitive_coverage)
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


def test_m386_8_rejects_an_architecture_without_matching_gap_catalog() -> None:
    shortened = TARGET_COGNITIVE_ARCHITECTURE.__class__(
        nodes=TARGET_COGNITIVE_ARCHITECTURE.nodes[:-1],
        entry_node_id=TARGET_COGNITIVE_ARCHITECTURE.entry_node_id,
        coordinator_node_id=TARGET_COGNITIVE_ARCHITECTURE.coordinator_node_id,
        response_node_id=TARGET_COGNITIVE_ARCHITECTURE.response_node_id,
        action_gate_node_id=TARGET_COGNITIVE_ARCHITECTURE.action_gate_node_id,
        reflection_node_id=TARGET_COGNITIVE_ARCHITECTURE.reflection_node_id,
        diagnostics_node_id="learning_candidate",
        invariants=TARGET_COGNITIVE_ARCHITECTURE.invariants,
    )
    with pytest.raises(ValueError, match="gaps must match"):
        diagnose_target_cognitive_coverage(shortened)
