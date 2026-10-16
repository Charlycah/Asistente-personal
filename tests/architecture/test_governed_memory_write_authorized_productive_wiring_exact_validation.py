from __future__ import annotations

import importlib
from dataclasses import replace

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)

_g8_contract = importlib.import_module(
    "tests.architecture."
    "test_intel_g8_source_neutral_materialization_to_existing_memory_write_adapter_contract_red"
)
_g8_proposal = _g8_contract._g8_proposal


class _MemoryGatewaySpy:
    def __init__(self) -> None:
        self.requests = []

    def remember_governed_learning(self, request):
        self.requests.append(request)
        return type(
            "_Stored", (), {"stored_count": 1, "stored_memory_ids": ("memory-1",)}
        )()


def _request():
    return GovernedMemoryWriteAdapterFoundation().adapt(_g8_proposal())


def _authorization(request):
    response = ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse(
        authorization_request_id="memory-write-execution-auth-request-1",
        memory_write_request_id=request.request_id,
        human_response_reference="conversation:memory-write-execution-auth-1",
        response_text="Sí, guardar ahora",
        approver="Carlos",
        exact_linkage=True,
    )
    return (
        M369ExplicitHumanLearningApprovalEvidenceFoundation()
        .evaluate_governed_memory_write_execution_authorization(request, response)
    )


def test_exact_authorization_allows_existing_productive_writer_once() -> None:
    request = _request()
    authorization = _authorization(request)
    gateway = _MemoryGatewaySpy()
    wiring = ProductiveGovernedLearningWiring(gateway)

    result = wiring.execute_certified_write_request(request, authorization)

    assert result.outcome is ProductiveGovernedLearningOutcome.STORED
    assert result.writer_call_performed is True
    assert gateway.requests == [request]


def test_missing_execution_authorization_fails_closed_before_writer() -> None:
    request = _request()
    gateway = _MemoryGatewaySpy()
    wiring = ProductiveGovernedLearningWiring(gateway)

    result = wiring.execute_certified_write_request(request)

    assert result.outcome is ProductiveGovernedLearningOutcome.REVIEW_REQUIRED
    assert result.writer_call_performed is False
    assert gateway.requests == []


def test_mismatched_execution_authorization_fails_closed_before_writer() -> None:
    request = _request()
    authorization = _authorization(request)
    assert authorization is not None
    mismatched = replace(
        authorization,
        memory_write_request_id="governed-memory-write-request-wrong",
    )
    gateway = _MemoryGatewaySpy()
    wiring = ProductiveGovernedLearningWiring(gateway)

    result = wiring.execute_certified_write_request(request, mismatched)

    assert result.outcome is ProductiveGovernedLearningOutcome.REVIEW_REQUIRED
    assert result.writer_call_performed is False
    assert gateway.requests == []


def test_exact_validation_covers_full_request_writer_lineage() -> None:
    request = _request()
    authorization = _authorization(request)
    assert authorization is not None
    gateway = _MemoryGatewaySpy()
    wiring = ProductiveGovernedLearningWiring(gateway)

    fields = (
        "materialization_proposal_id",
        "idempotency_key",
    )
    for field in fields:
        bad = replace(authorization, **{field: f"wrong-{field}"})
        result = wiring.execute_certified_write_request(request, bad)
        assert result.outcome is ProductiveGovernedLearningOutcome.REVIEW_REQUIRED

    assert gateway.requests == []


def test_new_g7_write_request_cannot_use_legacy_execute_seam() -> None:
    import inspect

    signature = inspect.signature(ProductiveGovernedLearningWiring.execute)
    assert tuple(signature.parameters) == (
        "self",
        "evaluation",
        "response",
        "current_turn_text",
    )
    assert "request" not in signature.parameters
    assert "authorization" not in signature.parameters


def test_certified_request_seam_requires_explicit_authorization_parameter() -> None:
    import inspect

    signature = inspect.signature(
        ProductiveGovernedLearningWiring.execute_certified_write_request
    )
    assert tuple(signature.parameters) == ("self", "request", "authorization")
    assert signature.parameters["authorization"].default is None
