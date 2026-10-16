from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from infrastructure.mail.gmail_oauth_governance import (
    GmailOAuthGovernance,
    GmailOAuthPolicy,
)
from infrastructure.mail.gmail_provider_transport import (
    GmailProviderRejectedError,
    GmailProviderTransport,
    GmailProviderTransportError,
    GmailTransportErrorCode,
)
from infrastructure.mail.gmail_retry_governance import (
    GmailRetryDecision,
    GmailRetryGovernance,
    GmailRetryPolicy,
)

NOW = datetime(2026, 7, 14, 15, tzinfo=timezone.utc)


class Credential:
    expires_at = NOW + timedelta(hours=1)
    scopes = ("gmail.readonly", "gmail.send")
    revoked = False

    def refresh(self):
        return None

    def revoke(self):
        self.revoked = True


class Provider:
    def load(self, account_fingerprint):
        return Credential()


class Backend:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def execute(self, operation, payload, *, timeout_seconds):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def governance(outcomes, *, policy=None, delays=None):
    oauth = GmailOAuthGovernance(
        account_fingerprint="account",
        credential_provider=Provider(),
        policy=GmailOAuthPolicy(required_scopes=("gmail.readonly",)),
    )
    transport = GmailProviderTransport(Backend(outcomes), oauth)
    observed = delays if delays is not None else []
    return GmailRetryGovernance(transport, policy, observed.append), transport.backend


def test_success_does_not_retry():
    boundary, backend = governance([{"ok": True}])
    assert boundary.execute("list_recent", now=NOW).payload == {"ok": True}
    assert backend.calls == 1


def test_timeout_is_retried_until_success():
    delays = []
    boundary, backend = governance([TimeoutError(), {"ok": True}], delays=delays)
    boundary.execute("list_recent", now=NOW)
    assert backend.calls == 2
    assert delays == [0.25]


def test_rate_limit_uses_exponential_backoff():
    from infrastructure.mail.gmail_provider_transport import GmailProviderRateLimitError

    delays = []
    boundary, _ = governance(
        [GmailProviderRateLimitError(), GmailProviderRateLimitError(), {"ok": True}],
        delays=delays,
    )
    boundary.execute("list_recent", now=NOW)
    assert delays == [0.25, 0.5]


def test_backoff_is_capped():
    policy = GmailRetryPolicy(
        max_attempts=4,
        initial_backoff_seconds=2,
        backoff_multiplier=3,
        max_backoff_seconds=4,
    )
    assert [policy.backoff_for_attempt(i) for i in (1, 2, 3)] == [2, 4, 4]


def test_non_retryable_error_stops_immediately():
    boundary, backend = governance([GmailProviderRejectedError("private")])
    with pytest.raises(GmailProviderTransportError) as captured:
        boundary.execute("list_recent", now=NOW)
    assert captured.value.code is GmailTransportErrorCode.REJECTED
    assert backend.calls == 1


def test_retryable_error_is_bounded_by_max_attempts():
    policy = GmailRetryPolicy(max_attempts=2, initial_backoff_seconds=0)
    boundary, backend = governance([TimeoutError(), TimeoutError()], policy=policy)
    with pytest.raises(GmailProviderTransportError):
        boundary.execute("list_recent", now=NOW)
    assert backend.calls == 2
    assert boundary.status()["exhausted_count"] == 1


def test_send_requires_idempotency_key_before_transport_call():
    boundary, backend = governance([{"ok": True}])
    with pytest.raises(ValueError, match="idempotency"):
        boundary.execute("send", {"to": "a", "subject": "s", "body": "b"}, now=NOW)
    assert backend.calls == 0


def test_send_accepts_non_empty_idempotency_key():
    boundary, backend = governance([{"ok": True}])
    boundary.execute(
        "send",
        {"to": "a", "subject": "s", "body": "b"},
        now=NOW,
        idempotency_key="request-1",
    )
    assert backend.calls == 1


def test_read_does_not_require_idempotency_key():
    boundary, backend = governance([{"ok": True}])
    boundary.execute("read", {"message_id": "m1"}, now=NOW)
    assert backend.calls == 1


def test_status_contains_safe_counts_and_decision():
    boundary, _ = governance([TimeoutError("secret"), {"ok": True}])
    boundary.execute("list_recent", now=NOW)
    status = boundary.status()
    assert status["retry_count"] == 1
    assert status["last_report"]["decision"] == GmailRetryDecision.SUCCESS.value
    assert "secret" not in repr(status)


def test_policy_rejects_invalid_values():
    with pytest.raises(ValueError):
        GmailRetryPolicy(max_attempts=0)
    with pytest.raises(ValueError):
        GmailRetryPolicy(backoff_multiplier=0.5)


def test_idempotency_key_is_not_exposed_in_status():
    boundary, _ = governance([{"ok": True}])
    boundary.execute(
        "send",
        {"to": "a", "subject": "s", "body": "b"},
        now=NOW,
        idempotency_key="private-key",
    )
    assert "private-key" not in repr(boundary.status())
