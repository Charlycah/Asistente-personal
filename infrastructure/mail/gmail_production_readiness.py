from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol


class GmailProductionDecision(str, Enum):
    GO = "go"
    CONDITIONAL = "conditional"
    NO_GO = "no_go"


@dataclass(frozen=True)
class GmailProductionReadinessPolicy:
    require_live_acceptance: bool = True
    allow_write_acceptance: bool = False
    max_retry_attempts: int = 5
    max_transport_timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if self.max_retry_attempts <= 0:
            raise ValueError("gmail production retry limit must be positive")
        if self.max_transport_timeout_seconds <= 0:
            raise ValueError("gmail production timeout limit must be positive")


@dataclass(frozen=True)
class GmailProductionCriterion:
    name: str
    passed: bool
    observed: str
    requirement: str

    def __post_init__(self) -> None:
        values = tuple(
            value.strip() for value in (self.name, self.observed, self.requirement)
        )
        if any(not value for value in values):
            raise ValueError("gmail production criterion fields must not be blank")
        object.__setattr__(self, "name", values[0])
        object.__setattr__(self, "observed", values[1])
        object.__setattr__(self, "requirement", values[2])


@dataclass(frozen=True)
class GmailProductionReadinessCertificate:
    decision: GmailProductionDecision
    criteria: tuple[GmailProductionCriterion, ...]
    created_at: datetime
    certificate_id: str = ""

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError(
                "gmail production certification time must be timezone-aware"
            )
        if not self.criteria:
            raise ValueError("gmail production certification criteria are required")
        if len({item.name for item in self.criteria}) != len(self.criteria):
            raise ValueError("gmail production criterion names must be unique")
        expected = sha256(
            "|".join(
                (
                    self.decision.value,
                    *(
                        f"{c.name}:{c.passed}:{c.observed}:{c.requirement}"
                        for c in self.criteria
                    ),
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.certificate_id and self.certificate_id != expected:
            raise ValueError("gmail production certificate id is inconsistent")
        object.__setattr__(self, "certificate_id", expected)

    @property
    def ready(self) -> bool:
        return self.decision is GmailProductionDecision.GO

    def to_dict(self) -> dict[str, object]:
        return {
            "milestone": "M227.6",
            "decision": self.decision.value,
            "ready": self.ready,
            "criterion_count": len(self.criteria),
            "passed_count": sum(item.passed for item in self.criteria),
            "certificate_id": self.certificate_id,
            "created_at": self.created_at.isoformat(),
            "criteria": tuple(
                {
                    "name": item.name,
                    "passed": item.passed,
                    "observed": item.observed,
                    "requirement": item.requirement,
                }
                for item in self.criteria
            ),
        }


class StatusProvider(Protocol):
    def status(self, **kwargs: object) -> Mapping[str, object]: ...


class GmailProductionReadinessCertifier:
    """M227.6 go/no-go authority for the composed Gmail deployment."""

    def __init__(
        self,
        *,
        runtime: StatusProvider,
        oauth: StatusProvider,
        retry: StatusProvider,
        transport: StatusProvider,
        acceptance: StatusProvider,
        policy: GmailProductionReadinessPolicy | None = None,
    ) -> None:
        self.runtime = runtime
        self.oauth = oauth
        self.retry = retry
        self.transport = transport
        self.acceptance = acceptance
        self.policy = policy or GmailProductionReadinessPolicy()
        self.last_certificate: GmailProductionReadinessCertificate | None = None

    def certify(
        self,
        *,
        now: datetime | None = None,
        live_acceptance_passed: bool = False,
    ) -> GmailProductionReadinessCertificate:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError(
                "gmail production certification time must be timezone-aware"
            )
        runtime = self.runtime.status(now=timestamp)
        oauth = self.oauth.status(now=timestamp)
        retry = self.retry.status()
        transport = self.transport.status()
        acceptance = self.acceptance.status()

        runtime_ready = runtime.get("state") == "ready"
        oauth_ready = oauth.get("state") == "ready" and oauth.get("usable") is True
        attempts = _as_int(retry.get("max_attempts"))
        retry_bounded = 0 < attempts <= self.policy.max_retry_attempts
        timeout = _as_float(transport.get("timeout_seconds"))
        transport_bounded = 0 < timeout <= self.policy.max_transport_timeout_seconds
        write_enabled = acceptance.get("write_enabled") is True
        write_policy_ok = self.policy.allow_write_acceptance or not write_enabled
        live_ok = live_acceptance_passed or not self.policy.require_live_acceptance

        criteria = (
            GmailProductionCriterion(
                "runtime_ready",
                runtime_ready,
                str(runtime.get("state", "unknown")),
                "ready",
            ),
            GmailProductionCriterion(
                "oauth_ready",
                oauth_ready,
                str(oauth.get("state", "unknown")),
                "ready and usable",
            ),
            GmailProductionCriterion(
                "retry_bounded",
                retry_bounded,
                str(attempts),
                f"1..{self.policy.max_retry_attempts} attempts",
            ),
            GmailProductionCriterion(
                "transport_timeout_bounded",
                transport_bounded,
                str(timeout),
                f"0..{self.policy.max_transport_timeout_seconds} seconds",
            ),
            GmailProductionCriterion(
                "acceptance_write_policy",
                write_policy_ok,
                "enabled" if write_enabled else "disabled",
                "disabled unless explicitly approved",
            ),
            GmailProductionCriterion(
                "live_account_acceptance",
                live_ok,
                "passed" if live_acceptance_passed else "not_provided",
                "passed" if self.policy.require_live_acceptance else "optional",
            ),
        )
        failed = sum(not item.passed for item in criteria)
        decision = (
            GmailProductionDecision.GO
            if failed == 0
            else GmailProductionDecision.CONDITIONAL
            if failed == 1 and not live_ok
            else GmailProductionDecision.NO_GO
        )
        certificate = GmailProductionReadinessCertificate(
            decision=decision,
            criteria=criteria,
            created_at=timestamp,
        )
        self.last_certificate = certificate
        return certificate

    def status(self) -> dict[str, object]:
        certificate = self.last_certificate
        return {
            "milestone": "M227.6",
            "certified": certificate is not None,
            "decision": certificate.decision.value if certificate else None,
            "ready": certificate.ready if certificate else False,
        }


def _as_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _as_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
