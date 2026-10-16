from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from infrastructure.mail.gmail_governed_integration import GmailGovernedIntegration
from infrastructure.mail.gmail_oauth_governance import GmailOAuthGovernance
from infrastructure.mail.gmail_provider_transport import GmailTransportResult
from infrastructure.mail.gmail_retry_governance import GmailRetryGovernance


class GmailRuntimeState(str, Enum):
    DISABLED = "disabled"
    READY = "ready"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class GmailRuntimeConfig:
    enabled: bool = False


@dataclass(frozen=True)
class GmailRuntimeSnapshot:
    state: GmailRuntimeState
    enabled: bool
    configured: bool
    reason: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "enabled": self.enabled,
            "configured": self.configured,
            "reason": self.reason,
        }


class GmailRuntimeComposition:
    """M226.8 configurable runtime boundary for the governed Gmail stack."""

    def __init__(
        self,
        *,
        config: GmailRuntimeConfig | None = None,
        integration: GmailGovernedIntegration | None = None,
        oauth: GmailOAuthGovernance | None = None,
        retry: GmailRetryGovernance | None = None,
    ) -> None:
        self.config = config or GmailRuntimeConfig()
        self.integration = integration
        self.oauth = oauth
        self.retry = retry
        self._validate_graph()

    @property
    def configured(self) -> bool:
        return all(
            item is not None for item in (self.integration, self.oauth, self.retry)
        )

    def snapshot(self, *, now: datetime | None = None) -> GmailRuntimeSnapshot:
        if not self.config.enabled:
            return GmailRuntimeSnapshot(
                state=GmailRuntimeState.DISABLED,
                enabled=False,
                configured=self.configured,
                reason=None,
            )
        if not self.configured:
            return GmailRuntimeSnapshot(
                state=GmailRuntimeState.DEGRADED,
                enabled=True,
                configured=False,
                reason="configuration_missing",
            )
        assert self.oauth is not None
        oauth_state = self.oauth.inspect(now=now).state.value
        if oauth_state != "ready":
            return GmailRuntimeSnapshot(
                state=GmailRuntimeState.DEGRADED,
                enabled=True,
                configured=True,
                reason=f"oauth_{oauth_state}",
            )
        return GmailRuntimeSnapshot(
            state=GmailRuntimeState.READY,
            enabled=True,
            configured=True,
            reason=None,
        )

    def execute(
        self,
        operation: str,
        payload: Mapping[str, Any] | None = None,
        *,
        now: datetime | None = None,
        idempotency_key: str | None = None,
    ) -> GmailTransportResult:
        snapshot = self.snapshot(now=now)
        if snapshot.state is not GmailRuntimeState.READY:
            raise RuntimeError(f"gmail runtime is not ready: {snapshot.state.value}")
        assert self.retry is not None
        return self.retry.execute(
            operation,
            payload,
            now=now,
            idempotency_key=idempotency_key,
        )

    def status(self, *, now: datetime | None = None) -> dict[str, object]:
        snapshot = self.snapshot(now=now)
        return snapshot.to_dict()

    def _validate_graph(self) -> None:
        supplied = tuple(
            item is not None for item in (self.integration, self.oauth, self.retry)
        )
        if any(supplied) and not all(supplied):
            raise ValueError(
                "gmail runtime dependencies must be supplied as a complete graph"
            )
