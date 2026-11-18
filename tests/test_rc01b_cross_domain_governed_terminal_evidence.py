"""Adversarial tests for governed terminal evidence contracts."""

from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_governed_terminal_evidence import (
    GovernedTerminalExecutionEvidence,
    GovernedTerminalStatus,
    terminal_evidence_from_result,
)


def evidence(
    *,
    status=GovernedTerminalStatus.SUCCEEDED,
    execution_id="a" * 64,
    item_count=1,
    response_present=True,
    producer_verified=False,
):
    return GovernedTerminalExecutionEvidence(
        source_id="governed-source",
        status=status,
        execution_id=execution_id,
        item_count=item_count,
        response_present=response_present,
        producer_verified=producer_verified,
    )


def test_success_is_structurally_valid():
    result = evidence()
    assert result.status is GovernedTerminalStatus.SUCCEEDED
    assert result.producer_verified is False


def test_empty_is_structurally_valid():
    result = evidence(
        status=GovernedTerminalStatus.EMPTY,
        item_count=0,
    )
    assert result.status is GovernedTerminalStatus.EMPTY


def test_failed_is_structurally_valid():
    result = evidence(
        status=GovernedTerminalStatus.FAILED,
        item_count=0,
    )
    assert result.status is GovernedTerminalStatus.FAILED


def test_rejected_without_execution_is_structurally_valid():
    result = evidence(
        status=GovernedTerminalStatus.REJECTED,
        execution_id=None,
        item_count=0,
        response_present=False,
    )
    assert result.execution_id is None


@pytest.mark.parametrize(
    "invalid",
    (None, "", " ", " source", "source ", 42, True),
)
def test_invalid_source_is_rejected(invalid):
    with pytest.raises(ValueError):
        GovernedTerminalExecutionEvidence(
            source_id=invalid,
            status=GovernedTerminalStatus.SUCCEEDED,
            execution_id="a" * 64,
            item_count=1,
            response_present=True,
        )


@pytest.mark.parametrize(
    "invalid",
    (None, "", " ", " a", "a ", 42, True),
)
def test_invalid_execution_is_rejected(invalid):
    with pytest.raises(ValueError):
        evidence(execution_id=invalid)


@pytest.mark.parametrize(
    "invalid",
    (-1, 1.0, True, None),
)
def test_invalid_item_count_is_rejected(invalid):
    with pytest.raises(ValueError):
        evidence(item_count=invalid)


def test_success_without_items_is_rejected():
    with pytest.raises(ValueError):
        evidence(item_count=0)


def test_empty_with_items_is_rejected():
    with pytest.raises(ValueError):
        evidence(
            status=GovernedTerminalStatus.EMPTY,
            item_count=1,
        )


def test_failed_with_items_is_rejected():
    with pytest.raises(ValueError):
        evidence(
            status=GovernedTerminalStatus.FAILED,
            item_count=1,
        )


def test_response_absence_is_rejected():
    with pytest.raises(ValueError):
        evidence(response_present=False)


def test_producer_verified_cannot_be_claimed():
    with pytest.raises(ValueError):
        evidence(producer_verified=True)


def test_rejected_cannot_claim_execution():
    with pytest.raises(ValueError):
        evidence(
            status=GovernedTerminalStatus.REJECTED,
            execution_id="a" * 64,
            item_count=0,
            response_present=False,
        )


def test_rejected_cannot_claim_response():
    with pytest.raises(ValueError):
        evidence(
            status=GovernedTerminalStatus.REJECTED,
            execution_id=None,
            item_count=0,
            response_present=True,
        )


def test_evidence_is_immutable():
    result = evidence()
    with pytest.raises(FrozenInstanceError):
        result.status = GovernedTerminalStatus.FAILED


def test_arbitrary_object_cannot_be_projected():
    class Forged:
        status = GovernedTerminalStatus.SUCCEEDED
        execution_id = "a" * 64

    assert terminal_evidence_from_result(Forged()) is None


def test_none_cannot_be_projected():
    assert terminal_evidence_from_result(None) is None


def test_contract_has_no_admission_api():
    assert not hasattr(
        GovernedTerminalExecutionEvidence, "admit"
    )
    assert not hasattr(
        GovernedTerminalExecutionEvidence, "register"
    )
    assert not hasattr(
        GovernedTerminalExecutionEvidence, "authorize"
    )
