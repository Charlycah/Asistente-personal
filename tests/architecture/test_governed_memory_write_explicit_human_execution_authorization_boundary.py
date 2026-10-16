from __future__ import annotations

import importlib
import inspect

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    AuthorizedGovernedMemoryWriteExecutionEvidence,
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)

_g8_contract = importlib.import_module(
    "tests.architecture."
    "test_intel_g8_source_neutral_materialization_to_existing_memory_write_adapter_contract_red"
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


def test_existing_human_authority_exposes_memory_write_execution_authorization() -> (
    None
):
    authority = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    request = _request()

    authorization = authority.evaluate_governed_memory_write_execution_authorization(
        request,
        _response(request.request_id),
    )

    assert isinstance(
        authorization,
        AuthorizedGovernedMemoryWriteExecutionEvidence,
    )
    assert authorization.memory_write_request_id == request.request_id
    assert (
        authorization.materialization_proposal_id == request.materialization_proposal_id
    )
    assert authorization.idempotency_key == request.idempotency_key
    assert authorization.writer_authority == request.writer_authority
    assert authorization.writer_component == request.writer_component
    assert authorization.writer_method == request.writer_method
    assert authorization.read_only is True
    assert authorization.write_performed is False
    assert authorization.memory_persisted is False
    assert authorization.memory_created is False
    assert authorization.executes_actions is False
    assert authorization.grants_authority is False


def test_memory_write_execution_authorization_fails_closed_on_wrong_request() -> None:
    authority = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    request = _request()

    authorization = authority.evaluate_governed_memory_write_execution_authorization(
        request,
        _response("governed-memory-write-request-wrong"),
    )

    assert authorization is None


def test_memory_write_execution_authorization_requires_explicit_apply_now_language(
) -> None:
    authority = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    request = _request()

    authorization = authority.evaluate_governed_memory_write_execution_authorization(
        request,
        _response(request.request_id, text="me parece bien"),
    )

    assert authorization is None


def test_memory_write_execution_authorization_does_not_execute_memory() -> None:
    source = inspect.getsource(
        M369ExplicitHumanLearningApprovalEvidenceFoundation.evaluate_governed_memory_write_execution_authorization
    )

    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source
    assert "OfficialMemoryGateway(" not in source
    assert "ProductiveGovernedLearningWiring" not in source
    assert ".submit(" not in source


def test_existing_productive_write_seam_is_unchanged_by_authorization_boundary() -> (
    None
):
    from app.productive_governed_learning_wiring import (
        ProductiveGovernedLearningWiring,
    )

    signature = inspect.signature(
        ProductiveGovernedLearningWiring.execute_certified_write_request
    )
    assert tuple(signature.parameters) == ("self", "request", "authorization")
