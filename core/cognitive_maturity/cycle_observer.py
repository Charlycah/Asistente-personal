from __future__ import annotations

from dataclasses import dataclass

from .cycle_contract import (
    CanonicalCognitiveCycle,
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    create_canonical_cognitive_cycle,
)
from .target_architecture import (
    TARGET_COGNITIVE_ARCHITECTURE,
    TargetCognitiveArchitecture,
)


@dataclass(frozen=True)
class CognitiveCycleObserverDiagnostic:
    cycle: CanonicalCognitiveCycle
    observed_nodes: int
    remaining_nodes: int
    sealed: bool
    read_only: bool = True
    grants_authority: bool = False

    def __post_init__(self) -> None:
        total = len(self.cycle.nodes)
        if self.observed_nodes < 0 or self.remaining_nodes < 0:
            raise ValueError("cognitive observer counts must not be negative")
        if self.observed_nodes + self.remaining_nodes != total:
            raise ValueError("cognitive observer counts are inconsistent")
        actual = self.cycle.count(CognitiveCycleNodeState.NOT_RECORDED)
        if self.remaining_nodes != actual:
            raise ValueError("cognitive observer remaining count is inconsistent")
        if not self.read_only or self.grants_authority:
            raise ValueError("cognitive observer diagnostic must remain advisory")


class CanonicalCognitiveCycleObserver:
    """Collect validated node metadata without observing runtime by itself."""

    def __init__(
        self,
        cycle_id: str,
        architecture: TargetCognitiveArchitecture = (
            TARGET_COGNITIVE_ARCHITECTURE
        ),
    ) -> None:
        baseline = create_canonical_cognitive_cycle(
            cycle_id,
            architecture=architecture,
        )
        self._cycle_id = baseline.cycle_id
        self._architecture = architecture
        self._records: dict[str, CognitiveCycleNodeRecord] = {}
        self._sealed = False

    @property
    def cycle_id(self) -> str:
        return self._cycle_id

    @property
    def sealed(self) -> bool:
        return self._sealed

    @property
    def observed_node_ids(self) -> tuple[str, ...]:
        return tuple(
            node.node_id
            for node in self._architecture.nodes
            if node.node_id in self._records
        )

    @property
    def remaining_node_ids(self) -> tuple[str, ...]:
        return tuple(
            node.node_id
            for node in self._architecture.nodes
            if node.node_id not in self._records
        )

    def observe(
        self,
        record: CognitiveCycleNodeRecord,
    ) -> CanonicalCognitiveCycle:
        if self._sealed:
            raise RuntimeError("canonical cognitive cycle observer is sealed")
        node_ids = {node.node_id for node in self._architecture.nodes}
        if record.node_id not in node_ids:
            raise ValueError("cognitive observer references an unknown node")
        if record.node_id in self._records:
            raise ValueError("cognitive observer cannot rewrite a node fact")
        if record.state is CognitiveCycleNodeState.NOT_RECORDED:
            raise ValueError("cognitive observer cannot record absent observation")
        self._records[record.node_id] = record
        return self.cycle

    @property
    def cycle(self) -> CanonicalCognitiveCycle:
        return create_canonical_cognitive_cycle(
            self._cycle_id,
            tuple(self._records.values()),
            architecture=self._architecture,
        )

    @property
    def diagnostics(self) -> CognitiveCycleObserverDiagnostic:
        cycle = self.cycle
        observed = len(self._records)
        return CognitiveCycleObserverDiagnostic(
            cycle=cycle,
            observed_nodes=observed,
            remaining_nodes=len(cycle.nodes) - observed,
            sealed=self._sealed,
        )

    def seal(self) -> CanonicalCognitiveCycle:
        self._sealed = True
        return self.cycle
