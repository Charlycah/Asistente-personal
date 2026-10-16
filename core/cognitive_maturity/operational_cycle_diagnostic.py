from __future__ import annotations

from dataclasses import dataclass

from .cycle_contract import (
    CanonicalCognitiveCycle,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
)
from .target_architecture import TARGET_COGNITIVE_ARCHITECTURE


@dataclass(frozen=True)
class OperationalNodeDiagnostic:
    node_id: str
    total_turns: int
    participated_turns: int
    omitted_turns: int
    degraded_turns: int
    blocked_turns: int
    not_recorded_turns: int
    participation_ratio: float
    observation_ratio: float

    def __post_init__(self) -> None:
        counts = (
            self.participated_turns,
            self.omitted_turns,
            self.degraded_turns,
            self.blocked_turns,
            self.not_recorded_turns,
        )
        if self.total_turns < 0 or any(value < 0 for value in counts):
            raise ValueError("operational node diagnostic counts are invalid")
        if sum(counts) != self.total_turns:
            raise ValueError("operational node diagnostic counts are inconsistent")
        if not 0.0 <= self.participation_ratio <= 1.0:
            raise ValueError("operational node participation ratio is invalid")
        if not 0.0 <= self.observation_ratio <= 1.0:
            raise ValueError("operational node observation ratio is invalid")


@dataclass(frozen=True)
class OperationalCycleDiagnostic:
    nodes: tuple[OperationalNodeDiagnostic, ...]
    diagnosed_turns: int
    complete_turns: int
    partial_turns: int
    degraded_turns: int
    blocked_turns: int
    unobserved_turns: int
    latest_cycle_id: str | None
    latest_outcome: CognitiveCycleOutcome | None
    latest_participated_node_ids: tuple[str, ...]
    latest_nonparticipating_node_ids: tuple[str, ...]
    latest_connected_prefix_node_ids: tuple[str, ...]
    latest_first_interruption_node_id: str | None
    unified_cycle_complete: bool
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False

    def __post_init__(self) -> None:
        outcomes = (
            self.complete_turns,
            self.partial_turns,
            self.degraded_turns,
            self.blocked_turns,
            self.unobserved_turns,
        )
        if self.diagnosed_turns < 0 or any(value < 0 for value in outcomes):
            raise ValueError("operational cycle diagnostic counts are invalid")
        if sum(outcomes) != self.diagnosed_turns:
            raise ValueError("operational cycle outcome counts are inconsistent")
        expected = tuple(
            node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        )
        if tuple(node.node_id for node in self.nodes) != expected:
            raise ValueError("operational diagnostic must cover the target graph")
        if not self.read_only or self.grants_authority:
            raise ValueError("operational cycle diagnostic must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("operational diagnostic cannot contain content")

    def node(self, node_id: str) -> OperationalNodeDiagnostic:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id == normalized:
                return node
        raise KeyError(node_id)


def _ratio(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def diagnose_operational_cycles(
    cycles: tuple[CanonicalCognitiveCycle, ...],
) -> OperationalCycleDiagnostic:
    cycles = tuple(cycles)
    expected_ids = tuple(
        node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
    )
    if any(
        tuple(node.node_id for node in cycle.nodes) != expected_ids
        for cycle in cycles
    ):
        raise ValueError("operational cycles must match the target graph")

    node_diagnostics = []
    for node_id in expected_ids:
        states = tuple(cycle.node(node_id).state for cycle in cycles)
        participated = states.count(CognitiveCycleNodeState.PARTICIPATED)
        omitted = states.count(CognitiveCycleNodeState.OMITTED)
        degraded = states.count(CognitiveCycleNodeState.DEGRADED)
        blocked = states.count(CognitiveCycleNodeState.BLOCKED)
        not_recorded = states.count(CognitiveCycleNodeState.NOT_RECORDED)
        observed = len(states) - not_recorded
        node_diagnostics.append(
            OperationalNodeDiagnostic(
                node_id=node_id,
                total_turns=len(cycles),
                participated_turns=participated,
                omitted_turns=omitted,
                degraded_turns=degraded,
                blocked_turns=blocked,
                not_recorded_turns=not_recorded,
                participation_ratio=_ratio(participated, len(cycles)),
                observation_ratio=_ratio(observed, len(cycles)),
            )
        )

    latest = cycles[-1] if cycles else None
    latest_participated = tuple(
        node.node_id
        for node in latest.nodes
        if node.state is CognitiveCycleNodeState.PARTICIPATED
    ) if latest else ()
    latest_nonparticipating = tuple(
        node.node_id
        for node in latest.nodes
        if node.state is not CognitiveCycleNodeState.PARTICIPATED
    ) if latest else ()
    prefix = []
    if latest is not None:
        for node in latest.nodes:
            if node.state is not CognitiveCycleNodeState.PARTICIPATED:
                break
            prefix.append(node.node_id)
    first_interruption = latest_nonparticipating[0] if latest_nonparticipating else None
    outcomes = tuple(cycle.outcome for cycle in cycles)
    return OperationalCycleDiagnostic(
        nodes=tuple(node_diagnostics),
        diagnosed_turns=len(cycles),
        complete_turns=outcomes.count(CognitiveCycleOutcome.COMPLETE),
        partial_turns=outcomes.count(CognitiveCycleOutcome.PARTIAL),
        degraded_turns=outcomes.count(CognitiveCycleOutcome.DEGRADED),
        blocked_turns=outcomes.count(CognitiveCycleOutcome.BLOCKED),
        unobserved_turns=outcomes.count(CognitiveCycleOutcome.UNOBSERVED),
        latest_cycle_id=latest.cycle_id if latest else None,
        latest_outcome=latest.outcome if latest else None,
        latest_participated_node_ids=latest_participated,
        latest_nonparticipating_node_ids=latest_nonparticipating,
        latest_connected_prefix_node_ids=tuple(prefix),
        latest_first_interruption_node_id=first_interruption,
        unified_cycle_complete=(
            latest is not None
            and latest.outcome is CognitiveCycleOutcome.COMPLETE
        ),
    )
