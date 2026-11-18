"""Tests for non-authorizing persisted-turn verification."""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from app.cross_domain_persisted_turn import matches_persisted_turn
from core.end_to_end_local_conversation.models import (
    LocalConversationTurn,
    LocalConversationTurnStatus,
)


def turn(**changes):
    values = {
        "owner": "owner",
        "session_id": "session",
        "sequence": 1,
        "user_text": "Consultar documento",
        "response_text": "Documento encontrado",
        "status": LocalConversationTurnStatus.COMPLETED,
        "pipeline_result_id": "pipeline-1",
        "operational_response_id": "response-1",
        "provider_call_performed": False,
        "retrieval_performed": True,
        "network_access_performed": False,
        "rationale": ("local_retrieval_completed",),
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
    }
    values.update(changes)
    return LocalConversationTurn(**values)


class Journal:
    def __init__(self, records=()):
        self.records = records
        self.calls = []

    def list_for_session(self, owner, session_id):
        self.calls.append((owner, session_id))
        return self.records


def test_exactly_one_matching_record_is_recognized():
    item = turn()
    journal = Journal((item,))
    assert matches_persisted_turn(item, journal=journal)
    assert journal.calls == [("owner", "session")]


def test_missing_record_is_rejected():
    assert not matches_persisted_turn(turn(), journal=Journal())


def test_duplicate_records_are_rejected():
    item = turn()
    assert not matches_persisted_turn(
        item, journal=Journal((item, item))
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"owner": "other"},
        {"session_id": "other"},
        {"sequence": 2},
        {"response_text": "Otra respuesta"},
    ),
)
def test_different_records_are_rejected(changes):
    item = turn()
    other = turn(**changes)
    assert not matches_persisted_turn(
        item, journal=Journal((other,))
    )


def test_full_record_difference_is_rejected():
    item = turn()
    other = replace(item, provider_call_performed=True)
    assert not matches_persisted_turn(
        item, journal=Journal((other,))
    )


def test_non_tuple_result_is_rejected():
    item = turn()
    journal = Journal([item])
    assert not matches_persisted_turn(item, journal=journal)


def test_missing_reader_is_rejected():
    assert not matches_persisted_turn(turn(), journal=object())


def test_reader_exception_is_rejected():
    class BrokenJournal:
        def list_for_session(self, owner, session_id):
            raise OSError("journal unavailable")

    assert not matches_persisted_turn(
        turn(), journal=BrokenJournal()
    )


def test_invalid_turn_is_rejected():
    assert not matches_persisted_turn(
        object(), journal=Journal()
    )


def test_boolean_sequence_is_rejected():
    item = replace(turn(), sequence=True, turn_id="")
    assert not matches_persisted_turn(
        item, journal=Journal((item,))
    )


def test_result_is_not_authorization():
    item = turn()
    result = matches_persisted_turn(
        item, journal=Journal((item,))
    )
    assert result is True
    assert type(result) is bool