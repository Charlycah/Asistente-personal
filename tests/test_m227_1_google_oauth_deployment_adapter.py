from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthCredentialMaterial,
    GoogleOAuthDeploymentAdapter,
    GoogleOAuthDeploymentConfig,
)


class FakeCredentials:
    def __init__(self, info: dict[str, object]) -> None:
        self.info = info
        self.token = str(info.get("token", ""))
        self.refresh_token = str(info.get("refresh_token", ""))
        self.expiry = datetime(2099, 1, 1, tzinfo=timezone.utc)
        self.scopes = ["scope.read"]
        self.valid = True
        self.expired = False
        self.refresh_calls = 0

    @classmethod
    def from_authorized_user_info(cls, info: dict[str, object]):
        return cls(info)

    def refresh(self, request: object) -> None:
        self.refresh_calls += 1


class FakeFlow:
    credentials = FakeCredentials({"token": "new-secret"})

    @classmethod
    def from_client_secrets_file(cls, filename: str, scopes: list[str]):
        assert Path(filename).is_file()
        assert scopes == ["scope.read"]
        return cls()

    def run_local_server(self, *, port: int):
        assert port == 0
        return self.credentials


def patch_import(monkeypatch):
    def fake_import(module_name: str):
        if module_name == "google.oauth2.credentials":
            return type("Module", (), {"Credentials": FakeCredentials})
        if module_name == "google.auth.transport.requests":
            return type("Module", (), {"Request": object})
        if module_name == "google_auth_oauthlib.flow":
            return type("Module", (), {"InstalledAppFlow": FakeFlow})
        raise ImportError(module_name)

    monkeypatch.setattr("importlib.import_module", fake_import)


def write_token(path: Path) -> None:
    path.write_text(
        json.dumps({"token": "access-secret", "refresh_token": "refresh-secret"}),
        encoding="utf-8",
    )


def test_environment_without_token_path_disables_adapter(monkeypatch):
    monkeypatch.delenv("ROBY_GMAIL_TOKEN_PATH", raising=False)
    assert GoogleOAuthDeploymentConfig.from_environment() is None


def test_environment_builds_external_path_configuration(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_GMAIL_TOKEN_PATH", str(tmp_path / "token.json"))
    monkeypatch.setenv("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", "true")
    config = GoogleOAuthDeploymentConfig.from_environment()
    assert config is not None
    assert config.allow_interactive_authorization is True


def test_missing_external_token_returns_none(tmp_path):
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=tmp_path / "missing.json")
    )
    assert adapter.load("account") is None


def test_json_token_is_loaded_through_google_auth(monkeypatch, tmp_path):
    patch_import(monkeypatch)
    token = tmp_path / "token.json"
    write_token(token)
    material = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=token)
    ).load("account")
    assert isinstance(material, GoogleOAuthCredentialMaterial)
    assert material.scopes == ("scope.read",)


def test_status_never_exposes_paths_or_token_values(monkeypatch, tmp_path):
    patch_import(monkeypatch)
    token = tmp_path / "private-token.json"
    write_token(token)
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=token)
    )
    adapter.load("account")
    rendered = str(adapter.status())
    assert str(token) not in rendered
    assert "access-secret" not in rendered
    assert "refresh-secret" not in rendered


def test_invalid_json_has_stable_secret_free_error(tmp_path):
    token = tmp_path / "token.json"
    token.write_text("not-json secret-value", encoding="utf-8")
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=token)
    )
    with pytest.raises(RuntimeError, match="credentials unavailable") as captured:
        adapter.load("account")
    assert "secret-value" not in str(captured.value)


def test_missing_google_dependency_has_stable_error(tmp_path):
    token = tmp_path / "token.json"
    write_token(token)
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=token)
    )
    with pytest.raises(RuntimeError, match="credentials unavailable"):
        adapter.load("account")


def test_material_refresh_uses_google_request(monkeypatch):
    patch_import(monkeypatch)
    credentials = FakeCredentials({"token": "secret"})
    material = GoogleOAuthCredentialMaterial(credentials)
    material.refresh()
    assert credentials.refresh_calls == 1


def test_material_revoke_is_local_and_secret_free():
    material = GoogleOAuthCredentialMaterial(FakeCredentials({"token": "secret"}))
    material.revoke()
    assert material.revoked is True


def test_interactive_authorization_is_disabled_by_default(tmp_path):
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=tmp_path / "token.json")
    )
    with pytest.raises(PermissionError, match="disabled"):
        adapter.authorize(("scope.read",))


def test_interactive_authorization_requires_client_configuration(tmp_path):
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(
            token_path=tmp_path / "token.json",
            allow_interactive_authorization=True,
        )
    )
    with pytest.raises(RuntimeError, match="client configuration unavailable"):
        adapter.authorize(("scope.read",))


def test_interactive_authorization_delegates_to_google_flow(monkeypatch, tmp_path):
    patch_import(monkeypatch)
    client = tmp_path / "client.json"
    client.write_text("{}", encoding="utf-8")
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(
            token_path=tmp_path / "token.json",
            client_secrets_path=client,
            allow_interactive_authorization=True,
        )
    )
    material = adapter.authorize(("scope.read",))
    assert material.scopes == ("scope.read",)
