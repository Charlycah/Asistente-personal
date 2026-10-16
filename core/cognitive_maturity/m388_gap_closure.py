from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .operational_cycle_diagnostic import OperationalCycleDiagnostic
from .post_m387_baseline import POST_M387_STRUCTURAL_GAP_NODE_IDS


class GapOperationalStatus(str, Enum):
    NEVER_OBSERVED = "never_observed"
    OBSERVED_WITHOUT_PARTICIPATION = "observed_without_participation"
    PARTICIPATED = "participated"


@dataclass(frozen=True)
class M388GapClosureSpec:
    node_id: str
    milestone: str
    adapter_path: str

    def __post_init__(self) -> None:
        if self.node_id not in POST_M387_STRUCTURAL_GAP_NODE_IDS:
            raise ValueError("M388 closure spec must reference an original gap")
        if not self.milestone.strip() or not self.adapter_path.strip():
            raise ValueError("M388 closure spec metadata must not be blank")


M388_GAP_CLOSURE_SPECS: tuple[M388GapClosureSpec, ...] = (
    M388GapClosureSpec(
        "perception_and_evidence",
        "M388.2",
        "core.cognitive_maturity:TextPerceptionEvidenceAdapter",
    ),
    M388GapClosureSpec(
        "epistemic_classification",
        "M388.3",
        "core.cognitive_maturity:EpistemicEvidenceAdapter",
    ),
    M388GapClosureSpec(
        "cognitive_state",
        "M388.4",
        "core.cognitive_maturity:CognitiveStateEvidenceAdapter",
    ),
    M388GapClosureSpec(
        "relational_affective_context",
        "M388.5",
        "core.cognitive_maturity:RelationalAffectiveEvidenceAdapter",
    ),
)


@dataclass(frozen=True)
class M388GapClosureNodeDiagnostic:
    node_id: str
    milestone: str
    adapter_path: str
    structurally_closed: bool
    operational_status: GapOperationalStatus
    observed_turns: int
    participated_turns: int
    safely_nonparticipating_turns: int
    not_recorded_turns: int

    def __post_init__(self) -> None:
        counts = (
            self.observed_turns,
            self.participated_turns,
            self.safely_nonparticipating_turns,
            self.not_recorded_turns,
        )
        if any(value < 0 for value in counts):
            raise ValueError("M388 closure node counts must not be negative")
        if self.participated_turns > self.observed_turns:
            raise ValueError("M388 participation cannot exceed observation")
        if self.observed_turns != (
            self.participated_turns + self.safely_nonparticipating_turns
        ):
            raise ValueError("M388 closure observation counts are inconsistent")


@dataclass(frozen=True)
class M388GapClosureDiagnostic:
    nodes: tuple[M388GapClosureNodeDiagnostic, ...]
    diagnosed_turns: int
    original_gap_count: int
    structurally_closed_count: int
    operationally_demonstrated_count: int
    remaining_structural_gap_node_ids: tuple[str, ...]
    structurally_closed_ratio: float
    operational_demonstration_ratio: float
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False

    def __post_init__(self) -> None:
        expected = POST_M387_STRUCTURAL_GAP_NODE_IDS
        if tuple(node.node_id for node in self.nodes) != expected:
            raise ValueError("M388 closure diagnostic must cover original gaps")
        if self.original_gap_count != len(expected):
            raise ValueError("M388 original gap count is inconsistent")
        if not 0.0 <= self.structurally_closed_ratio <= 1.0:
            raise ValueError("M388 structural closure ratio is invalid")
        if not 0.0 <= self.operational_demonstration_ratio <= 1.0:
            raise ValueError("M388 operational demonstration ratio is invalid")
        if not self.read_only or self.grants_authority:
            raise ValueError("M388 closure diagnostic must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("M388 closure diagnostic cannot contain content")

    def node(self, node_id: str) -> M388GapClosureNodeDiagnostic:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id == normalized:
                return node
        raise KeyError(node_id)

    @property
    def all_structural_gaps_closed(self) -> bool:
        return self.structurally_closed_count == self.original_gap_count

    @property
    def all_gaps_operationally_demonstrated(self) -> bool:
        return self.operationally_demonstrated_count == self.original_gap_count


def diagnose_m388_gap_closure(
    operational: OperationalCycleDiagnostic,
) -> M388GapClosureDiagnostic:
    nodes = []
    for spec in M388_GAP_CLOSURE_SPECS:
        observed = operational.node(spec.node_id)
        observed_turns = observed.total_turns - observed.not_recorded_turns
        if observed.participated_turns:
            status = GapOperationalStatus.PARTICIPATED
        elif observed_turns:
            status = GapOperationalStatus.OBSERVED_WITHOUT_PARTICIPATION
        else:
            status = GapOperationalStatus.NEVER_OBSERVED
        nodes.append(
            M388GapClosureNodeDiagnostic(
                node_id=spec.node_id,
                milestone=spec.milestone,
                adapter_path=spec.adapter_path,
                structurally_closed=True,
                operational_status=status,
                observed_turns=observed_turns,
                participated_turns=observed.participated_turns,
                safely_nonparticipating_turns=(
                    observed.omitted_turns
                    + observed.degraded_turns
                    + observed.blocked_turns
                ),
                not_recorded_turns=observed.not_recorded_turns,
            )
        )
    result = tuple(nodes)
    total = len(result)
    structurally_closed = sum(node.structurally_closed for node in result)
    demonstrated = sum(
        node.operational_status is GapOperationalStatus.PARTICIPATED
        for node in result
    )
    return M388GapClosureDiagnostic(
        nodes=result,
        diagnosed_turns=operational.diagnosed_turns,
        original_gap_count=total,
        structurally_closed_count=structurally_closed,
        operationally_demonstrated_count=demonstrated,
        remaining_structural_gap_node_ids=tuple(
            node.node_id for node in result if not node.structurally_closed
        ),
        structurally_closed_ratio=structurally_closed / total,
        operational_demonstration_ratio=demonstrated / total,
    )
