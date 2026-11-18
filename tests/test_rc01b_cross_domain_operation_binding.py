"""Tests for non-authorizing operation-to-turn matching."""

from dataclasses import dataclass

import pytest

from app.cross_domain_context_resolver import ContextDomain
from app.cross_domain_operation_binding import matches_operation_to_turn
from app.cross_domain_operation_evidence import CrossDomainOperationEvidence


@dataclass(frozen=True)
class Turn:
    owner: str = "owner"
    session_id: str = "session"
    turn_id: str = "turn-1"
    sequence: int = 1


def evidence(**changes):
    values = {
        "owner": "owner",
        "session_id": "session",
        "domain": ContextDomain.LIBRARY,
        "operation": "local_document_retrieval",
        "execution_id": "execution-1",
        "outcome": "completed",
    }
    values.update(changes)
    return CrossDomainOperationEvidence(**values)


def test_matching_turn_is_structurally_recognized():
    turn = Turn()
    assert matches_operation_to_turn(evidence(), turn, (turn,))


def test_missing_turn_is_rejected():
    assert not matches_operation_to_turn(evidence(), Turn(), ())


@pytest.mark.parametrize(
    "candidate",
    (
        Turn(owner="other"),
        Turn(session_id="other"),
        Turn(turn_id="other"),
        Turn(sequence=2),
    ),
)
def test_mismatched_history_candidate_is_rejected(candidate):
    assert not matches_operation_to_turn(
        evidence(), Turn(), (candidate,)
    )


def test_evidence_owner_mismatch_is_rejected():
    turn = Turn()
    assert not matches_operation_to_turn(
        evidence(owner="other"), turn, (turn,)
    )


def test_evidence_session_mismatch_is_rejected():
    turn = Turn()
    assert not matches_operation_to_turn(
        evidence(session_id="other"), turn, (turn,)
    )


@pytest.mark.parametrize(
    "turn",
    (
        Turn(owner=""),
        Turn(session_id=""),
        Turn(turn_id=""),
        Turn(sequence=0),
        Turn(sequence=True),
    ),
)
def test_invalid_turn_is_rejected(turn):
    assert not matches_operation_to_turn(evidence(), turn, (turn,))


def test_noniterable_history_is_rejected():
    assert not matches_operation_to_turn(evidence(), Turn(), None)


def test_invalid_evidence_is_rejected():
    turn = Turn()
    assert not matches_operation_to_turn(object(), turn, (turn,))


def test_binding_does_not_produce_authorization():
    turn = Turn()
    result = matches_operation_to_turn(evidence(), turn, (turn,))
    assert result is True
    assert type(result) is bool