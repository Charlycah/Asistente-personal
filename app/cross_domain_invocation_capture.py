"""Non-authorizing, invocation-local capture of execution observations.

Observations are caller-supplied data, not authenticated producer
evidence. No provenance admission or registration occurs here.
"""

from dataclasses import dataclass
from enum import Enum
from secrets import token_urlsafe
from threading import RLock


class InvocationCaptureState(str, Enum):
    STARTED = "started"
    OBSERVED = "observed"
    CLOSED = "closed"


class InvocationExecutionStatus(str, Enum):
    SUCCEEDED = "succeeded"
    EMPTY = "empty"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class InvocationCaptureSnapshot:
    invocation_id: str
    owner: str
    session_id: str
    state: InvocationCaptureState
    execution_id: str | None = None
    execution_status: InvocationExecutionStatus | None = None

    def __post_init__(self) -> None:
        if not _valid(self.invocation_id):
            raise ValueError("invalid invocation_id")
        if not _valid(self.owner):
            raise ValueError("invalid owner")
        if not _valid(self.session_id):
            raise ValueError("invalid session_id")
        if type(self.state) is not InvocationCaptureState:
            raise ValueError("invalid capture state")
        if self.execution_id is None:
            if self.execution_status is not None:
                raise ValueError("status without execution")
            if self.state is InvocationCaptureState.OBSERVED:
                raise ValueError("observed without execution")
        else:
            if not _valid(self.execution_id):
                raise ValueError("invalid execution_id")
            if type(self.execution_status) is not InvocationExecutionStatus:
                raise ValueError("invalid execution status")
            if self.state is InvocationCaptureState.STARTED:
                raise ValueError("started with execution")


@dataclass
class _CaptureRecord:
    owner: str
    session_id: str
    state: InvocationCaptureState = InvocationCaptureState.STARTED
    execution_id: str | None = None
    execution_status: InvocationExecutionStatus | None = None


def _valid(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value == value.strip()
    )


class CrossDomainInvocationCapture:
    """Track one terminal observation per invocation, without authority."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._records: dict[str, _CaptureRecord] = {}
        self._used_execution_ids: set[str] = set()

    def begin(self, *, owner: str, session_id: str) -> str:
        if not _valid(owner) or not _valid(session_id):
            raise ValueError("invalid invocation identity")

        with self._lock:
            invocation_id = token_urlsafe(32)
            while invocation_id in self._records:
                invocation_id = token_urlsafe(32)
            self._records[invocation_id] = _CaptureRecord(
                owner=owner,
                session_id=session_id,
            )
            return invocation_id

    def observe(
        self,
        invocation_id: str,
        *,
        owner: str,
        session_id: str,
        execution_id: str,
        status: InvocationExecutionStatus,
    ) -> bool:
        if (
            not _valid(invocation_id)
            or not _valid(owner)
            or not _valid(session_id)
            or not _valid(execution_id)
            or type(status) is not InvocationExecutionStatus
        ):
            return False

        with self._lock:
            record = self._records.get(invocation_id)
            if (
                record is None
                or record.state is not InvocationCaptureState.STARTED
                or record.owner != owner
                or record.session_id != session_id
                or execution_id in self._used_execution_ids
            ):
                return False

            record.execution_id = execution_id
            record.execution_status = status
            record.state = InvocationCaptureState.OBSERVED
            self._used_execution_ids.add(execution_id)
            return True

    def snapshot(
        self,
        invocation_id: str,
        *,
        owner: str,
        session_id: str,
    ) -> InvocationCaptureSnapshot | None:
        if (
            not _valid(invocation_id)
            or not _valid(owner)
            or not _valid(session_id)
        ):
            return None

        with self._lock:
            record = self._records.get(invocation_id)
            if (
                record is None
                or record.owner != owner
                or record.session_id != session_id
            ):
                return None

            return InvocationCaptureSnapshot(
                invocation_id=invocation_id,
                owner=record.owner,
                session_id=record.session_id,
                state=record.state,
                execution_id=record.execution_id,
                execution_status=record.execution_status,
            )

    def close(
        self,
        invocation_id: str,
        *,
        owner: str,
        session_id: str,
    ) -> bool:
        if (
            not _valid(invocation_id)
            or not _valid(owner)
            or not _valid(session_id)
        ):
            return False

        with self._lock:
            record = self._records.get(invocation_id)
            if (
                record is None
                or record.owner != owner
                or record.session_id != session_id
                or record.state is InvocationCaptureState.CLOSED
            ):
                return False

            record.state = InvocationCaptureState.CLOSED
            return True
