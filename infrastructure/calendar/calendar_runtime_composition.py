from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from infrastructure.calendar.calendar_runtime_resilience import (
    CalendarReadinessReport,
    CalendarRecoveryAction,
    CalendarRecoveryPlan,
    readiness_from_snapshot,
    recovery_plan_from_readiness,
)
from infrastructure.calendar.google_calendar_adapter import (
    GoogleCalendarAdapter,
    GoogleCalendarApiServiceFactory,
)
from infrastructure.config.secrets_loader import SecretsLoader
from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthActivationResult,
    GoogleOAuthDeploymentAdapter,
    GoogleOAuthDeploymentConfig,
)

CALENDAR_EVENT_SCOPE = "https://www.googleapis.com/auth/calendar.events"
CALENDAR_FREEBUSY_SCOPE = "https://www.googleapis.com/auth/calendar.events.freebusy"
DEFAULT_CALENDAR_SCOPES = (CALENDAR_EVENT_SCOPE, CALENDAR_FREEBUSY_SCOPE)


class CalendarRuntimeState(str, Enum):
    DISABLED = "disabled"
    READY = "ready"
    DEGRADED = "degraded"


@dataclass(frozen=True)
class CalendarRuntimeConfig:
    enabled: bool = False
    account_fingerprint: str = "primary"
    required_scopes: tuple[str, ...] = DEFAULT_CALENDAR_SCOPES

    def __post_init__(self) -> None:
        if not self.account_fingerprint.strip():
            raise ValueError("calendar account fingerprint must not be blank")
        normalized = tuple(scope.strip() for scope in self.required_scopes)
        if not normalized or any(not scope for scope in normalized):
            raise ValueError("calendar oauth scopes must not be blank")
        if len(set(normalized)) != len(normalized):
            raise ValueError("calendar oauth scopes must be unique")
        object.__setattr__(self, "required_scopes", normalized)


@dataclass(frozen=True)
class CalendarRuntimeSnapshot:
    state: CalendarRuntimeState
    enabled: bool
    configured: bool
    credentials_available: bool
    scopes_satisfied: bool
    interactive_authorization_allowed: bool
    reason: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "state": self.state.value,
            "enabled": self.enabled,
            "configured": self.configured,
            "credentials_available": self.credentials_available,
            "scopes_satisfied": self.scopes_satisfied,
            "interactive_authorization_allowed": (
                self.interactive_authorization_allowed
            ),
            "reason": self.reason,
        }


