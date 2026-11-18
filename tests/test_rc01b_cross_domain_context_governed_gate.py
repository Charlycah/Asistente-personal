from types import SimpleNamespace

import pytest

from app.cross_domain_context_provenance import CrossDomainContextProvenance
from app.cross_domain_context_resolver import ContextDecision
from app.cross_domain_context_runtime_boundary import (
    resolve_runtime_cross_domain_context,
)
from core.cognitive_maturity import IdentityContextAccessGate


class CountingRuntime:
    def __init__(self):
        self.bootstrap = SimpleNamespace(
            config=SimpleNamespace(owner="owner", session_id="session")
        )
        self.calls = 0

    def authorized_recent_turns(self):
        self.calls += 1
        return ()


@pytest.mark.parametrize(
    ("governed", "scoped", "shared"),
    [
        (False, True, True),
        (True, False, True),
        (True, True, False),
        (False, False, True),
    ],
)
def test_insufficient_gate_denies_before_history(
    monkeypatch, governed, scoped, shared
):
    state = SimpleNamespace(
        governed_entry=governed,
        session_scoped=scoped,
        shared_conversation_context_allowed=shared,
    )
    monkeypatch.setattr(
        IdentityContextAccessGate,
        "current",
        staticmethod(lambda: state),
    )
    runtime = CountingRuntime()
    result = resolve_runtime_cross_domain_context(
        "seguimos con aquella",
        runtime=runtime,
        session_id="session",
        provenance=CrossDomainContextProvenance(),
    )
    assert result.decision is ContextDecision.UNRESOLVED
    assert runtime.calls == 0


def test_missing_governed_fields_fail_closed(monkeypatch):
    monkeypatch.setattr(
        IdentityContextAccessGate,
        "current",
        staticmethod(
            lambda: SimpleNamespace(
                shared_conversation_context_allowed=True
            )
        ),
    )
    runtime = CountingRuntime()
    result = resolve_runtime_cross_domain_context(
        "seguimos con aquella",
        runtime=runtime,
        session_id="session",
        provenance=CrossDomainContextProvenance(),
    )
    assert result.decision is ContextDecision.UNRESOLVED
    assert runtime.calls == 0


def test_actual_unmanaged_compatibility_fails_closed(monkeypatch):
    from core.cognitive_maturity.identity_context_access import (
        _UNMANAGED_COMPATIBILITY,
    )

    monkeypatch.setattr(
        IdentityContextAccessGate,
        "current",
        staticmethod(lambda: _UNMANAGED_COMPATIBILITY),
    )
    runtime = CountingRuntime()
    result = resolve_runtime_cross_domain_context(
        "seguimos con aquella",
        runtime=runtime,
        session_id="session",
        provenance=CrossDomainContextProvenance(),
    )
    assert result.decision is ContextDecision.UNRESOLVED
    assert runtime.calls == 0
