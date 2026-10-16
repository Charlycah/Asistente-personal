from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from infrastructure.mail.gmail_oauth_governance import (
    GmailOAuthGovernance,
    GmailOAuthPolicy,
)
from infrastructure.mail.gmail_provider_transport import (
    GmailProviderRateLimitError,
    GmailProviderRejectedError,
    GmailProviderTransport,
    GmailProviderTransportError,
    GmailProviderTransportPolicy,
    GmailTransportErrorCode,
    GmailTransportOperation,
)

NOW = datetime(2026, 7, 14, 15, tzinfo=timezone.utc)


@dataclass
class Credential:
    expires_at: datetime | None = NOW + timedelta(hours=1)
    scopes: tuple[str, ...] = ("gmail.readonly", "gmail.send")
    revoked: bool = False

    def refresh(self) -> None:
        self.expires_at = NOW + timedelta(hours=1)

    def revoke(self) -> None:
        self.revoked = True


class Provider:
    def __init__(self, item: Credential | None) -> None:
        self.item = item

    def load(self, account_fingerprint: str) -> Credential | None:
        return self.item


class Backend:
    def __init__(self, result: Any = None, error: Exception | None = None) -> None:
        self.result = {"ok": True} if result is None else result
        self.error = error
        self.calls: list[tuple[object, object, float]] = []

    def execute(self, operation, payload, *, timeout_seconds):
        self.calls.append((operation, payload, timeout_seconds))
        if self.error is not None:
            raise self.error
        return self.result


def transport(
    backend: Backend | None = None,
    credential: Credential | None = None,
    policy: GmailProviderTransportPolicy | None = None,
) -> GmailProviderTransport:
    oauth = GmailOAuthGovernance(
        account_fingerprint="account-fingerprint",
        credential_provider=Provider(credential or Credential()),
        policy=GmailOAuthPolicy(required_scopes=("gmail.readonly",)),
    )
    return GmailProviderTransport(backend or Backend(), oauth, policy)


def test_executes_canonical_operation_with_policy_timeout():
    backend = Backend({"messages": []})
    boundary = transport(
        backend,
        policy=GmailProviderTransportPolicy(timeout_seconds=7.5),
    )
    result = boundary.execute("list_recent", {"limit": 10}, now=NOW)
    assert result.operation is GmailTransportOperation.LIST_RECENT
    assert result.payload == {"messages": []}
    assert backend.calls[0][2] == 7.5


def test_result_status_does_not_publish_payload_values():
    result = transport(Backend({"token": "secret", "messages": ["private"]})).execute(
        "list_recent", now=NOW
    )
    status = result.status()
    assert status["payload_field_count"] == 2
    assert "secret" not in repr(status)
    assert "private" not in repr(status)


def test_search_requires_query_before_backend_call():
    backend = Backend()
    with pytest.raises(ValueError, match="query"):
        transport(backend).execute("search", {}, now=NOW)
    assert backend.calls == []


def test_local_result_limit_is_enforced():
    policy = GmailProviderTransportPolicy(max_result_items=5)
    with pytest.raises(ValueError, match="exceeds local policy"):
        transport(policy=policy).execute("list_recent", {"limit": 6}, now=NOW)


def test_absent_credentials_fail_before_backend_call():
    backend = Backend()
    oauth = GmailOAuthGovernance(
        account_fingerprint="account-fingerprint",
        credential_provider=Provider(None),
        policy=GmailOAuthPolicy(required_scopes=()),
    )
    boundary = GmailProviderTransport(backend, oauth)
    with pytest.raises(GmailProviderTransportError) as captured:
        boundary.execute("read", {"message_id": "m1"}, now=NOW)
    assert captured.value.code is GmailTransportErrorCode.AUTHENTICATION
    assert backend.calls == []


@pytest.mark.parametrize(
    ("error", "code", "retryable"),
    [
        (TimeoutError("secret timeout detail"), GmailTransportErrorCode.TIMEOUT, True),
        (
            GmailProviderRateLimitError("secret quota detail"),
            GmailTransportErrorCode.RATE_LIMITED,
            True,
        ),
        (ConnectionError("secret host"), GmailTransportErrorCode.UNAVAILABLE, True),
        (
            GmailProviderRejectedError("secret rejection"),
            GmailTransportErrorCode.REJECTED,
            False,
        ),
    ],
)
def test_provider_failures_are_normalized_without_backend_text(error, code, retryable):
    with pytest.raises(GmailProviderTransportError) as captured:
        transport(Backend(error=error)).execute("list_recent", now=NOW)
    assert captured.value.code is code
    assert captured.value.retryable is retryable
    assert "secret" not in str(captured.value)


def test_non_mapping_response_is_rejected():
    with pytest.raises(GmailProviderTransportError) as captured:
        transport(Backend(result=["unexpected"])).execute("list_recent", now=NOW)
    assert captured.value.code is GmailTransportErrorCode.INVALID_RESPONSE


def test_status_is_secret_free_and_tracks_counts():
    boundary = transport()
    boundary.execute("read", {"message_id": "private-id"}, now=NOW)
    status = boundary.status()
    assert status["request_count"] == 1
    assert status["failure_count"] == 0
    assert status["last_operation"] == "read"
    assert "private-id" not in repr(status)
    assert "gmail.readonly" not in repr(status)


def test_operation_and_payload_are_immutable_at_backend_boundary():
    backend = Backend()
    boundary = transport(backend)
    boundary.execute(
        GmailTransportOperation.CREATE_DRAFT,
        {"to": ("a@example.com",), "subject": "S", "body": "B"},
        now=NOW,
    )
    sent_payload = backend.calls[0][1]
    with pytest.raises(TypeError):
        sent_payload["subject"] = "changed"
