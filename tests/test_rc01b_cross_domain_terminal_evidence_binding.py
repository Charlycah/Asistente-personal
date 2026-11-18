"""Adversarial tests for non-authorizing terminal evidence binding."""

from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
)
from app.cross_domain_invocation_capture import (
    CrossDomainInvocationCapture,
    InvocationCaptureState,
    InvocationExecutionStatus,
)
from app.cross_domain_terminal_evidence_binding import (
    CrossDomainTerminalEvidenceBinding,
    TerminalBindingDecision,
    TerminalBindingReason,
    bind_terminal_evidence,
)


def scenario(
    *,
    capture_status=InvocationExecutionStatus.SUCCEEDED,
    evidence_status=GovernedTerminalStatus.SUCCEEDED,
    execution_id="a" * 64,
    evidence_execution_id=None,
    item_count=1,
    close=False,
):
    capture = CrossDomainInvocationCapture()
    invocation_id = capture.begin(owner="owner", session_id="session")
    assert capture.observe(
        invocation_id,
        owner="owner",
        session_id="session",
        execution_id=execution_id,
        status=capture_status,
    )
    if close:
        assert capture.close(
            invocation_id,
            owner="owner",
            session_id="session",
        )
    snapshot = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    evidence = GovernedTerminalExecutionEvidence(
        source_id="governed-source",
        status=evidence_status,
        execution_id=(
            execution_id
            if evidence_execution_id is None
            else evidence_execution_id
        ),
        item_count=item_count,
        response_present=True,
    )
    return snapshot, evidence


def bind(snapshot, evidence, owner="owner", session="session"):
    return bind_terminal_evidence(
        snapshot=snapshot,
        evidence=evidence,
        owner=owner,
        session_id=session,
    )


def test_successful_structural_match():
    snapshot, evidence = scenario()
    result = bind(snapshot, evidence)
    assert result.decision is TerminalBindingDecision.MATCHED
    assert result.reason is TerminalBindingReason.STRUCTURAL_MATCH
    assert result.invocation_id == snapshot.invocation_id
    assert result.execution_id == evidence.execution_id


def test_closed_observed_invocation_can_match():
    snapshot, evidence = scenario(close=True)
    assert snapshot.state is InvocationCaptureState.CLOSED
    assert bind(snapshot, evidence).decision is TerminalBindingDecision.MATCHED


@pytest.mark.parametrize(
    "status",
    (
        InvocationExecutionStatus.EMPTY,
        InvocationExecutionStatus.FAILED,
    ),
)
def test_non_successful_execution_is_unresolved(status):
    snapshot, evidence = scenario(
        capture_status=status,
        evidence_status=GovernedTerminalStatus(status.value),
        item_count=0,
    )
    result = bind(snapshot, evidence)
    assert result.decision is TerminalBindingDecision.UNRESOLVED
    assert result.reason is TerminalBindingReason.EXECUTION_NOT_SUCCESSFUL


def test_execution_mismatch_is_rejected():
    snapshot, evidence = scenario(
        evidence_execution_id="b" * 64,
    )
    result = bind(snapshot, evidence)
    assert result.decision is TerminalBindingDecision.REJECTED
    assert result.reason is TerminalBindingReason.EXECUTION_MISMATCH


def test_status_mismatch_is_rejected():
    snapshot, evidence = scenario(
        evidence_status=GovernedTerminalStatus.EMPTY,
        item_count=0,
    )
    result = bind(snapshot, evidence)
    assert result.decision is TerminalBindingDecision.REJECTED
    assert result.reason is TerminalBindingReason.STATUS_MISMATCH


@pytest.mark.parametrize(
    "owner,session",
    (
        ("other", "session"),
        ("owner", "other"),
        ("other", "other"),
    ),
)
def test_identity_mismatch_is_rejected(owner, session):
    snapshot, evidence = scenario()
    result = bind(snapshot, evidence, owner, session)
    assert result.decision is TerminalBindingDecision.REJECTED
    assert result.reason is TerminalBindingReason.IDENTITY_MISMATCH


def test_started_invocation_is_unresolved():
    capture = CrossDomainInvocationCapture()
    invocation_id = capture.begin(owner="owner", session_id="session")
    snapshot = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    _, evidence = scenario()
    result = bind(snapshot, evidence)
    assert result.decision is TerminalBindingDecision.UNRESOLVED
    assert result.reason is TerminalBindingReason.INVOCATION_NOT_OBSERVED


def test_closed_without_observation_is_unresolved():
    capture = CrossDomainInvocationCapture()
    invocation_id = capture.begin(owner="owner", session_id="session")
    assert capture.close(
        invocation_id, owner="owner", session_id="session"
    )
    snapshot = capture.snapshot(
        invocation_id, owner="owner", session_id="session"
    )
    _, evidence = scenario()
    assert bind(snapshot, evidence).decision is TerminalBindingDecision.UNRESOLVED


@pytest.mark.parametrize("invalid", (None, object(), {}, "forged"))
def test_invalid_snapshot_is_rejected(invalid):
    _, evidence = scenario()
    assert bind(invalid, evidence).decision is TerminalBindingDecision.REJECTED


@pytest.mark.parametrize("invalid", (None, object(), {}, "forged"))
def test_invalid_evidence_is_rejected(invalid):
    snapshot, _ = scenario()
    assert bind(snapshot, invalid).decision is TerminalBindingDecision.REJECTED


def test_binding_result_is_immutable():
    snapshot, evidence = scenario()
    result = bind(snapshot, evidence)
    with pytest.raises(FrozenInstanceError):
        result.decision = TerminalBindingDecision.REJECTED


def test_inconsistent_matched_result_is_rejected():
    with pytest.raises(ValueError):
        CrossDomainTerminalEvidenceBinding(
            decision=TerminalBindingDecision.MATCHED,
            reason=TerminalBindingReason.STRUCTURAL_MATCH,
        )


def test_unresolved_result_cannot_carry_ids():
    with pytest.raises(ValueError):
        CrossDomainTerminalEvidenceBinding(
            decision=TerminalBindingDecision.UNRESOLVED,
            reason=TerminalBindingReason.EXECUTION_NOT_SUCCESSFUL,
            invocation_id="inv",
        )


def test_no_authorization_api():
    assert not hasattr(CrossDomainTerminalEvidenceBinding, "admit")
    assert not hasattr(CrossDomainTerminalEvidenceBinding, "register")
    assert not hasattr(CrossDomainTerminalEvidenceBinding, "authorize")
