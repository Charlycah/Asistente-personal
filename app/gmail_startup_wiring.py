from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from hashlib import sha256

from app.gmail_diagnostic_runtime import GmailDiagnosticRuntime
from infrastructure.mail.gmail_subject_announcement import (
    GmailStartupSubjectAnnouncer,
    GmailSubjectAnnouncement,
    GmailSubjectAnnouncementPolicy,
    GoogleGmailUnreadSubjectProvider,
)
from infrastructure.mail.google_gmail_api_backend import GoogleApiClientFactory
from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthDeploymentAdapter,
    GoogleOAuthDeploymentConfig,
)

_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
_TRUE = {"1", "true", "yes", "on"}
_SUCCESS_TRACE_ENV = "ROBY_GMAIL_DIAGNOSTIC_TRACE_ON_SUCCESS"


@dataclass(frozen=True)
class GmailStartupWiringConfig:
    enabled: bool
    account_address: str
    max_subjects: int = 5
    timeout_seconds: float = 10.0

    @classmethod
    def from_environment(cls) -> GmailStartupWiringConfig:
        gmail_enabled = _env_bool("ROBY_GMAIL_ENABLED", False)
        announcement_enabled = _env_bool(
            "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED", gmail_enabled
        )
        account = _first_environment_value(
            "ROBY_GMAIL_ACCOUNT_ADDRESS",
            "ROBY_GMAIL_EMAIL",
            "GMAIL_ADDRESS",
            "EMAIL_USER",
        )
        return cls(
            enabled=gmail_enabled and announcement_enabled,
            account_address=account,
            max_subjects=_env_positive_int(
                "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_MAX_RESULTS", 5
            ),
            timeout_seconds=_env_positive_float(
                "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_TIMEOUT_SECONDS", 10.0
            ),
        )


def build_gmail_startup_announcer_from_environment() -> (
    GmailStartupSubjectAnnouncer | None
):
    config = GmailStartupWiringConfig.from_environment()
    if not config.enabled:
        return None
    if not config.account_address:
        raise RuntimeError("gmail startup account address is not configured")
    oauth_config = GoogleOAuthDeploymentConfig.from_environment()
    if oauth_config is None:
        raise RuntimeError("gmail oauth deployment configuration is missing")
    adapter = GoogleOAuthDeploymentAdapter(oauth_config)
    account_fingerprint = sha256(
        config.account_address.strip().casefold().encode("utf-8")
    ).hexdigest()

    def load_credentials() -> object:
        adapter.activate(account_fingerprint, (_READONLY_SCOPE,))
        material = adapter.load(account_fingerprint)
        if material is None:
            raise RuntimeError("gmail oauth credentials are unavailable")
        return material.deployment_credentials

    provider = GoogleGmailUnreadSubjectProvider(
        GoogleApiClientFactory(load_credentials),
        timeout_seconds=config.timeout_seconds,
    )
    return GmailStartupSubjectAnnouncer(
        provider,
        GmailSubjectAnnouncementPolicy(
            enabled=True,
            max_subjects=config.max_subjects,
            timeout_seconds=config.timeout_seconds,
        ),
    )


def announce_gmail_startup_from_environment(
    *, write: Callable[[str], None] = print
) -> GmailSubjectAnnouncement | None:
    """Run the optional read-only startup announcement without blocking ROBY startup."""
    try:
        announcer = build_gmail_startup_announcer_from_environment()
        if announcer is None:
            return None
        result = announcer.announce()
    except (RuntimeError, ValueError, PermissionError, ImportError, OSError) as exc:
        report = GmailDiagnosticRuntime().from_exception(exc)
        for line in report.console_lines():
            write(line)
        return None
    if result.text:
        write(f"Roby> {result.text}")
    if _env_bool(_SUCCESS_TRACE_ENV, False):
        report = GmailDiagnosticRuntime().from_success()
        for line in report.console_lines():
            write(line)
    return result


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    return raw.strip().casefold() in _TRUE


def _first_environment_value(*names: str) -> str:
    for name in names:
        value = os.getenv(name, "").strip()
        if value:
            return value
    return ""


def _env_positive_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _env_positive_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value
