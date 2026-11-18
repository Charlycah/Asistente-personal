"""Adversarial tests for isolated invocation capture."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.cross_domain_invocation_capture import (
    CrossDomainInvocationCapture,
    InvocationCaptureSnapshot,
    InvocationCaptureState,
    InvocationExecutionStatus,
)


def started(capture, owner="owner", session="session"):
    invocation_id = capture.begin(owner=owner, session_id=session)
    return invocation_id


def observe(
    capture,
    invocation_id,
    *,
    owner="owner",
    session="session",
    execution="execution-1",
    status=InvocationExecutionStatus.SUCCEEDED,
):
    return capture.observe(
        invocation_id,
        owner=owner,
        session_id=session,
        execution_id=execution,
        status=status,
    )


def test_begin_creates_started_snapshot():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    result = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    assert result.state is InvocationCaptureState.STARTED
    assert result.execution_id is None
    assert result.execution_status is None


def test_observe_success_once():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert observe(capture, invocation_id)
    assert not observe(capture, invocation_id, execution="execution-2")
    result = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    assert result.state is InvocationCaptureState.OBSERVED
    assert result.execution_status is InvocationExecutionStatus.SUCCEEDED


@pytest.mark.parametrize("status", tuple(InvocationExecutionStatus))
def test_all_terminal_statuses_are_preserved(status):
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert observe(capture, invocation_id, status=status)
    result = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    assert result.execution_status is status


@pytest.mark.parametrize(
    "wrong",
    (
        {"owner": "other"},
        {"session": "other"},
        {"owner": "other", "session": "other"},
    ),
)
def test_wrong_identity_does_not_consume_invocation(wrong):
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert not observe(capture, invocation_id, **wrong)
    assert observe(capture, invocation_id)


def test_unknown_invocation_is_rejected():
    capture = CrossDomainInvocationCapture()
    assert not observe(capture, "unknown")


def test_execution_id_cannot_be_reused():
    capture = CrossDomainInvocationCapture()
    first = started(capture)
    second = started(capture)
    assert observe(capture, first)
    assert not observe(capture, second)
    assert observe(capture, second, execution="execution-2")


def test_failed_execution_id_cannot_be_reused():
    capture = CrossDomainInvocationCapture()
    first = started(capture)
    second = started(capture)
    assert observe(
        capture,
        first,
        status=InvocationExecutionStatus.FAILED,
    )
    assert not observe(capture, second)


def test_close_before_observation():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert capture.close(
        invocation_id, owner="owner", session_id="session"
    )
    assert not observe(capture, invocation_id)


def test_close_after_observation_preserves_data():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert observe(capture, invocation_id)
    assert capture.close(
        invocation_id, owner="owner", session_id="session"
    )
    result = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    assert result.state is InvocationCaptureState.CLOSED
    assert result.execution_id == "execution-1"


def test_close_is_not_repeatable():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert capture.close(
        invocation_id, owner="owner", session_id="session"
    )
    assert not capture.close(
        invocation_id, owner="owner", session_id="session"
    )


@pytest.mark.parametrize(
    "invalid",
    (None, "", " ", " owner", "owner ", 123, True),
)
def test_begin_rejects_invalid_identity(invalid):
    capture = CrossDomainInvocationCapture()
    with pytest.raises(ValueError):
        capture.begin(owner=invalid, session_id="session")


@pytest.mark.parametrize(
    "invalid",
    (None, "", " ", " execution", "execution ", 123, True),
)
def test_observe_rejects_invalid_execution_id(invalid):
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert not observe(capture, invocation_id, execution=invalid)
    assert observe(capture, invocation_id)


def test_snapshot_wrong_identity_is_hidden():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    assert capture.snapshot(
        invocation_id, owner="other", session_id="session"
    ) is None


def test_snapshot_is_immutable():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)
    result = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    with pytest.raises(AttributeError):
        result.state = InvocationCaptureState.CLOSED


def test_snapshot_rejects_inconsistent_state():
    with pytest.raises(ValueError):
        InvocationCaptureSnapshot(
            invocation_id="inv",
            owner="owner",
            session_id="session",
            state=InvocationCaptureState.OBSERVED,
        )


def test_cross_session_interleaving_is_isolated():
    capture = CrossDomainInvocationCapture()
    first = started(capture, "owner-a", "session-a")
    second = started(capture, "owner-b", "session-b")

    assert observe(
        capture,
        second,
        owner="owner-b",
        session="session-b",
        execution="execution-b",
    )
    assert observe(
        capture,
        first,
        owner="owner-a",
        session="session-a",
        execution="execution-a",
    )

    assert capture.snapshot(
        first, owner="owner-b", session_id="session-b"
    ) is None


def test_concurrent_observation_has_single_winner():
    capture = CrossDomainInvocationCapture()
    invocation_id = started(capture)

    def attempt(index):
        return observe(
            capture,
            invocation_id,
            execution=f"execution-{index}",
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(32)))

    assert sum(results) == 1


def test_concurrent_execution_reuse_has_single_winner():
    capture = CrossDomainInvocationCapture()
    invocations = [started(capture) for _ in range(32)]

    def attempt(invocation_id):
        return observe(capture, invocation_id)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, invocations))

    assert sum(results) == 1


def test_no_admission_or_registration_api():
    capture = CrossDomainInvocationCapture()
    assert not hasattr(capture, "admit")
    assert not hasattr(capture, "register")
    assert not hasattr(capture, "bind")
    assert not hasattr(capture, "authorize")
