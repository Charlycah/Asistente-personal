from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from time import sleep
from typing import Any

from infrastructure.mail.gmail_provider_transport import (
    GmailProviderTransport,
    GmailProviderTransportError,
    GmailTransportOperation,
    GmailTransportResult,
)


class GmailRetryDecision(str, Enum):
    SUCCESS = "success"
    RETRY = "retry"
    STOP = "stop"


@dataclass(frozen=True)
class GmailRetryPolicy:
    max_attempts: int = 3
    initial_backoff_seconds: float = 0.25
    backoff_multiplier: float = 2.0
    max_backoff_seconds: float = 5.0
    require_send_idempotency_key: bool = True

    def __post_init__(self) -> None:
        if self.max_attempts <= 0:
            raise ValueError("gmail retry attempts must be positive")
        if self.initial_backoff_seconds < 0:
            raise ValueError("gmail retry backoff must not be negative")
        if self.backoff_multiplier < 1:
            raise ValueError("gmail retry multiplier must be at least one")
        if self.max_backoff_seconds < 0:
            raise ValueError("gmail retry maximum backoff must not be negative")

    def backoff_for_attempt(self, attempt: int) -> float:
        if attempt <= 0:
            raise ValueError("gmail retry attempt must be positive")
        delay = self.initial_backoff_seconds * self.backoff_multiplier ** (attempt - 1)
        return min(delay, self.max_backoff_seconds)


@dataclass(frozen=True)
class GmailRetryReport:
    operation: GmailTransportOperation
    attempts: int
    decision: GmailRetryDecision
    completed_at: datetime

    def to_dict(self) -> dict[str, object]:
        return {
            "operation": self.operation.value,
            "attempts": self.attempts,
            "decision": self.decision.value,
            "completed_at": self.completed_at.isoformat(),
        }


class GmailRetryGovernance:
    """M226.7 bounded retry and idempotency authority for Gmail transport."""

    def __init__(
        self,
        transport: GmailProviderTransport,
        policy: GmailRetryPolicy | None = None,
        sleeper: Callable[[float], None] = sleep,
    ) -> None:
        self.transport = transport
        self.policy = policy or GmailRetryPolicy()
        self._sleeper = sleeper
        self._execution_count = 0
        self._retry_count = 0
        self._exhausted_count = 0
        self._last_report: GmailRetryReport | None = None

    def execute(
        self,
        operation: GmailTransportOperation | str,
        payload: Mapping[str, Any] | None = None,
        *,
        now: datetime | None = None,
        idempotency_key: str | None = None,
    ) -> GmailTransportResult:
        resolved = self.transport._resolve_operation(operation)
        self._validate_idempotency(resolved, idempotency_key)
        self._execution_count += 1
        for attempt in range(1, self.policy.max_attempts + 1):
            try:
                result = self.transport.execute(resolved, payload, now=now)
            except GmailProviderTransportError as exc:
                if not exc.retryable or attempt >= self.policy.max_attempts:
                    if exc.retryable:
                        self._exhausted_count += 1
                    self._last_report = self._report(
                        resolved, attempt, GmailRetryDecision.STOP
                    )
                    raise
                self._retry_count += 1
                self._last_report = self._report(
                    resolved, attempt, GmailRetryDecision.RETRY
                )
                self._sleeper(self.policy.backoff_for_attempt(attempt))
                continue
            self._last_report = self._report(
                resolved, attempt, GmailRetryDecision.SUCCESS
            )
            return result
        raise RuntimeError("unreachable gmail retry state")

    def status(self) -> dict[str, object]:
        return {
            "max_attempts": self.policy.max_attempts,
            "execution_count": self._execution_count,
            "retry_count": self._retry_count,
            "exhausted_count": self._exhausted_count,
            "last_report": (
                self._last_report.to_dict() if self._last_report is not None else None
            ),
        }

    def _validate_idempotency(
        self,
        operation: GmailTransportOperation,
        idempotency_key: str | None,
    ) -> None:
        if operation is not GmailTransportOperation.SEND:
            return
        if not self.policy.require_send_idempotency_key:
            return
        if idempotency_key is None or not idempotency_key.strip():
            raise ValueError("gmail send requires an idempotency key")

    @staticmethod
    def _report(
        operation: GmailTransportOperation,
        attempts: int,
        decision: GmailRetryDecision,
    ) -> GmailRetryReport:
        return GmailRetryReport(
            operation=operation,
            attempts=attempts,
            decision=decision,
            completed_at=datetime.now(timezone.utc),
        )
