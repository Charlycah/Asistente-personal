from __future__ import annotations

import importlib
import inspect
from dataclasses import replace
from types import SimpleNamespace

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
)
from app.official_runtime_composition import OfficialROBYRuntime
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)

_g8_contract = importlib.import_module(
    "tests.architecture."
    "test_intel_g8_source_neutral_materialization_to_existing_"
    "memory_write_adapter_contract_red"
)
_g8_proposal = _g8_contract._g8_proposal


class _MemoryGateway:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.requests = []

    def remember_governed_learning(self, request):
        self.requests.append(request)
        if self.fail:
            raise RuntimeError("writer unavailable")
        return SimpleNamespace(
            stored_count=1,
            stored_memory_ids=("memory-1",),
        )


def _request():
    return GovernedMemoryWriteAdapterFoundation().adapt(_g8_proposal())


def _runtime(wiring):
    runtime = OfficialROBYRuntime.__new__(OfficialROBYRuntime)
    runtime.composition = SimpleNamespace(
        productive_governed_learning_wiring=wiring,
    )
    return runtime


def _authorization(wiring, request, session_id="session-a"):
    wiring.retain_pending_governed_memory_write_request(session_id, request)
    response = ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse(
        authorization_request_id="auth-request-1",
        memory_write_request_id=request.request_id,
        human_response_reference="conversation:test:response-1",
        response_text="Sí, guardar ahora",
        approver="Carlos",
        exact_linkage=True,
    )
    return wiring.evaluate_pending_governed_memory_write_execution_authorization(
        session_id,
        response,
    )


def test_exact_pending_authorized_reentry_stores_and_consumes_pending() -> None:
    gateway = _MemoryGateway()
    wiring = ProductiveGovernedLearningWiring(gateway)
    request = _request()
    authorization = _authorization(wiring, request)
    runtime = _runtime(wiring)

    result = runtime.execute_pending_authorized_governed_memory_write(
        session_id="session-a",
        authorization=authorization,
    )

    assert result is not None
    assert result.outcome is ProductiveGovernedLearningOutcome.STORED
    assert result.writer_call_performed is True
    assert gateway.requests == [request]
    assert wiring.pending_governed_memory_write_request("session-a") is None


def test_mismatched_authorization_does_not_write_or_consume_pending() -> None:
    gateway = _MemoryGateway()
    wiring = ProductiveGovernedLearningWiring(gateway)
    request_a = _request()
    authorization = _authorization(wiring, request_a, "session-a")
    request_b = replace(
        _request(),
        request_id="governed-memory-write-request-mismatched",
    )
    wiring.retain_pending_governed_memory_write_request("session-b", request_b)
    runtime = _runtime(wiring)

    result = runtime.execute_pending_authorized_governed_memory_write(
        session_id="session-b",
        authorization=authorization,
    )

    assert result is not None
    assert result.outcome is ProductiveGovernedLearningOutcome.REVIEW_REQUIRED
    assert result.writer_call_performed is False
    assert gateway.requests == []
    assert (
        wiring.pending_governed_memory_write_request("session-b")
        is request_b
    )


def test_writer_failure_retains_exact_pending_request() -> None:
    gateway = _MemoryGateway(fail=True)
    wiring = ProductiveGovernedLearningWiring(gateway)
    request = _request()
    authorization = _authorization(wiring, request)
    runtime = _runtime(wiring)

    result = runtime.execute_pending_authorized_governed_memory_write(
        session_id="session-a",
        authorization=authorization,
    )

    assert result is not None
    assert result.outcome is ProductiveGovernedLearningOutcome.WRITE_FAILED
    assert result.writer_call_performed is False
    assert wiring.pending_governed_memory_write_request("session-a") is request


def test_missing_pending_request_fails_closed_without_writer() -> None:
    gateway = _MemoryGateway()
    wiring = ProductiveGovernedLearningWiring(gateway)
    request = _request()
    authorization = _authorization(wiring, request)
    wiring.consume_pending_governed_memory_write_request("session-a", request)
    runtime = _runtime(wiring)

    result = runtime.execute_pending_authorized_governed_memory_write(
        session_id="session-a",
        authorization=authorization,
    )

    assert result is None
    assert gateway.requests == []


def test_consume_requires_exact_pending_request_lineage() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request_a = _request()
    request_b = replace(
        _request(),
        request_id="governed-memory-write-request-mismatched",
    )
    wiring.retain_pending_governed_memory_write_request("session-a", request_a)

    assert (
        wiring.consume_pending_governed_memory_write_request(
            "session-a",
            request_b,
        )
        is False
    )
    assert wiring.pending_governed_memory_write_request("session-a") is request_a
    assert (
        wiring.consume_pending_governed_memory_write_request(
            "session-a",
            request_a,
        )
        is True
    )
    assert wiring.pending_governed_memory_write_request("session-a") is None


def test_official_runtime_execution_reuses_existing_reentry_only() -> None:
    source = inspect.getsource(
        OfficialROBYRuntime.execute_pending_authorized_governed_memory_write
    )

    assert "execute_authorized_governed_memory_write(" in source
    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source
    assert "_memory_write_authorization_matches" not in source


def test_ui_transport_still_stops_before_execution() -> None:
    from app.runtime_ui_adapter import LocalConversationUIAdapter

    source = inspect.getsource(LocalConversationUIAdapter)

    assert "execute_pending_authorized_governed_memory_write(" not in source
    assert "execute_authorized_governed_memory_write(" not in source
    assert "remember_governed_learning(" not in source
