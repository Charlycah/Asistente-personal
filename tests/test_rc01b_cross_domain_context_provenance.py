from dataclasses import dataclass

import pytest

from app.cross_domain_context_provenance import (
    ContextProvenanceRecord,
    CrossDomainContextProvenance,
)
from app.cross_domain_context_resolver import ContextDomain


@dataclass(frozen=True)
class Turn:
    turn_id: str
    owner: str
    session_id: str
    sequence: int


def record(
    turn_id="t1",
    owner="owner",
    session_id="session",
    domain=ContextDomain.MUSIC,
    sequence=1,
    provenance="governed_music",
):
    return ContextProvenanceRecord(
        turn_id, owner, session_id, domain, sequence, provenance
    )


def test_explicit_registered_turn_is_available():
    registry = CrossDomainContextProvenance()
    registry.register(record())
    result = registry.authorized_antecedents(
        (Turn("t1", "owner", "session", 1),),
        owner="owner",
        session_id="session",
    )
    assert len(result) == 1
    assert result[0].domain is ContextDomain.MUSIC
    assert result[0].authorized is True


def test_unregistered_turn_is_not_inferred():
    registry = CrossDomainContextProvenance()
    assert registry.authorized_antecedents(
        (Turn("t1", "owner", "session", 1),),
        owner="owner",
        session_id="session",
    ) == ()


def test_owner_session_and_sequence_must_match():
    registry = CrossDomainContextProvenance()
    registry.register(record())
    for turn in (
        Turn("t1", "other", "session", 1),
        Turn("t1", "owner", "other", 1),
        Turn("t1", "owner", "session", 2),
    ):
        assert registry.authorized_antecedents(
            (turn,), owner="owner", session_id="session"
        ) == ()


def test_conflicting_registration_is_rejected():
    registry = CrossDomainContextProvenance()
    registry.register(record())
    with pytest.raises(ValueError):
        registry.register(record(domain=ContextDomain.DOCUMENTS))


def test_duplicate_registration_is_idempotent():
    registry = CrossDomainContextProvenance()
    registry.register(record())
    registry.register(record())
    assert len(
        registry.authorized_antecedents(
            (Turn("t1", "owner", "session", 1),),
            owner="owner",
            session_id="session",
        )
    ) == 1


def test_invalid_provenance_is_rejected():
    with pytest.raises(ValueError):
        record(provenance="  ")


def test_invalid_sequence_is_rejected():
    with pytest.raises(ValueError):
        record(sequence=True)


def test_duplicate_authorized_turns_are_not_repeated():
    registry = CrossDomainContextProvenance()
    registry.register(record())
    turn = Turn("t1", "owner", "session", 1)
    result = registry.authorized_antecedents(
        (turn, turn), owner="owner", session_id="session"
    )
    assert len(result) == 1
