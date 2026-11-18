"""Isolated tests for the non-authorizing execution binder."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.cross_domain_execution_binding import (
    CrossDomainExecutionBinder,
    ExecutionBindingDecision,
    ExecutionBindingResult,
)
from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
)


def evidence(
    *,
    source_id="nasa",
    status=GovernedTerminalStatus.SUCCEEDED,
    execution_id="a" * 64,
    item_count=1,
):
    return GovernedTerminalExecutionEvidence(
        source_id=source_id,
        status=status,
        execution_id=execution_id,
        item_count=item_count,
        response_present=True,
    )


def fields(**changes):
    values = {
        "invocation_id": "inv-1",
        "owner": "owner",
        "session_id": "session",
        "evidence": evidence(),
    }
    values.update(changes)
    return values


def bound():
    binder = CrossDomainExecutionBinder()
    result = binder.bind(**fields())
    assert result.decision is ExecutionBindingDecision.BOUND
    return binder


def test_valid_evidence_can_be_bound():
    binder = bound()
    result = binder.verify(**fields())
    assert result.decision is ExecutionBindingDecision.VERIFIED
    assert result.producer_verified is False


def test_unknown_invocation_is_unresolved():
    binder = CrossDomainExecutionBinder()
    result = binder.verify(**fields())
    assert result.decision is ExecutionBindingDecision.UNRESOLVED


@pytest.mark.parametrize(
    "changed",
    (
        {"invocation_id": "other"},
        {"owner": "other"},
        {"session_id": "other"},
        {"evidence": evidence(source_id="apple")},
        {"evidence": evidence(execution_id="b" * 64)},
    ),
)
def test_mismatched_binding_is_unresolved(changed):
    binder = bound()
    result = binder.verify(**fields(**changed))
    assert result.decision is ExecutionBindingDecision.UNRESOLVED


@pytest.mark.parametrize(
    "name",
    ("invocation_id", "owner", "session_id"),
)
def test_invalid_identity_is_rejected(name):
    binder = CrossDomainExecutionBinder()
    result = binder.bind(**fields(**{name: "  "}))
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_invalid_evidence_type_is_rejected():
    binder = CrossDomainExecutionBinder()
    result = binder.bind(**fields(evidence=object()))
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_rejected_terminal_evidence_is_rejected():
    binder = CrossDomainExecutionBinder()
    result = binder.bind(
        **fields(
            evidence=GovernedTerminalExecutionEvidence(
                source_id="nasa",
                status=GovernedTerminalStatus.REJECTED,
                execution_id=None,
                item_count=0,
                response_present=False,
            )
        )
    )
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_empty_terminal_outcome_remains_distinct():
    binder = CrossDomainExecutionBinder()
    result = binder.bind(
        **fields(
            evidence=evidence(
                status=GovernedTerminalStatus.EMPTY,
                item_count=0,
            )
        )
    )
    assert result.decision is ExecutionBindingDecision.BOUND
    assert result.producer_verified is False


def test_failed_terminal_outcome_remains_distinct():
    binder = CrossDomainExecutionBinder()
    result = binder.bind(
        **fields(
            evidence=evidence(
                status=GovernedTerminalStatus.FAILED,
                item_count=0,
            )
        )
    )
    assert result.decision is ExecutionBindingDecision.BOUND
    assert result.producer_verified is False


def test_duplicate_invocation_is_rejected():
    binder = bound()
    result = binder.bind(
        **fields(evidence=evidence(execution_id="b" * 64))
    )
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_duplicate_execution_is_rejected():
    binder = bound()
    result = binder.bind(**fields(invocation_id="inv-2"))
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_consumption_is_single_use():
    binder = bound()
    first = binder.consume(**fields())
    second = binder.consume(**fields())
    assert first.decision is ExecutionBindingDecision.CONSUMED
    assert second.decision is ExecutionBindingDecision.UNRESOLVED


def test_consumed_binding_cannot_be_verified():
    binder = bound()
    binder.consume(**fields())
    result = binder.verify(**fields())
    assert result.decision is ExecutionBindingDecision.UNRESOLVED


def test_consumed_execution_cannot_be_rebound():
    binder = bound()
    binder.consume(**fields())
    result = binder.bind(**fields(invocation_id="inv-2"))
    assert result.decision is ExecutionBindingDecision.REJECTED


def test_instances_are_isolated():
    first = bound()
    second = CrossDomainExecutionBinder()
    assert (
        first.verify(**fields()).decision
        is ExecutionBindingDecision.VERIFIED
    )
    assert (
        second.verify(**fields()).decision
        is ExecutionBindingDecision.UNRESOLVED
    )


def test_concurrent_consumption_is_single_use():
    binder = bound()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(
            pool.map(lambda _: binder.consume(**fields()), range(16))
        )

    assert sum(
        result.decision is ExecutionBindingDecision.CONSUMED
        for result in results
    ) == 1


def test_structurally_fabricated_evidence_is_not_authenticated():
    binder = CrossDomainExecutionBinder()
    fabricated = evidence()
    result = binder.bind(**fields(evidence=fabricated))
    assert result.decision is ExecutionBindingDecision.BOUND
    assert result.producer_verified is False


def test_positive_result_cannot_claim_producer_authentication():
    with pytest.raises(ValueError):
        ExecutionBindingResult(
            decision=ExecutionBindingDecision.BOUND,
            invocation_id="inv-1",
            execution_id="a" * 64,
            producer_verified=True,
        )
