from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

from infrastructure.mail.gmail_provider_transport import GmailTransportOperation


class GmailAcceptanceState(str, Enum):
    DISABLED = "disabled"
    BLOCKED = "blocked"
    READY = "ready"


@dataclass(frozen=True)
class GmailAcceptanceConfig:
    enabled: bool = False
    allow_write: bool = False
    search_query: str = "in:inbox"
    recipient: str | None = None
    max_results: int = 3

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> GmailAcceptanceConfig:
        source = os.environ if env is None else env
        return cls(
            enabled=_truthy(source.get("ROBY_GMAIL_ACCEPTANCE_ENABLED")),
            allow_write=_truthy(source.get("ROBY_GMAIL_ACCEPTANCE_ALLOW_WRITE")),
            search_query=(
                source.get("ROBY_GMAIL_ACCEPTANCE_SEARCH_QUERY", "in:inbox").strip()
                or "in:inbox"
            ),
            recipient=_clean_optional(source.get("ROBY_GMAIL_ACCEPTANCE_RECIPIENT")),
            max_results=_positive_int(
                source.get("ROBY_GMAIL_ACCEPTANCE_MAX_RESULTS"), default=3
            ),
        )


@dataclass(frozen=True)
class GmailAcceptancePreflight:
    state: GmailAcceptanceState
    reason: str | None
    write_enabled: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "reason": self.reason,
            "write_enabled": self.write_enabled,
        }


@dataclass(frozen=True)
class GmailAcceptanceCheck:
    name: str
    passed: bool
    operation: str


@dataclass(frozen=True)
class GmailAcceptanceReport:
    state: GmailAcceptanceState
    checks: tuple[GmailAcceptanceCheck, ...]
    write_exercised: bool

    @property
    def passed(self) -> bool:
        return self.state is GmailAcceptanceState.READY and all(
            check.passed for check in self.checks
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "passed": self.passed,
            "check_count": len(self.checks),
            "write_exercised": self.write_exercised,
            "checks": tuple(
                {
                    "name": check.name,
                    "passed": check.passed,
                    "operation": check.operation,
                }
                for check in self.checks
            ),
        }


class GmailAcceptanceRuntime(Protocol):
    def status(self, *, now: object | None = None) -> Mapping[str, object]: ...

    def execute(
        self,
        operation: str | GmailTransportOperation,
        payload: Mapping[str, Any] | None = None,
        *,
        now: object | None = None,
        idempotency_key: str | None = None,
    ) -> object: ...


class GmailRealAccountAcceptance:
    """M227.5 opt-in acceptance harness for a deployment-owned Gmail account."""

    def __init__(
        self,
        runtime: GmailAcceptanceRuntime,
        config: GmailAcceptanceConfig | None = None,
    ) -> None:
        self._runtime = runtime
        self.config = config or GmailAcceptanceConfig()
        self._runs = 0
        self._failures = 0

    def preflight(self, *, now: object | None = None) -> GmailAcceptancePreflight:
        if not self.config.enabled:
            return GmailAcceptancePreflight(
                GmailAcceptanceState.DISABLED,
                "acceptance_disabled",
                False,
            )
        runtime_state = str(self._runtime.status(now=now).get("state", "unknown"))
        if runtime_state != "ready":
            return GmailAcceptancePreflight(
                GmailAcceptanceState.BLOCKED,
                "runtime_not_ready",
                False,
            )
        if self.config.allow_write and not self.config.recipient:
            return GmailAcceptancePreflight(
                GmailAcceptanceState.BLOCKED,
                "recipient_missing",
                False,
            )
        return GmailAcceptancePreflight(
            GmailAcceptanceState.READY,
            None,
            self.config.allow_write,
        )

    def run(self, *, now: object | None = None) -> GmailAcceptanceReport:
        preflight = self.preflight(now=now)
        if preflight.state is not GmailAcceptanceState.READY:
            raise RuntimeError(f"gmail acceptance blocked: {preflight.reason}")
        self._runs += 1
        checks: list[GmailAcceptanceCheck] = []
        try:
            recent = self._runtime.execute(
                GmailTransportOperation.LIST_RECENT,
                {"limit": self.config.max_results},
                now=now,
            )
            checks.append(self._check("list_recent", recent, "list_recent"))
            search = self._runtime.execute(
                GmailTransportOperation.SEARCH,
                {
                    "query": self.config.search_query,
                    "limit": self.config.max_results,
                },
                now=now,
            )
            checks.append(self._check("search", search, "search"))
            message_id = _first_message_id(search) or _first_message_id(recent)
            if message_id:
                read = self._runtime.execute(
                    GmailTransportOperation.READ,
                    {"message_id": message_id},
                    now=now,
                )
                checks.append(self._check("read", read, "read"))
            else:
                checks.append(GmailAcceptanceCheck("read", True, "read_skipped_empty"))
            if self.config.allow_write:
                payload = {
                    "to": self.config.recipient,
                    "subject": "ROBY Gmail acceptance certification",
                    "body": "Automated acceptance message generated by ROBY.",
                }
                draft = self._runtime.execute(
                    GmailTransportOperation.CREATE_DRAFT,
                    payload,
                    now=now,
                )
                checks.append(self._check("create_draft", draft, "create_draft"))
                sent = self._runtime.execute(
                    GmailTransportOperation.SEND,
                    payload,
                    now=now,
                    idempotency_key="m227.5-acceptance-send",
                )
                checks.append(self._check("send", sent, "send"))
        except Exception:
            self._failures += 1
            raise
        return GmailAcceptanceReport(
            state=GmailAcceptanceState.READY,
            checks=tuple(checks),
            write_exercised=self.config.allow_write,
        )

    def status(self) -> dict[str, object]:
        return {
            "milestone": "M227.5",
            "enabled": self.config.enabled,
            "write_enabled": self.config.allow_write,
            "runs": self._runs,
            "failures": self._failures,
        }

    @staticmethod
    def _check(name: str, result: object, operation: str) -> GmailAcceptanceCheck:
        return GmailAcceptanceCheck(
            name=name,
            passed=result is not None,
            operation=operation,
        )


def _first_message_id(result: object) -> str | None:
    payload = getattr(result, "payload", result)
    if not isinstance(payload, Mapping):
        return None
    messages = payload.get("messages", ())
    if not isinstance(messages, (list, tuple)) or not messages:
        return None
    first = messages[0]
    if not isinstance(first, Mapping):
        return None
    value = first.get("id")
    return str(value) if value else None


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _clean_optional(value: str | None) -> str | None:
    cleaned = str(value or "").strip()
    return cleaned or None


def _positive_int(value: str | None, *, default: int) -> int:
    if value is None or not str(value).strip():
        return default
    parsed = int(value)
    if parsed <= 0:
        raise ValueError("gmail acceptance max results must be positive")
    return parsed
