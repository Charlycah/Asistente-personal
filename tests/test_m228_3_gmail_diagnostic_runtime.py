from __future__ import annotations

import json

from app.gmail_diagnostic_runtime import (
    GmailDiagnosticRuntime,
    GmailDiagnosticState,
)
from app.gmail_startup_wiring import announce_gmail_startup_from_environment


def clear_gmail(monkeypatch):
    for name in (
        "ROBY_GMAIL_ENABLED",
        "ROBY_GMAIL_STARTUP_ANNOUNCEMENT_ENABLED",
        "ROBY_GMAIL_ACCOUNT_ADDRESS",
        "ROBY_GMAIL_EMAIL",
        "GMAIL_ADDRESS",
        "EMAIL_USER",
        "ROBY_GMAIL_TOKEN_PATH",
        "ROBY_GMAIL_CLIENT_SECRETS_PATH",
        "ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH",
    ):
        monkeypatch.delenv(name, raising=False)


def test_disabled_runtime_is_reported_without_console_noise(monkeypatch):
    clear_gmail(monkeypatch)
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.state is GmailDiagnosticState.DISABLED
    assert report.primary.code == "gmail_disabled"
    assert report.console_lines() == ()


def test_missing_account_is_exactly_identified(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    token = tmp_path / "token.json"
    token.write_text(json.dumps(valid_token()))
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(token))
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.state is GmailDiagnosticState.DEGRADED
    assert report.primary.component == "configuration"
    assert report.primary.code == "account_missing"


def test_missing_token_path_is_exactly_identified(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.primary.component == "oauth"
    assert report.primary.code == "token_path_missing"


def test_missing_token_file_is_exactly_identified(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(tmp_path / "absent.json"))
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.primary.component == "token"
    assert report.primary.code == "token_missing"


def test_invalid_token_json_is_exactly_identified(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    token = tmp_path / "token.json"
    token.write_text("not-json")
    configure(monkeypatch, token)
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.primary.code == "token_invalid_json"


def test_missing_token_fields_are_exactly_identified(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    token = tmp_path / "token.json"
    token.write_text("{}")
    configure(monkeypatch, token)
    assert (
        GmailDiagnosticRuntime().inspect_environment().primary.code
        == "token_fields_missing"
    )


def test_missing_readonly_scope_is_exactly_identified(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    token = tmp_path / "token.json"
    payload = valid_token()
    payload["scopes"] = ["https://www.googleapis.com/auth/gmail.send"]
    token.write_text(json.dumps(payload))
    configure(monkeypatch, token)
    report = GmailDiagnosticRuntime().inspect_environment()
    assert report.primary.component == "scopes"
    assert report.primary.code == "readonly_scope_missing"


def test_interactive_oauth_requires_client_secrets(monkeypatch, tmp_path):
    clear_gmail(monkeypatch)
    monkeypatch.chdir(tmp_path)

    token = tmp_path / "token.json"
    token.write_text(json.dumps(valid_token()))
    configure(monkeypatch, token)
    monkeypatch.setenv("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", "true")

    report = GmailDiagnosticRuntime().inspect_environment()
    finding = next(
        item for item in report.findings if item.component == "client_secrets"
    )

    assert finding.code == "client_secrets_path_missing"


def test_permission_failure_is_classified_without_private_detail():
    error = PermissionError("/private/secret/token.json")
    report = GmailDiagnosticRuntime().from_exception(error)
    rendered = " ".join(report.console_lines())
    assert report.primary.component == "permissions"
    assert report.primary.code == "permission_denied"
    assert "/private/secret" not in rendered


def test_nested_import_failure_is_classified():
    try:
        try:
            raise ImportError("private module name")
        except ImportError as cause:
            raise RuntimeError("wrapper") from cause
    except RuntimeError as error:
        report = GmailDiagnosticRuntime().from_exception(error)
    assert report.primary.component == "google_auth"
    assert report.primary.code == "dependency_import_failed"


def test_secure_store_failure_is_classified():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("secure credential store read failed")
    )
    assert report.primary.component == "secure_credential_store"
    assert report.primary.code == "secure_store_read_failed"


def test_subject_lookup_failure_is_classified():
    report = GmailDiagnosticRuntime().from_exception(
        RuntimeError("gmail unread subject lookup failed")
    )
    assert report.primary.component == "startup_announcement"
    assert report.primary.code == "subject_lookup_failed"


def test_startup_wiring_prints_actionable_diagnostic(monkeypatch):
    class Announcer:
        def announce(self):
            raise RuntimeError("gmail unread subject lookup failed: private")

    monkeypatch.setattr(
        "app.gmail_startup_wiring.build_gmail_startup_announcer_from_environment",
        lambda: Announcer(),
    )
    lines = []
    assert announce_gmail_startup_from_environment(write=lines.append) is None
    assert lines[0].startswith(
        "GMAIL> DEGRADED [startup_announcement/subject_lookup_failed]:"
    )
    assert "private" not in lines[0]


def test_report_serialization_is_secret_free(monkeypatch):
    clear_gmail(monkeypatch)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "secret@example.com")
    report = GmailDiagnosticRuntime().inspect_environment()
    rendered = repr(report.to_dict())
    assert "secret@example.com" not in rendered
    assert "ROBY_GMAIL_ACCOUNT_ADDRESS" not in rendered


def valid_token():
    return {
        "client_id": "id",
        "client_secret": "secret",
        "refresh_token": "refresh",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
    }


def configure(monkeypatch, token):
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(token))
