from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_intent_reasoning_evidence_sink",
    default=None,
)

_INTENT_KINDS = frozenset(
    {
        "greeting",
        "question",
        "request",
        "continuation",
        "comment",
        "attention",
        "farewell",
        "incomplete",
        "not_applicable",
    }
)
_INTENT_ACTIONS = frozenset(
    {
        "route_to_greeting",
        "route_to_reasoning",
        "route_to_action",
        "route_to_context",
        "route_to_dialogue",
        "route_to_attention",
        "route_to_farewell",
        "request_completion",
        "withhold",
        "none",
    }
)
_REASONING_STATUSES = frozenset(
    {"completed", "abstained", "blocked", "review_required"}
)


def _value(item: object | None) -> str | None:
    if item is None:
        return None
    return str(getattr(item, "value", item)).strip().casefold()


class IntentReasoningEvidenceAdapter:
    """Observe canonical intent routing and governed reasoning metadata."""

    NODE_ID = "intent_and_reasoning"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("intent reasoning evidence sink must be callable")
        token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        try:
            yield
        finally:
            _EVIDENCE_SINK.reset(token)

    def observe(
        self,
        *,
        intent_kind: object,
        intent_action: object,
        reasoning_status: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        kind = _value(intent_kind)
        action = _value(intent_action)
        reasoning = _value(reasoning_status)
        if kind not in _INTENT_KINDS or action not in _INTENT_ACTIONS:
            raise ValueError("intent reasoning evidence is not canonical")
        if reasoning is not None and reasoning not in _REASONING_STATUSES:
            raise ValueError("reasoning status is not canonical")
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None

        evidence = (f"intent:{kind}", f"intent:{action}")
        if action in {"withhold", "request_completion", "none"}:
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                evidence_codes=evidence,
                reason_codes=("intent_reasoning:entry_not_routable",),
            )
        elif action != "route_to_reasoning":
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=(*evidence, "reasoning:not_required"),
            )
        elif reasoning == "completed":
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=(*evidence, "reasoning:completed"),
            )
        elif reasoning == "blocked":
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                evidence_codes=evidence,
                reason_codes=("reasoning:blocked",),
            )
        else:
            reason = (
                f"reasoning:{reasoning}"
                if reasoning is not None
                else "reasoning:result_missing"
            )
            record = CognitiveCycleNodeRecord(
                node_id=self.NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=evidence,
                reason_codes=(reason,),
            )
        sink(record)
        return record
