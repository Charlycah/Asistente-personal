from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .target_architecture import (
    TARGET_COGNITIVE_ARCHITECTURE,
    TargetCognitiveArchitecture,
)

_SAFE_CODE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,127}$")


class CognitiveCycleNodeState(str, Enum):
    NOT_RECORDED = "not_recorded"
    PARTICIPATED = "participated"
    OMITTED = "omitted"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


class CognitiveCycleOutcome(str, Enum):
    UNOBSERVED = "unobserved"
    COMPLETE = "complete"
    PARTIAL = "partial"
    DEGRADED = "degraded"
    BLOCKED = "blocked"


def _safe_codes(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    normalized = tuple(item.strip().casefold() for item in values)
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"cognitive cycle {label} must be unique")
    if any(not _SAFE_CODE.fullmatch(item) for item in normalized):
        raise ValueError(f"cognitive cycle {label} must use safe codes")
    return normalized


@dataclass(frozen=True)
class CognitiveCycleNodeRecord:
    node_id: str
    state: CognitiveCycleNodeState | str
    evidence_codes: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        node_id = self.node_id.strip().casefold()
        state = CognitiveCycleNodeState(self.state)
        if not _SAFE_CODE.fullmatch(node_id):
            raise ValueError("cognitive cycle node id must use a safe code")
        evidence = _safe_codes(self.evidence_codes, "evidence codes")
        reasons = _safe_codes(self.reason_codes, "reason codes")
        if state is CognitiveCycleNodeState.NOT_RECORDED and (
            evidence or reasons
        ):
            raise ValueError("unrecorded cognitive node cannot claim metadata")
        if state is CognitiveCycleNodeState.PARTICIPATED:
            if not evidence:
                raise ValueError("participating cognitive node requires evidence")
            if reasons:
                raise ValueError("participating cognitive node cannot claim a reason")
        if state in {
            CognitiveCycleNodeState.OMITTED,
            CognitiveCycleNodeState.DEGRADED,
            CognitiveCycleNodeState.BLOCKED,
        } and not reasons:
            raise ValueError("non-participating cognitive node requires a reason")
        if state is CognitiveCycleNodeState.DEGRADED and not evidence:
            raise ValueError("degraded cognitive node requires partial evidence")
        object.__setattr__(self, "node_id", node_id)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "evidence_codes", evidence)
        object.__setattr__(self, "reason_codes", reasons)


@dataclass(frozen=True)
class CanonicalCognitiveCycle:
    cycle_id: str
    nodes: tuple[CognitiveCycleNodeRecord, ...]
    schema_version: str = "m386.9"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False

    def __post_init__(self) -> None:
        cycle_id = self.cycle_id.strip().casefold()
        if not _SAFE_CODE.fullmatch(cycle_id):
            raise ValueError("canonical cognitive cycle id must use a safe code")
        if self.schema_version != "m386.9":
            raise ValueError("canonical cognitive cycle schema is unsupported")
        if not self.read_only or self.grants_authority:
            raise ValueError("canonical cognitive cycle must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("canonical cognitive cycle cannot contain content")
        expected = tuple(
            node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        )
        actual = tuple(node.node_id for node in self.nodes)
        if actual != expected:
            raise ValueError(
                "canonical cognitive cycle nodes must match target graph order"
            )
        object.__setattr__(self, "cycle_id", cycle_id)
        object.__setattr__(self, "nodes", tuple(self.nodes))

    @property
    def outcome(self) -> CognitiveCycleOutcome:
        states = tuple(node.state for node in self.nodes)
        if all(state is CognitiveCycleNodeState.NOT_RECORDED for state in states):
            return CognitiveCycleOutcome.UNOBSERVED
        if any(state is CognitiveCycleNodeState.BLOCKED for state in states):
            return CognitiveCycleOutcome.BLOCKED
        if any(state is CognitiveCycleNodeState.DEGRADED for state in states):
            return CognitiveCycleOutcome.DEGRADED
        if all(state is CognitiveCycleNodeState.PARTICIPATED for state in states):
            return CognitiveCycleOutcome.COMPLETE
        return CognitiveCycleOutcome.PARTIAL

    def node(self, node_id: str) -> CognitiveCycleNodeRecord:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id == normalized:
                return node
        raise KeyError(node_id)

    def count(self, state: CognitiveCycleNodeState) -> int:
        return sum(node.state is state for node in self.nodes)


def create_canonical_cognitive_cycle(
    cycle_id: str,
    records: tuple[CognitiveCycleNodeRecord, ...] = (),
    architecture: TargetCognitiveArchitecture = TARGET_COGNITIVE_ARCHITECTURE,
) -> CanonicalCognitiveCycle:
    expected_ids = tuple(node.node_id for node in architecture.nodes)
    supplied = {record.node_id: record for record in records}
    if len(supplied) != len(records):
        raise ValueError("canonical cognitive cycle records must be unique")
    unknown = set(supplied) - set(expected_ids)
    if unknown:
        raise ValueError("canonical cognitive cycle references unknown nodes")
    nodes = tuple(
        supplied.get(
            node_id,
            CognitiveCycleNodeRecord(
                node_id=node_id,
                state=CognitiveCycleNodeState.NOT_RECORDED,
            ),
        )
        for node_id in expected_ids
    )
    return CanonicalCognitiveCycle(cycle_id=cycle_id, nodes=nodes)
