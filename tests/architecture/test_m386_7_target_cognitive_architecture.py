from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_maturity import (
    TARGET_COGNITIVE_ARCHITECTURE,
    CognitiveNodeRole,
    CognitiveNodeStatus,
)

EXPECTED_NODES = {
    "conversation_ingress",
    "unified_coordination",
    "identity_and_context",
    "perception_and_evidence",
    "memory_recall",
    "knowledge_retrieval",
    "epistemic_classification",
    "cognitive_state",
    "relational_affective_context",
    "intent_and_reasoning",
    "planning",
    "safety_permissions",
    "decision",
    "response_composition",
    "action_gate",
    "post_turn_reflection",
    "learning_candidate",
    "unified_diagnostics",
}


def test_m386_7_target_graph_covers_the_complete_cognitive_turn() -> None:
    node_ids = {node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes}
    assert node_ids == EXPECTED_NODES
    assert len(node_ids) == len(TARGET_COGNITIVE_ARCHITECTURE.nodes)


def test_m386_7_graph_has_one_entry_and_one_coordinator() -> None:
    entries = [
        node
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        if node.role is CognitiveNodeRole.ENTRY
    ]
    coordinators = [
        node
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        if node.role is CognitiveNodeRole.COORDINATOR
    ]
    assert [node.node_id for node in entries] == ["conversation_ingress"]
    assert [node.node_id for node in coordinators] == ["unified_coordination"]


def test_m386_7_unified_brain_coordinates_without_domain_authority() -> None:
    coordinator = TARGET_COGNITIVE_ARCHITECTURE.node("unified_coordination")
    assert coordinator.existing_authority == "app.unified_brain:UnifiedBrain"
    assert coordinator.owns_domain_authority is False
    assert coordinator.may_produce_external_effect is False
    assert coordinator.depends_on == ("conversation_ingress",)


def test_m386_7_dependencies_form_an_explicit_topological_order() -> None:
    positions = {
        node.node_id: index
        for index, node in enumerate(TARGET_COGNITIVE_ARCHITECTURE.nodes)
    }
    for node in TARGET_COGNITIVE_ARCHITECTURE.nodes:
        assert all(
            positions[item] < positions[node.node_id] for item in node.depends_on
        )


def test_m386_7_reuses_the_five_canonical_domain_facades() -> None:
    expected = {
        "memory_recall": "CanonicalMemoryFacade",
        "cognitive_state": "CanonicalCognitiveStateFacade",
        "planning": "CanonicalPlanningFacade",
        "decision": "CanonicalDecisionFacade",
        "post_turn_reflection": "CanonicalReflectionFacade",
    }
    for node_id, authority_name in expected.items():
        node = TARGET_COGNITIVE_ARCHITECTURE.node(node_id)
        assert authority_name in node.existing_authority


def test_m386_7_epistemic_classification_precedes_reasoning_and_decision() -> None:
    epistemic = TARGET_COGNITIVE_ARCHITECTURE.node("epistemic_classification")
    reasoning = TARGET_COGNITIVE_ARCHITECTURE.node("intent_and_reasoning")
    safety = TARGET_COGNITIVE_ARCHITECTURE.node("safety_permissions")
    assert epistemic.status is CognitiveNodeStatus.CONTRACT_ONLY
    assert epistemic.node_id in reasoning.depends_on
    assert epistemic.node_id in safety.depends_on


def test_m386_7_safety_precedes_both_decision_and_action() -> None:
    decision = TARGET_COGNITIVE_ARCHITECTURE.node("decision")
    action = TARGET_COGNITIVE_ARCHITECTURE.node("action_gate")
    assert "safety_permissions" in decision.depends_on
    assert "safety_permissions" in action.depends_on
    assert "decision" in action.depends_on


def test_m386_7_only_action_gate_may_produce_external_effect() -> None:
    external = [
        node
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        if node.may_produce_external_effect
    ]
    assert [node.node_id for node in external] == ["action_gate"]
    assert external[0].role is CognitiveNodeRole.GATE
    assert external[0].status is CognitiveNodeStatus.PARTIAL


def test_m386_7_reflection_and_learning_follow_response_or_action() -> None:
    reflection = TARGET_COGNITIVE_ARCHITECTURE.node("post_turn_reflection")
    learning = TARGET_COGNITIVE_ARCHITECTURE.node("learning_candidate")
    assert set(reflection.depends_on) == {"response_composition", "action_gate"}
    assert learning.depends_on == ("post_turn_reflection",)
    assert learning.owns_domain_authority is False


def test_m386_7_diagnostics_remain_partial_read_only_observation() -> None:
    diagnostics = TARGET_COGNITIVE_ARCHITECTURE.node("unified_diagnostics")
    assert diagnostics.role is CognitiveNodeRole.OBSERVER
    assert diagnostics.status is CognitiveNodeStatus.PARTIAL
    assert diagnostics.may_produce_external_effect is False
    assert set(diagnostics.depends_on) == {
        "post_turn_reflection",
        "learning_candidate",
    }


def test_m386_7_graph_declares_current_integration_gaps() -> None:
    statuses = {node.status for node in TARGET_COGNITIVE_ARCHITECTURE.nodes}
    assert statuses == {
        CognitiveNodeStatus.OPERATIONAL,
        CognitiveNodeStatus.PARTIAL,
        CognitiveNodeStatus.CONTRACT_ONLY,
    }
    assert sum(
        node.status is CognitiveNodeStatus.CONTRACT_ONLY
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    ) == 1


def test_m386_7_architecture_is_immutable_and_grants_no_authority() -> None:
    assert all(
        not node.grants_action_authority
        for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    )
    with pytest.raises(FrozenInstanceError):
        TARGET_COGNITIVE_ARCHITECTURE.entry_node_id = "altered"
    with pytest.raises(KeyError):
        TARGET_COGNITIVE_ARCHITECTURE.node("invented_parallel_brain")
