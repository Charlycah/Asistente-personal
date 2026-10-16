from __future__ import annotations

from app.gmail_startup_wiring import (
    GmailStartupWiringConfig,
    announce_gmail_startup_from_environment,
    build_gmail_startup_announcer_from_environment,
)
from infrastructure.mail.gmail_subject_announcement import GmailSubjectAnnouncement


def clear_gmail(monkeypatch):
    for name in (
        "ROBY_GMAIL_ENABLED",
        "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED",
        "ROBY_GMAIL_ACCOUNT_ADDRESS",
        "ROBY_GMAIL_EMAIL",
        "GMAIL_ADDRESS",
        "EMAIL_USER",
        "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_MAX_RESULTS",
        "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_TIMEOUT_SECONDS",
        "ROBY_GMAIL_TOKEN_PATH",
    ):
        monkeypatch.delenv(name, raising=False)


def test_wiring_is_disabled_by_default(monkeypatch):
    clear_gmail(monkeypatch)
    assert GmailStartupWiringConfig.from_environment().enabled is False
    assert build_gmail_startup_announcer_from_environment() is None


def test_gmail_enabled_enables_announcement_by_default(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    config = GmailStartupWiringConfig.from_environment()
    assert config.enabled is True


def test_explicit_announcement_disable_wins(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED", "false")
    assert GmailStartupWiringConfig.from_environment().enabled is False


def test_account_alias_is_supported(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("EMAIL_USER", "legacy@example.com")
    assert (
        GmailStartupWiringConfig.from_environment().account_address
        == "legacy@example.com"
    )


def test_limits_are_read_from_environment(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_STARTUP_ANNOUNCEMENT_MAX_RESULTS", "3")
    monkeypatch.setenv("ROBY_GMAIL_STARTUP_ANNOUNCEMENT_TIMEOUT_SECONDS", "4.5")
    config = GmailStartupWiringConfig.from_environment()
    assert config.max_subjects == 3
    assert config.timeout_seconds == 4.5


def test_invalid_limit_is_rejected(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_STARTUP_ANNOUNCEMENT_MAX_RESULTS", "0")
    try:
        GmailStartupWiringConfig.from_environment()
    except ValueError as exc:
        assert "MAX_RESULTS" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_missing_account_degrades_without_crashing(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert lines[0].startswith("GMAIL> DEGRADED [configuration/account_missing]:")


def test_successful_announcement_is_rendered(monkeypatch):
    result = GmailSubjectAnnouncement(subjects=("Uno",), text="Tenés un correo nuevo.")

    class Announcer:
        def announce(self):
            return result

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is result
    assert lines == ["Roby> Tenés un correo nuevo."]


def test_provider_failure_is_degradable(monkeypatch):
    class Announcer:
        def announce(self):
            raise RuntimeError("secret provider detail")

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert "secret provider detail" not in " ".join(lines)


def test_source_does_not_reference_password_authentication():
    source = __import__("pathlib").Path("app/gmail_startup_wiring.py").read_text()
    assert "password" not in source.casefold()
    assert "pickle" not in source.casefold()
