from __future__ import annotations

from dataclasses import dataclass

from .models import CognitiveMaturityEvidence
from .target_architecture import (
    TARGET_COGNITIVE_ARCHITECTURE,
    CognitiveNodeStatus,
    TargetCognitiveArchitecture,
    TargetCognitiveNode,
)

E = CognitiveMaturityEvidence

STANDARD_TARGET_EVIDENCE = frozenset(
    {
        E.CONTRACT,
        E.ARCHITECTURE_TEST,
        E.RUNTIME_INTEGRATION,
        E.OPERATIONAL_DIAGNOSTIC,
    }
)

NODE_MATURITY_GAPS: dict[str, tuple[str, ...]] = {
    "conversation_ingress": (
        "Expose entry availability and degraded-state evidence.",
    ),
    "unified_coordination": (
        "Report participation of every target node without absorbing it.",
    ),
    "identity_and_context": (
        "Expose identity resolution provenance without personal content.",
    ),
    "perception_and_evidence": (
        "Certify each real channel and reject unavailable observations.",
        "Expose consent, source and freshness metadata.",
    ),
    "memory_recall": (
        "Expose recall participation, provenance and safe degradation.",
    ),
    "knowledge_retrieval": (
        "Converge local and external sources behind one governed contract.",
        "Diagnose source freshness and insufficient evidence.",
    ),
    "epistemic_classification": (
        "Integrate classification into the productive cognitive turn.",
        "Prove that uncertainty reaches reasoning and response metadata.",
    ),
    "cognitive_state": (
        "Make attention, goals and doubts influence the turn traceably.",
        "Expose inspection and reset without private content.",
    ),
    "relational_affective_context": (
        "Unify relational context and simulated affect behind one adapter.",
        "Prove that expression never changes facts, permissions or decisions.",
    ),
    "intent_and_reasoning": (
        "Expose governed participation and epistemic input diagnostics.",
    ),
    "planning": (
        "Expose plan participation without treating a plan as permission.",
    ),
    "safety_permissions": (
        "Expose applied boundaries, permission mode and safe degradation.",
    ),
    "decision": (
        "Expose the selected outcome and authority lineage safely.",
    ),
    "response_composition": (
        "Expose assembly participation and degraded response mode.",
    ),
    "action_gate": (
        "Unify prevalidated actions behind the official effect boundary.",
        "Certify permission, reversibility, audit and human interruption.",
    ),
    "post_turn_reflection": (
        "Expose observation coverage without revealing turn content.",
    ),
    "learning_candidate": (
        "Unify proposals behind review, rejection and rollback controls.",
        "Prove that no candidate changes productive behavior automatically.",
    ),
    "unified_diagnostics": (
        "Join node metadata into one read-only snapshot.",
        "Prove redaction, stable degradation and absence of authority.",
    ),
}


@dataclass(frozen=True)
class CognitiveNodeCoverage:
    node_id: str
    title: str
    declared_status: CognitiveNodeStatus
    demonstrated_evidence: frozenset[CognitiveMaturityEvidence]
    required_evidence: frozenset[CognitiveMaturityEvidence]
    missing_evidence: frozenset[CognitiveMaturityEvidence]
    maturity_gaps: tuple[str, ...]
    runtime_integrated: bool
    diagnostically_observed: bool
    may_produce_external_effect: bool

    def __post_init__(self) -> None:
        if not self.node_id.strip() or not self.title.strip():
            raise ValueError("cognitive coverage identity must not be blank")
        expected_missing = self.required_evidence - self.demonstrated_evidence
        if self.missing_evidence != expected_missing:
            raise ValueError("cognitive coverage missing evidence is inconsistent")
        if not self.maturity_gaps or any(
            not item.strip() for item in self.maturity_gaps
        ):
            raise ValueError("cognitive coverage requires explicit maturity gaps")
        if self.diagnostically_observed and not self.runtime_integrated:
            raise ValueError("diagnostic observation requires runtime integration")


