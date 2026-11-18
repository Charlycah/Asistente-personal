from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from app.cross_domain_context_provenance import (
    ContextProvenanceRecord,
    CrossDomainContextProvenance,
)
from app.cross_domain_context_resolver import (
    ContextDecision,
    ContextDomain,
)
from app.cross_domain_context_runtime_boundary import (
    resolve_runtime_cross_domain_context,
)
from core.cognitive_maturity import IdentityContextAccessGate


@dataclass(frozen=True)
class Turn:
    turn_id: str
    owner: str
    session_id: str
    sequence: int


class FakeRuntime:
    def __init__(self):
        self.bootstrap = SimpleNamespace(
            config=SimpleNamespace(
                owner="owner",
                session_id="session",
            )
        )
        self.calls = 0

    def authorized_recent_turns(self):
        self.calls += 1
        return (Turn("music-1", "owner", "session", 1),)


def registry():
    result = CrossDomainContextProvenance()
    result.register(
        ContextProvenanceRecord(
            turn_id="music-1",
            owner="owner",
            session_id="session",
            domain=ContextDomain.MUSIC,
            sequence=1,
            provenance="governed_music",
        )
    )
    return result


@pytest.fixture
def gate(monkeypatch):
    state = SimpleNamespace(
        governed_entry=True,
        session_scoped=True,
        shared_conversation_context_allowed=True,
    )
    monkeypatch.setattr(
        IdentityContextAccessGate,
        "current",
        classmethod(lambda cls: state),
    )
    return state


def resolve(runtime=None, session="session", provenance=None):
    if runtime is None:
        runtime = FakeRuntime()
    if provenance is None:
        provenance = registry()
    return resolve_runtime_cross_domain_context(
        "seguimos con aquella",
        runtime=runtime,
        session_id=session,
        provenance=provenance,
    )


def test_authorized_runtime_resolves_context(gate):
    result = resolve()
    assert result.decision is ContextDecision.CONTINUE
    assert result.domain is ContextDomain.MUSIC
    assert result.antecedent_turn_id == "music-1"


def test_disabled_gate_denies_without_reading(gate):
    gate.shared_conversation_context_allowed = False
    runtime = FakeRuntime()
    assert resolve(runtime).decision is ContextDecision.UNRESOLVED
    assert runtime.calls == 0


def test_session_mismatch_denies_without_reading(gate):
    runtime = FakeRuntime()
    assert resolve(runtime, session="other").decision is ContextDecision.UNRESOLVED
    assert runtime.calls == 0


def test_missing_reader_fails_closed(gate):
    runtime = FakeRuntime()
    runtime.authorized_recent_turns = None
    assert resolve(runtime).decision is ContextDecision.UNRESOLVED


def test_external_reader_is_rejected(gate):
    runtime = FakeRuntime()

    def external_reader():
        return (Turn("music-1", "owner", "session", 1),)

    runtime.authorized_recent_turns = external_reader
    assert resolve(runtime).decision is ContextDecision.UNRESOLVED


def test_other_object_bound_reader_is_rejected(gate):
    runtime = FakeRuntime()
    other = FakeRuntime()
    runtime.authorized_recent_turns = other.authorized_recent_turns
    assert resolve(runtime).decision is ContextDecision.UNRESOLVED


def test_unregistered_provenance_fails_closed(gate):
    assert resolve(
        provenance=CrossDomainContextProvenance()
    ).decision is ContextDecision.UNRESOLVED


def test_invalid_runtime_fails_closed(gate):
    assert resolve(runtime=object()).decision is ContextDecision.UNRESOLVED


def test_invalid_session_fails_closed(gate):
    assert resolve(session="").decision is ContextDecision.UNRESOLVED
