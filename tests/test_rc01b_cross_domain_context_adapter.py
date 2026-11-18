from dataclasses import dataclass

import pytest

from app.cross_domain_context_adapter import (
    resolve_authorized_cross_domain_context,
)
from app.cross_domain_context_provenance import (
    ContextProvenanceRecord,
    CrossDomainContextProvenance,
)
from app.cross_domain_context_resolver import (
    ContextDecision,
    ContextDomain,
)


@dataclass(frozen=True)
class Turn:
    turn_id: str
    owner: str
    session_id: str
    sequence: int


def make_context():
    registry = CrossDomainContextProvenance()
    registry.register(
        ContextProvenanceRecord(
            turn_id="music-1",
            owner="owner",
            session_id="session",
            domain=ContextDomain.MUSIC,
            sequence=1,
            provenance="governed_music",
        )
    )
    return registry, (
        Turn("music-1", "owner", "session", 1),
    )


def resolve(
    text="seguimos con aquella",
    *,
    allowed=True,
    owner="owner",
    session="session",
    reader=None,
    registry=None,
):
    default_registry, turns = make_context()

    if registry is None:
        registry = default_registry
    if reader is None:
        def reader():
            return turns

    return resolve_authorized_cross_domain_context(
        text,
        owner=owner,
        session_id=session,
        context_allowed=allowed,
        authorized_turns_reader=reader,
        provenance=registry,
    )


def test_natural_followup_resolves_music():
    result = resolve()
    assert result.decision is ContextDecision.CONTINUE
    assert result.domain is ContextDomain.MUSIC
    assert result.antecedent_turn_id == "music-1"


def test_disabled_context_fails_closed():
    assert resolve(allowed=False).decision is ContextDecision.UNRESOLVED


def test_other_owner_cannot_reuse_context():
    assert resolve(owner="other").decision is ContextDecision.UNRESOLVED


def test_other_session_cannot_reuse_context():
    assert resolve(session="other").decision is ContextDecision.UNRESOLVED


def test_unregistered_turn_is_not_inferred():
    registry = CrossDomainContextProvenance()
    assert resolve(registry=registry).decision is ContextDecision.UNRESOLVED


def test_reader_exception_fails_closed():
    def broken_reader():
        raise RuntimeError("reader failed")

    assert resolve(reader=broken_reader).decision is ContextDecision.UNRESOLVED


def test_invalid_reader_result_fails_closed():
    assert resolve(reader=lambda: None).decision is ContextDecision.UNRESOLVED


def test_empty_history_fails_closed():
    assert resolve(reader=lambda: ()).decision is ContextDecision.UNRESOLVED


@pytest.mark.parametrize(
    "text",
    ["", "   ", None],
)
def test_invalid_text_fails_closed(text):
    assert resolve(text).decision is ContextDecision.UNRESOLVED


def test_permission_denied_does_not_call_reader():
    calls = []

    def reader():
        calls.append("called")
        return ()

    resolve(allowed=False, reader=reader)
    assert calls == []


def test_invalid_owner_does_not_call_reader():
    calls = []

    def reader():
        calls.append("called")
        return ()

    resolve(owner="", reader=reader)
    assert calls == []


def test_invalid_session_does_not_call_reader():
    calls = []

    def reader():
        calls.append("called")
        return ()

    resolve(session="", reader=reader)
    assert calls == []
