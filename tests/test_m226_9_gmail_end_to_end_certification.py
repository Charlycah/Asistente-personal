from __future__ import annotations

from datetime import datetime, timezone

import pytest

from infrastructure.mail.gmail_e2e_certification import build_gmail_e2e_certification

NOW = datetime(2026, 7, 14, 18, tzinfo=timezone.utc)
DRAFT = {"to": ("ana@example.com",), "subject": "Hola", "body": "Texto"}


def harness():
    return build_gmail_e2e_certification(now=NOW)


def test_certification_runtime_is_ready_and_registered():
    status = harness().status(now=NOW)
    assert status["runtime_state"] == "ready"
    assert status["registered"] is True


def test_recent_crosses_gateway_runtime_and_transport():
    report = harness().certify("recent", {"limit": 5}, now=NOW)
    assert report.gateway_status == "routed"
    assert report.transport_operation == "list_recent"


def test_search_is_certified_end_to_end():
    report = harness().certify("search", {"query": "project"}, now=NOW)
    assert report.action == "search"
    assert report.attempts == 1


def test_read_is_certified_end_to_end():
    report = harness().certify("read", {"message_id": "m-1"}, now=NOW)
    assert report.transport_operation == "read"


def test_compose_maps_to_provider_draft():
    report = harness().certify("compose", DRAFT, now=NOW)
    assert report.transport_operation == "create_draft"


def test_draft_is_certified_end_to_end():
    report = harness().certify("draft", DRAFT, now=NOW)
    assert report.gateway_status == "routed"


def test_reply_is_certified_as_governed_draft():
    payload = dict(DRAFT, message_id="m-1")
    report = harness().certify("reply", payload, now=NOW)
    assert report.action == "reply"
    assert report.transport_operation == "create_draft"


def test_send_requires_idempotency_before_transport():
    item = harness()
    with pytest.raises(ValueError, match="idempotency"):
        item.certify("send", DRAFT, now=NOW)
    assert item.backend.calls == []


def test_send_is_certified_with_idempotency():
    report = harness().certify("send", DRAFT, now=NOW, idempotency_key="send-1")
    assert report.transport_operation == "send"
    assert report.gateway_status == "routed"


def test_retryable_provider_failure_is_recovered():
    item = harness()
    item.backend.failures_remaining = 1
    report = item.certify("read", {"message_id": "m-1"}, now=NOW)
    assert report.attempts == 2


def test_report_and_status_are_secret_free():
    item = harness()
    report = item.certify("send", DRAFT, now=NOW, idempotency_key="private-key")
    rendered = repr((report.to_dict(), item.status(now=NOW)))
    assert "private-key" not in rendered
    assert "ana@example.com" not in rendered
    assert "Texto" not in rendered


def test_invalid_payload_stops_before_gateway_and_transport():
    item = harness()
    with pytest.raises(ValueError, match="required fields"):
        item.certify("search", {}, now=NOW)
    assert item.backend.calls == []
    assert item.integration.audit_log == ()
