"""Tests for non-authorizing provenance admission contracts."""

from dataclasses import FrozenInstanceError, replace

import pytest

from app.cross_domain_context_resolver import ContextDomain
from app.cross_domain_provenance_admission_contracts import (
    AdmissionDecision,
    AdmissionReason,
    ProvenanceAdmissionRequest,
    ProvenanceAdmissionResult,
)


def request(**changes):
    values = {
        "invocation_id": "invocation-1",
        "owner": "owner",
        "session_id": "session",
        "domain": ContextDomain.DOCUMENTS,
        "execution_id": "execution-1",
        "turn_id": "turn-1",
        "sequence": 1,
    }
    values.update(changes)
    return ProvenanceAdmissionRequest(**values)


def test_valid_request():
    candidate = request()
    assert candidate.domain is ContextDomain.DOCUMENTS
    assert candidate.sequence == 1


@pytest.mark.parametrize(
    "field",
    (
        "invocation_id",
        "owner",
        "session_id",
        "execution_id",
        "turn_id",
    ),
)
def test_empty_identifier_rejected(field):
    with pytest.raises(ValueError):
        request(**{field: ""})


@pytest.mark.parametrize(
    "field",
    (
        "invocation_id",
        "owner",
        "session_id",
        "execution_id",
        "turn_id",
    ),
)
def test_whitespace_identifier_rejected(field):
    with pytest.raises(ValueError):
        request(**{field: " invalid "})


@pytest.mark.parametrize(
    "field",
    (
        "invocation_id",
        "owner",
        "session_id",
        "execution_id",
        "turn_id",
    ),
)
def test_non_string_identifier_rejected(field):
    with pytest.raises(ValueError):
        request(**{field: None})


def test_invalid_domain_rejected():
    with pytest.raises(ValueError):
        request(domain="documents")


@pytest.mark.parametrize("sequence", (0, -1, True, 1.5, "1", None))
def test_invalid_sequence_rejected(sequence):
    with pytest.raises(ValueError):
        request(sequence=sequence)


def test_request_is_immutable():
    candidate = request()
    with pytest.raises(FrozenInstanceError):
        candidate.owner = "other"


def test_valid_admitted_result():
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.ADMITTED,
        reason=AdmissionReason.VERIFIED,
        request=request(),
    )
    assert result.decision is AdmissionDecision.ADMITTED


def test_rejected_result_without_request():
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.REJECTED,
        reason=AdmissionReason.INVALID_REQUEST,
    )
    assert result.request is None


def test_unresolved_result():
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.UNRESOLVED,
        reason=AdmissionReason.INSUFFICIENT_EVIDENCE,
    )
    assert result.decision is AdmissionDecision.UNRESOLVED


def test_admitted_requires_verified_reason():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision=AdmissionDecision.ADMITTED,
            reason=AdmissionReason.EXECUTION_FAILED,
            request=request(),
        )


def test_admitted_requires_request():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision=AdmissionDecision.ADMITTED,
            reason=AdmissionReason.VERIFIED,
        )


def test_verified_reason_requires_admitted():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision=AdmissionDecision.REJECTED,
            reason=AdmissionReason.VERIFIED,
            request=request(),
        )


def test_invalid_decision_rejected():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision="admitted",
            reason=AdmissionReason.VERIFIED,
            request=request(),
        )


def test_invalid_reason_rejected():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision=AdmissionDecision.REJECTED,
            reason="invalid_request",
        )


def test_invalid_request_object_rejected():
    with pytest.raises(ValueError):
        ProvenanceAdmissionResult(
            decision=AdmissionDecision.REJECTED,
            reason=AdmissionReason.INVALID_REQUEST,
            request=object(),
        )


def test_result_is_immutable():
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.UNRESOLVED,
        reason=AdmissionReason.INSUFFICIENT_EVIDENCE,
    )
    with pytest.raises(FrozenInstanceError):
        result.reason = AdmissionReason.INTERNAL_FAILURE


def test_contract_does_not_grant_authority():
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.ADMITTED,
        reason=AdmissionReason.VERIFIED,
        request=request(),
    )
    assert not hasattr(result, "authorized")
    assert not hasattr(result, "register")
    assert not hasattr(result, "capability")


def test_caller_can_construct_admitted_data():
    candidate = request()
    result = ProvenanceAdmissionResult(
        decision=AdmissionDecision.ADMITTED,
        reason=AdmissionReason.VERIFIED,
        request=candidate,
    )
    changed = replace(result, reason=AdmissionReason.VERIFIED)
    assert changed.decision is AdmissionDecision.ADMITTED
    assert changed.request == candidate
