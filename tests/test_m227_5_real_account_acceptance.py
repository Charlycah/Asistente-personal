from __future__ import annotations

from dataclasses import dataclass

import pytest

from infrastructure.mail.gmail_real_account_acceptance import (
    GmailAcceptanceConfig,
    GmailAcceptanceState,
    GmailRealAccountAcceptance,
)


@dataclass
class Result:
    payload: dict[str, object]


class Runtime:
    def __init__(self, state="ready"):
        self.state = state
        self.calls = []

    def status(self, *, now=None):
        del now
        return {"state": self.state, "token": "must-not-leak"}

    def execute(self, operation, payload=None, *, now=None, idempotency_key=None):
        del now
        self.calls.append((operation.value, dict(payload or {}), idempotency_key))
        if operation.value in {"list_recent", "search"}:
            return Result({"messages": ({"id": "m1"},)})
        return Result({"id": "m1"})


def test_acceptance_is_disabled_by_default():
    acceptance = GmailRealAccountAcceptance(Runtime())
    assert acceptance.preflight().state is GmailAcceptanceState.DISABLED


def test_config_reads_explicit_environment_values():
    config = GmailAcceptanceConfig.from_env(
        {
            "ROBY_GMAIL_ACCEPTANCE_ENABLED": "true",
            "ROBY_GMAIL_ACCEPTANCE_ALLOW_WRITE": "yes",
            "ROBY_GMAIL_ACCEPTANCE_SEARCH_QUERY": "label:inbox newer_than:1d",
            "ROBY_GMAIL_ACCEPTANCE_RECIPIENT": "sandbox@example.invalid",
            "ROBY_GMAIL_ACCEPTANCE_MAX_RESULTS": "5",
        }
    )
    assert config.enabled and config.allow_write and config.max_results == 5


def test_invalid_result_limit_is_rejected():
    with pytest.raises(ValueError, match="must be positive"):
        GmailAcceptanceConfig.from_env({"ROBY_GMAIL_ACCEPTANCE_MAX_RESULTS": "0"})


def test_runtime_must_be_ready():
    acceptance = GmailRealAccountAcceptance(
        Runtime("degraded"), GmailAcceptanceConfig(enabled=True)
    )
    assert acceptance.preflight().reason == "runtime_not_ready"


def test_write_acceptance_requires_recipient():
    acceptance = GmailRealAccountAcceptance(
        Runtime(), GmailAcceptanceConfig(enabled=True, allow_write=True)
    )
    assert acceptance.preflight().reason == "recipient_missing"


def test_read_only_acceptance_runs_list_search_and_read():
    runtime = Runtime()
    report = GmailRealAccountAcceptance(
        runtime, GmailAcceptanceConfig(enabled=True)
    ).run()
    assert report.passed
    assert [call[0] for call in runtime.calls] == ["list_recent", "search", "read"]


def test_empty_mailbox_is_a_valid_read_acceptance_result():
    runtime = Runtime()

    def execute(operation, payload=None, *, now=None, idempotency_key=None):
        del payload, now, idempotency_key
        runtime.calls.append((operation.value, {}, None))
        return Result({"messages": ()})

    runtime.execute = execute
    report = GmailRealAccountAcceptance(
        runtime, GmailAcceptanceConfig(enabled=True)
    ).run()
    assert report.passed
    assert report.checks[-1].operation == "read_skipped_empty"


def test_write_acceptance_creates_draft_and_sends_with_idempotency():
    runtime = Runtime()
    config = GmailAcceptanceConfig(
        enabled=True,
        allow_write=True,
        recipient="sandbox@example.invalid",
    )
    report = GmailRealAccountAcceptance(runtime, config).run()
    assert report.write_exercised
    assert runtime.calls[-1][0] == "send"
    assert runtime.calls[-1][2] == "m227.5-acceptance-send"


def test_blocked_run_does_not_touch_runtime_execute():
    runtime = Runtime()
    acceptance = GmailRealAccountAcceptance(runtime)
    with pytest.raises(RuntimeError, match="acceptance blocked"):
        acceptance.run()
    assert runtime.calls == []


def test_failure_counter_is_incremented_without_leaking_exception():
    runtime = Runtime()

    def fail(*args, **kwargs):
        del args, kwargs
        raise ConnectionError("provider secret text")

    runtime.execute = fail
    acceptance = GmailRealAccountAcceptance(
        runtime, GmailAcceptanceConfig(enabled=True)
    )
    with pytest.raises(ConnectionError):
        acceptance.run()
    assert acceptance.status()["failures"] == 1
    assert "provider secret" not in repr(acceptance.status())


def test_report_is_secret_free():
    runtime = Runtime()
    report = GmailRealAccountAcceptance(
        runtime,
        GmailAcceptanceConfig(
            enabled=True,
            search_query="from:private@example.com",
        ),
    ).run()
    assert "private@example.com" not in repr(report.to_dict())


def test_status_does_not_publish_recipient_or_query():
    acceptance = GmailRealAccountAcceptance(
        Runtime(),
        GmailAcceptanceConfig(
            enabled=True,
            allow_write=True,
            recipient="secret@example.com",
            search_query="subject:secret",
        ),
    )
    rendered = repr(acceptance.status())
    assert "secret@example.com" not in rendered
    assert "subject:secret" not in rendered
