"""Instance-local execution attestation contract.

This registry records caller-supplied associations. It does not
authenticate a producer, grant capabilities, or admit provenance.
"""

from dataclasses import dataclass
from enum import Enum
from threading import RLock


def _valid(value: object) -> bool:
    return (
        type(value) is str
        and bool(value.strip())
        and value == value.strip()
    )


class ExecutionAttestationDecision(str, Enum):
    RECORDED = "recorded"
    VERIFIED = "verified"
    CONSUMED = "consumed"
    REJECTED = "rejected"
    UNRESOLVED = "unresolved"


class ExecutionAttestationState(str, Enum):
    RECORDED = "recorded"
    CONSUMED = "consumed"


@dataclass(frozen=True)
class ExecutionAttestation:
    invocation_id: str
    execution_id: str
    owner: str
    session_id: str
    source_id: str
    state: ExecutionAttestationState

    def __post_init__(self) -> None:
        for name in (
            "invocation_id",
            "execution_id",
            "owner",
            "session_id",
            "source_id",
        ):
            if not _valid(getattr(self, name)):
                raise ValueError(f"invalid {name}")

        if type(self.state) is not ExecutionAttestationState:
            raise ValueError("invalid attestation state")


@dataclass(frozen=True)
class ExecutionAttestationResult:
    decision: ExecutionAttestationDecision
    attestation: ExecutionAttestation | None = None

    def __post_init__(self) -> None:
        if type(self.decision) is not ExecutionAttestationDecision:
            raise ValueError("invalid attestation decision")

        has_record = self.attestation is not None

        if self.decision in (
            ExecutionAttestationDecision.RECORDED,
            ExecutionAttestationDecision.VERIFIED,
            ExecutionAttestationDecision.CONSUMED,
        ):
            if not has_record:
                raise ValueError("missing attestation")
            if type(self.attestation) is not ExecutionAttestation:
                raise ValueError("invalid attestation")
        elif has_record:
            raise ValueError("unresolved result cannot expose attestation")


class CrossDomainExecutionAttestationRegistry:
    """Store exact associations without producer authority."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._by_invocation: dict[str, ExecutionAttestation] = {}
        self._by_execution: dict[str, str] = {}

    def record(
        self,
        *,
        invocation_id: str,
        execution_id: str,
        owner: str,
        session_id: str,
        source_id: str,
    ) -> ExecutionAttestationResult:
        values = (
            invocation_id,
            execution_id,
            owner,
            session_id,
            source_id,
        )
        if not all(_valid(value) for value in values):
            return ExecutionAttestationResult(
                ExecutionAttestationDecision.REJECTED
            )

        with self._lock:
            if (
                invocation_id in self._by_invocation
                or execution_id in self._by_execution
            ):
                return ExecutionAttestationResult(
                    ExecutionAttestationDecision.REJECTED
                )

            attestation = ExecutionAttestation(
                invocation_id=invocation_id,
                execution_id=execution_id,
                owner=owner,
                session_id=session_id,
                source_id=source_id,
                state=ExecutionAttestationState.RECORDED,
            )
            self._by_invocation[invocation_id] = attestation
            self._by_execution[execution_id] = invocation_id

            return ExecutionAttestationResult(
                ExecutionAttestationDecision.RECORDED,
                attestation,
            )

    def verify(
        self,
        *,
        invocation_id: str,
        execution_id: str,
        owner: str,
        session_id: str,
        source_id: str,
    ) -> ExecutionAttestationResult:
        values = (
            invocation_id,
            execution_id,
            owner,
            session_id,
            source_id,
        )
        if not all(_valid(value) for value in values):
            return ExecutionAttestationResult(
                ExecutionAttestationDecision.REJECTED
            )

        with self._lock:
            record = self._by_invocation.get(invocation_id)

            if (
                record is None
                or record.execution_id != execution_id
                or record.owner != owner
                or record.session_id != session_id
                or record.source_id != source_id
                or record.state is not ExecutionAttestationState.RECORDED
            ):
                return ExecutionAttestationResult(
                    ExecutionAttestationDecision.UNRESOLVED
                )

            return ExecutionAttestationResult(
                ExecutionAttestationDecision.VERIFIED,
                record,
            )

    def consume(
        self,
        *,
        invocation_id: str,
        execution_id: str,
        owner: str,
        session_id: str,
        source_id: str,
    ) -> ExecutionAttestationResult:
        values = (
            invocation_id,
            execution_id,
            owner,
            session_id,
            source_id,
        )
        if not all(_valid(value) for value in values):
            return ExecutionAttestationResult(
                ExecutionAttestationDecision.REJECTED
            )

        with self._lock:
            record = self._by_invocation.get(invocation_id)

            if (
                record is None
                or record.execution_id != execution_id
                or record.owner != owner
                or record.session_id != session_id
                or record.source_id != source_id
                or record.state is not ExecutionAttestationState.RECORDED
            ):
                return ExecutionAttestationResult(
                    ExecutionAttestationDecision.UNRESOLVED
                )

            consumed = ExecutionAttestation(
                invocation_id=record.invocation_id,
                execution_id=record.execution_id,
                owner=record.owner,
                session_id=record.session_id,
                source_id=record.source_id,
                state=ExecutionAttestationState.CONSUMED,
            )
            self._by_invocation[invocation_id] = consumed

            return ExecutionAttestationResult(
                ExecutionAttestationDecision.CONSUMED,
                consumed,
            )
