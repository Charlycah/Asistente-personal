from __future__ import annotations

import importlib
import inspect
from types import SimpleNamespace

import app.runtime_ui_adapter as runtime_ui_adapter
from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    AuthorizedGovernedMemoryWriteExecutionEvidence,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.official_runtime_composition import OfficialROBYRuntime
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring
from app.runtime_ui_adapter import LocalConversationUIAdapter

_g8_contract = importlib.import_module(
    "tests.architecture."
    "test_intel_g8_source_neutral_materialization_to_existing_"
    "memory_write_adapter_contract_red"
)
_g8_proposal = _g8_contract._g8_proposal


def _request():
    return GovernedMemoryWriteAdapterFoundation().adapt(_g8_proposal())


def _official_runtime_with_wiring(wiring):
    runtime = OfficialROBYRuntime.__new__(OfficialROBYRuntime)
    runtime.composition = SimpleNamespace(
        productive_governed_learning_wiring=wiring,
    )
    return runtime


def test_official_runtime_transports_raw_explicit_response_to_existing_m369() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()
    wiring.retain_pending_governed_memory_write_request("session-a", request)
    runtime = _official_runtime_with_wiring(wiring)

    authorization = (
        runtime.evaluate_pending_governed_memory_write_conversational_response(
            session_id="session-a",
            response_text="Sí, guardar ahora",
            human_response_reference="conversation:test:session-a:response-1",
            approver="Carlos",
        )
    )

    assert isinstance(
        authorization,
        AuthorizedGovernedMemoryWriteExecutionEvidence,
    )
    assert authorization.memory_write_request_id == request.request_id
    assert authorization.human_response_reference == (
        "conversation:test:session-a:response-1"
    )
    assert authorization.approver == "Carlos"
    assert authorization.read_only is True
    assert authorization.write_performed is False


def test_official_runtime_transport_fails_closed_without_exact_pending_request(
) -> None:
    runtime = _official_runtime_with_wiring(ProductiveGovernedLearningWiring(None))

    authorization = (
        runtime.evaluate_pending_governed_memory_write_conversational_response(
            session_id="session-missing",
            response_text="Sí, guardar ahora",
            human_response_reference="conversation:test:missing:response-1",
            approver="Carlos",
        )
    )

    assert authorization is None


def test_generic_affirmation_remains_rejected_by_existing_m369_authority() -> None:
    wiring = ProductiveGovernedLearningWiring(None)
    request = _request()
    wiring.retain_pending_governed_memory_write_request("session-a", request)
    runtime = _official_runtime_with_wiring(wiring)

    for text in ("sí", "dale", "me parece bien"):
        authorization = (
            runtime.evaluate_pending_governed_memory_write_conversational_response(
                session_id="session-a",
                response_text=text,
                human_response_reference=f"conversation:test:{text}",
                approver="Carlos",
            )
        )
        assert authorization is None


class _FakeBrain:
    def __init__(self, runtime) -> None:
        self.runtime = runtime
        self.received = []

    @property
    def diagnostics(self):
        return None

    def process(self, message, *, origin, session_id, now=None):
        self.received.append((message, origin, session_id))
        return SimpleNamespace(
            status=SimpleNamespace(value="completed"),
            response_text="respuesta normal",
            session_id=session_id,
        )


def _dummy_gateway():
    return OfficialConversationGateway.__new__(OfficialConversationGateway)


def test_ui_adapter_only_offers_raw_text_when_pending_request_exists(
    monkeypatch,
) -> None:
    monkeypatch.setattr(runtime_ui_adapter, "UnifiedBrain", _FakeBrain)
    calls = []

    def reader(session_id: str) -> bool:
        return session_id == "session-a"

    evidence = object()

    def evaluator(**kwargs):
        calls.append(kwargs)
        return evidence

    adapter = LocalConversationUIAdapter(
        _dummy_gateway(),
        pending_memory_write_reader=reader,
        pending_memory_write_response_evaluator=evaluator,
    )

    response = adapter.submit_text(
        "  Sí, guardar ahora  ",
        session_id="session-a",
    )

    assert response.text == "respuesta normal"
    assert len(calls) == 1
    assert calls[0]["session_id"] == "session-a"
    assert calls[0]["response_text"] == "Sí, guardar ahora"
    assert calls[0]["human_response_reference"].startswith(
        "conversation:desktop_text:session-a:"
    )
    assert adapter.last_memory_write_execution_authorization is evidence

    adapter.submit_text("dale", session_id="session-b")
    assert len(calls) == 1
    assert adapter.last_memory_write_execution_authorization is None


def test_ui_adapter_transport_contains_no_memory_authorization_parser() -> None:
    source = inspect.getsource(LocalConversationUIAdapter)

    assert "_AFFIRMATIVE_RE" not in source
    assert "guardar ahora" not in source.casefold()
    assert "execute_authorized_governed_memory_write(" not in source
    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source


def test_official_runtime_transport_stops_before_productive_reentry() -> None:
    source = inspect.getsource(
        OfficialROBYRuntime.
        evaluate_pending_governed_memory_write_conversational_response
    )

    assert "evaluate_pending_governed_memory_write_execution_authorization" in source
    assert "execute_authorized_governed_memory_write(" not in source
    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source


def test_desktop_bootstrap_binds_same_official_runtime_without_gateway_surgery(
) -> None:
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app/desktop_bootstrap.py"
    ).read_text(encoding="utf-8")

    assert "official_runtime = build_official_runtime_from_environment(" in source
    assert "runtime = official_runtime.conversation" in source
    assert "LocalConversationUIAdapter(runtime)" in source
    assert "official_runtime.has_pending_governed_memory_write" in source
    assert (
        "evaluate_pending_governed_memory_write_conversational_response"
        in source
    )
