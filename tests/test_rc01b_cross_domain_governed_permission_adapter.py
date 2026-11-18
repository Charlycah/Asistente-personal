"""Fail-closed tests for the isolated M63 observation adapter."""

from dataclasses import FrozenInstanceError, replace

import pytest

from app.cross_domain_execution_authorization import (
    CrossDomainExecutionAuthorization,
    ExecutionAuthorizationDecision,
    ExecutionAuthorizationRequest,
)
from app.cross_domain_governed_permission_adapter import (
    CrossDomainGovernedPermissionAdapter,
    GovernedPermissionObservation,
    GovernedPermissionStatus,
)
from core.capability_registry import CapabilityDescriptor, PermissionScope
from core.permission_consent import PermissionConsentManager


def operation(**changes):
    fields = {
        "owner": "owner",
        "session_id": "session",
        "source_id": "source",
        "capability": "information_source",
        "invocation_id": "invocation",
    }
    fields.update(changes)
    return ExecutionAuthorizationRequest(**fields)


def descriptor(**changes):
    fields = {
        "name": "information_source",
        "description": "Governed information lookup",
        "permission_scope": PermissionScope.NONE,
    }
    fields.update(changes)
    return CapabilityDescriptor(**fields)


def adapter():
    return CrossDomainGovernedPermissionAdapter(
        PermissionConsentManager()
    )


def test_m63_allowed_never_authorizes_execution():
    result = adapter().evaluate(operation(), descriptor())
    assert result.status is GovernedPermissionStatus.POLICY_ALLOWED
    assert result.authorized is False


@pytest.mark.parametrize(
    "field",
    ["owner", "session_id", "source_id", "capability", "invocation_id"],
)
def test_identity_variations_never_authorize(field):
    request = replace(operation(), **{field: "different"})
    result = adapter().evaluate(request, descriptor())
    assert result.authorized is False


@pytest.mark.parametrize(
    "invalid",
    [None, True, False, {}, "request", object()],
)
def test_invalid_request_rejected(invalid):
    result = adapter().evaluate(invalid, descriptor())
    assert result.status is GovernedPermissionStatus.REJECTED


@pytest.mark.parametrize(
    "invalid",
    [None, True, False, {}, "descriptor", object()],
)
def test_invalid_descriptor_rejected(invalid):
    result = adapter().evaluate(operation(), invalid)
    assert result.status is GovernedPermissionStatus.REJECTED


def test_mismatched_capability_rejected():
    result = adapter().evaluate(
        operation(), descriptor(name="other_capability")
    )
    assert result.status is GovernedPermissionStatus.REJECTED
    assert result.reason == "capability_mismatch"


def test_disabled_capability_rejected():
    result = adapter().evaluate(
        operation(), descriptor(enabled=False)
    )
    assert result.status is GovernedPermissionStatus.REJECTED


def test_explicit_consent_scope_not_silently_authorized():
    result = adapter().evaluate(
        operation(),
        descriptor(
            permission_scope=PermissionScope.WRITE,
            requires_confirmation=True,
        ),
    )
    assert result.status is GovernedPermissionStatus.CONSENT_REQUIRED
    assert result.authorized is False


def test_permission_observation_is_immutable():
    result = adapter().evaluate(operation(), descriptor())
    with pytest.raises(FrozenInstanceError):
        result.authorized = True


def test_fabricated_authorized_observation_rejected():
    with pytest.raises(ValueError):
        GovernedPermissionObservation(
            GovernedPermissionStatus.POLICY_ALLOWED,
            "fabricated",
            authorized=True,
        )


def test_noncanonical_manager_rejected():
    with pytest.raises(ValueError):
        CrossDomainGovernedPermissionAdapter(object())


def test_existing_execution_authority_remains_closed():
    result = CrossDomainExecutionAuthorization().evaluate(operation())
    assert result.decision is ExecutionAuthorizationDecision.UNRESOLVED
    assert result.authorized is False


def test_adapter_exposes_no_execution_method():
    subject = adapter()
    assert not hasattr(subject, "execute")
    assert not hasattr(subject, "grant")
    assert not hasattr(subject, "admit")