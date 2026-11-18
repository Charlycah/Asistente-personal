"""Tests for non-authorizing invocation correlation."""

from datetime import datetime, timezone

from app.cross_domain_invocation_correlation import (
    CrossDomainInvocationCorrelator,
    InvocationCorrelation,
)
from core.end_to_end_local_conversation.models import (
    LocalConversationTurn,
    LocalConversationTurnStatus,
)


def make_turn(**changes):
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
    def __init__(self, *turns):
        self.turns = tuple(turns)

    def list_for_session(self, owner, session_id):
        return tuple(
            turn
            for turn in self.turns
            if turn.owner == owner and turn.session_id == session_id
        )


def prepared(*, owner="owner", session_id="session", execution_id="execution-1"):
    correlator = CrossDomainInvocationCorrelator()
    invocation_id = correlator.begin(owner=owner, session_id=session_id)
    assert correlator.capture(
        invocation_id,
        owner=owner,
        session_id=session_id,
        execution_id=execution_id,
        succeeded=True,
    )
    return correlator, invocation_id


def test_valid_persisted_turn_correlates():
    turn = make_turn()
    correlator, invocation_id = prepared()
    result = correlator.bind(invocation_id, turn=turn, journal=Journal(turn))
    assert isinstance(result, InvocationCorrelation)
    assert result.execution_id == "execution-1"
    assert result.turn_id == turn.turn_id


def test_missing_persistence_is_rejected():
    correlator, invocation_id = prepared()
    assert correlator.bind(
        invocation_id, turn=make_turn(), journal=Journal()
    ) is None


def test_owner_mismatch_is_rejected():
    correlator, invocation_id = prepared()
    turn = make_turn(owner="other")
    assert correlator.bind(invocation_id, turn=turn, journal=Journal(turn)) is None


def test_session_mismatch_is_rejected():
    correlator, invocation_id = prepared()
    turn = make_turn(session_id="other")
    assert correlator.bind(invocation_id, turn=turn, journal=Journal(turn)) is None


def test_failed_execution_cannot_be_captured():
    correlator = CrossDomainInvocationCorrelator()
    invocation_id = correlator.begin(owner="owner", session_id="session")
    assert not correlator.capture(
        invocation_id,
        owner="owner",
        session_id="session",
        execution_id="execution-1",
        succeeded=False,
    )
    turn = make_turn()
    assert correlator.bind(invocation_id, turn=turn, journal=Journal(turn)) is None


def test_capture_cannot_cross_sessions():
    correlator = CrossDomainInvocationCorrelator()
    invocation_id = correlator.begin(owner="owner", session_id="session")
    assert not correlator.capture(
        invocation_id,
        owner="owner",
        session_id="other",
        execution_id="execution-1",
        succeeded=True,
    )


def test_execution_cannot_be_reused():
    correlator = CrossDomainInvocationCorrelator()
    first = correlator.begin(owner="owner", session_id="session")
    second = correlator.begin(owner="owner", session_id="session")
    assert correlator.capture(
        first,
        owner="owner",
        session_id="session",
        execution_id="execution-1",
        succeeded=True,
    )
    assert not correlator.capture(
        second,
        owner="owner",
        session_id="session",
        execution_id="execution-1",
        succeeded=True,
    )


def test_turn_cannot_be_reused():
    correlator = CrossDomainInvocationCorrelator()
    first = correlator.begin(owner="owner", session_id="session")
    second = correlator.begin(owner="owner", session_id="session")
    for invocation_id, execution_id in (
        (first, "execution-1"),
        (second, "execution-2"),
    ):
        assert correlator.capture(
            invocation_id,
            owner="owner",
            session_id="session",
            execution_id=execution_id,
            succeeded=True,
        )
    turn = make_turn()
    assert correlator.bind(first, turn=turn, journal=Journal(turn)) is not None
    assert correlator.bind(second, turn=turn, journal=Journal(turn)) is None


def test_failed_bind_consumes_invocation():
    correlator, invocation_id = prepared()
    turn = make_turn()
    assert correlator.bind(invocation_id, turn=turn, journal=Journal()) is None
    assert correlator.bind(invocation_id, turn=turn, journal=Journal(turn)) is None


def test_closed_invocation_rejects_capture_and_bind():
    correlator = CrossDomainInvocationCorrelator()
    invocation_id = correlator.begin(owner="owner", session_id="session")
    assert correlator.close(invocation_id)
    assert not correlator.capture(
        invocation_id,
        owner="owner",
        session_id="session",
        execution_id="execution-1",
        succeeded=True,
    )
    turn = make_turn()
    assert correlator.bind(invocation_id, turn=turn, journal=Journal(turn)) is None


def test_duplicate_capture_is_rejected():
    correlator, invocation_id = prepared()
    assert not correlator.capture(
        invocation_id,
        owner="owner",
        session_id="session",
        execution_id="execution-2",
        succeeded=True,
    )


def test_invalid_identity_is_rejected():
    correlator = CrossDomainInvocationCorrelator()
    for owner, session_id in (
        ("", "session"),
        ("owner", " "),
        (" owner ", "session"),
    ):
        try:
            correlator.begin(owner=owner, session_id=session_id)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid identity was accepted")


def test_duplicate_journal_record_is_rejected():
    correlator, invocation_id = prepared()
    turn = make_turn()
    assert correlator.bind(
        invocation_id, turn=turn, journal=Journal(turn, turn)
    ) is None


def test_structural_correlation_does_not_grant_authority():
    turn = make_turn()
    correlator, invocation_id = prepared()
    result = correlator.bind(invocation_id, turn=turn, journal=Journal(turn))
    assert result is not None
    assert not hasattr(result, "authorized")
    assert not hasattr(result, "provenance")
