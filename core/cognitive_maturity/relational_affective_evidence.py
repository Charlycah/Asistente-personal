from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_relational_affective_evidence_sink",
    default=None,
)


class RelationalAffectiveEvidenceAdapter:
    """Observe relational context and explicitly simulated expression."""

    NODE_ID = "relational_affective_context"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("relational affective evidence sink must be callable")
        token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        try:
            yield
        finally:
            _EVIDENCE_SINK.reset(token)

    def observe_context(
        self,
        *,
        interlocutor_resolved: bool,
        relationship_snapshot: object | None,
        personality_profile: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None
        if not interlocutor_resolved:
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("relational_affective:interlocutor_unresolved",),
            )
        elif self._violates_integrity(personality_profile):
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("relational_affective:integrity_violation",),
            )
        elif relationship_snapshot is None and personality_profile is None:
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("relational_affective:authorities_unavailable",),
            )
        else:
            evidence = []
            reasons = []
            if relationship_snapshot is None:
                reasons.append("relational_affective:relationship_unavailable")
            else:
                evidence.append("relationship:snapshot_read")
                evidence.append(
                    "relationship:confirmed_context"
                    if bool(getattr(relationship_snapshot, "has_context", False))
                    else "relationship:no_confirmed_context"
                )
            if personality_profile is None:
                reasons.append("relational_affective:simulation_unavailable")
            else:
                evidence.extend(
                    (
                        "affect:explicitly_simulated",
                        "expression:profile_available",
                    )
                )
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=(
                    CognitiveCycleNodeState.PARTICIPATED
                    if not reasons
                    else CognitiveCycleNodeState.DEGRADED
                ),
                evidence_codes=tuple(evidence),
                reason_codes=tuple(reasons),
            )
        sink(record)
        return record

    @staticmethod
    def _violates_integrity(profile: object | None) -> bool:
        if profile is None:
            return False
        return bool(
            getattr(profile, "identity_changed", False)
            or getattr(profile, "creates_parallel_brain", False)
        )
