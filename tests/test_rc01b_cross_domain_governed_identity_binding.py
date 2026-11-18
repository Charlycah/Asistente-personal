from dataclasses import FrozenInstanceError

import pytest

from app.cross_domain_execution_authorization import ExecutionAuthorizationRequest
from app.cross_domain_governed_identity_binding import (
    CrossDomainGovernedIdentityBinder,
    GovernedIdentityBindingDecision,
    GovernedIdentityBindingResult,
)
from app.cross_domain_invocation_capture import (
    CrossDomainInvocationCapture,
    InvocationExecutionStatus,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry


def setup_binding():
    registry = OfficialRuntimeCapabilityRegistry()
    capture = CrossDomainInvocationCapture()
    invocation_id = capture.begin(owner="owner", session_id="session")
    binder = CrossDomainGovernedIdentityBinder(registry, capture)
    request = ExecutionAuthorizationRequest(
        owner="owner",
        session_id="session",
        source_id="source",
        capability="capability.test",
        invocation_id=invocation_id,
    )
    return registry, capture, binder, request


def register_test_capability(registry):
    registry.register(
        name="capability.test",
        description="Test capability",
        interceptor=object(),
    )


def test_missing_capability_is_unresolved():
    _, _, binder, request = setup_binding()
    result = binder.evaluate(request)
    assert result.decision is GovernedIdentityBindingDecision.UNRESOLVED
    assert result.authorized is False


def test_registered_capability_is_structurally_bound():
    registry, _, binder, request = setup_binding()
    register_test_capability(registry)
    result = binder.evaluate(request)
    assert result.decision is GovernedIdentityBindingDecision.BOUND
    assert result.authorized is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("owner", "other"),
        ("session_id", "other"),
        ("invocation_id", "invented"),
    ],
)
def test_identity_mismatch_is_rejected(field, value):
    registry, _, binder, request = setup_binding()
    register_test_capability(registry)
    values = {
        "owner": request.owner,
        "session_id": request.session_id,
        "source_id": request.source_id,
        "capability": request.capability,
        "invocation_id": request.invocation_id,
    }
    values[field] = value
    changed = ExecutionAuthorizationRequest(**values)
    result = binder.evaluate(changed)
    assert result.decision is GovernedIdentityBindingDecision.REJECTED
    assert result.authorized is False


def test_observed_invocation_is_not_eligible():
    registry, capture, binder, request = setup_binding()
    register_test_capability(registry)
    assert capture.observe(
        request.invocation_id,
        owner=request.owner,
        session_id=request.session_id,
        execution_id="execution-1",
        status=InvocationExecutionStatus.SUCCEEDED,
    )
    result = binder.evaluate(request)
    assert result.decision is GovernedIdentityBindingDecision.REJECTED


def test_invalid_request_is_rejected():
    registry, _, binder, _ = setup_binding()
    register_test_capability(registry)
    result = binder.evaluate(object())
    assert result.decision is GovernedIdentityBindingDecision.REJECTED


def test_result_cannot_be_forged_as_authorized():
    with pytest.raises(ValueError):
        GovernedIdentityBindingResult(
            GovernedIdentityBindingDecision.BOUND,
            "fabricated",
            authorized=True,
        )


def test_result_is_immutable():
    result = GovernedIdentityBindingResult(
        GovernedIdentityBindingDecision.UNRESOLVED,
        "test",
    )
    with pytest.raises(FrozenInstanceError):
        result.authorized = True


def test_binder_has_no_execution_methods():
    _, _, binder, _ = setup_binding()
    for name in ("execute", "grant", "admit", "consume"):
        assert not hasattr(binder, name)