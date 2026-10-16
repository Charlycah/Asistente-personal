from __future__ import annotations

import ast
from pathlib import Path

from app.approved_learning_memory_materialization import ApprovedLearningScope
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanLearningApprovalResponse,
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

from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import (
    _evaluation,
)

ROOT = Path(__file__).resolve().parents[2]


def _runtime(tmp_path: Path) -> MemoryRuntimeIntegration:
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(root_path=tmp_path / "memory")
    )


def _response(evaluation, text="Sí", **changes):
    preference = evaluation.preference_candidate
    assert preference is not None
    values = {
        "approval_request_id": "learning-approval-request-1",
        "evaluation_report_id": evaluation.report_id,
        "learning_candidate_id": evaluation.learning_candidate_id,
        "preference_candidate_id": preference.preference_id,
        "human_response_reference": "conversation:approval-answer",
        "response_text": text,
        "approver": "Carlos",
        "scope": ApprovedLearningScope.PROJECT,
        "exact_linkage": True,
    }
    values.update(changes)
    return ExplicitHumanLearningApprovalResponse(**values)


def test_v1_approved_durable_learning_is_written_once(tmp_path) -> None:
    evaluation = _evaluation()
    response = _response(evaluation)
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos")
    wiring = ProductiveGovernedLearningWiring(gateway)

    first = wiring.execute(evaluation, response, current_turn_text="Sí")
    second = wiring.execute(evaluation, response, current_turn_text="Sí")

    assert first.outcome is ProductiveGovernedLearningOutcome.STORED
    assert second.outcome is ProductiveGovernedLearningOutcome.ALREADY_STORED
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
    assert record.category is LearningCategory.USER_PREFERENCE
    assert record.metadata["approval_scope"] == "project"
    assert record.metadata["approver"] == "Carlos"
    assert record.metadata["human_response_reference"] == (
        "conversation:approval-answer"
    )


def test_v1_rejected_learning_never_calls_memory_writer(tmp_path) -> None:
    evaluation = _evaluation()
    runtime = _runtime(tmp_path)
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )

    result = wiring.execute(
        evaluation,
        _response(evaluation, "No"),
        current_turn_text="No",
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.REJECTED
    assert result.writer_call_performed is False
    assert result.write_request is None
    assert runtime.count(owner="Carlos") == 0


def test_v1_current_turn_mismatch_abstains_before_approval(tmp_path) -> None:
    evaluation = _evaluation()
    runtime = _runtime(tmp_path)
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )

    result = wiring.execute(
        evaluation,
        _response(evaluation, "Sí"),
        current_turn_text="No",
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.ABSTAIN
    assert result.approval is None
    assert result.writer_call_performed is False
    assert runtime.count(owner="Carlos") == 0


def test_v1_session_scope_never_materializes_durable_memory(tmp_path) -> None:
    evaluation = _evaluation()
    runtime = _runtime(tmp_path)
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )

    result = wiring.execute(
        evaluation,
        _response(evaluation, scope=ApprovedLearningScope.SESSION),
        current_turn_text="Sí",
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.REVIEW_REQUIRED
    assert result.writer_call_performed is False
    assert result.write_request is None
    assert runtime.count(owner="Carlos") == 0


def test_v1_missing_memory_gateway_fails_closed_without_queue() -> None:
    evaluation = _evaluation()
    wiring = ProductiveGovernedLearningWiring(None)

    result = wiring.execute(
        evaluation,
        _response(evaluation),
        current_turn_text="Sí",
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.MEMORY_UNAVAILABLE
    assert result.writer_call_performed is False
    assert result.write_request is not None


def test_v1_writer_failure_is_contained_and_does_not_raise() -> None:
    class FailingWriter:
        def remember_governed_learning(self, request):
            raise RuntimeError("write failed")

    evaluation = _evaluation()
    result = ProductiveGovernedLearningWiring(FailingWriter()).execute(
        evaluation,
        _response(evaluation),
        current_turn_text="Sí",
    )

    assert result.outcome is ProductiveGovernedLearningOutcome.WRITE_FAILED
    assert result.writer_call_performed is False
    assert result.write_request is not None


def test_v1_runtime_root_uses_one_memory_gateway_instance_for_both_roles() -> None:
    source = (ROOT / "app" / "runtime_root_factory.py").read_text(encoding="utf-8")
    assert "official_memory_gateway = (" in source
    assert "interceptor=official_memory_gateway" in source
    assert (
        "governed_learning_memory_gateway=official_memory_gateway"
        in source
    )
    assert source.count("OfficialMemoryGateway(") == 1


def test_v1_official_composition_injects_memory_without_registry_lookup() -> None:
    source = (
        ROOT / "app" / "official_runtime_composition.py"
    ).read_text(encoding="utf-8")
    assert '"governed_learning_memory_gateway"' in source
    assert "governed_learning_memory_gateway=memory_gateway" in source


def test_v1_gateway_keeps_constructor_backward_compatible_and_one_core() -> None:
    source = (
        ROOT / "app" / "official_conversation_gateway.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    constructors = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert constructors == [52]
    assert "governed_learning_memory_gateway=None" in source
    assert "learning_approval_evaluation=None" in source
    assert "learning_approval_response=None" in source


def test_v1_wiring_has_no_registry_store_background_or_new_authority() -> None:
    source = (
        ROOT / "app" / "productive_governed_learning_wiring.py"
    ).read_text(encoding="utf-8")
    prohibited = (
        "OfficialRuntimeCapabilityRegistry",
        "CognitiveMemoryStore",
        "threading",
        "asyncio",
        "subprocess",
        "class LearningAuthority",
        "class MemoryAuthority",
        "class CuriosityAuthority",
    )
    assert all(item not in source for item in prohibited)
