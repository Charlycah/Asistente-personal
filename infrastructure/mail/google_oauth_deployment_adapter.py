from __future__ import annotations

import importlib
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

from infrastructure.mail.secure_credential_store import SecureCredentialStore
from infrastructure.system.private_file_permissions import harden_private_path

_DEFAULT_CLIENT_SECRETS_FILENAME = "credentials.json"


class OAuthCredentialsLike(Protocol):
    token: str | None
    refresh_token: str | None
    expiry: datetime | None
    scopes: list[str] | tuple[str, ...] | None
    valid: bool
    expired: bool

    def refresh(self, request: object) -> None: ...

    def to_json(self) -> str: ...


@dataclass(frozen=True)
class GoogleOAuthDeploymentConfig:
    """External deployment inputs; paths are never serialized by status()."""

    token_path: Path
    client_secrets_path: Path | None = None
    allow_interactive_authorization: bool = False

    @classmethod
    def from_environment(cls) -> GoogleOAuthDeploymentConfig | None:
        raw_token = os.getenv("ROBY_GMAIL_TOKEN_PATH", "").strip()
        if not raw_token:
            return None
        client_secrets_path = resolve_google_client_secrets_path()
        interactive = (
            os.getenv("ROBY_GMAIL_ALLOW_INTERACTIVE_OAUTH", "").strip().lower()
        )
        return cls(
            token_path=Path(raw_token).expanduser(),
            client_secrets_path=client_secrets_path,
            allow_interactive_authorization=interactive in {"1", "true", "yes", "on"},
        )


def resolve_google_client_secrets_path() -> Path | None:
    """Resolve governed Client Secrets with explicit configuration precedence."""
    raw_client = os.getenv("ROBY_GMAIL_CLIENT_SECRETS_PATH", "").strip()
    if raw_client:
        return Path(raw_client).expanduser()
    fallback = Path.cwd() / _DEFAULT_CLIENT_SECRETS_FILENAME
    return fallback if fallback.is_file() else None


@dataclass(frozen=True)
class GoogleOAuthActivationResult:
    """Secret-free result of one explicit interactive OAuth activation."""

    source: str
    refreshed: bool
    persisted: bool
    usable: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "refreshed": self.refreshed,
            "persisted": self.persisted,
            "usable": self.usable,
        }


class GoogleOAuthCredentialMaterial:
    """Provider-neutral facade over google-auth credentials."""

    def __init__(self, credentials: OAuthCredentialsLike) -> None:
        self._credentials = credentials
        self._revoked = False

    @property
    def expires_at(self) -> datetime | None:
        expiry = self._credentials.expiry
        if expiry is not None and expiry.tzinfo is None:
            return expiry.replace(tzinfo=timezone.utc)
        return expiry

    @property
    def scopes(self) -> tuple[str, ...]:
        return tuple(self._credentials.scopes or ())

    @property
    def revoked(self) -> bool:
        return self._revoked

    @property
    def deployment_credentials(self) -> OAuthCredentialsLike:
        """Return the deployment-owned SDK credential object without serializing it."""
        return self._credentials

    def refresh(self) -> None:
        request_type = _import_symbol("google.auth.transport.requests", "Request")
        self._credentials.refresh(request_type())

    def revoke(self) -> None:
        self._revoked = True


