from __future__ import annotations

import ast
import importlib
from pathlib import Path

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from app.memory_consolidation import OfficialMemoryGateway
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)
from core.cognitive_memory import LearningCategory
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

_g8_contract = importlib.import_module(
    __package__
    + (
        ".test_intel_g8_source_neutral_materialization_to_existing_memory_"
        "write_adapter_contract_red"
    )
)
_g8_proposal = _g8_contract._g8_proposal

ROOT = Path(__file__).resolve().parents[2]


def _runtime(tmp_path: Path) -> MemoryRuntimeIntegration:
    return MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=tmp_path / "memory"))


def _source_neutral_write_request():
    return GovernedMemoryWriteAdapterFoundation().adapt(_g8_proposal())


def _execution_authorization(request):
    response = ExplicitHumanGovernedMemoryWriteExecutionAuthorizationResponse(
        authorization_request_id="g9-memory-write-execution-auth-request",
        memory_write_request_id=request.request_id,
        human_response_reference="test:g9-execution-authorization",
        response_text="Sí, guardar ahora",
        approver="Carlos",
        exact_linkage=True,
    )
    return (
        M369ExplicitHumanLearningApprovalEvidenceFoundation()
        .evaluate_governed_memory_write_execution_authorization(request, response)
    )


def test_source_neutral_certified_write_request_reaches_existing_gateway_once(
    tmp_path: Path,
) -> None:
    request = _source_neutral_write_request()
    runtime = _runtime(tmp_path)
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )

    authorization = _execution_authorization(request)
    first = wiring.execute_certified_write_request(request, authorization)
    second = wiring.execute_certified_write_request(request, authorization)

    assert first.outcome is ProductiveGovernedLearningOutcome.STORED
    assert second.outcome is ProductiveGovernedLearningOutcome.ALREADY_STORED
    assert first.write_request is request
    assert second.write_request is request
    assert first.writer_call_performed is True
    assert second.writer_call_performed is True
    assert runtime.count(owner="Carlos") == 1

    records = runtime.private_store("Carlos").search(
        __import__(
            "core.cognitive_memory_store",
            fromlist=["CognitiveMemorySearch"],
        ).CognitiveMemorySearch(limit=10)
    )
    record = records[0]
    assert record.category is LearningCategory.STABLE_KNOWLEDGE
    assert (
        record.metadata["policy_candidate_id"]
        == request.memory_item.metadata["policy_candidate_id"]
    )
    assert "preference_candidate_id" not in record.metadata
    assert "learning_kind" not in record.metadata


def test_source_neutral_certified_write_request_missing_gateway_fails_closed() -> None:
    request = _source_neutral_write_request()

    authorization = _execution_authorization(request)
    result = ProductiveGovernedLearningWiring(None).execute_certified_write_request(
        request, authorization
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE
    assert result.write_request is request
    assert result.writer_call_performed is False


def test_source_neutral_certified_write_request_writer_failure_is_contained() -> None:
    class FailingWriter:
        def remember_governed_learning(self, request):
            raise RuntimeError("write failed")

    request = _source_neutral_write_request()
    result = ProductiveGovernedLearningWiring(
        FailingWriter()
    ).execute_certified_write_request(request, _execution_authorization(request))

    assert result.outcome is ProductiveGovernedLearningOutcome.WRITE_FAILED
    assert result.write_request is request
    assert result.writer_call_performed is False


def test_source_neutral_productive_reachability_reuses_one_existing_authority() -> None:
    source_path = ROOT / "app" / "productive_governed_learning_wiring.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    classes = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    assert "ProductiveGovernedLearningWiring" in classes
    assert "SourceNeutralProductiveGovernedLearningWiring" not in classes
    assert "SourceNeutralMemoryWriter" not in classes
    assert "G8MemoryGateway" not in classes
    assert "OfficialMemoryGateway(" not in source
    assert "PreferenceCandidate(" not in source
    assert "CuriosityLearningKind.PREFERENCE" not in source
