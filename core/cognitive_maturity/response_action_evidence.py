from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_response_action_evidence_sink",
    default=None,
)
_OBSERVED_NODES: ContextVar[frozenset[str]] = ContextVar(
    "roby_response_action_observed_nodes",
    default=frozenset(),
)


def _value(item: object | None) -> str:
    return str(getattr(item, "value", item or "missing")).strip().casefold()


class ResponseActionEvidenceAdapter:
    """Observe response composition and official action boundaries."""

    RESPONSE_NODE_ID = "response_composition"
    ACTION_NODE_ID = "action_gate"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("response action evidence sink must be callable")
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

    def observe_response_status(
        self,
        status: object,
    ) -> CognitiveCycleNodeRecord | None:
        normalized = _value(status)
        if normalized == "completed":
            record = CognitiveCycleNodeRecord(
                node_id=self.RESPONSE_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("response_composition:completed",),
            )
        elif normalized == "partial":
            record = CognitiveCycleNodeRecord(
                node_id=self.RESPONSE_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("response_composition:deliverable",),
                reason_codes=("response_composition:limitations_present",),
            )
        elif normalized == "not_applicable":
            record = CognitiveCycleNodeRecord(
                node_id=self.RESPONSE_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("response_composition:not_applicable",),
            )
        elif normalized == "withheld":
            record = CognitiveCycleNodeRecord(
                node_id=self.RESPONSE_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("response_composition:withheld",),
            )
        else:
            record = CognitiveCycleNodeRecord(
                node_id=self.RESPONSE_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("response_composition:attempted",),
                reason_codes=("response_composition:failed",),
            )
        return self._emit(record)

    def observe_tool_context(
        self,
        context: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        status = _value(getattr(context, "status", None))
        if status == "executed":
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("action_gate:tool_gateway_routed",),
            )
        elif status == "blocked":
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("action_gate:tool_execution_blocked",),
            )
        elif status == "failed":
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("action_gate:tool_gateway_invoked",),
                reason_codes=("action_gate:tool_execution_failed",),
            )
        else:
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("action_gate:no_tool_requested",),
            )
        return self._emit(record)

    def observe_official_capability(
        self,
        *,
        external_scope: bool,
        completed: bool,
    ) -> CognitiveCycleNodeRecord | None:
        if not completed:
            return None
        if not external_scope:
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("action_gate:no_external_effect_claimed",),
            )
        else:
            record = CognitiveCycleNodeRecord(
                node_id=self.ACTION_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("action_gate:official_capability_completed",),
                reason_codes=("action_gate:generic_permission_proof_unavailable",),
            )
        return self._emit(record)
