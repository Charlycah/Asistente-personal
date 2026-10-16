from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.runtime_root_factory import (
    build_gmail_runtime_from_environment,
    build_runtime_root,
)
from infrastructure.mail.gmail_runtime_composition import (
    GmailRuntimeComposition,
    GmailRuntimeConfig,
    GmailRuntimeState,
)

NOW = datetime(2026, 7, 14, 16, tzinfo=timezone.utc)


class OAuth:
    class Snapshot:
        def __init__(self, state):
            self.state = state

    class State:
        def __init__(self, value):
            self.value = value

    def __init__(self, state="ready"):
        self.state = state

    def inspect(self, *, now=None):
        return self.Snapshot(self.State(self.state))


class Retry:
    def __init__(self):
        self.calls = []

    def execute(self, operation, payload=None, *, now=None, idempotency_key=None):
        self.calls.append((operation, payload, now, idempotency_key))
        return "result"


def complete_runtime(*, enabled=True, oauth_state="ready"):
    return GmailRuntimeComposition(
        config=GmailRuntimeConfig(enabled=enabled),
        integration=object(),
        oauth=OAuth(oauth_state),
        retry=Retry(),
    )


def test_disabled_runtime_is_observable_without_configuration():
    runtime = GmailRuntimeComposition()
    assert runtime.status() == {
        "state": "disabled",
        "enabled": False,
        "configured": False,
        "reason": None,
    }


def test_enabled_runtime_degrades_when_graph_is_missing():
    runtime = GmailRuntimeComposition(config=GmailRuntimeConfig(enabled=True))
    assert runtime.snapshot().state is GmailRuntimeState.DEGRADED
    assert runtime.status()["reason"] == "configuration_missing"


def test_partial_graph_is_rejected():
    with pytest.raises(ValueError, match="complete graph"):
        GmailRuntimeComposition(integration=object())


def test_complete_ready_graph_reports_ready():
    assert complete_runtime().snapshot(now=NOW).state is GmailRuntimeState.READY


def test_oauth_not_ready_degrades_without_secret_material():
    status = complete_runtime(oauth_state="expired").status(now=NOW)
    assert status["reason"] == "oauth_expired"
    assert "token" not in repr(status).casefold()


def test_execute_delegates_to_retry_boundary():
    runtime = complete_runtime()
    assert runtime.execute("read", {"message_id": "m1"}, now=NOW) == "result"
    assert runtime.retry.calls[0][0] == "read"


def test_execute_forwards_send_idempotency_key():
    runtime = complete_runtime()
    runtime.execute("send", {"body": "x"}, now=NOW, idempotency_key="key-1")
    assert runtime.retry.calls[0][3] == "key-1"


def test_disabled_runtime_rejects_execution_before_retry():
    runtime = complete_runtime(enabled=False)
    with pytest.raises(RuntimeError, match="disabled"):
        runtime.execute("read", now=NOW)
    assert runtime.retry.calls == []


def test_environment_factory_is_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ROBY_GMAIL_ENABLED", raising=False)
    assert build_gmail_runtime_from_environment().status()["state"] == "disabled"


def test_environment_factory_enables_degraded_shell(monkeypatch):
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "true")
    status = build_gmail_runtime_from_environment().status()
    assert status["state"] == "degraded"
    assert status["reason"] == "configuration_missing"


def test_official_root_omits_disabled_gmail_runtime(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    monkeypatch.delenv("ROBY_GMAIL_ENABLED", raising=False)
    root = build_runtime_root()
    assert root.compose().gmail_runtime is None


def test_official_root_exposes_enabled_degraded_runtime(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    monkeypatch.setenv("ROBY_GMAIL_ENABLED", "1")
    root = build_runtime_root()
    runtime = root.compose().gmail_runtime
    assert runtime is root.dependencies.gmail_runtime
    assert runtime.status()["state"] == "degraded"
