from __future__ import annotations

from core.cognitive_maturity import (
    M388_GAP_CLOSURE_SPECS,
    create_canonical_cognitive_cycle,
    diagnose_m388_gap_closure,
    diagnose_operational_cycles,
)


def test_m388_5_5_evidence_matrix_covers_the_complete_cycle() -> None:
    cycle = create_canonical_cognitive_cycle("matrix-template")
    expected = {
        "conversation_ingress", "unified_coordination", "identity_and_context",
        "memory_recall", "knowledge_retrieval", "perception_and_evidence",
        "epistemic_classification", "cognitive_state", "relational_affective_context",
        "intent_and_reasoning", "planning", "decision", "action_gate",
        "response_composition", "post_turn_reflection", "learning_candidate",
        "safety_permissions", "unified_diagnostics",
    }
    assert {node.node_id for node in cycle.nodes} == expected


def test_m388_5_5_m388_gap_specs_have_milestone_and_adapter_evidence() -> None:
    assert len(M388_GAP_CLOSURE_SPECS) == 4
    assert all(item.milestone.startswith("M388.") for item in M388_GAP_CLOSURE_SPECS)
    assert all(":" in item.adapter_path for item in M388_GAP_CLOSURE_SPECS)


def test_m388_5_5_empty_evidence_never_claims_operational_success() -> None:
    diagnostic = diagnose_m388_gap_closure(diagnose_operational_cycles(()))
    assert diagnostic.all_structural_gaps_closed is True
    assert diagnostic.all_gaps_operationally_demonstrated is False
    assert diagnostic.operationally_demonstrated_count == 0


def test_m388_5_5_certification_remains_read_only_and_non_authoritative() -> None:
    diagnostic = diagnose_m388_gap_closure(diagnose_operational_cycles(()))
    assert diagnostic.read_only is True
    assert diagnostic.grants_authority is False
    assert diagnostic.contains_conversation_content is False
