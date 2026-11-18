"""Adversarial tests for non-authorizing admission composition."""

import inspect

import pytest

from app.cross_domain_context_resolver import ContextDomain
from app.cross_domain_provenance_admission_composition import (
    CrossDomainProvenanceAdmissionComposition,
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


def test_valid_candidate_remains_unresolved():
    request = candidate()
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
        request
    )
    assert result.decision is AdmissionDecision.UNRESOLVED
    assert result.reason is AdmissionReason.EXECUTION_NOT_VERIFIED
    assert result.request is request


@pytest.mark.parametrize(
    "invalid",
    (None, True, False, 0, "", {}, [], object()),
)
def test_invalid_input_is_rejected(invalid):
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
        invalid
    )
    assert result.decision is AdmissionDecision.REJECTED
    assert result.reason is AdmissionReason.INVALID_REQUEST
    assert result.request is None


def test_fabricated_admission_result_is_rejected():
    forged = ProvenanceAdmissionResult(
        decision=AdmissionDecision.ADMITTED,
        reason=AdmissionReason.VERIFIED,
        request=candidate(),
    )
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
        forged
    )
    assert result.decision is AdmissionDecision.REJECTED
    assert result.reason is AdmissionReason.INVALID_REQUEST


@pytest.mark.parametrize("domain", tuple(ContextDomain))
def test_no_domain_can_be_admitted(domain):
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
        candidate(domain=domain)
    )
    assert result.decision is AdmissionDecision.UNRESOLVED


@pytest.mark.parametrize(
    "execution_id",
    ("claimed-success", "a" * 64, "governed-execution"),
)
def test_execution_id_cannot_authorize(execution_id):
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
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
def test_identity_variations_cannot_authorize(changes):
    result = CrossDomainProvenanceAdmissionComposition().evaluate(
        candidate(**changes)
    )
    assert result.decision is AdmissionDecision.UNRESOLVED


def test_public_api_is_evaluation_only():
    subject = CrossDomainProvenanceAdmissionComposition()
    assert not hasattr(subject, "register")
    assert not hasattr(subject, "admit")
    assert not hasattr(subject, "capture")
    assert not hasattr(subject, "bind")
    assert not hasattr(subject, "begin")


def test_no_public_dependency_exposure():
    subject = CrossDomainProvenanceAdmissionComposition()
    assert not hasattr(subject, "correlator")
    assert not hasattr(subject, "authority")
    assert not hasattr(subject, "journal")
    assert not hasattr(subject, "provenance")


def test_constructor_rejects_dependency_injection():
    signature = inspect.signature(
        CrossDomainProvenanceAdmissionComposition
    )
    assert not signature.parameters

    with pytest.raises(TypeError):
        CrossDomainProvenanceAdmissionComposition(
            journal=object()
        )

    with pytest.raises(TypeError):
        CrossDomainProvenanceAdmissionComposition(
            authority=object()
        )


def test_repeated_evaluation_is_stable():
    subject = CrossDomainProvenanceAdmissionComposition()
    request = candidate()
    first = subject.evaluate(request)
    second = subject.evaluate(request)
    assert first == second
    assert first.decision is AdmissionDecision.UNRESOLVED


def test_instances_are_independent():
    first = CrossDomainProvenanceAdmissionComposition()
    second = CrossDomainProvenanceAdmissionComposition()

    assert first is not second
    assert first.evaluate(candidate()) == second.evaluate(
        candidate()
    )


def test_no_instance_dictionary_for_dynamic_dependencies():
    subject = CrossDomainProvenanceAdmissionComposition()
    assert not hasattr(subject, "__dict__")

    with pytest.raises(AttributeError):
        subject.journal = object()


def test_evaluation_never_returns_admitted():
    subject = CrossDomainProvenanceAdmissionComposition()

    for domain in ContextDomain:
        result = subject.evaluate(candidate(domain=domain))
        assert result.decision is not AdmissionDecision.ADMITTED
        assert result.reason is not AdmissionReason.VERIFIED
