from __future__ import annotations

import importlib
import inspect

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    AuthorizedGovernedMemoryWriteExecutionEvidence,
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
)
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring

_g8_contract = importlib.import_module(
    "tests.architecture."
    "test_intel_g8_source_neutral_materialization_to_existing_"
    "memory_write_adapter_contract_red"
)
_g8_proposal = _g8_contract._g8_proposal


def _request():
    return GovernedMemoryWriteAdapterFoundation().adapt(_g8_proposal())


def _response(request_id: str, text: str = "Sí, guardar ahora"):
    return ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse(
        authorization_request_id="memory-write-execution-auth-request-1",
        memory_write_request_id=request_id,
        human_response_reference="conversation:memory-write-execution-auth-1",
        response_text=text,
        approver="Carlos",
        exact_linkage=True,
    )


def test_pending_request_is_isolated_by_session() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()

    retained = wiring.retain_pending_governed_memory_write_request(
        "session-a",
        request,
    )

    assert retained is request
    assert wiring.pending_governed_memory_write_request("session-a") is request
    assert wiring.pending_governed_memory_write_request("session-b") is None


def test_pending_request_requires_session_identity() -> None:
    wiring = ProductiveGovernedLearningWiring(None)

    try:
        wiring.retain_pending_governed_memory_write_request(" ", _request())
    except ValueError as exc:
        assert str(exc) == "pending governed memory write requires session identity"
    else:
        raise AssertionError("blank session identity must fail closed")


def test_missing_pending_request_cannot_produce_authorization() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()

    authorization = (
        wiring.evaluate_pending_governed_memory_write_execution_authorization(
            "missing-session",
            _response(request.request_id),
        )
    )

    assert authorization is None


def test_wrong_request_linkage_fails_closed() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()
    wiring.retain_pending_governed_memory_write_request("session-a", request)

    authorization = (
        wiring.evaluate_pending_governed_memory_write_execution_authorization(
            "session-a",
            _response("governed-memory-write-request-wrong"),
        )
    )

    assert authorization is None


def test_non_explicit_apply_now_language_fails_closed() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()
    wiring.retain_pending_governed_memory_write_request("session-a", request)

    authorization = (
        wiring.evaluate_pending_governed_memory_write_execution_authorization(
            "session-a",
            _response(request.request_id, text="me parece bien"),
        )
    )

    assert authorization is None


def test_exact_pending_request_and_explicit_response_yield_inert_evidence() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()
    wiring.retain_pending_governed_memory_write_request("session-a", request)

    authorization = (
        wiring.evaluate_pending_governed_memory_write_execution_authorization(
            "session-a",
            _response(request.request_id),
        )
    )

    assert isinstance(
        authorization,
        AuthorizedGovernedMemoryWriteExecutionEvidence,
    )
    assert authorization.memory_write_request_id == request.request_id
    assert authorization.read_only is True
    assert authorization.write_performed is False
    assert authorization.memory_persisted is False
    assert authorization.memory_created is False
    assert authorization.executes_actions is False
    assert authorization.grants_authority is False


def test_pending_authorization_evaluation_does_not_execute_or_write_memory() -> None:
    source = inspect.getsource(
        ProductiveGovernedLearningWiring.
        evaluate_pending_governed_memory_write_execution_authorization
    )

    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source
    assert "_persist_certified_write_request(" not in source


def test_existing_productive_and_legacy_seams_remain_separate() -> None:
    legacy = inspect.signature(ProductiveGovernedLearningWiring.execute)
    certified = inspect.signature(
        ProductiveGovernedLearningWiring.execute_certified_write_request
    )

    assert tuple(legacy.parameters) == (
        "self",
        "evaluation",
        "response",
        "current_turn_text",
    )
    assert tuple(certified.parameters) == ("self", "request", "authorization")
