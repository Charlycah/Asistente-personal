"""Adversarial tests for the isolated non-authorizing authority."""

from dataclasses import replace

import pytest

from app.cross_domain_context_resolver import ContextDomain
from app.cross_domain_provenance_admission_authority import (
    CrossDomainProvenanceAdmissionAuthority,
)
from app.cross_domain_provenance_admission_contracts import (
    AdmissionDecision,
    AdmissionReason,
    ProvenanceAdmissionRequest,
    ProvenanceAdmissionResult,
)


def candidate(**changes):
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


def authority():
    return CrossDomainProvenanceAdmissionAuthority()


def test_valid_candidate_is_unresolved():
    request = candidate()
    result = authority().evaluate(request)
    assert result.decision is AdmissionDecision.UNRESOLVED
    assert result.reason is AdmissionReason.EXECUTION_NOT_VERIFIED
    assert result.request is request


@pytest.mark.parametrize(
    "invalid",
    (
        None,
        True,
        False,
        0,
        1,
        "",
        "admitted",
        {},
        [],
        object(),
    ),
)
def test_invalid_request_is_rejected(invalid):
    result = authority().evaluate(invalid)
    assert result.decision is AdmissionDecision.REJECTED
    assert result.reason is AdmissionReason.INVALID_REQUEST
    assert result.request is None


def test_caller_fabricated_admitted_result_is_rejected():
    fabricated = ProvenanceAdmissionResult(
        decision=AdmissionDecision.ADMITTED,
        reason=AdmissionReason.VERIFIED,
        request=candidate(),
    )
    result = authority().evaluate(fabricated)
    assert result.decision is AdmissionDecision.REJECTED
    assert result.reason is AdmissionReason.INVALID_REQUEST


@pytest.mark.parametrize(
    "domain",
    tuple(ContextDomain),
)
def test_every_domain_remains_unresolved(domain):
    result = authority().evaluate(candidate(domain=domain))
    assert result.decision is AdmissionDecision.UNRESOLVED
    assert result.reason is AdmissionReason.EXECUTION_NOT_VERIFIED


@pytest.mark.parametrize(
    "execution_id",
    (
        "execution-1",
        "a" * 64,
        "claimed-success",
        "governed-execution",
    ),
)
def test_execution_id_never_authenticates(execution_id):
    result = authority().evaluate(
        candidate(execution_id=execution_id)
    )
    assert result.decision is AdmissionDecision.UNRESOLVED


@pytest.mark.parametrize(
    "changes",
    (
        {"owner": "other-owner"},
        {"session_id": "other-session"},
        {"invocation_id": "other-invocation"},
        {"turn_id": "other-turn"},
        {"sequence": 999},
    ),
)
def test_arbitrary_identity_changes_do_not_admit(changes):
    result = authority().evaluate(candidate(**changes))
    assert result.decision is AdmissionDecision.UNRESOLVED


def test_repeated_evaluation_never_admits():
    subject = authority()
    request = candidate()
    first = subject.evaluate(request)
    second = subject.evaluate(request)
    assert first == second
    assert first.decision is AdmissionDecision.UNRESOLVED


def test_separate_instances_never_admit():
    request = candidate()
    first = authority().evaluate(request)
    second = authority().evaluate(request)
    assert first == second
    assert first.decision is AdmissionDecision.UNRESOLVED


def test_authority_has_no_registration_interface():
    subject = authority()
    assert not hasattr(subject, "register")
    assert not hasattr(subject, "admit")
    assert not hasattr(subject, "capture")


def test_authority_has_no_journal_or_provenance_registry():
    subject = authority()
    assert not hasattr(subject, "journal")
    assert not hasattr(subject, "provenance")
    assert not hasattr(subject, "_journal")
    assert not hasattr(subject, "_provenance")


def test_request_mutation_cannot_enable_admission():
    original = candidate()
    changed = replace(
        original,
        execution_id="b" * 64,
        sequence=2,
    )
    assert authority().evaluate(changed).decision is (
        AdmissionDecision.UNRESOLVED
    )


def test_unexpected_evaluation_failure_is_closed(monkeypatch):
    subject = authority()

    def broken(_request):
        raise RuntimeError("unexpected evaluation failure")

    monkeypatch.setattr(subject, "_evaluate_candidate", broken)

    result = subject.evaluate(candidate())
    assert result.decision is AdmissionDecision.UNRESOLVED
    assert result.reason is AdmissionReason.INTERNAL_FAILURE
    assert result.request is None


def test_result_cannot_be_admitted():
    result = authority().evaluate(candidate())
    assert result.decision is not AdmissionDecision.ADMITTED
    assert result.reason is not AdmissionReason.VERIFIED
