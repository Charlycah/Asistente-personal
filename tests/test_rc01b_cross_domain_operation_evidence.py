"""Tests for structural, non-authorizing operation evidence."""

from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_context_resolver import ContextDomain
from app.cross_domain_operation_evidence import CrossDomainOperationEvidence


def evidence(**overrides):
    values = {
        "owner": "owner",
        "session_id": "session",
        "domain": ContextDomain.LIBRARY,
        "operation": "local_document_retrieval",
        "execution_id": "execution-1",
        "outcome": "completed",
    }
    values.update(overrides)
    return CrossDomainOperationEvidence(**values)


def test_valid_evidence_is_structural_only():
    item = evidence()
    assert item.domain is ContextDomain.LIBRARY
    assert item.execution_id == "execution-1"
    assert not hasattr(item, "authorized")


@pytest.mark.parametrize(
    "field",
    ("owner", "session_id", "operation", "execution_id", "outcome"),
)
@pytest.mark.parametrize("invalid", ("", "  ", None, 7))
def test_invalid_identity_or_operation_fields_are_rejected(field, invalid):
    with pytest.raises(ValueError):
        evidence(**{field: invalid})


@pytest.mark.parametrize(
    "field",
    ("owner", "session_id", "operation", "execution_id", "outcome"),
)
def test_surrounding_whitespace_is_rejected(field):
    with pytest.raises(ValueError):
        evidence(**{field: " value "})


def test_invalid_domain_is_rejected():
    with pytest.raises(ValueError):
        evidence(domain="library")


def test_evidence_is_immutable():
    item = evidence()
    with pytest.raises(FrozenInstanceError):
        item.operation = "other"


def test_evidence_does_not_register_provenance():
    item = evidence()
    assert not hasattr(item, "register")
    assert not hasattr(item, "authorized_antecedents")