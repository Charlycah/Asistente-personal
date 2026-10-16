from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningResult,
)

_g9_contract = importlib.import_module(
    __package__
    + (
        ".test_intel_g9_source_neutral_write_request_productive_"
        "reachability_contract_red"
    )
)
_source_neutral_write_request = _g9_contract._source_neutral_write_request

ROOT = Path(__file__).resolve().parents[2]


class _Turn:
    session_id = "runtime-session"


class _RuntimeStub:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str) -> _Turn:
        return _Turn()


class _CertifiedRequestWiringSpy:
    def __init__(self) -> None:
        self.requests = []

    def execute_certified_write_request(self, request):
        self.requests.append(request)
        return ProductiveGovernedLearningResult(
            outcome=ProductiveGovernedLearningOutcome.STORED,
            rationale_codes=("governed_learning_written_once",),
            write_request=request,
            stored_memory_ids=("memory:g10",),
            writer_call_performed=True,
        )


def test_g10_submit_exposes_explicit_certified_write_request_seam() -> None:
    signature = inspect.signature(OfficialConversationGateway.submit)

    parameter = signature.parameters["governed_memory_write_request"]
    assert parameter.default is None
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY


def test_g10_submit_routes_certified_request_to_existing_productive_wiring() -> None:
    request = _source_neutral_write_request()
    gateway = OfficialConversationGateway(_RuntimeStub())
    spy = _CertifiedRequestWiringSpy()
    gateway._productive_governed_learning_wiring = spy

    turn = gateway.submit(
        "confirmación de aprendizaje gobernado",
        session_id="g10-source-neutral",
        governed_memory_write_request=request,
    )

    assert spy.requests == [request]
    assert turn.response_path == "interceptor"
    assert turn.provider_call_performed is False
    assert turn.retrieval_performed is False
    assert turn.network_access_performed is False
    assert request.request_id in turn.pipeline_result_id


def test_g10_source_neutral_turn_does_not_fabricate_preference_semantics() -> None:
    request = _source_neutral_write_request()
    result = ProductiveGovernedLearningResult(
        outcome=ProductiveGovernedLearningOutcome.STORED,
        rationale_codes=("governed_learning_written_once",),
        write_request=request,
        stored_memory_ids=("memory:g10",),
        writer_call_performed=True,
    )
    gateway = object.__new__(OfficialConversationGateway)
    gateway._runtime = _RuntimeStub()
    gateway._submitted_turns = 0

    turn = gateway._governed_learning_turn(
        "confirmación",
        result,
        session_id="g10-source-neutral",
        now=None,
    )

    assert "preferencia" not in turn.response_text.casefold()
    assert "memoria oficial" in turn.response_text.casefold()


def test_g10_reuses_existing_gateway_wiring_and_memory_authority_only() -> None:
    source_path = ROOT / "app" / "official_conversation_gateway.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    assert "OfficialConversationGateway" in classes
    assert "SourceNeutralOfficialConversationGateway" not in classes
    assert "SourceNeutralProductiveGovernedLearningWiring" not in classes
    assert "SourceNeutralMemoryGateway" not in classes
    assert "OfficialMemoryGateway(" not in source
    assert "PreferenceCandidate(" not in source
    assert "CuriosityLearningKind.PREFERENCE" not in source


def test_g10_submit_does_not_reopen_certification_pipeline() -> None:
    source = inspect.getsource(OfficialConversationGateway.submit)

    prohibited = (
        "GovernedMemoryWriteAdapterFoundation(",
        "GovernedG7ApprovedLearningMemoryMaterialization",
        "GovernedMemoryMaterializationProposal",
        "PreferenceCandidate(",
        "CuriosityLearningKind.PREFERENCE",
    )
    assert all(item not in source for item in prohibited)
