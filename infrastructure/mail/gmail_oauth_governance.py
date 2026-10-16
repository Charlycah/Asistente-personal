from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol


class GmailOAuthState(str, Enum):
    """Secret-free lifecycle states for governed Gmail credentials."""

    ABSENT = "absent"
    READY = "ready"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INSUFFICIENT_SCOPE = "insufficient_scope"


class GmailCredentialMaterial(Protocol):
    """Minimal provider-neutral credential contract consumed by ROBY."""

    @property
    def expires_at(self) -> datetime | None: ...

    @property
    def scopes(self) -> Iterable[str]: ...

    @property
    def revoked(self) -> bool: ...

    def refresh(self) -> None: ...

    def revoke(self) -> None: ...


class GmailCredentialProvider(Protocol):
    """Boundary for loading credentials from an external secret store."""

    def load(self, account_fingerprint: str) -> GmailCredentialMaterial | None: ...


@dataclass(frozen=True)
class GmailOAuthPolicy:
    """Local OAuth policy independent from provider SDKs and token formats."""

    required_scopes: tuple[str, ...] = (
        "https://www.googleapis.com/auth/gmail.readonly",
    )
    allow_refresh: bool = True
    allow_revoke: bool = True

    def __post_init__(self) -> None:
        normalized = tuple(scope.strip() for scope in self.required_scopes)
        if any(not scope for scope in normalized):
            raise ValueError("gmail oauth scopes must not be blank")
        if len(set(normalized)) != len(normalized):
            raise ValueError("gmail oauth scopes must be unique")


@dataclass(frozen=True)
class GmailOAuthSnapshot:
    """Immutable, secret-free description of one credential lifecycle state."""

    account_fingerprint: str
    state: GmailOAuthState
    granted_scope_fingerprints: tuple[str, ...]
    required_scope_fingerprints: tuple[str, ...]
    expires_at: datetime | None
    refresh_allowed: bool
    revoke_allowed: bool

    def __post_init__(self) -> None:
        if not self.account_fingerprint.strip():
            raise ValueError("gmail oauth account fingerprint must not be blank")
        if self.expires_at is not None and self.expires_at.tzinfo is None:
            raise ValueError("gmail oauth expiry must be timezone-aware")

    @property
    def usable(self) -> bool:
        return self.state is GmailOAuthState.READY

    def to_dict(self) -> dict[str, object]:
        return {
            "account_fingerprint": self.account_fingerprint,
            "state": self.state.value,
            "granted_scope_fingerprints": self.granted_scope_fingerprints,
            "required_scope_fingerprints": self.required_scope_fingerprints,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "refresh_allowed": self.refresh_allowed,
            "revoke_allowed": self.revoke_allowed,
            "usable": self.usable,
        }


class GmailOAuthGovernance:
    """M226.5 governed OAuth lifecycle boundary without secret persistence."""

    def __init__(
        self,
        *,
        account_fingerprint: str,
        credential_provider: GmailCredentialProvider,
        policy: GmailOAuthPolicy | None = None,
    ) -> None:
        if not account_fingerprint.strip():
            raise ValueError("gmail oauth account fingerprint must not be blank")
        self._account_fingerprint = account_fingerprint
        self._provider = credential_provider
        self.policy = policy or GmailOAuthPolicy()

    @staticmethod
    def fingerprint_scope(scope: str) -> str:
        normalized = scope.strip()
        if not normalized:
            raise ValueError("gmail oauth scope must not be blank")
        return sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def inspect(self, *, now: datetime | None = None) -> GmailOAuthSnapshot:
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            raise ValueError("gmail oauth inspection time must be timezone-aware")
        material = self._provider.load(self._account_fingerprint)
        required = tuple(sorted(self.policy.required_scopes))
        if material is None:
            return self._snapshot(GmailOAuthState.ABSENT, (), required, None)

        granted = tuple(sorted(set(material.scopes)))
        expiry = material.expires_at
        if expiry is not None and expiry.tzinfo is None:
            raise ValueError("gmail oauth credential expiry must be timezone-aware")
        if material.revoked:
            state = GmailOAuthState.REVOKED
        elif not set(required).issubset(granted):
            state = GmailOAuthState.INSUFFICIENT_SCOPE
        elif expiry is not None and expiry <= current:
            state = GmailOAuthState.EXPIRED
        else:
            state = GmailOAuthState.READY
        return self._snapshot(state, granted, required, expiry)

    def refresh(self, *, now: datetime | None = None) -> GmailOAuthSnapshot:
        if not self.policy.allow_refresh:
            raise PermissionError("gmail oauth refresh disabled by policy")
        material = self._provider.load(self._account_fingerprint)
        if material is None:
            raise RuntimeError("gmail oauth credentials are unavailable")
        if material.revoked:
            raise PermissionError("gmail oauth credentials are revoked")
        material.refresh()
        return self.inspect(now=now)

    def revoke(self, *, now: datetime | None = None) -> GmailOAuthSnapshot:
        if not self.policy.allow_revoke:
            raise PermissionError("gmail oauth revoke disabled by policy")
        material = self._provider.load(self._account_fingerprint)
        if material is None:
            raise RuntimeError("gmail oauth credentials are unavailable")
        material.revoke()
        return self.inspect(now=now)

    def status(self, *, now: datetime | None = None) -> Mapping[str, object]:
        return self.inspect(now=now).to_dict()

    def _snapshot(
        self,
        state: GmailOAuthState,
        granted: Iterable[str],
        required: Iterable[str],
        expires_at: datetime | None,
    ) -> GmailOAuthSnapshot:
        return GmailOAuthSnapshot(
            account_fingerprint=self._account_fingerprint,
            state=state,
            granted_scope_fingerprints=tuple(
                self.fingerprint_scope(scope) for scope in granted
            ),
            required_scope_fingerprints=tuple(
                self.fingerprint_scope(scope) for scope in required
            ),
            expires_at=expires_at,
            refresh_allowed=self.policy.allow_refresh,
            revoke_allowed=self.policy.allow_revoke,
        )
