from datetime import datetime, timedelta, timezone

import pytest

from infrastructure.calendar.calendar_runtime_composition import (
    CALENDAR_EVENT_SCOPE,
    CALENDAR_FREEBUSY_SCOPE,
    CalendarRuntimeComposition,
    CalendarRuntimeConfig,
)
from infrastructure.calendar.calendar_runtime_resilience import (
    CalendarErrorKind,
    CalendarReadinessLevel,
    CalendarRecoveryAction,
    classify_calendar_failure,
    recovery_plan_from_failure,
)
from infrastructure.calendar.google_calendar_adapter import (
    CalendarProviderAuthenticationError,
    CalendarProviderRateLimitError,
    CalendarProviderRejectedError,
    GoogleCalendarAdapter,
)


class Credentials:
    def __init__(self, *, scopes=(), valid=True, expired=False) -> None:
        self.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        self.scopes = list(scopes)
        self.valid = valid
        self.expired = expired
        self.refresh_token = "refresh"
        self.token = "secret"


class Material:
    def __init__(self, credentials: Credentials) -> None:
        self.deployment_credentials = credentials
        self.scopes = tuple(credentials.scopes)
        self.expires_at = credentials.expiry
        self.revoked = False


class OAuth:
    def __init__(self, material=None, *, interactive=False) -> None:
        self.material = material
        self.config = type(
            "Config",
            (),
            {"allow_interactive_authorization": interactive},
        )()
        self.activations = 0

    def load(self, account_fingerprint):
        return self.material

    def activate(self, account_fingerprint, scopes):
        self.activations += 1
        return "recovered"


def _provider() -> GoogleCalendarAdapter:
    return GoogleCalendarAdapter(lambda: object())


def test_disabled_runtime_reports_non_blocking_readiness() -> None:
    runtime = CalendarRuntimeComposition()

    report = runtime.readiness()
    plan = runtime.recovery_plan()

    assert report.level is CalendarReadinessLevel.DISABLED
    assert report.blockers == ()
    assert plan.action is CalendarRecoveryAction.ENABLE
    assert plan.automatic is False


def test_missing_configuration_is_blocked_and_requires_operator() -> None:
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True)
    )

    assert runtime.readiness().blockers == ("configuration_missing",)
    assert runtime.recovery_plan().action is CalendarRecoveryAction.CONFIGURE
    with pytest.raises(RuntimeError, match="operator action"):
        runtime.recover()


def test_missing_credentials_warn_when_interactive_oauth_is_disabled() -> None:
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(interactive=False),
        provider=_provider(),
    )

    report = runtime.readiness()

    assert report.level is CalendarReadinessLevel.BLOCKED
    assert report.warnings == ("interactive_authorization_disabled",)
    assert runtime.recovery_plan().action is CalendarRecoveryAction.AUTHORIZE


def test_explicit_recovery_delegates_to_governed_oauth_activation() -> None:
    oauth = OAuth(interactive=True)
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=oauth,
        provider=_provider(),
    )

    assert runtime.recover() == "recovered"
    assert oauth.activations == 1


def test_ready_runtime_does_not_allow_unnecessary_recovery() -> None:
    credentials = Credentials(
        scopes=(CALENDAR_EVENT_SCOPE, CALENDAR_FREEBUSY_SCOPE)
    )
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(Material(credentials)),
        provider=_provider(),
    )

    assert runtime.readiness().level is CalendarReadinessLevel.READY
    assert runtime.recovery_plan().action is CalendarRecoveryAction.NONE
    with pytest.raises(RuntimeError, match="does not require recovery"):
        runtime.recover()


@pytest.mark.parametrize(
    ("error", "kind", "action", "retryable"),
    [
        (
            CalendarProviderAuthenticationError("auth"),
            CalendarErrorKind.AUTHENTICATION,
            CalendarRecoveryAction.REFRESH_OR_AUTHORIZE,
            False,
        ),
        (
            CalendarProviderRateLimitError("limit"),
            CalendarErrorKind.RATE_LIMIT,
            CalendarRecoveryAction.RETRY_LATER,
            True,
        ),
        (
            CalendarProviderRejectedError("bad"),
            CalendarErrorKind.REJECTED,
            CalendarRecoveryAction.REVIEW_REQUEST,
            False,
        ),
        (
            TimeoutError("slow"),
            CalendarErrorKind.TIMEOUT,
            CalendarRecoveryAction.RETRY_LATER,
            True,
        ),
        (
            ConnectionError("offline"),
            CalendarErrorKind.PROVIDER_UNAVAILABLE,
            CalendarRecoveryAction.RETRY_LATER,
            True,
        ),
        (
            RuntimeError("unknown"),
            CalendarErrorKind.UNKNOWN,
            CalendarRecoveryAction.MANUAL_REVIEW,
            False,
        ),
    ],
)
def test_provider_failures_have_stable_recovery_plans(
    error, kind, action, retryable
) -> None:
    failure = classify_calendar_failure(error)
    plan = recovery_plan_from_failure(failure)

    assert failure.kind is kind
    assert failure.retryable is retryable
    assert plan.action is action
    assert plan.automatic is False


def test_status_exposes_secret_free_readiness_and_recovery() -> None:
    runtime = CalendarRuntimeComposition(
        config=CalendarRuntimeConfig(enabled=True),
        oauth=OAuth(),
        provider=_provider(),
    )

    status = runtime.status()

    assert status["readiness"]["reason"] == "credentials_absent"
    assert status["recovery"]["action"] == "authorize"
    assert "token" not in repr(status).casefold()
