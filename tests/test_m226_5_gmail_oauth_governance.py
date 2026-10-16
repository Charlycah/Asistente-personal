from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from infrastructure.mail.gmail_governed_integration import GmailGovernedIntegration
from infrastructure.mail.gmail_oauth_governance import (
    GmailOAuthGovernance,
    GmailOAuthPolicy,
    GmailOAuthSnapshot,
    GmailOAuthState,
)
from infrastructure.mail.mail_action_adapter import MailActionAdapter
from infrastructure.mail.mail_adapter import MailReaderAdapter

READ_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"
NOW = datetime(2099, 7, 14, 15, tzinfo=timezone.utc)


@dataclass
class FakeCredential:
    token: str
    refresh_token: str
    expires_at: datetime | None
    scopes: tuple[str, ...]
    revoked: bool = False
    refresh_calls: int = 0
    revoke_calls: int = 0

    def refresh(self) -> None:
        self.refresh_calls += 1
        self.expires_at = NOW + timedelta(hours=1)

    def revoke(self) -> None:
        self.revoke_calls += 1
        self.revoked = True


class FakeProvider:
    def __init__(self, credential: FakeCredential | None) -> None:
        self.credential = credential
        self.loads: list[str] = []

    def load(self, account_fingerprint: str) -> FakeCredential | None:
        self.loads.append(account_fingerprint)
        return self.credential


class NullReader:
    pass


class NullActions:
    pass


def governance(
    credential: FakeCredential | None,
    *,
    policy: GmailOAuthPolicy | None = None,
) -> GmailOAuthGovernance:
    return GmailOAuthGovernance(
        account_fingerprint="account-fingerprint",
        credential_provider=FakeProvider(credential),
        policy=policy,
    )


def credential(
    *,
    expires_at: datetime | None = None,
    scopes: tuple[str, ...] = (READ_SCOPE,),
) -> FakeCredential:
    return FakeCredential(
        token="access-secret",
        refresh_token="refresh-secret",
        expires_at=expires_at or NOW + timedelta(minutes=30),
        scopes=scopes,
    )


def test_absent_credentials_have_explicit_state():
    snapshot = governance(None).inspect(now=NOW)
    assert snapshot.state is GmailOAuthState.ABSENT
    assert snapshot.usable is False


def test_ready_credentials_are_usable():
    snapshot = governance(credential()).inspect(now=NOW)
    assert snapshot.state is GmailOAuthState.READY
    assert snapshot.usable is True


def test_expired_credentials_are_not_usable():
    snapshot = governance(credential(expires_at=NOW - timedelta(seconds=1))).inspect(
        now=NOW
    )
    assert snapshot.state is GmailOAuthState.EXPIRED


def test_revoked_credentials_have_precedence():
    item = credential(expires_at=NOW - timedelta(seconds=1))
    item.revoked = True
    assert governance(item).inspect(now=NOW).state is GmailOAuthState.REVOKED


def test_missing_required_scope_is_detected():
    policy = GmailOAuthPolicy(required_scopes=(READ_SCOPE, SEND_SCOPE))
    snapshot = governance(credential(), policy=policy).inspect(now=NOW)
    assert snapshot.state is GmailOAuthState.INSUFFICIENT_SCOPE


def test_snapshot_never_exposes_tokens_or_raw_scopes():
    item = credential()
    rendered = str(governance(item).inspect(now=NOW).to_dict())
    assert item.token not in rendered
    assert item.refresh_token not in rendered
    assert READ_SCOPE not in rendered


def test_snapshot_is_immutable():
    snapshot = governance(credential()).inspect(now=NOW)
    assert isinstance(snapshot, GmailOAuthSnapshot)
    with pytest.raises(AttributeError):
        snapshot.state = GmailOAuthState.REVOKED


def test_refresh_is_delegated_and_reinspected():
    item = credential(expires_at=NOW - timedelta(minutes=1))
    snapshot = governance(item).refresh(now=NOW)
    assert item.refresh_calls == 1
    assert snapshot.state is GmailOAuthState.READY


def test_refresh_can_be_disabled_by_policy():
    policy = GmailOAuthPolicy(allow_refresh=False)
    with pytest.raises(PermissionError, match="refresh disabled"):
        governance(credential(), policy=policy).refresh(now=NOW)


def test_revoke_is_delegated_and_reported():
    item = credential()
    snapshot = governance(item).revoke(now=NOW)
    assert item.revoke_calls == 1
    assert snapshot.state is GmailOAuthState.REVOKED


def test_naive_expiry_is_rejected():
    item = credential(expires_at=datetime(2026, 7, 14, 15))
    with pytest.raises(ValueError, match="timezone-aware"):
        governance(item).inspect(now=NOW)


def test_gmail_status_reports_optional_oauth_governance():
    oauth = governance(credential())
    integration = GmailGovernedIntegration(
        account_address="carlos@example.com",
        reader=MailReaderAdapter(NullReader()),
        actions=MailActionAdapter(NullActions()),
        oauth_governance=oauth,
    )
    status = integration.status()
    assert status["oauth_governance_enabled"] is True
    assert status["oauth_state"] == "ready"