class GoogleOAuthDeploymentAdapter:
    """M227.1 deployment adapter loading Google credentials from external files."""

    def __init__(
        self,
        config: GoogleOAuthDeploymentConfig,
        *,
        credential_store: SecureCredentialStore | None = None,
    ) -> None:
        self.config = config
        self._credential_store = credential_store
        self._loads = 0
        self._failures = 0
        self._authorizations = 0
        self._refreshes = 0
        self._persisted = 0

    def load(self, account_fingerprint: str) -> GoogleOAuthCredentialMaterial | None:
        if not account_fingerprint.strip():
            raise ValueError("gmail oauth account fingerprint must not be blank")
        self._loads += 1
        path = self.config.token_path
        try:
            payload = (
                self._credential_store.load(account_fingerprint)
                if self._credential_store is not None
                else None
            )
            if payload is None:
                if not path.is_file():
                    return None
                payload = _load_json_object(path)
            credentials_type = _import_symbol(
                "google.oauth2.credentials", "Credentials"
            )
            credentials = credentials_type.from_authorized_user_info(payload)
        except (OSError, ValueError, TypeError, ImportError, AttributeError) as exc:
            self._failures += 1
            raise RuntimeError(
                "google oauth deployment credentials unavailable"
            ) from exc
        return GoogleOAuthCredentialMaterial(credentials)

    def authorize(self, scopes: tuple[str, ...]) -> GoogleOAuthCredentialMaterial:
        credentials = self._authorize_credentials(scopes)
        return GoogleOAuthCredentialMaterial(credentials)

    def activate(
        self,
        account_fingerprint: str,
        scopes: tuple[str, ...],
    ) -> GoogleOAuthActivationResult:
        """Load, refresh, or explicitly authorize and persist Google credentials."""
        if not account_fingerprint.strip():
            raise ValueError("gmail oauth account fingerprint must not be blank")
        material = self.load(account_fingerprint)
        source = "stored"
        refreshed = False
        if material is None:
            credentials = self._authorize_credentials(scopes)
            material = GoogleOAuthCredentialMaterial(credentials)
            source = "interactive"
        elif material._credentials.expired and material._credentials.refresh_token:
            try:
                material.refresh()
            except (OSError, ValueError, TypeError, ImportError, AttributeError) as exc:
                self._failures += 1
                raise RuntimeError("google oauth credential refresh failed") from exc
            refreshed = True
            self._refreshes += 1
        elif not material._credentials.valid:
            credentials = self._authorize_credentials(scopes)
            material = GoogleOAuthCredentialMaterial(credentials)
            source = "interactive"

        payload = _serialize_authorized_user_credentials(material._credentials)
        self._persist(account_fingerprint, payload)
        usable = bool(material._credentials.valid and not material._credentials.expired)
        return GoogleOAuthActivationResult(
            source=source,
            refreshed=refreshed,
            persisted=True,
            usable=usable,
        )

    def _authorize_credentials(self, scopes: tuple[str, ...]) -> OAuthCredentialsLike:
        if not self.config.allow_interactive_authorization:
            raise PermissionError(
                "interactive google oauth disabled by deployment policy"
            )
        client_path = self.config.client_secrets_path
        if client_path is None or not client_path.is_file():
            raise RuntimeError("google oauth client configuration unavailable")
        if not scopes or any(not scope.strip() for scope in scopes):
            raise ValueError("google oauth scopes must not be blank")
        try:
            flow_type = _import_symbol("google_auth_oauthlib.flow", "InstalledAppFlow")
            flow = flow_type.from_client_secrets_file(str(client_path), list(scopes))
            credentials = flow.run_local_server(port=0)
        except (OSError, ValueError, TypeError, ImportError, AttributeError) as exc:
            self._failures += 1
            raise RuntimeError("interactive google oauth authorization failed") from exc
        self._authorizations += 1
        return credentials

    def _persist(self, account_fingerprint: str, payload: dict[str, object]) -> None:
        try:
            if self._credential_store is not None:
                self._credential_store.save(account_fingerprint, payload)
            else:
                _atomic_write_json(self.config.token_path, payload)
        except (OSError, ValueError, TypeError) as exc:
            self._failures += 1
            raise RuntimeError("google oauth credential persistence failed") from exc
        self._persisted += 1

    def status(self) -> dict[str, object]:
        return {
            "configured": (
                self._credential_store is not None or self.config.token_path.is_file()
            ),
            "secure_store_enabled": self._credential_store is not None,
            "client_configuration_available": (
                self.config.client_secrets_path is not None
                and self.config.client_secrets_path.is_file()
            ),
            "interactive_authorization_allowed": (
                self.config.allow_interactive_authorization
            ),
            "loads": self._loads,
            "failures": self._failures,
            "authorizations": self._authorizations,
            "refreshes": self._refreshes,
            "persisted": self._persisted,
        }


def _load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        payload = json.load(stream)
    if not isinstance(payload, dict):
        raise ValueError("google oauth token document must be an object")
    return payload


def _import_symbol(module_name: str, symbol_name: str) -> Any:
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise ImportError("google oauth deployment dependency unavailable") from exc
    try:
        return getattr(module, symbol_name)
    except AttributeError as exc:
        raise ImportError("google oauth deployment dependency incomplete") from exc


def _serialize_authorized_user_credentials(
    credentials: OAuthCredentialsLike,
) -> dict[str, object]:
    try:
        payload = json.loads(credentials.to_json())
    except (AttributeError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("google oauth credentials are not serializable") from exc
    if not isinstance(payload, dict):
        raise ValueError("google oauth credentials must serialize to an object")
    return payload


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, sort_keys=True, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        harden_private_path(path)
    finally:
        if temporary.exists():
            temporary.unlink()
