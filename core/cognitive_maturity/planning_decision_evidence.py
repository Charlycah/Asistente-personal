from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_planning_decision_evidence_sink",
    default=None,
)
_OBSERVED_NODES: ContextVar[frozenset[str]] = ContextVar(
    "roby_planning_decision_observed_nodes",
    default=frozenset(),
)


class PlanningDecisionEvidenceAdapter:
    """Observe planning, safety and decision without granting execution."""

    PLANNING_NODE_ID = "planning"
    SAFETY_NODE_ID = "safety_permissions"
    DECISION_NODE_ID = "decision"

    @contextmanager
    def capture(self, sink: EvidenceSink) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("planning decision evidence sink must be callable")
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

    def observe_direct_plan(
        self,
        *,
        safe_step_executed: bool,
    ) -> tuple[CognitiveCycleNodeRecord, ...]:
        emitted = []
        planning = self._emit(
            CognitiveCycleNodeRecord(
                node_id=self.PLANNING_NODE_ID,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("planning:governed_plan_completed",),
            )
        )
        if planning is not None:
            emitted.append(planning)
        safety = self._emit(
            CognitiveCycleNodeRecord(
                node_id=self.SAFETY_NODE_ID,
                state=(
                    CognitiveCycleNodeState.PARTICIPATED
                    if safe_step_executed
                    else CognitiveCycleNodeState.BLOCKED
                ),
                evidence_codes=(
                    ("safety_permissions:safe_capability_selected",)
                    if safe_step_executed
                    else ()
                ),
                reason_codes=(
                    ()
                    if safe_step_executed
                    else ("safety_permissions:no_safe_capability",)
                ),
            )
        )
        if safety is not None:
            emitted.append(safety)
        return tuple(emitted)

    def observe_unified_decision(
        self,
        *,
        scenario_detected: bool,
        safe_result_selected: bool,
    ) -> tuple[CognitiveCycleNodeRecord, ...]:
        if not scenario_detected:
            return ()
        emitted = []
        safety = self._emit(
            CognitiveCycleNodeRecord(
                node_id=self.SAFETY_NODE_ID,
                state=(
                    CognitiveCycleNodeState.PARTICIPATED
                    if safe_result_selected
                    else CognitiveCycleNodeState.BLOCKED
                ),
                evidence_codes=(
                    ("safety_permissions:coordinated_capabilities_checked",)
                    if safe_result_selected
                    else ()
                ),
                reason_codes=(
                    ()
                    if safe_result_selected
                    else ("safety_permissions:no_safe_capability",)
                ),
            )
        )
        if safety is not None:
            emitted.append(safety)
        decision = self._emit(
            CognitiveCycleNodeRecord(
                node_id=self.DECISION_NODE_ID,
                state=(
                    CognitiveCycleNodeState.PARTICIPATED
                    if safe_result_selected
                    else CognitiveCycleNodeState.DEGRADED
                ),
                evidence_codes=(
                    (
                        "decision:unified_coordination_completed"
                        if safe_result_selected
                        else "decision:scenario_detected"
                    ),
                ),
                reason_codes=(
                    ()
                    if safe_result_selected
                    else ("decision:no_safe_result",)
                ),
            )
        )
        if decision is not None:
            emitted.append(decision)
        return tuple(emitted)

    def observe_cognitive_runtime(
        self,
        result: object | None,
    ) -> tuple[CognitiveCycleNodeRecord, ...]:
        contributions = tuple(getattr(result, "contributions", ()))
        by_stage = {
            str(getattr(item, "stage", "")).strip().casefold(): item
            for item in contributions
        }
        planning = by_stage.get("planning")
        executive = by_stage.get("executive")
        emitted = []
        planning_record = self._contribution_record(
            self.PLANNING_NODE_ID,
            planning,
            applied_code="planning:approved_context_applied",
            skipped_reason="planning:not_required",
            failed_reason="planning:contributor_failed",
        )
        decision_record = self._contribution_record(
            self.DECISION_NODE_ID,
            executive,
            applied_code="decision:executive_coordination_applied",
            skipped_reason="decision:not_required",
            failed_reason="decision:contributor_failed",
        )
        for record in (planning_record, decision_record):
            observed = self._emit(record)
            if observed is not None:
                emitted.append(observed)
        applied = any(
            self._status(item) == "applied" for item in (planning, executive)
        )
        safety_record = CognitiveCycleNodeRecord(
            node_id=self.SAFETY_NODE_ID,
            state=(
                CognitiveCycleNodeState.PARTICIPATED
                if applied
                else CognitiveCycleNodeState.OMITTED
            ),
            evidence_codes=(
                ("safety_permissions:advisory_only",) if applied else ()
            ),
            reason_codes=(
                () if applied else ("safety_permissions:no_action_candidate",)
            ),
        )
        observed_safety = self._emit(safety_record)
        if observed_safety is not None:
            emitted.append(observed_safety)
        return tuple(emitted)

    def _contribution_record(
        self,
        node_id: str,
        contribution: object | None,
        *,
        applied_code: str,
        skipped_reason: str,
        failed_reason: str,
    ) -> CognitiveCycleNodeRecord:
        status = self._status(contribution)
        if status == "applied":
            return CognitiveCycleNodeRecord(
                node_id=node_id,
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=(applied_code,),
            )
        if status == "failed":
            return CognitiveCycleNodeRecord(
                node_id=node_id,
                state=CognitiveCycleNodeState.DEGRADED,
                evidence_codes=(f"{node_id}:contributor_invoked",),
                reason_codes=(failed_reason,),
            )
        return CognitiveCycleNodeRecord(
            node_id=node_id,
            state=CognitiveCycleNodeState.OMITTED,
            reason_codes=(skipped_reason,),
        )

    @staticmethod
    def _status(contribution: object | None) -> str:
        status = getattr(contribution, "status", None)
        return str(getattr(status, "value", status or "missing")).casefold()
