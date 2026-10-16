from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
)


def cognitive_dossier():
    cycle = create_canonical_cognitive_cycle(
        "turn-m389-1",
        (
            CognitiveCycleNodeRecord(
                "conversation_ingress",
                CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("gateway:accepted",),
            ),
            CognitiveCycleNodeRecord(
                "epistemic_classification",
                CognitiveCycleNodeState.DEGRADED,
                evidence_codes=(
                    "epistemic:fact",
                    "epistemic:inference",
                    "epistemic:hypothesis",
                    "epistemic:unknown",
                ),
                reason_codes=("epistemic:uncertainty_present",),
            ),
            CognitiveCycleNodeRecord(
                "cognitive_state",
                CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("cognitive_state:read_failed",),
                reason_codes=("cognitive_state:authority_unavailable",),
            ),
            CognitiveCycleNodeRecord(
                "action_gate",
                CognitiveCycleNodeState.BLOCKED,
                reason_codes=("permission:conflict",),
            ),
        ),
    )
    return create_cognitive_turn_dossier(cycle)

