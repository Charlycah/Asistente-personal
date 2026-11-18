"""In-memory, non-authorizing terminal execution reuse guard.

A reservation is structural only. It cannot authenticate a producer,
grant permissions, register provenance, or admit a conversation turn.
"""

from dataclasses import dataclass
from enum import Enum
from threading import RLock

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
)
from app.cross_domain_invocation_capture import InvocationCaptureSnapshot
from app.cross_domain_terminal_evidence_binding import (
    TerminalBindingDecision,
    bind_terminal_evidence,
)


class TerminalReuseDecision(str, Enum):
    RESERVED = "reserved"
    IDEMPOTENT = "idempotent"
    CONFLICT = "conflict"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class TerminalReuseResult:
    decision: TerminalReuseDecision

    def __post_init__(self) -> None:
        if type(self.decision) is not TerminalReuseDecision:
            raise ValueError("invalid reuse decision")


@dataclass(frozen=True)
class _Reservation:
    owner: str
    session_id: str
    invocation_id: str
    execution_id: str
    source_id: str
    status: str
    item_count: int


class CrossDomainTerminalReuseGuard:
    """Prevent conflicting terminal associations within one registry."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._by_execution: dict[str, _Reservation] = {}
        self._by_invocation: dict[str, _Reservation] = {}

    def reserve(
        self,
        *,
        snapshot: object,
        evidence: object,
        owner: str,
        session_id: str,
    ) -> TerminalReuseResult:
        """Reserve only after structural matching, never authorization."""
        binding = bind_terminal_evidence(
            snapshot=snapshot,
            evidence=evidence,
            owner=owner,
            session_id=session_id,
        )

        if binding.decision is TerminalBindingDecision.REJECTED:
            return TerminalReuseResult(TerminalReuseDecision.REJECTED)

        if binding.decision is TerminalBindingDecision.UNRESOLVED:
            return TerminalReuseResult(TerminalReuseDecision.UNRESOLVED)

        # Exact types and identity were checked by the binding function.
        if (
            type(snapshot) is not InvocationCaptureSnapshot
            or type(evidence) is not GovernedTerminalExecutionEvidence
            or binding.invocation_id is None
            or binding.execution_id is None
        ):
            return TerminalReuseResult(TerminalReuseDecision.REJECTED)

        candidate = _Reservation(
            owner=owner,
            session_id=session_id,
            invocation_id=binding.invocation_id,
            execution_id=binding.execution_id,
            source_id=evidence.source_id,
            status=evidence.status.value,
            item_count=evidence.item_count,
        )

        with self._lock:
            existing_execution = self._by_execution.get(
                candidate.execution_id
            )
            existing_invocation = self._by_invocation.get(
                candidate.invocation_id
            )

            if (
                existing_execution is None
                and existing_invocation is None
            ):
                self._by_execution[candidate.execution_id] = candidate
                self._by_invocation[candidate.invocation_id] = candidate
                return TerminalReuseResult(
                    TerminalReuseDecision.RESERVED
                )

            if (
                existing_execution == candidate
                and existing_invocation == candidate
            ):
                return TerminalReuseResult(
                    TerminalReuseDecision.IDEMPOTENT
                )

            # Do not disclose the conflicting owner, session, or ID.
            return TerminalReuseResult(
                TerminalReuseDecision.CONFLICT
            )
