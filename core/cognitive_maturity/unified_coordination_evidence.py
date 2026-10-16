from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

_COORDINATION_ACTIVE: ContextVar[bool] = ContextVar(
    "roby_unified_coordination_evidence_active",
    default=False,
)


class UnifiedCoordinationEvidenceAdapter:
    """Expose a scoped fact while UnifiedBrain delegates to the gateway."""

    EVIDENCE_CODE = "unified_brain:delegated"
    NODE_ID = "unified_coordination"

    @contextmanager
    def activate(self) -> Iterator[None]:
        token: Token[bool] = _COORDINATION_ACTIVE.set(True)
        try:
            yield
        finally:
            _COORDINATION_ACTIVE.reset(token)

    def current_record(self) -> CognitiveCycleNodeRecord | None:
        if not _COORDINATION_ACTIVE.get():
            return None
        return CognitiveCycleNodeRecord(
            node_id=self.NODE_ID,
            state=CognitiveCycleNodeState.PARTICIPATED,
            evidence_codes=(self.EVIDENCE_CODE,),
        )