class CalendarRuntimeComposition:
    """Controlled runtime boundary for Google Calendar deployment activation."""

    def __init__(
        self,
        *,
        config: CalendarRuntimeConfig | None = None,
        oauth: GoogleOAuthDeploymentAdapter | None = None,
        provider: GoogleCalendarAdapter | None = None,
    ) -> None:
        self.config = config or CalendarRuntimeConfig()
        self.oauth = oauth
        self.provider = provider
        if (oauth is None) is not (provider is None):
            raise ValueError(
                "calendar runtime dependencies must be supplied as a complete graph"
            )

    @property
    def configured(self) -> bool:
        return self.oauth is not None and self.provider is not None

    def snapshot(self) -> CalendarRuntimeSnapshot:
        interactive = bool(
            self.oauth and self.oauth.config.allow_interactive_authorization
        )
        if not self.config.enabled:
            return CalendarRuntimeSnapshot(
                state=CalendarRuntimeState.DISABLED,
                enabled=False,
                configured=self.configured,
                credentials_available=False,
                scopes_satisfied=False,
                interactive_authorization_allowed=interactive,
                reason=None,
            )
        if not self.configured:
            return CalendarRuntimeSnapshot(
                state=CalendarRuntimeState.DEGRADED,
                enabled=True,
                configured=False,
                credentials_available=False,
                scopes_satisfied=False,
                interactive_authorization_allowed=interactive,
                reason="configuration_missing",
            )
        assert self.oauth is not None
        try:
            material = self.oauth.load(self.config.account_fingerprint)
        except RuntimeError:
            return CalendarRuntimeSnapshot(
                state=CalendarRuntimeState.DEGRADED,
                enabled=True,
                configured=True,
                credentials_available=False,
                scopes_satisfied=False,
                interactive_authorization_allowed=interactive,
                reason="credentials_invalid",
            )
        if material is None:
            return CalendarRuntimeSnapshot(
                state=CalendarRuntimeState.DEGRADED,
                enabled=True,
                configured=True,
                credentials_available=False,
                scopes_satisfied=False,
                interactive_authorization_allowed=interactive,
                reason="credentials_absent",
            )
        granted = set(material.scopes)
        scopes_satisfied = set(self.config.required_scopes).issubset(granted)
        if material.revoked:
            reason = "credentials_revoked"
        elif not scopes_satisfied:
            reason = "insufficient_scope"
        else:
            deployment = material.deployment_credentials
            if material.expires_at is not None and deployment.expired:
                reason = "credentials_expired"
            elif not deployment.valid:
                reason = "credentials_unusable"
            else:
                return CalendarRuntimeSnapshot(
                    state=CalendarRuntimeState.READY,
                    enabled=True,
                    configured=True,
                    credentials_available=True,
                    scopes_satisfied=True,
                    interactive_authorization_allowed=interactive,
                    reason=None,
                )
        return CalendarRuntimeSnapshot(
            state=CalendarRuntimeState.DEGRADED,
            enabled=True,
            configured=True,
            credentials_available=True,
            scopes_satisfied=scopes_satisfied,
            interactive_authorization_allowed=interactive,
            reason=reason,
        )

    def activate(self) -> GoogleOAuthActivationResult:
        if not self.config.enabled:
            raise RuntimeError("calendar runtime is disabled")
        if self.oauth is None:
            raise RuntimeError("calendar runtime configuration is missing")
        return self.oauth.activate(
            self.config.account_fingerprint,
            self.config.required_scopes,
        )

    def require_provider(self) -> GoogleCalendarAdapter:
        snapshot = self.snapshot()
        if snapshot.state is not CalendarRuntimeState.READY:
            raise RuntimeError(
                "calendar runtime is not ready: "
                f"{snapshot.reason or snapshot.state.value}"
            )
        assert self.provider is not None
        return self.provider

    def readiness(self) -> CalendarReadinessReport:
        snapshot = self.snapshot()
        return readiness_from_snapshot(
            state=snapshot.state.value,
            reason=snapshot.reason,
            interactive_authorization_allowed=(
                snapshot.interactive_authorization_allowed
            ),
        )

    def recovery_plan(self) -> CalendarRecoveryPlan:
        return recovery_plan_from_readiness(self.readiness())

    def recover(self) -> GoogleOAuthActivationResult:
        plan = self.recovery_plan()
        if plan.action is CalendarRecoveryAction.NONE:
            raise RuntimeError("calendar runtime does not require recovery")
        if plan.action in {
            CalendarRecoveryAction.ENABLE,
            CalendarRecoveryAction.CONFIGURE,
            CalendarRecoveryAction.MANUAL_REVIEW,
        }:
            raise RuntimeError(
                f"calendar recovery requires operator action: {plan.action.value}"
            )
        return self.activate()

    def status(self) -> dict[str, object]:
        snapshot = self.snapshot()
        return {
            **snapshot.to_dict(),
            "readiness": self.readiness().to_dict(),
            "recovery": self.recovery_plan().to_dict(),
        }


def build_calendar_runtime_from_environment(
    *,
    secrets_loader: SecretsLoader | None = None,
    environment: Callable[[str], str | None] | None = None,
) -> CalendarRuntimeComposition:
    """Build Calendar without mutating the canonical credentials document."""
    loader = secrets_loader or SecretsLoader()
    getenv = environment or os.getenv
    enabled = _environment_flag(getenv("ROBY_CALENDAR_ENABLED"))
    account = (getenv("ROBY_CALENDAR_ACCOUNT_FINGERPRINT") or "primary").strip()
    token_value = loader.get("GOOGLE_TOKEN_FILE")
    client_value = loader.get("GOOGLE_CLIENT_SECRET_FILE")
    interactive = _environment_flag(getenv("ROBY_CALENDAR_ALLOW_INTERACTIVE_OAUTH"))
    config = CalendarRuntimeConfig(enabled=enabled, account_fingerprint=account)
    if not token_value:
        return CalendarRuntimeComposition(config=config)

    deployment_config = GoogleOAuthDeploymentConfig(
        token_path=Path(token_value).expanduser(),
        client_secrets_path=(Path(client_value).expanduser() if client_value else None),
        allow_interactive_authorization=interactive,
    )
    oauth = GoogleOAuthDeploymentAdapter(deployment_config)

    def load_credentials() -> object:
        material = oauth.load(config.account_fingerprint)
        if material is None:
            return None
        return material.deployment_credentials

    provider = GoogleCalendarAdapter(GoogleCalendarApiServiceFactory(load_credentials))
    return CalendarRuntimeComposition(
        config=config,
        oauth=oauth,
        provider=provider,
    )


def _environment_flag(value: str | None) -> bool:
    return (value or "").strip().casefold() in {"1", "true", "yes", "on"}
