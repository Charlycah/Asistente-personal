from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_reflection_learning_evidence_sink",
    default=None,
)
_OBSERVED_NODES: ContextVar[frozenset[str]] = ContextVar(
    "roby_reflection_learning_observed_nodes",
    default=frozenset(),
)


def _value(item: object | None) -> str:
    return str(getattr(item, "value", item or "missing")).strip().casefold()


class ReflectionLearningEvidenceAdapter:
    """Observe post-turn reflection and review-only learning candidates."""

    REFLECTION_NODE_ID = "post_turn_reflection"
    LEARNING_NODE_ID = "learning_candidate"
    DIAGNOSTICS_NODE_ID = "unified_diagnostics"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("reflection learning evidence sink must be callable")
        sink_token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        nodes_token: Token[frozenset[str]] = _OBSERVED_NODES.set(frozenset())
        try:
            yield
        finally:
            _OBSERVED_NODES.reset(nodes_token)
            _EVIDENCE_SINK.reset(sink_token)

    def _emit(
        self,
        record: CognitiveCycleNodeRecord,
    ) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None or record.node_id in _OBSERVED_NODES.get():
            return None
        sink(record)
        _OBSERVED_NODES.set(_OBSERVED_NODES.get() | {record.node_id})
        return record

    def observe_reflection(
        self,
        reflection: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        if reflection is None:
            record = CognitiveCycleNodeRecord(
                node_id=self.REFLECTION_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("post_turn_reflection:not_observed",),
            )
        else:
            evidence = ["post_turn_reflection:metadata_observed"]
            if _value(getattr(reflection, "response_path", None)) == "degraded":
                evidence.append("post_turn_reflection:degradation_assessed")
            record = CognitiveCycleNodeRecord(
                node_id=self.REFLECTION_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=tuple(evidence),
            )
        return self._emit(record)

    def observe_learning_candidate(
        self,
        candidate: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        if candidate is None:
            record = CognitiveCycleNodeRecord(
                node_id=self.LEARNING_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("learning_candidate:none_proposed",),
            )
        elif (
            _value(getattr(candidate, "disposition", None)) == "review_required"
            and not bool(getattr(candidate, "accepted_as_knowledge", False))
            and not bool(getattr(candidate, "persistence_authorized", False))
        ):
            record = CognitiveCycleNodeRecord(
                node_id=self.LEARNING_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("learning_candidate:review_required",),
            )
        else:
            record = CognitiveCycleNodeRecord(
                node_id=self.LEARNING_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("learning_candidate:governance_violation",),
            )
        return self._emit(record)

    def observe_diagnostics(
        self,
        *,
        reflection_observed: bool,
        learning_assessed: bool,
    ) -> CognitiveCycleNodeRecord | None:
        if reflection_observed and learning_assessed:
            record = CognitiveCycleNodeRecord(
                node_id=self.DIAGNOSTICS_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("unified_diagnostics:turn_closure_observed",),
            )
        elif reflection_observed or learning_assessed:
            record = CognitiveCycleNodeRecord(
                node_id=self.DIAGNOSTICS_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("unified_diagnostics:closure_attempted",),
                reason_codes=("unified_diagnostics:incomplete_observation",),
            )
        else:
            record = CognitiveCycleNodeRecord(
                node_id=self.DIAGNOSTICS_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("unified_diagnostics:not_observed",),
            )
        return self._emit(record)
