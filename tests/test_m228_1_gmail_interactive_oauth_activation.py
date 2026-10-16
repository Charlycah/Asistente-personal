from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthActivationResult,
    GoogleOAuthDeploymentAdapter,
    GoogleOAuthDeploymentConfig,
)
from infrastructure.system.private_file_permissions import (
    private_path_is_restrictive,
)


class FakeCredentials:
    next_info: dict[str, object] = {}

    def __init__(self, info: dict[str, object]) -> None:
        self.info = dict(info)
        self.token = str(info.get("token", ""))
        self.refresh_token = str(info.get("refresh_token", ""))
        self.expiry = datetime(2099, 1, 1, tzinfo=timezone.utc)
        self.scopes = list(info.get("scopes", ["scope.read"]))
        self.valid = bool(info.get("valid", True))
        self.expired = bool(info.get("expired", False))
        self.refresh_calls = 0

    @classmethod
    def from_authorized_user_info(cls, info: dict[str, object]):
        return cls(info)

    def refresh(self, request: object) -> None:
        self.refresh_calls += 1
        self.token = "refreshed-secret"
        self.valid = True
        self.expired = False

    def to_json(self) -> str:
        return json.dumps(
            {
                "token": self.token,
                "refresh_token": self.refresh_token,
                "scopes": self.scopes,
                "valid": self.valid,
                "expired": self.expired,
            }
        )


class FakeFlow:
    @classmethod
    def from_client_secrets_file(cls, filename: str, scopes: list[str]):
        assert Path(filename).is_file()
        instance = cls()
        instance.scopes = scopes
        return instance

    def run_local_server(self, *, port: int):
        assert port == 0
        return FakeCredentials(
            {
                "token": "interactive-secret",
                "refresh_token": "interactive-refresh",
                "scopes": self.scopes,
            }
        )


class MemoryStore:
    def __init__(self, payload: dict[str, object] | None = None) -> None:
        self.payload = payload
        self.saved: tuple[str, dict[str, object]] | None = None

    def load(self, account_fingerprint: str) -> dict[str, object] | None:
        return dict(self.payload) if self.payload is not None else None

    def save(self, account_fingerprint: str, payload: dict[str, object]) -> None:
        self.saved = (account_fingerprint, dict(payload))
        self.payload = dict(payload)

    def delete(self, account_fingerprint: str) -> bool:
        self.payload = None
        return True


def patch_google(monkeypatch) -> None:
    def fake_import(module_name: str):
        if module_name == "google.oauth2.credentials":
            return type("Module", (), {"Credentials": FakeCredentials})
        if module_name == "google.auth.transport.requests":
            return type("Module", (), {"Request": object})
        if module_name == "google_auth_oauthlib.flow":
            return type("Module", (), {"InstalledAppFlow": FakeFlow})
        raise ImportError(module_name)

    monkeypatch.setattr("importlib.import_module", fake_import)


def configured_adapter(tmp_path: Path, *, store: MemoryStore | None = None):
    client = tmp_path / "client.json"
    client.write_text("{}", encoding="utf-8")
    return GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(
            token_path=tmp_path / "token.json",
            client_secrets_path=client,
            allow_interactive_authorization=True,
        ),
        credential_store=store,
    )


def test_activation_result_is_secret_free():
    result = GoogleOAuthActivationResult("interactive", False, True, True)
    assert result.to_dict() == {
        "source": "interactive",
        "refreshed": False,
        "persisted": True,
        "usable": True,
    }


def test_missing_credentials_trigger_interactive_flow(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    result = configured_adapter(tmp_path).activate("acct", ("scope.read",))
    assert result.source == "interactive"
    assert result.usable is True


def test_interactive_activation_persists_external_json(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    adapter = configured_adapter(tmp_path)
    adapter.activate("acct", ("scope.read",))
    payload = json.loads((tmp_path / "token.json").read_text(encoding="utf-8"))
    assert payload["refresh_token"] == "interactive-refresh"


def test_external_token_permissions_are_restrictive(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    adapter = configured_adapter(tmp_path)
    adapter.activate("acct", ("scope.read",))
    assert private_path_is_restrictive(tmp_path / "token.json")


def test_secure_store_is_preferred_for_persistence(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    store = MemoryStore()
    result = configured_adapter(tmp_path, store=store).activate("acct", ("scope.read",))
    assert result.persisted is True
    assert store.saved is not None
    assert not (tmp_path / "token.json").exists()


def test_expired_stored_credentials_are_refreshed(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    store = MemoryStore(
        {
            "token": "expired-secret",
            "refresh_token": "refresh-secret",
            "scopes": ["scope.read"],
            "valid": False,
            "expired": True,
        }
    )
    result = configured_adapter(tmp_path, store=store).activate("acct", ("scope.read",))
    assert result.source == "stored"
    assert result.refreshed is True
    assert store.saved is not None
    assert store.saved[1]["token"] == "refreshed-secret"


def test_valid_stored_credentials_are_repersisted_without_authorization(
    monkeypatch, tmp_path
):
    patch_google(monkeypatch)
    store = MemoryStore(
        {
            "token": "stored-secret",
            "refresh_token": "refresh-secret",
            "scopes": ["scope.read"],
            "valid": True,
            "expired": False,
        }
    )
    result = configured_adapter(tmp_path, store=store).activate("acct", ("scope.read",))
    assert result.source == "stored"
    assert result.refreshed is False


def test_invalid_credentials_without_refresh_trigger_interactive(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    store = MemoryStore(
        {
            "token": "invalid-secret",
            "refresh_token": "",
            "scopes": ["scope.read"],
            "valid": False,
            "expired": True,
        }
    )
    result = configured_adapter(tmp_path, store=store).activate("acct", ("scope.read",))
    assert result.source == "interactive"


def test_activation_remains_disabled_without_explicit_policy(tmp_path):
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=tmp_path / "token.json")
    )
    with pytest.raises(PermissionError, match="disabled"):
        adapter.activate("acct", ("scope.read",))


def test_activation_rejects_blank_account(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    with pytest.raises(ValueError, match="fingerprint"):
        configured_adapter(tmp_path).activate(" ", ("scope.read",))


def test_status_reports_counts_without_secret_values(monkeypatch, tmp_path):
    patch_google(monkeypatch)
    adapter = configured_adapter(tmp_path)
    adapter.activate("acct", ("scope.read",))
    rendered = str(adapter.status())
    assert "interactive-secret" not in rendered
    assert str(tmp_path) not in rendered
    assert adapter.status()["authorizations"] == 1
    assert adapter.status()["persisted"] == 1


def test_persistence_failure_has_stable_secret_free_error(monkeypatch, tmp_path):
    patch_google(monkeypatch)

    class BrokenStore(MemoryStore):
        def save(self, account_fingerprint: str, payload: dict[str, object]) -> None:
            raise OSError("interactive-secret leaked path")

    adapter = configured_adapter(tmp_path, store=BrokenStore())
    with pytest.raises(RuntimeError, match="persistence failed") as captured:
        adapter.activate("acct", ("scope.read",))
    assert "interactive-secret" not in str(captured.value)
