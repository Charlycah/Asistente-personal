from __future__ import annotations

from dataclasses import dataclass

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState
from .simulated_inner_state import (
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
)
from .unified_epistemic_evidence import UnifiedEpistemicCategory


@dataclass(frozen=True)
class SafeRelationalAffectiveIntegration:
    """Read-only translation of governed relational evidence into M390 signals."""

    evaluator_id: str = "safe_relational_affective_integration"
    node_id: str = "relational_affective_context"
    read_only: bool = True
    grants_authority: bool = False
    infers_identity: bool = False
    infers_presence: bool = False
    persists_state: bool = False
    modifies_relationships: bool = False
    modifies_personality: bool = False

    def evaluate(
        self,
        record: CognitiveCycleNodeRecord | None,
    ) -> tuple[SimulatedInnerStateSignal, ...]:
        if record is None:
            return ()
        if record.node_id != self.node_id:
            raise ValueError(
                "relational integration requires canonical relational node"
            )
        if record.state is CognitiveCycleNodeState.NOT_RECORDED:
            return ()
        if record.state is CognitiveCycleNodeState.BLOCKED:
            return (self._blocked(record),)
        if record.state in {
            CognitiveCycleNodeState.OMITTED,
            CognitiveCycleNodeState.DEGRADED,
        }:
            return (self._uncertain(record),)
        return (self._participated(record),)

    @staticmethod
    def _participated(record: CognitiveCycleNodeRecord) -> SimulatedInnerStateSignal:
        confirmed = "relationship:confirmed_context" in record.evidence_codes
        return SimulatedInnerStateSignal(
            source_authority="relational_affective_context",
            source_reference="canonical_cycle_node",
            epistemic_category=UnifiedEpistemicCategory.OBSERVED,
            affective_tone=SimulatedAffectiveTone.NEUTRAL,
            activation_level=SimulatedActivationLevel.MODERATE,
            stability_level=SimulatedStabilityLevel.STABLE,
            concern_level=SimulatedConcernLevel.NONE,
            relational_openness=(
                SimulatedRelationalOpenness.OPEN
                if confirmed
                else SimulatedRelationalOpenness.BALANCED
            ),
            dominant_state=SimulatedDominantState.SUPPORTIVE,
            evidence_codes=tuple(
                sorted(
                    {
                        "affective_signal_from_relational_context",
                        *record.evidence_codes,
                    }
                )
            ),
        )

    @staticmethod
    def _uncertain(record: CognitiveCycleNodeRecord) -> SimulatedInnerStateSignal:
        return SimulatedInnerStateSignal(
            source_authority="relational_affective_context",
            source_reference="canonical_cycle_node",
            epistemic_category=UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION,
            affective_tone=SimulatedAffectiveTone.UNKNOWN,
            activation_level=SimulatedActivationLevel.UNKNOWN,
            stability_level=SimulatedStabilityLevel.UNKNOWN,
            concern_level=SimulatedConcernLevel.UNKNOWN,
            relational_openness=SimulatedRelationalOpenness.UNKNOWN,
            dominant_state=SimulatedDominantState.UNCERTAIN,
            evidence_codes=tuple(
                sorted(
                    {
                        "relational_context_not_sufficient_for_affective_claim",
                        *record.evidence_codes,
                        *record.reason_codes,
                    }
                )
            ),
        )

    @staticmethod
    def _blocked(record: CognitiveCycleNodeRecord) -> SimulatedInnerStateSignal:
        return SimulatedInnerStateSignal(
            source_authority="relational_affective_context",
            source_reference="canonical_cycle_node",
            epistemic_category=UnifiedEpistemicCategory.INSUFFICIENT_INFORMATION,
            affective_tone=SimulatedAffectiveTone.UNKNOWN,
            activation_level=SimulatedActivationLevel.UNKNOWN,
            stability_level=SimulatedStabilityLevel.UNKNOWN,
            concern_level=SimulatedConcernLevel.HIGH,
            relational_openness=SimulatedRelationalOpenness.RESERVED,
            dominant_state=SimulatedDominantState.CAUTIOUS,
            evidence_codes=tuple(
                sorted(
                    {
                        "relational_context_blocked_by_integrity_boundary",
                        *record.reason_codes,
                    }
                )
            ),
            risk_codes=("relational_affective_integrity_boundary",),
        )
