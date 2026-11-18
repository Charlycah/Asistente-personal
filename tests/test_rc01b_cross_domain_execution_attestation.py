"""Isolated tests for the non-authorizing attestation registry."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from app.cross_domain_execution_attestation import (
    CrossDomainExecutionAttestationRegistry,
    ExecutionAttestation,
    ExecutionAttestationDecision,
    ExecutionAttestationState,
)


def fields(**changes):
    values = {
        "invocation_id": "inv-1",
        "execution_id": "exec-1",
        "owner": "owner",
        "session_id": "session",
        "source_id": "nasa",
    }
    values.update(changes)
    return values


def registry_with_record():
    registry = CrossDomainExecutionAttestationRegistry()
    result = registry.record(**fields())
    assert result.decision is ExecutionAttestationDecision.RECORDED
    return registry


def test_record_creates_instance_local_association():
    registry = registry_with_record()
    result = registry.verify(**fields())
    assert result.decision is ExecutionAttestationDecision.VERIFIED
    assert result.attestation.state is ExecutionAttestationState.RECORDED


def test_unknown_invocation_is_unresolved():
    registry = CrossDomainExecutionAttestationRegistry()
    result = registry.verify(**fields())
    assert result.decision is ExecutionAttestationDecision.UNRESOLVED


@pytest.mark.parametrize(
    "changed",
    (
        {"invocation_id": "other"},
        {"execution_id": "other"},
        {"owner": "other"},
        {"session_id": "other"},
        {"source_id": "other"},
    ),
)
def test_mismatch_is_unresolved(changed):
    registry = registry_with_record()
    result = registry.verify(**fields(**changed))
    assert result.decision is ExecutionAttestationDecision.UNRESOLVED
    assert result.attestation is None


@pytest.mark.parametrize(
    "name",
    (
        "invocation_id",
        "execution_id",
        "owner",
        "session_id",
        "source_id",
    ),
)
def test_invalid_identity_rejected(name):
    registry = CrossDomainExecutionAttestationRegistry()
    result = registry.record(**fields(**{name: "  "}))
    assert result.decision is ExecutionAttestationDecision.REJECTED


def test_duplicate_invocation_rejected():
    registry = registry_with_record()
    result = registry.record(**fields(execution_id="exec-2"))
    assert result.decision is ExecutionAttestationDecision.REJECTED


def test_duplicate_execution_rejected():
    registry = registry_with_record()
    result = registry.record(**fields(invocation_id="inv-2"))
    assert result.decision is ExecutionAttestationDecision.REJECTED


def test_consume_is_single_use():
    registry = registry_with_record()
    first = registry.consume(**fields())
    second = registry.consume(**fields())
    assert first.decision is ExecutionAttestationDecision.CONSUMED
    assert second.decision is ExecutionAttestationDecision.UNRESOLVED


def test_consumed_record_cannot_be_verified():
    registry = registry_with_record()
    registry.consume(**fields())
    result = registry.verify(**fields())
    assert result.decision is ExecutionAttestationDecision.UNRESOLVED


def test_consumed_execution_cannot_be_reregistered():
    registry = registry_with_record()
    registry.consume(**fields())
    result = registry.record(**fields(invocation_id="inv-2"))
    assert result.decision is ExecutionAttestationDecision.REJECTED


def test_registry_instances_are_isolated():
    first = registry_with_record()
    second = CrossDomainExecutionAttestationRegistry()
    assert first.verify(**fields()).decision is ExecutionAttestationDecision.VERIFIED
    assert second.verify(**fields()).decision is ExecutionAttestationDecision.UNRESOLVED


def test_concurrent_consumption_allows_only_one():
    registry = registry_with_record()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: registry.consume(**fields()), range(16)))

    assert sum(
        result.decision is ExecutionAttestationDecision.CONSUMED
        for result in results
    ) == 1


def test_attestation_is_not_producer_authentication():
    registry = registry_with_record()
    result = registry.verify(**fields())
    assert result.decision is ExecutionAttestationDecision.VERIFIED
    assert not hasattr(result.attestation, "producer_verified")
    assert not hasattr(result.attestation, "authorized")
    assert not hasattr(result.attestation, "admitted")


def test_invalid_attestation_state_is_rejected():
    with pytest.raises(ValueError):
        ExecutionAttestation(
            **fields(),
            state="recorded",
        )
