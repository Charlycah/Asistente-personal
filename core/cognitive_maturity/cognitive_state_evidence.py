from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_cognitive_state_evidence_sink",
    default=None,
)


class CognitiveStateEvidenceAdapter:
    """Observe the canonical cognitive-state facade without copying content."""

    NODE_ID = "cognitive_state"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("cognitive state evidence sink must be callable")
        token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        try:
            yield
        finally:
            _EVIDENCE_SINK.reset(token)

    def observe_facade(self, facade: object) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None
        if not bool(getattr(facade, "bound", False)):
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("cognitive_state:authority_unavailable",),
            )
            sink(record)
            return record

        try:
            state = facade.current()
        except (RuntimeError, ValueError, TypeError):
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("cognitive_state:snapshot_attempted",),
                reason_codes=("cognitive_state:snapshot_unavailable",),
            )
            sink(record)
            return record

        evidence = ["cognitive_state:snapshot_read"]
        if bool(getattr(state, "is_empty", False)):
            evidence.append("cognitive_state:empty")
        else:
            if getattr(state, "active_objective", None) is not None:
                evidence.append("cognitive_state:objective_present")
            if getattr(state, "current_focus", None) is not None:
                evidence.append("cognitive_state:focus_present")
            if getattr(state, "last_decision", None) is not None:
                evidence.append("cognitive_state:last_decision_present")
            confidence = getattr(state, "confidence", None)
            if isinstance(confidence, (int, float)):
                evidence.append("cognitive_state:confidence_available")
        record = CognitiveCycleNodeRecord(
            node_id=self.NODE_ID,
            state=CognitiveCycleNodeState.PARTICIPATED,
            evidence_codes=tuple(evidence),
        )
        sink(record)
        return record
