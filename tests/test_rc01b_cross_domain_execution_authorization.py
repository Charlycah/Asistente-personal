"""Security tests for the isolated execution authorization contract."""

from dataclasses import FrozenInstanceError, replace

import pytest

from app.cross_domain_execution_authorization import (
    CrossDomainExecutionAuthorization,
    ExecutionAuthorizationDecision,
    ExecutionAuthorizationReason,
    ExecutionAuthorizationRequest,
    ExecutionAuthorizationResult,
)


def request(**overrides):
    values = {
        "owner": "owner",
        "session_id": "session",
        "source_id": "source",
        "capability": "information_source",
        "invocation_id": "invocation",
    }
    values.update(overrides)
    return ExecutionAuthorizationRequest(**values)


def test_valid_request_remains_unresolved():
    result = CrossDomainExecutionAuthorization().evaluate(request())
    assert result.decision is ExecutionAuthorizationDecision.UNRESOLVED
    assert result.reason is ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE
    assert result.authorized is False


@pytest.mark.parametrize(
    "field",
    [
        "owner",
        "session_id",
        "source_id",
        "capability",
        "invocation_id",
    ],
)
@pytest.mark.parametrize(
    "invalid",
    [None, "", " ", " padded ", True, 42],
)
def test_invalid_identity_fields_are_rejected(field, invalid):
    with pytest.raises(ValueError):
        request(**{field: invalid})


@pytest.mark.parametrize(
    "untrusted",
    [True, False, "true", 1, {}, object()],
)
def test_caller_permission_never_authorizes(untrusted):
    result = CrossDomainExecutionAuthorization().evaluate(
        request(),
        external_access_authorized=untrusted,
    )
    assert result.decision is ExecutionAuthorizationDecision.REJECTED
    assert result.reason is ExecutionAuthorizationReason.UNTRUSTED_PERMISSION
    assert result.authorized is False


@pytest.mark.parametrize(
    "invalid",
    [None, True, False, {}, "request", object()],
)
def test_noncanonical_requests_are_rejected(invalid):
    result = CrossDomainExecutionAuthorization().evaluate(invalid)
    assert result.decision is ExecutionAuthorizationDecision.REJECTED
    assert result.authorized is False


def test_fabricated_authorized_result_is_rejected():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.AUTHORIZED,
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
            authorized=True,
        )


def test_fabricated_authorized_decision_even_without_flag_is_rejected():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.AUTHORIZED,
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
        )


def test_unresolved_cannot_claim_authorized():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.UNRESOLVED,
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
            authorized=True,
        )


def test_rejected_cannot_claim_authorized():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.REJECTED,
            reason=ExecutionAuthorizationReason.INVALID_REQUEST,
            authorized=True,
        )


def test_invalid_decision_type_is_rejected():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision="authorized",
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
        )


def test_invalid_reason_type_is_rejected():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.UNRESOLVED,
            reason="authority_unavailable",
        )


def test_authorized_flag_must_be_exact_boolean():
    with pytest.raises(ValueError):
        ExecutionAuthorizationResult(
            decision=ExecutionAuthorizationDecision.UNRESOLVED,
            reason=ExecutionAuthorizationReason.AUTHORITY_UNAVAILABLE,
            authorized=0,
        )


def test_request_is_immutable():
    with pytest.raises(FrozenInstanceError):
        request().owner = "other"


def test_result_is_immutable():
    result = CrossDomainExecutionAuthorization().evaluate(request())
    with pytest.raises(FrozenInstanceError):
        result.authorized = True


def test_changed_owner_does_not_grant_authority():
    original = request()
    changed = replace(original, owner="another_owner")
    evaluator = CrossDomainExecutionAuthorization()

    assert evaluator.evaluate(original).authorized is False
    assert evaluator.evaluate(changed).authorized is False


def test_changed_session_does_not_grant_authority():
    changed = replace(request(), session_id="another_session")
    result = CrossDomainExecutionAuthorization().evaluate(changed)
    assert result.decision is ExecutionAuthorizationDecision.UNRESOLVED


def test_changed_source_does_not_grant_authority():
    changed = replace(request(), source_id="another_source")
    result = CrossDomainExecutionAuthorization().evaluate(changed)
    assert result.authorized is False


def test_changed_capability_does_not_grant_authority():
    changed = replace(request(), capability="other_capability")
    result = CrossDomainExecutionAuthorization().evaluate(changed)
    assert result.authorized is False


def test_repeated_evaluation_never_grants_authority():
    evaluator = CrossDomainExecutionAuthorization()
    operation = request()

    for _ in range(3):
        result = evaluator.evaluate(operation)
        assert result.decision is ExecutionAuthorizationDecision.UNRESOLVED
        assert result.authorized is False


def test_result_cannot_be_used_as_request():
    evaluator = CrossDomainExecutionAuthorization()
    first = evaluator.evaluate(request())
    second = evaluator.evaluate(first)

    assert second.decision is ExecutionAuthorizationDecision.REJECTED
    assert second.reason is ExecutionAuthorizationReason.INVALID_REQUEST


def test_no_executor_is_invoked():
    class Executor:
        def __init__(self):
            self.calls = 0

        def execute(self, query):
            self.calls += 1
            raise AssertionError("execution must not occur")

    executor = Executor()
    evaluator = CrossDomainExecutionAuthorization()

    result = evaluator.evaluate(
        request(),
        external_access_authorized=True,
    )

    assert result.authorized is False
    assert executor.calls == 0


def test_evaluator_exposes_no_execution_method():
    evaluator = CrossDomainExecutionAuthorization()
    assert not hasattr(evaluator, "execute")
    assert not hasattr(evaluator, "grant")
    assert not hasattr(evaluator, "admit")