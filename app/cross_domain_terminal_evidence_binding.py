"""Non-authorizing binding of invocation capture and terminal evidence.

MATCHED means structural consistency only. It does not authenticate
a producer, attest an execution, or authorize provenance.
"""

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
)
from app.cross_domain_invocation_capture import (
    InvocationCaptureSnapshot,
    InvocationCaptureState,
    InvocationExecutionStatus,
)


class TerminalBindingDecision(str, Enum):
    MATCHED = "matched"
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"


class TerminalBindingReason(str, Enum):
    STRUCTURAL_MATCH = "structural_match"
    INVALID_INPUT = "invalid_input"
    IDENTITY_MISMATCH = "identity_mismatch"
    INVOCATION_NOT_OBSERVED = "invocation_not_observed"
    EXECUTION_MISMATCH = "execution_mismatch"
    STATUS_MISMATCH = "status_mismatch"
    EXECUTION_NOT_SUCCESSFUL = "execution_not_successful"
    PRODUCER_NOT_VERIFIED = "producer_not_verified"


@dataclass(frozen=True)
class CrossDomainTerminalEvidenceBinding:
    decision: TerminalBindingDecision
    reason: TerminalBindingReason
    invocation_id: str | None = None
    execution_id: str | None = None

    def __post_init__(self) -> None:
        if type(self.decision) is not TerminalBindingDecision:
            raise ValueError("invalid decision")
        if type(self.reason) is not TerminalBindingReason:
            raise ValueError("invalid reason")

        matched = self.decision is TerminalBindingDecision.MATCHED
        if matched != (
            self.reason is TerminalBindingReason.STRUCTURAL_MATCH
        ):
            raise ValueError("inconsistent binding decision")

        if matched:
            if not _valid(self.invocation_id):
                raise ValueError("matched invocation missing")
            if not _valid(self.execution_id):
                raise ValueError("matched execution missing")
        elif (
            self.invocation_id is not None
            or self.execution_id is not None
        ):
            raise ValueError("unresolved binding cannot carry identifiers")


def _valid(value: object) -> bool:
    return (
        type(value) is str
        and bool(value.strip())
        and value == value.strip()
    )


def _result(
    decision: TerminalBindingDecision,
    reason: TerminalBindingReason,
    *,
    invocation_id: str | None = None,
    execution_id: str | None = None,
) -> CrossDomainTerminalEvidenceBinding:
    return CrossDomainTerminalEvidenceBinding(
        decision=decision,
        reason=reason,
        invocation_id=invocation_id,
        execution_id=execution_id,
    )


def bind_terminal_evidence(
    *,
    snapshot: object,
    evidence: object,
    owner: str,
    session_id: str,
) -> CrossDomainTerminalEvidenceBinding:
    """Compare structural values; never authenticate or admit provenance."""
    if (
        type(snapshot) is not InvocationCaptureSnapshot
        or type(evidence) is not GovernedTerminalExecutionEvidence
        or not _valid(owner)
        or not _valid(session_id)
    ):
        return _result(
            TerminalBindingDecision.REJECTED,
            TerminalBindingReason.INVALID_INPUT,
        )

    if snapshot.owner != owner or snapshot.session_id != session_id:
        return _result(
            TerminalBindingDecision.REJECTED,
            TerminalBindingReason.IDENTITY_MISMATCH,
        )

    if snapshot.state not in (
        InvocationCaptureState.OBSERVED,
        InvocationCaptureState.CLOSED,
    ) or snapshot.execution_id is None:
        return _result(
            TerminalBindingDecision.UNRESOLVED,
            TerminalBindingReason.INVOCATION_NOT_OBSERVED,
        )

    if evidence.execution_id != snapshot.execution_id:
        return _result(
            TerminalBindingDecision.REJECTED,
            TerminalBindingReason.EXECUTION_MISMATCH,
        )

    expected_status = {
        InvocationExecutionStatus.SUCCEEDED:
            GovernedTerminalStatus.SUCCEEDED,
        InvocationExecutionStatus.EMPTY:
            GovernedTerminalStatus.EMPTY,
        InvocationExecutionStatus.FAILED:
            GovernedTerminalStatus.FAILED,
        InvocationExecutionStatus.REJECTED:
            GovernedTerminalStatus.REJECTED,
    }.get(snapshot.execution_status)

    if expected_status is not evidence.status:
        return _result(
            TerminalBindingDecision.REJECTED,
            TerminalBindingReason.STATUS_MISMATCH,
        )

    if evidence.status is not GovernedTerminalStatus.SUCCEEDED:
        return _result(
            TerminalBindingDecision.UNRESOLVED,
            TerminalBindingReason.EXECUTION_NOT_SUCCESSFUL,
        )

    if evidence.producer_verified is not False:
        return _result(
            TerminalBindingDecision.UNRESOLVED,
            TerminalBindingReason.PRODUCER_NOT_VERIFIED,
        )

    return _result(
        TerminalBindingDecision.MATCHED,
        TerminalBindingReason.STRUCTURAL_MATCH,
        invocation_id=snapshot.invocation_id,
        execution_id=snapshot.execution_id,
    )
