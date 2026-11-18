"""Non-authorizing terminal evidence contract for governed executions.

These values describe terminal outcomes but do not authenticate
their producer, invocation, owner, session, or persistence.
"""

from dataclasses import dataclass
from enum import Enum


class GovernedTerminalStatus(str, Enum):
    SUCCEEDED = "succeeded"
    EMPTY = "empty"
    FAILED = "failed"
    REJECTED = "rejected"


def _valid(value: object) -> bool:
    return (
        type(value) is str
        and bool(value.strip())
        and value == value.strip()
    )


@dataclass(frozen=True)
class GovernedTerminalExecutionEvidence:
    source_id: str
    status: GovernedTerminalStatus
    execution_id: str | None
    item_count: int
    response_present: bool
    producer_verified: bool = False

    def __post_init__(self) -> None:
        if not _valid(self.source_id):
            raise ValueError("invalid source_id")

        if type(self.status) is not GovernedTerminalStatus:
            raise ValueError("invalid terminal status")

        if type(self.item_count) is not int or self.item_count < 0:
            raise ValueError("invalid item_count")

        if type(self.response_present) is not bool:
            raise ValueError("invalid response_present")

        if self.producer_verified is not False:
            raise ValueError("producer authentication is unavailable")

        if self.status is GovernedTerminalStatus.REJECTED:
            if (
                self.execution_id is not None
                or self.item_count != 0
                or self.response_present
            ):
                raise ValueError("invalid rejected outcome")
            return

        if not _valid(self.execution_id):
            raise ValueError("missing execution_id")

        if not self.response_present:
            raise ValueError("terminal response missing")

        if self.status is GovernedTerminalStatus.SUCCEEDED:
            if self.item_count <= 0:
                raise ValueError("success requires items")
        elif self.item_count != 0:
            raise ValueError("non-success outcome cannot contain items")


def terminal_evidence_from_result(
    result: object,
) -> GovernedTerminalExecutionEvidence | None:
    """Project a result structurally, without authenticating its origin."""
    from app.governed_source_query import (
        GovernedSourceQueryResult,
    )

    if type(result) is not GovernedSourceQueryResult:
        return None

    try:
        response = result.response
        if response is None:
            return None

        if response.status is not result.status:
            return None

        if response.source_id != result.query.source_id:
            return None

        status = GovernedTerminalStatus(result.status.value)

        if status is GovernedTerminalStatus.REJECTED:
            return None

        execution_id = result.execution_id
        if not _valid(execution_id) or len(execution_id) != 64:
            return None

        return GovernedTerminalExecutionEvidence(
            source_id=result.query.source_id,
            status=status,
            execution_id=execution_id,
            item_count=len(response.raw_items),
            response_present=True,
        )
    except (AttributeError, TypeError, ValueError):
        return None
