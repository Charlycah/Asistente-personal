from __future__ import annotations

from dataclasses import dataclass

from .operational_cycle_diagnostic import OperationalCycleDiagnostic
from .target_architecture import TARGET_COGNITIVE_ARCHITECTURE

POST_M387_EVIDENCE_CAPABLE_NODE_IDS: tuple[str, ...] = (
    "conversation_ingress",
    "unified_coordination",
    "identity_and_context",
    "memory_recall",
    "knowledge_retrieval",
    "intent_and_reasoning",
    "planning",
    "safety_permissions",
    "decision",
    "response_composition",
    "action_gate",
    "post_turn_reflection",
    "learning_candidate",
    "unified_diagnostics",
)

POST_M387_STRUCTURAL_GAP_NODE_IDS: tuple[str, ...] = (
    "perception_and_evidence",
    "epistemic_classification",
    "cognitive_state",
    "relational_affective_context",
)


@dataclass(frozen=True)
class PostM387ScenarioBaseline:
    scenario_id: str
    label: str
    required_observed_node_ids: tuple[str, ...]
    may_produce_external_effect: bool = False

    def __post_init__(self) -> None:
        target_ids = {
            node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        }
        if not self.scenario_id.strip() or not self.label.strip():
            raise ValueError("post-M387 scenario identity must not be blank")
        if not self.required_observed_node_ids:
            raise ValueError("post-M387 scenario requires observed nodes")
        if len(self.required_observed_node_ids) != len(
            set(self.required_observed_node_ids)
        ):
            raise ValueError("post-M387 scenario nodes must be unique")
        if not set(self.required_observed_node_ids) <= target_ids:
            raise ValueError("post-M387 scenario references unknown nodes")


POST_M387_SCENARIOS: tuple[PostM387ScenarioBaseline, ...] = (
    PostM387ScenarioBaseline(
        "simple_conversation",
        "Conversación identificada",
        (
            "conversation_ingress",
            "unified_coordination",
            "identity_and_context",
            "response_composition",
            "post_turn_reflection",
            "learning_candidate",
            "unified_diagnostics",
        ),
    ),
    PostM387ScenarioBaseline(
        "memory_supported_conversation",
        "Conversación con memoria",
        ("identity_and_context", "memory_recall", "response_composition"),
    ),
    PostM387ScenarioBaseline(
        "knowledge_supported_conversation",
        "Conversación con conocimiento",
        ("knowledge_retrieval", "response_composition"),
    ),
    PostM387ScenarioBaseline(
        "governed_decision",
        "Decisión gobernada",
        (
            "intent_and_reasoning",
            "planning",
            "safety_permissions",
            "decision",
            "response_composition",
        ),
    ),
    PostM387ScenarioBaseline(
        "governed_external_action",
        "Acción externa gobernada",
        ("safety_permissions", "decision", "action_gate"),
        may_produce_external_effect=True,
    ),
    PostM387ScenarioBaseline(
        "safe_degradation",
        "Degradación segura",
        (
            "conversation_ingress",
            "response_composition",
            "post_turn_reflection",
            "unified_diagnostics",
        ),
    ),
)


@dataclass(frozen=True)
class PostM387OperationalBaseline:
    total_nodes: int
    evidence_capable_node_ids: tuple[str, ...]
    structural_gap_node_ids: tuple[str, ...]
    scenarios: tuple[PostM387ScenarioBaseline, ...]
    diagnosed_turns: int
    observed_node_ids: tuple[str, ...]
    participated_node_ids: tuple[str, ...]
    never_observed_node_ids: tuple[str, ...]
    latest_connected_prefix_node_ids: tuple[str, ...]
    latest_first_interruption_node_id: str | None
    unified_cycle_complete: bool
    evidence_capable_ratio: float
    observation_ratio: float
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False

    def __post_init__(self) -> None:
        target_ids = tuple(
            node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        )
        if self.total_nodes != len(target_ids):
            raise ValueError("post-M387 baseline must cover the target graph")
        if set(self.evidence_capable_node_ids) | set(
            self.structural_gap_node_ids
        ) != set(target_ids):
            raise ValueError("post-M387 baseline node partition is incomplete")
        if set(self.evidence_capable_node_ids) & set(
            self.structural_gap_node_ids
        ):
            raise ValueError("post-M387 baseline node partition overlaps")
        if self.diagnosed_turns < 0:
            raise ValueError("post-M387 diagnosed turn count is invalid")
        if not 0.0 <= self.evidence_capable_ratio <= 1.0:
            raise ValueError("post-M387 evidence ratio is invalid")
        if not 0.0 <= self.observation_ratio <= 1.0:
            raise ValueError("post-M387 observation ratio is invalid")
        if not self.read_only or self.grants_authority:
            raise ValueError("post-M387 baseline must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("post-M387 baseline cannot contain content")

    def scenario(self, scenario_id: str) -> PostM387ScenarioBaseline:
        normalized = scenario_id.strip().casefold()
        for scenario in self.scenarios:
            if scenario.scenario_id == normalized:
                return scenario
        raise KeyError(scenario_id)


def diagnose_post_m387_baseline(
    diagnostic: OperationalCycleDiagnostic,
) -> PostM387OperationalBaseline:
    target_ids = tuple(
        node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    )
    if tuple(node.node_id for node in diagnostic.nodes) != target_ids:
        raise ValueError("post-M387 diagnostic must match the target graph")
    observed = tuple(
        node.node_id for node in diagnostic.nodes if node.observation_ratio > 0.0
    )
    participated = tuple(
        node.node_id
        for node in diagnostic.nodes
        if node.participation_ratio > 0.0
    )
    never_observed = tuple(node_id for node_id in target_ids if node_id not in observed)
    total = len(target_ids)
    return PostM387OperationalBaseline(
        total_nodes=total,
        evidence_capable_node_ids=POST_M387_EVIDENCE_CAPABLE_NODE_IDS,
        structural_gap_node_ids=POST_M387_STRUCTURAL_GAP_NODE_IDS,
        scenarios=POST_M387_SCENARIOS,
        diagnosed_turns=diagnostic.diagnosed_turns,
        observed_node_ids=observed,
        participated_node_ids=participated,
        never_observed_node_ids=never_observed,
        latest_connected_prefix_node_ids=(
            diagnostic.latest_connected_prefix_node_ids
        ),
        latest_first_interruption_node_id=(
            diagnostic.latest_first_interruption_node_id
        ),
        unified_cycle_complete=diagnostic.unified_cycle_complete,
        evidence_capable_ratio=len(POST_M387_EVIDENCE_CAPABLE_NODE_IDS) / total,
        observation_ratio=len(observed) / total,
    )
