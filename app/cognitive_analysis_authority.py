from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity import CognitiveTurnDossier
from core.cognitive_maturity.cycle_contract import CognitiveCycleNodeState
from core.cognitive_maturity.target_architecture import (
    TARGET_COGNITIVE_ARCHITECTURE,
)


class CognitiveAnalysisStatus(StrEnum):
    COMPLETED = "completed"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class CognitiveEpistemicSummary:
    levels_present: tuple[str, ...]
    unknown_present: bool
    evidence_codes: tuple[str, ...]
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class CognitiveAnalysisReport:
    report_id: str
    dossier_id: str
    cycle_id: str
    source_evidence_fingerprint: str
    cycle_outcome: str
    participating_authorities: tuple[str, ...]
    visited_node_ids: tuple[str, ...]
    degraded_node_ids: tuple[str, ...]
    blocked_node_ids: tuple[str, ...]
    unknown_node_ids: tuple[str, ...]
    contradiction_codes: tuple[str, ...]
    risk_codes: tuple[str, ...]
    epistemic_summary: CognitiveEpistemicSummary
    analysis_fingerprint: str
    schema_version: str = "m389.1"
    read_only: bool = True
    deterministic: bool = True
    grants_authority: bool = False
    contains_conversation_content: bool = False
    modifies_productive_state: bool = False


@dataclass(frozen=True)
class CognitiveAnalysisResult:
    status: CognitiveAnalysisStatus
    report: CognitiveAnalysisReport | None
    failure_code: str | None = None
    read_only: bool = True
    affects_turn_result: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        completed = self.status is CognitiveAnalysisStatus.COMPLETED
        if completed != (self.report is not None):
            raise ValueError("completed analysis requires exactly one report")
        if completed == (self.failure_code is not None):
            raise ValueError("degraded analysis requires one failure code")


class CognitiveAnalysisAuthority:
    """Single pure authority for deterministic post-turn cognitive analysis."""

    AUTHORITY_KEY = "cognitive_analysis_authority"

    def analyze(self, dossier: CognitiveTurnDossier) -> CognitiveAnalysisReport:
        if not isinstance(dossier, CognitiveTurnDossier):
            raise TypeError("cognitive analysis requires a cognitive turn dossier")
        if not dossier.read_only or dossier.grants_authority:
            raise ValueError("cognitive analysis source must remain read-only")

        visited = tuple(
            node.node_id
            for node in dossier.nodes
            if node.state is not CognitiveCycleNodeState.NOT_RECORDED
        )
        participated = tuple(
            TARGET_COGNITIVE_ARCHITECTURE.node(node_id).existing_authority
            for node_id in dossier.participated_node_ids
        )
        degraded = self._node_ids(dossier, CognitiveCycleNodeState.DEGRADED)
        blocked = self._node_ids(dossier, CognitiveCycleNodeState.BLOCKED)
        unknown = self._node_ids(dossier, CognitiveCycleNodeState.NOT_RECORDED)
        all_codes = tuple(
            code
            for node in dossier.nodes
            for code in (*node.evidence_codes, *node.reason_codes)
        )
        contradictions = tuple(
            code for code in all_codes if "contradict" in code or "conflict" in code
        )
        risks = tuple(
            f"analysis:degraded:{node_id}" for node_id in degraded
        ) + tuple(f"analysis:blocked:{node_id}" for node_id in blocked)
        epistemic = self._epistemic_summary(dossier)
        fingerprint = self._fingerprint(
            dossier=dossier,
            participating_authorities=participated,
            visited_node_ids=visited,
            degraded_node_ids=degraded,
            blocked_node_ids=blocked,
            unknown_node_ids=unknown,
            contradiction_codes=contradictions,
            risk_codes=risks,
            epistemic_summary=epistemic,
        )
        return CognitiveAnalysisReport(
            report_id=f"analysis-{dossier.cycle_id}",
            dossier_id=dossier.dossier_id,
            cycle_id=dossier.cycle_id,
            source_evidence_fingerprint=dossier.evidence_fingerprint,
            cycle_outcome=dossier.outcome.value,
            participating_authorities=participated,
            visited_node_ids=visited,
            degraded_node_ids=degraded,
            blocked_node_ids=blocked,
            unknown_node_ids=unknown,
            contradiction_codes=contradictions,
            risk_codes=risks,
            epistemic_summary=epistemic,
            analysis_fingerprint=fingerprint,
        )

    @staticmethod
    def _node_ids(
        dossier: CognitiveTurnDossier,
        state: CognitiveCycleNodeState,
    ) -> tuple[str, ...]:
        return tuple(node.node_id for node in dossier.nodes if node.state is state)

    @staticmethod
    def _epistemic_summary(
        dossier: CognitiveTurnDossier,
    ) -> CognitiveEpistemicSummary:
        node = dossier.node("epistemic_classification")
        ordered_levels = ("fact", "inference", "hypothesis", "unknown")
        levels = tuple(
            level
            for level in ordered_levels
            if f"epistemic:{level}" in node.evidence_codes
        )
        return CognitiveEpistemicSummary(
            levels_present=levels,
            unknown_present="unknown" in levels,
            evidence_codes=node.evidence_codes,
            reason_codes=node.reason_codes,
        )

    @staticmethod
    def _fingerprint(
        *,
        dossier: CognitiveTurnDossier,
        participating_authorities: tuple[str, ...],
        visited_node_ids: tuple[str, ...],
        degraded_node_ids: tuple[str, ...],
        blocked_node_ids: tuple[str, ...],
        unknown_node_ids: tuple[str, ...],
        contradiction_codes: tuple[str, ...],
        risk_codes: tuple[str, ...],
        epistemic_summary: CognitiveEpistemicSummary,
    ) -> str:
        values = (
            "m389.1",
            dossier.dossier_id,
            dossier.evidence_fingerprint,
            dossier.outcome.value,
            *participating_authorities,
            *visited_node_ids,
            *degraded_node_ids,
            *blocked_node_ids,
            *unknown_node_ids,
            *contradiction_codes,
            *risk_codes,
            *epistemic_summary.levels_present,
            *epistemic_summary.evidence_codes,
            *epistemic_summary.reason_codes,
        )
        return sha256("|".join(values).encode("utf-8")).hexdigest()

