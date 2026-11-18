"""Non-authorizing binding of invocation identity to terminal evidence.

Caller-supplied evidence is not producer authentication. This module
does not execute queries, grant capabilities, or admit provenance.
"""

from dataclasses import dataclass
from enum import Enum

from app.cross_domain_execution_attestation import (
    CrossDomainExecutionAttestationRegistry,
    ExecutionAttestationDecision,
)
from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
)


def _valid(value: object) -> bool:
    return (
        type(value) is str
        and bool(value.strip())
        and value == value.strip()
    )


class ExecutionBindingDecision(str, Enum):
    BOUND = "bound"
    VERIFIED = "verified"
    CONSUMED = "consumed"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ExecutionBindingResult:
    decision: ExecutionBindingDecision
    invocation_id: str | None = None
    execution_id: str | None = None
    producer_verified: bool = False

    def __post_init__(self) -> None:
        if type(self.decision) is not ExecutionBindingDecision:
            raise ValueError("invalid binding decision")

        if self.producer_verified is not False:
            raise ValueError("producer authentication is unavailable")

        positive = self.decision in (
            ExecutionBindingDecision.BOUND,
            ExecutionBindingDecision.VERIFIED,
            ExecutionBindingDecision.CONSUMED,
        )

        if positive:
            if not _valid(self.invocation_id):
                raise ValueError("missing invocation_id")
            if not _valid(self.execution_id):
                raise ValueError("missing execution_id")
        elif self.invocation_id is not None or self.execution_id is not None:
            raise ValueError("negative binding cannot expose identifiers")


class CrossDomainExecutionBinder:
    """Bind terminal evidence to an instance-local invocation registry."""

    def __init__(self) -> None:
        self._registry = CrossDomainExecutionAttestationRegistry()

    @staticmethod
    def _fields(
        *,
        invocation_id: str,
        owner: str,
        session_id: str,
        evidence: GovernedTerminalExecutionEvidence,
    ) -> dict[str, str] | None:
        if not all(
            _valid(value)
            for value in (invocation_id, owner, session_id)
        ):
            return None

        if type(evidence) is not GovernedTerminalExecutionEvidence:
            return None

        if not _valid(evidence.execution_id):
            return None

        if not _valid(evidence.source_id):
            return None

        if evidence.producer_verified is not False:
            return None

        if evidence.status is GovernedTerminalStatus.REJECTED:
            return None

        if evidence.response_present is not True:
            return None

        return {
            "invocation_id": invocation_id,
            "execution_id": evidence.execution_id,
            "owner": owner,
            "session_id": session_id,
            "source_id": evidence.source_id,
        }

    def bind(
        self,
        *,
        invocation_id: str,
        owner: str,
        session_id: str,
        evidence: GovernedTerminalExecutionEvidence,
    ) -> ExecutionBindingResult:
        fields = self._fields(
            invocation_id=invocation_id,
            owner=owner,
            session_id=session_id,
            evidence=evidence,
        )
        if fields is None:
            return ExecutionBindingResult(
                ExecutionBindingDecision.REJECTED
            )

        recorded = self._registry.record(**fields)
        if recorded.decision is not ExecutionAttestationDecision.RECORDED:
            return ExecutionBindingResult(
                ExecutionBindingDecision.REJECTED
            )

        return ExecutionBindingResult(
            ExecutionBindingDecision.BOUND,
            invocation_id=fields["invocation_id"],
            execution_id=fields["execution_id"],
        )

    def verify(
        self,
        *,
        invocation_id: str,
        owner: str,
        session_id: str,
        evidence: GovernedTerminalExecutionEvidence,
    ) -> ExecutionBindingResult:
        fields = self._fields(
            invocation_id=invocation_id,
            owner=owner,
            session_id=session_id,
            evidence=evidence,
        )
        if fields is None:
            return ExecutionBindingResult(
                ExecutionBindingDecision.REJECTED
            )

        verified = self._registry.verify(**fields)
        if verified.decision is not ExecutionAttestationDecision.VERIFIED:
            return ExecutionBindingResult(
                ExecutionBindingDecision.UNRESOLVED
            )

        return ExecutionBindingResult(
            ExecutionBindingDecision.VERIFIED,
            invocation_id=fields["invocation_id"],
            execution_id=fields["execution_id"],
        )

    def consume(
        self,
        *,
        invocation_id: str,
        owner: str,
        session_id: str,
        evidence: GovernedTerminalExecutionEvidence,
    ) -> ExecutionBindingResult:
        fields = self._fields(
            invocation_id=invocation_id,
            owner=owner,
            session_id=session_id,
            evidence=evidence,
        )
        if fields is None:
            return ExecutionBindingResult(
                ExecutionBindingDecision.REJECTED
            )

        consumed = self._registry.consume(**fields)
        if consumed.decision is not ExecutionAttestationDecision.CONSUMED:
            return ExecutionBindingResult(
                ExecutionBindingDecision.UNRESOLVED
            )

        return ExecutionBindingResult(
            ExecutionBindingDecision.CONSUMED,
            invocation_id=fields["invocation_id"],
            execution_id=fields["execution_id"],
        )
