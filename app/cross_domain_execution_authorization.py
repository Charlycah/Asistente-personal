"""Fail-closed contract for cross-domain execution authorization.

This module does not grant execution capabilities or authenticate callers.
No production authority is connected at this stage.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionAuthorizationDecision(str, Enum):
    UNRESOLVED = "unresolved"
    REJECTED = "rejected"
    AUTHORIZED = "authorized"


class ExecutionAuthorizationReason(str, Enum):
    AUTHORITY_UNAVAILABLE = "authority_unavailable"
    INVALID_REQUEST = "invalid_request"
    UNTRUSTED_PERMISSION = "untrusted_permission"


def _valid_identifier(value: object) -> bool:
    return (
        type(value) is str
        and bool(value.strip())
        and value == value.strip()
    )


@dataclass(frozen=True)
class ExecutionAuthorizationRequest:
    owner: str
    session_id: str
    source_id: str
    capability: str
    invocation_id: str

    def __post_init__(self) -> None:
        for field in (
            "owner",
            "session_id",
            "source_id",
            "capability",
            "invocation_id",
        ):
            if not _valid_identifier(getattr(self, field)):
                raise ValueError(f"invalid authorization field: {field}")


@dataclass(frozen=True)
class ExecutionAuthorizationResult:
    decision: ExecutionAuthorizationDecision
    reason: ExecutionAuthorizationReason
    authorized: bool = False

    def __post_init__(self) -> None:
        if type(self.decision) is not ExecutionAuthorizationDecision:
            raise ValueError("invalid authorization decision")

        if type(self.reason) is not ExecutionAuthorizationReason:
            raise ValueError("invalid authorization reason")

        if type(self.authorized) is not bool:
            raise ValueError("invalid authorized flag")

        if self.decision is ExecutionAuthorizationDecision.AUTHORIZED:
            raise ValueError(
                "authorized decisions require a governed authority"
            )

        if self.authorized:
            raise ValueError(
                "unverified authorization cannot grant execution"
            )


class CrossDomainExecutionAuthorization:
    """Non-authorizing evaluator until a real authority is integrated."""

    def evaluate(
        self,
        request: object,
        *,
        external_access_authorized: object = None,
    ) -> ExecutionAuthorizationResult:
        if type(request) is not ExecutionAuthorizationRequest:
            return ExecutionAuthorizationResult(
                decision=ExecutionAuthorizationDecision.REJECTED,
                reason=ExecutionAuthorizationReason.INVALID_REQUEST,
            )

        if external_access_authorized is not None:
            return ExecutionAuthorizationResult(
                decision=ExecutionAuthorizationDecision.REJECTED,
                reason=ExecutionAuthorizationReason.UNTRUSTED_PERMISSION,
            )

        return ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.UNRESOLVED,
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
        )