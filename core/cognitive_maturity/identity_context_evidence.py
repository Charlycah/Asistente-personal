from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from .cycle_contract import CognitiveCycleNodeRecord, CognitiveCycleNodeState

EvidenceSink = Callable[[CognitiveCycleNodeRecord], None]

_EVIDENCE_SINK: ContextVar[EvidenceSink | None] = ContextVar(
    "roby_identity_context_evidence_sink",
    default=None,
)
_INTERLOCUTOR_RESOLVED: ContextVar[bool] = ContextVar(
    "roby_interlocutor_resolved_for_identity_evidence",
    default=False,
)


class IdentityContextEvidenceAdapter:
    """Translate resolution flags into redacted canonical cycle evidence."""

    NODE_ID = "identity_and_context"

    @contextmanager
    def capture(
        self,
        sink: EvidenceSink,
        *,
        interlocutor_resolved: bool = False,
    ) -> Iterator[None]:
        if not callable(sink):
            raise TypeError("identity context evidence sink must be callable")
        token: Token[EvidenceSink | None] = _EVIDENCE_SINK.set(sink)
        interlocutor_token: Token[bool] = _INTERLOCUTOR_RESOLVED.set(
            interlocutor_resolved
        )
        try:
            yield
        finally:
            _INTERLOCUTOR_RESOLVED.reset(interlocutor_token)
            _EVIDENCE_SINK.reset(token)

    @staticmethod
    def current_interlocutor_resolved() -> bool:
        return _INTERLOCUTOR_RESOLVED.get()

    def observe_resolution(
        self,
        *,
        coownership_scoped: bool,
        session_scoped: bool,
        context_bounded: bool,
        interlocutor_resolved: bool,
    ) -> CognitiveCycleNodeRecord | None:
        sink = _EVIDENCE_SINK.get()
        if sink is None:
            return None
        checks = (
            (
                coownership_scoped,
                "identity_context:joint_coownership",
                "coownership:not_canonical",
            ),
            (
                session_scoped,
                "identity_context:session_scoped",
                "session:not_scoped",
            ),
            (
                context_bounded,
                "identity_context:bounded_history",
                "context:not_bounded",
            ),
            (
                interlocutor_resolved,
                "identity_context:interlocutor_resolved",
                "interlocutor:not_resolved",
            ),
        )
        evidence = tuple(code for passed, code, _ in checks if passed)
        reasons = tuple(reason for passed, _, reason in checks if not passed)
        if not reasons:
            state = CognitiveCycleNodeState.PARTICIPATED
        elif evidence:
            state = CognitiveCycleNodeState.DEGRADED
        else:
            state = CognitiveCycleNodeState.BLOCKED
        record = CognitiveCycleNodeRecord(
            node_id=self.NODE_ID,
            state=state,
            evidence_codes=evidence,
            reason_codes=reasons,
        )
        sink(record)
        return record
