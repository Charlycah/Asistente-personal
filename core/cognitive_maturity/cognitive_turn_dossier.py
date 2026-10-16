from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from .cycle_contract import (
    CanonicalCognitiveCycle,
    CognitiveCycleNodeState,
    CognitiveCycleOutcome,
)
from .target_architecture import TARGET_COGNITIVE_ARCHITECTURE


@dataclass(frozen=True)
class CognitiveTurnDossierNode:
    node_id: str
    state: CognitiveCycleNodeState
    evidence_codes: tuple[str, ...]
    reason_codes: tuple[str, ...]

    def __post_init__(self) -> None:
        expected = TARGET_COGNITIVE_ARCHITECTURE.node(self.node_id).node_id
        if self.node_id != expected:
            raise ValueError("cognitive turn dossier node id is not canonical")
        if self.state is CognitiveCycleNodeState.NOT_RECORDED and (
            self.evidence_codes or self.reason_codes
        ):
            raise ValueError("unrecorded dossier node cannot claim metadata")


@dataclass(frozen=True)
class CognitiveTurnDossier:
    dossier_id: str
    cycle_id: str
    nodes: tuple[CognitiveTurnDossierNode, ...]
    outcome: CognitiveCycleOutcome
    participated_node_ids: tuple[str, ...]
    nonparticipating_node_ids: tuple[str, ...]
    connected_prefix_node_ids: tuple[str, ...]
    first_interruption_node_id: str | None
    evidence_fingerprint: str
    source_schema_version: str = "m386.9"
    schema_version: str = "m387.2"
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    persists_private_content: bool = False

    def __post_init__(self) -> None:
        expected = tuple(
            node.node_id for node in TARGET_COGNITIVE_ARCHITECTURE.nodes
        )
        actual = tuple(node.node_id for node in self.nodes)
        if actual != expected:
            raise ValueError("cognitive turn dossier must cover the target graph")
        if self.dossier_id != f"dossier-{self.cycle_id}":
            raise ValueError("cognitive turn dossier lineage is inconsistent")
        if self.source_schema_version != "m386.9" or self.schema_version != "m387.2":
            raise ValueError("cognitive turn dossier schema is unsupported")
        if not self.read_only or self.grants_authority:
            raise ValueError("cognitive turn dossier must remain advisory")
        if self.contains_conversation_content or self.persists_private_content:
            raise ValueError("cognitive turn dossier cannot contain private content")
        if self.evidence_fingerprint != _fingerprint(self.cycle_id, self.nodes):
            raise ValueError("cognitive turn dossier fingerprint is inconsistent")

    def node(self, node_id: str) -> CognitiveTurnDossierNode:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id == normalized:
                return node
        raise KeyError(node_id)


@dataclass(frozen=True)
class CognitiveTurnDossierSnapshot:
    dossiers: tuple[CognitiveTurnDossier, ...]
    total_dossiers: int
    latest_dossier: CognitiveTurnDossier | None
    read_only: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False

    def __post_init__(self) -> None:
        if self.total_dossiers != len(self.dossiers):
            raise ValueError("cognitive turn dossier count is inconsistent")
        expected_latest = self.dossiers[-1] if self.dossiers else None
        if self.latest_dossier != expected_latest:
            raise ValueError("cognitive turn latest dossier is inconsistent")
        ids = tuple(item.dossier_id for item in self.dossiers)
        if len(ids) != len(set(ids)):
            raise ValueError("cognitive turn dossier ids must be unique")
        if not self.read_only or self.grants_authority:
            raise ValueError("cognitive turn dossier snapshot must remain advisory")
        if self.contains_conversation_content:
            raise ValueError("cognitive turn dossier snapshot cannot contain content")


def _fingerprint(
    cycle_id: str,
    nodes: tuple[CognitiveTurnDossierNode, ...],
) -> str:
    parts = [cycle_id]
    for node in nodes:
        parts.extend(
            (
                node.node_id,
                node.state.value,
                ",".join(node.evidence_codes),
                ",".join(node.reason_codes),
            )
        )
    return sha256("|".join(parts).encode("utf-8")).hexdigest()


def create_cognitive_turn_dossier(
    cycle: CanonicalCognitiveCycle,
) -> CognitiveTurnDossier:
    nodes = tuple(
        CognitiveTurnDossierNode(
            node_id=node.node_id,
            state=node.state,
            evidence_codes=node.evidence_codes,
            reason_codes=node.reason_codes,
        )
        for node in cycle.nodes
    )
    participated = tuple(
        node.node_id
        for node in nodes
        if node.state is CognitiveCycleNodeState.PARTICIPATED
    )
    nonparticipating = tuple(
        node.node_id
        for node in nodes
        if node.state is not CognitiveCycleNodeState.PARTICIPATED
    )
    prefix = []
    for node in nodes:
        if node.state is not CognitiveCycleNodeState.PARTICIPATED:
            break
        prefix.append(node.node_id)
    return CognitiveTurnDossier(
        dossier_id=f"dossier-{cycle.cycle_id}",
        cycle_id=cycle.cycle_id,
        nodes=nodes,
        outcome=cycle.outcome,
        participated_node_ids=participated,
        nonparticipating_node_ids=nonparticipating,
        connected_prefix_node_ids=tuple(prefix),
        first_interruption_node_id=(
            nonparticipating[0] if nonparticipating else None
        ),
        evidence_fingerprint=_fingerprint(cycle.cycle_id, nodes),
        source_schema_version=cycle.schema_version,
    )


def create_cognitive_turn_dossier_snapshot(
    cycles: tuple[CanonicalCognitiveCycle, ...],
) -> CognitiveTurnDossierSnapshot:
    dossiers = tuple(create_cognitive_turn_dossier(cycle) for cycle in cycles)
    return CognitiveTurnDossierSnapshot(
        dossiers=dossiers,
        total_dossiers=len(dossiers),
        latest_dossier=dossiers[-1] if dossiers else None,
    )
