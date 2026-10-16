from __future__ import annotations

import json
from pathlib import Path

import pytest

from infrastructure.mail.google_oauth_deployment_adapter import (
    GoogleOAuthDeploymentAdapter,
    GoogleOAuthDeploymentConfig,
)
from infrastructure.mail.secure_credential_store import EncryptedFileCredentialStore
from infrastructure.system.private_file_permissions import (
    private_path_is_restrictive,
)


class FakeProtector:
    def __init__(self, key_id: str, key: int) -> None:
        self._key_id = key_id
        self._key = key

    @property
    def key_id(self) -> str:
        return self._key_id

    def protect(self, plaintext: bytes) -> bytes:
        return bytes(value ^ self._key for value in plaintext)

    def unprotect(self, ciphertext: bytes) -> bytes:
        return bytes(value ^ self._key for value in ciphertext)


def make_store(tmp_path: Path) -> EncryptedFileCredentialStore:
    return EncryptedFileCredentialStore(tmp_path / "vault", FakeProtector("key-a", 73))


def test_save_and_load_round_trip_without_plaintext_on_disk(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    payload = {"token": "secret-token", "refresh_token": "refresh-secret"}
    store.save("account-abc", payload)
    assert store.load("account-abc") == payload
    raw = next((tmp_path / "vault").glob("*.cred")).read_text()
    assert "secret-token" not in raw
    assert "refresh-secret" not in raw


def test_missing_record_returns_none(tmp_path: Path) -> None:
    assert make_store(tmp_path).load("account-abc") is None


def test_record_filename_does_not_expose_account_fingerprint(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("user@example.invalid", {"token": "x"})
    path = next((tmp_path / "vault").glob("*.cred"))
    assert "user" not in path.name
    assert "example" not in path.name


def test_invalid_account_fingerprint_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="fingerprint is invalid"):
        make_store(tmp_path).save("../escape", {"token": "x"})


def test_tampered_ciphertext_fails_without_publishing_secret(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "super-secret"})
    path = next((tmp_path / "vault").glob("*.cred"))
    envelope = json.loads(path.read_text())
    envelope["ciphertext"] = "not-valid-base64!"
    path.write_text(json.dumps(envelope))
    with pytest.raises(RuntimeError) as error:
        store.load("account-abc")
    assert "super-secret" not in str(error.value)


def test_rotation_reencrypts_with_new_protector(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "secret"})
    before = next((tmp_path / "vault").glob("*.cred")).read_bytes()
    assert store.rotate("account-abc", FakeProtector("key-b", 19)) is True
    after = next((tmp_path / "vault").glob("*.cred")).read_bytes()
    assert before != after
    assert store.load("account-abc") == {"token": "secret"}
    assert store.status()["rotations"] == 1


def test_rotation_of_missing_record_is_false(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    assert store.rotate("account-abc", FakeProtector("key-b", 19)) is False


def test_delete_removes_record_and_is_idempotent(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "secret"})
    assert store.delete("account-abc") is True
    assert store.delete("account-abc") is False
    assert store.load("account-abc") is None


def test_status_is_secret_free(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "secret"})
    status = store.status()
    text = repr(status)
    assert status["records"] == 1
    assert status["writes"] == 1
    assert "secret" not in text
    assert "key-a" not in text
    assert str(tmp_path) not in text


def test_local_permissions_are_restrictive(tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "secret"})
    root = tmp_path / "vault"
    credential = next(root.glob("*.cred"))
    assert private_path_is_restrictive(root, directory=True)
    assert private_path_is_restrictive(credential)


def test_google_adapter_prefers_secure_store(monkeypatch, tmp_path: Path) -> None:
    store = make_store(tmp_path)
    store.save("account-abc", {"token": "from-store"})

    class Credentials:
        @classmethod
        def from_authorized_user_info(cls, payload):
            assert payload["token"] == "from-store"
            instance = cls()
            instance.expiry = None
            instance.scopes = []
            return instance

    monkeypatch.setattr(
        "infrastructure.mail.google_oauth_deployment_adapter._import_symbol",
        lambda module, symbol: Credentials,
    )
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=tmp_path / "missing.json"),
        credential_store=store,
    )
    assert adapter.load("account-abc") is not None
    assert adapter.status()["secure_store_enabled"] is True


def test_google_adapter_falls_back_to_external_token_file(
    monkeypatch, tmp_path: Path
) -> None:
    token_path = tmp_path / "token.json"
    token_path.write_text('{"token":"from-file"}')

    class Credentials:
        @classmethod
        def from_authorized_user_info(cls, payload):
            assert payload["token"] == "from-file"
            instance = cls()
            instance.expiry = None
            instance.scopes = []
            return instance

    monkeypatch.setattr(
        "infrastructure.mail.google_oauth_deployment_adapter._import_symbol",
        lambda module, symbol: Credentials,
    )
    adapter = GoogleOAuthDeploymentAdapter(
        GoogleOAuthDeploymentConfig(token_path=token_path),
        credential_store=make_store(tmp_path),
    )
    assert adapter.load("account-abc") is not None