@dataclass(frozen=True)
class CognitiveGraphCoverageDiagnostic:
    nodes: tuple[CognitiveNodeCoverage, ...]
    total_nodes: int
    operational_nodes: int
    partial_nodes: int
    contract_only_nodes: int
    runtime_integrated_nodes: int
    diagnostically_observed_nodes: int
    operational_coverage_ratio: float
    runtime_integration_ratio: float
    diagnostic_observation_ratio: float
    priority_gaps: tuple[str, ...]
    complete: bool
    read_only: bool = True
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if self.total_nodes != len(self.nodes) or self.total_nodes <= 0:
            raise ValueError("cognitive graph coverage node total is inconsistent")
        status_total = (
            self.operational_nodes
            + self.partial_nodes
            + self.contract_only_nodes
        )
        if status_total != self.total_nodes:
            raise ValueError("cognitive graph coverage status counts are inconsistent")
        counts = (
            self.runtime_integrated_nodes,
            self.diagnostically_observed_nodes,
        )
        if any(value < 0 or value > self.total_nodes for value in counts):
            raise ValueError("cognitive graph coverage evidence count is invalid")
        ratios = (
            self.operational_coverage_ratio,
            self.runtime_integration_ratio,
            self.diagnostic_observation_ratio,
        )
        if any(value < 0.0 or value > 1.0 for value in ratios):
            raise ValueError("cognitive graph coverage ratio is invalid")
        if not self.priority_gaps:
            raise ValueError("cognitive graph coverage requires priority gaps")
        if not self.read_only or self.grants_authority:
            raise ValueError("cognitive graph coverage must remain advisory")

    def node(self, node_id: str) -> CognitiveNodeCoverage:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id.casefold() == normalized:
                return node
        raise KeyError(node_id)


def _demonstrated_evidence(
    node: TargetCognitiveNode,
) -> frozenset[CognitiveMaturityEvidence]:
    evidence = {E.CONTRACT, E.ARCHITECTURE_TEST}
    if node.status is CognitiveNodeStatus.OPERATIONAL:
        evidence.add(E.RUNTIME_INTEGRATION)
    return frozenset(evidence)


def diagnose_target_cognitive_coverage(
    architecture: TargetCognitiveArchitecture = TARGET_COGNITIVE_ARCHITECTURE,
) -> CognitiveGraphCoverageDiagnostic:
    node_ids = {node.node_id for node in architecture.nodes}
    if node_ids != set(NODE_MATURITY_GAPS):
        raise ValueError("cognitive coverage gaps must match target architecture")

    coverage_nodes = tuple(
        CognitiveNodeCoverage(
            node_id=node.node_id,
            title=node.title,
            declared_status=node.status,
            demonstrated_evidence=_demonstrated_evidence(node),
            required_evidence=STANDARD_TARGET_EVIDENCE,
            missing_evidence=(
                STANDARD_TARGET_EVIDENCE - _demonstrated_evidence(node)
            ),
            maturity_gaps=NODE_MATURITY_GAPS[node.node_id],
            runtime_integrated=(
                node.status is CognitiveNodeStatus.OPERATIONAL
            ),
            diagnostically_observed=False,
            may_produce_external_effect=node.may_produce_external_effect,
        )
        for node in architecture.nodes
    )
    total = len(coverage_nodes)
    operational = sum(
        node.declared_status is CognitiveNodeStatus.OPERATIONAL
        for node in coverage_nodes
    )
    partial = sum(
        node.declared_status is CognitiveNodeStatus.PARTIAL
        for node in coverage_nodes
    )
    contract_only = sum(
        node.declared_status is CognitiveNodeStatus.CONTRACT_ONLY
        for node in coverage_nodes
    )
    integrated = sum(node.runtime_integrated for node in coverage_nodes)
    observed = sum(node.diagnostically_observed for node in coverage_nodes)
    priority = tuple(
        node.node_id
        for status in (
            CognitiveNodeStatus.CONTRACT_ONLY,
            CognitiveNodeStatus.PARTIAL,
        )
        for node in coverage_nodes
        if node.declared_status is status
    )
    return CognitiveGraphCoverageDiagnostic(
        nodes=coverage_nodes,
        total_nodes=total,
        operational_nodes=operational,
        partial_nodes=partial,
        contract_only_nodes=contract_only,
        runtime_integrated_nodes=integrated,
        diagnostically_observed_nodes=observed,
        operational_coverage_ratio=operational / total,
        runtime_integration_ratio=integrated / total,
        diagnostic_observation_ratio=observed / total,
        priority_gaps=priority,
        complete=False,
    )


TARGET_COGNITIVE_COVERAGE = diagnose_target_cognitive_coverage()
