from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from infrastructure.calendar.google_calendar_adapter import (
    CalendarProviderAuthenticationError,
    CalendarProviderRateLimitError,
    CalendarProviderRejectedError,
)


class CalendarReadinessLevel(str, Enum):
    DISABLED = "disabled"
    BLOCKED = "blocked"
    READY = "ready"


class CalendarErrorKind(str, Enum):
    AUTHENTICATION = "authentication"
    RATE_LIMIT = "rate_limit"
    REJECTED = "rejected"
    TIMEOUT = "timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    UNKNOWN = "unknown"


class CalendarRecoveryAction(str, Enum):
    NONE = "none"
    ENABLE = "enable"
    CONFIGURE = "configure"
    AUTHORIZE = "authorize"
    REFRESH_OR_AUTHORIZE = "refresh_or_authorize"
    GRANT_SCOPES = "grant_scopes"
    RETRY_LATER = "retry_later"
    REVIEW_REQUEST = "review_request"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class CalendarReadinessReport:
    level: CalendarReadinessLevel
    operational: bool
    reason: str | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "level": self.level.value,
            "operational": self.operational,
            "reason": self.reason,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class CalendarFailure:
    kind: CalendarErrorKind
    retryable: bool
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind.value,
            "retryable": self.retryable,
            "message": self.message,
        }


@dataclass(frozen=True)
class CalendarRecoveryPlan:
    action: CalendarRecoveryAction
    recoverable: bool
    automatic: bool
    reason: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "action": self.action.value,
            "recoverable": self.recoverable,
            "automatic": self.automatic,
            "reason": self.reason,
        }


def classify_calendar_failure(exc: Exception) -> CalendarFailure:
    if isinstance(exc, CalendarProviderAuthenticationError):
        return CalendarFailure(
            kind=CalendarErrorKind.AUTHENTICATION,
            retryable=False,
            message="calendar_authentication_failed",
        )
    if isinstance(exc, CalendarProviderRateLimitError):
        return CalendarFailure(
            kind=CalendarErrorKind.RATE_LIMIT,
            retryable=True,
            message="calendar_rate_limit_reached",
        )
    if isinstance(exc, CalendarProviderRejectedError):
        return CalendarFailure(
            kind=CalendarErrorKind.REJECTED,
            retryable=False,
            message="calendar_request_rejected",
        )
    if isinstance(exc, TimeoutError):
        return CalendarFailure(
            kind=CalendarErrorKind.TIMEOUT,
            retryable=True,
            message="calendar_provider_timeout",
        )
    if isinstance(exc, (ConnectionError, OSError)):
        return CalendarFailure(
            kind=CalendarErrorKind.PROVIDER_UNAVAILABLE,
            retryable=True,
            message="calendar_provider_unavailable",
        )
    return CalendarFailure(
        kind=CalendarErrorKind.UNKNOWN,
        retryable=False,
        message="calendar_unknown_failure",
    )


def readiness_from_snapshot(
    *,
    state: str,
    reason: str | None,
    interactive_authorization_allowed: bool,
) -> CalendarReadinessReport:
    if state == "disabled":
        return CalendarReadinessReport(
            level=CalendarReadinessLevel.DISABLED,
            operational=False,
            reason=None,
            blockers=(),
            warnings=("calendar_disabled",),
        )
    if state == "ready":
        return CalendarReadinessReport(
            level=CalendarReadinessLevel.READY,
            operational=True,
            reason=None,
            blockers=(),
            warnings=(),
        )
    warnings = ()
    if reason in {
        "credentials_absent",
        "credentials_expired",
        "credentials_unusable",
        "credentials_revoked",
        "insufficient_scope",
    } and not interactive_authorization_allowed:
        warnings = ("interactive_authorization_disabled",)
    return CalendarReadinessReport(
        level=CalendarReadinessLevel.BLOCKED,
        operational=False,
        reason=reason,
        blockers=((reason or "calendar_not_ready"),),
        warnings=warnings,
    )


def recovery_plan_from_readiness(
    report: CalendarReadinessReport,
) -> CalendarRecoveryPlan:
    reason = report.reason
    if report.level is CalendarReadinessLevel.READY:
        return CalendarRecoveryPlan(
            action=CalendarRecoveryAction.NONE,
            recoverable=True,
            automatic=False,
            reason=None,
        )
    if report.level is CalendarReadinessLevel.DISABLED:
        return CalendarRecoveryPlan(
            action=CalendarRecoveryAction.ENABLE,
            recoverable=True,
            automatic=False,
            reason="calendar_disabled",
        )
    actions = {
        "configuration_missing": CalendarRecoveryAction.CONFIGURE,
        "credentials_absent": CalendarRecoveryAction.AUTHORIZE,
        "credentials_invalid": CalendarRecoveryAction.AUTHORIZE,
        "credentials_revoked": CalendarRecoveryAction.AUTHORIZE,
        "credentials_expired": CalendarRecoveryAction.REFRESH_OR_AUTHORIZE,
        "credentials_unusable": CalendarRecoveryAction.REFRESH_OR_AUTHORIZE,
        "insufficient_scope": CalendarRecoveryAction.GRANT_SCOPES,
    }
    action = actions.get(reason, CalendarRecoveryAction.MANUAL_REVIEW)
    return CalendarRecoveryPlan(
        action=action,
        recoverable=action is not CalendarRecoveryAction.MANUAL_REVIEW,
        automatic=False,
        reason=reason,
    )


def recovery_plan_from_failure(failure: CalendarFailure) -> CalendarRecoveryPlan:
    if failure.kind is CalendarErrorKind.AUTHENTICATION:
        action = CalendarRecoveryAction.REFRESH_OR_AUTHORIZE
    elif failure.retryable:
        action = CalendarRecoveryAction.RETRY_LATER
    elif failure.kind is CalendarErrorKind.REJECTED:
        action = CalendarRecoveryAction.REVIEW_REQUEST
    else:
        action = CalendarRecoveryAction.MANUAL_REVIEW
    return CalendarRecoveryPlan(
        action=action,
        recoverable=action is not CalendarRecoveryAction.MANUAL_REVIEW,
        automatic=False,
        reason=failure.message,
    )
