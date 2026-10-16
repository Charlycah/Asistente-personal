from __future__ import annotations

import json
from pathlib import Path

from app.gmail_diagnostic_runtime import GmailDiagnosticRuntime
from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthDeploymentConfig,
    resolve_google_client_secrets_path,
)


def _clear(monkeypatch) -> None:
    for name in (
        "ROBY_GMAIL_CLIENT_SECRETS_PATH",
        "ROBY_GMAIL_TOKEN_PATH",
        "ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH",
        "ROBY_GMAIL_ENABLED",
        "ROBY_GMAIL_ACCOUNT_ADDRESS",
    ):
        monkeypatch.delenv(name, raising=False)


def test_resolver_uses_credentials_json_when_environment_is_absent(
    monkeypatch, tmp_path
):
    _clear(monkeypatch)
    credentials = tmp_path / "credentials.json"
    credentials.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    assert resolve_google_client_secrets_path() == credentials


def test_explicit_environment_path_has_absolute_precedence(monkeypatch, tmp_path):
    _clear(monkeypatch)
    fallback = tmp_path / "credentials.json"
    fallback.write_text("{}", encoding="utf-8")
    explicit = tmp_path / "configured.json"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_GMAIL_CLIENT_SECRETS_PATH", str(explicit))

    assert resolve_google_client_secrets_path() == explicit


def test_config_from_environment_receives_governed_fallback(monkeypatch, tmp_path):
    _clear(monkeypatch)
    credentials = tmp_path / "credentials.json"
    credentials.write_text("{}", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(tmp_path / "token.json"))

    config = GoogleOAuthDeploymentConfig.from_environment()

    assert config is not None
    assert config.client_secrets_path == credentials


def test_diagnostic_accepts_local_credentials_fallback(monkeypatch, tmp_path):
    _clear(monkeypatch)
    credentials = tmp_path / "credentials.json"
    credentials.write_text("{}", encoding="utf-8")
    token = tmp_path / "token.json"
    token.write_text(
        json.dumps(
            {
                "client_id": "id",
                "client_secret": "secret",
                "refresh_token": "refresh",
                "scopes": ["https://www.googleapis.com/auth/gmail.readonly"],
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(token))
    monkeypatch.setenv("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", "true")

    report = GmailDiagnosticRuntime().inspect_environment()
    finding = next(
        item for item in report.findings if item.component == "client_secrets"
    )

    assert finding.code == "client_secrets_available"


def test_missing_fallback_keeps_actionable_diagnostic(monkeypatch, tmp_path):
    _clear(monkeypatch)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    monkeypatch.setenv("ROBY_GMAIL_ACCOUNT_ADDRESS", "user@example.com")
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(tmp_path / "token.json"))
    monkeypatch.setenv("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", "true")

    report = GmailDiagnosticRuntime().inspect_environment()
    finding = next(
        item for item in report.findings if item.component == "client_secrets"
    )

    assert finding.code == "client_secrets_path_missing"
    assert "credentials.json" in finding.remediation
    assert str(Path.cwd()) not in " ".join(report.console_lines())
