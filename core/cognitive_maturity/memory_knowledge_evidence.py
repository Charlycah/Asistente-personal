from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_memory_knowledge_evidence_sink",
    default=None,
)
_KNOWLEDGE_PLAN_STATUS: ContextVar[str | None] = ContextVar(
    "roby_knowledge_plan_status",
    default=None,
)


class MemoryKnowledgeEvidenceAdapter:
    """Translate productive recall metadata into redacted node evidence."""

    MEMORY_NODE_ID = "memory_recall"
    KNOWLEDGE_NODE_ID = "knowledge_retrieval"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("memory knowledge evidence sink must be callable")
        sink_token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        plan_token: Token[str | None] = _KNOWLEDGE_PLAN_STATUS.set(None)
        try:
            yield
        finally:
            _KNOWLEDGE_PLAN_STATUS.reset(plan_token)
            _EVIDENCE_SINK.reset(sink_token)

    def observe_memory(
        self,
        *,
        runtime_available: bool,
        access_allowed: bool,
        recall_completed: bool,
        context_included: bool = False,
    ) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None
        if not runtime_available:
            record = CognitiveCycleNodeRecord(
                node_id=self.MEMORY_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("memory_recall:runtime_unavailable",),
            )
        elif not access_allowed:
            record = CognitiveCycleNodeRecord(
                node_id=self.MEMORY_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("memory_recall:private_context_denied",),
            )
        elif not recall_completed:
            record = CognitiveCycleNodeRecord(
                node_id=self.MEMORY_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("memory_recall:not_completed",),
            )
        else:
            detail = (
                "memory_recall:context_included"
                if context_included
                else "memory_recall:no_relevant_items"
            )
            record = CognitiveCycleNodeRecord(
                node_id=self.MEMORY_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("memory_recall:completed", detail),
            )
        sink(record)
        return record

    @staticmethod
    def observe_knowledge_plan(status: object) -> None:
        if _EVIDENCE_SINK.get() is None:
            return
        value = getattr(status, "value", status)
        _KNOWLEDGE_PLAN_STATUS.set(str(value).strip().casefold())

    def observe_knowledge_execution(
        self,
        execution: object | None,
    ) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None
        plan_status = _KNOWLEDGE_PLAN_STATUS.get()
        if plan_status == "not_applicable":
            record = CognitiveCycleNodeRecord(
                node_id=self.KNOWLEDGE_NODE_ID,
                state=CognitiveCycleNodeState.OMITTED,
                reason_codes=("knowledge_retrieval:not_applicable",),
            )
        elif plan_status == "withheld":
            record = CognitiveCycleNodeRecord(
                node_id=self.KNOWLEDGE_NODE_ID,
                state=CognitiveCycleNodeState.BLOCKED,
                reason_codes=("knowledge_retrieval:withheld",),
            )
        elif execution is None:
            record = CognitiveCycleNodeRecord(
                node_id=self.KNOWLEDGE_NODE_ID,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=("knowledge_retrieval:planned",),
                reason_codes=("knowledge_retrieval:execution_missing",),
            )
        else:
            status = getattr(getattr(execution, "status", None), "value", None)
            performed = bool(getattr(execution, "retrieval_performed", False))
            if status == "completed" and performed:
                record = CognitiveCycleNodeRecord(
                    node_id=self.KNOWLEDGE_NODE_ID,
                    state=CognitiveCycleNodeState.PARTICIPATED,
                    evidence_codes=("knowledge_retrieval:completed",),
                )
            elif status in {"withheld", "not_applicable"}:
                state = (
                    CognitiveCycleNodeState.BLOCKED
                    if status == "withheld"
                    else CognitiveCycleNodeState.OMITTED
                )
                record = CognitiveCycleNodeRecord(
                    node_id=self.KNOWLEDGE_NODE_ID,
                    state=state,
                    reason_codes=(f"knowledge_retrieval:{status}",),
                )
            else:
                evidence = (
                    ("knowledge_retrieval:partial_result",)
                    if performed
                    else ("knowledge_retrieval:planned",)
                )
                record = CognitiveCycleNodeRecord(
                    node_id=self.KNOWLEDGE_NODE_ID,
                    state=CognitiveCycleNodeState.DEGRADED,
                    evidence_codes=evidence,
                    reason_codes=(
                        f"knowledge_retrieval:{status or 'execution_unknown'}",
                    ),
                )
        sink(record)
        return record
