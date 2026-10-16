from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

MODULE = "app.governed_local_evidence_reasoning_reentry"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PRODUCTIVE_MODULE = (
    PROJECT_ROOT / "app/productive_reasoning_local_library_bridge_invocation.py"
)
RUNTIME_FACTORY = PROJECT_ROOT / "app/runtime_root_factory.py"
LEVEL2_REENTRY = PROJECT_ROOT / "app/governed_level2_reasoning_reentry.py"


def _module():
    return importlib.import_module(MODULE)


def _adapter_type():
    return _module().GovernedLocalEvidenceReasoningReentryV1


def test_cap17_local_evidence_reentry_exposes_one_instrumental_adapter() -> None:
    module = _module()
    assert hasattr(module, "GovernedLocalEvidenceReasoningReentryV1")
    assert hasattr(module, "GovernedLocalEvidenceReasoningReentryRequest")
    assert hasattr(module, "GovernedLocalEvidenceReasoningReentryResult")
    assert hasattr(module, "GovernedLocalEvidenceReasoningReentryStatus")


def test_cap17_local_evidence_reentry_status_contract_is_explicit() -> None:
    status_type = _module().GovernedLocalEvidenceReasoningReentryStatus
    values = {item.value for item in status_type}
    assert values == {
        "reevaluated",
        "not_eligible",
        "already_consumed",
        "review_required",
        "lineage_mismatch",
    }


def test_cap17_local_evidence_reentry_request_preserves_original_lineage() -> None:
    request_type = _module().GovernedLocalEvidenceReasoningReentryRequest
    fields = set(request_type.__dataclass_fields__)
    assert {
        "owner",
        "turn_id",
        "originating_reasoning_id",
        "requirement",
        "episode_id",
        "bridge_result",
    } <= fields


def test_cap17_local_evidence_reentry_result_is_auditable() -> None:
    result_type = _module().GovernedLocalEvidenceReasoningReentryResult
    fields = set(result_type.__dataclass_fields__)
    assert {
        "reentry_id",
        "status",
        "owner",
        "turn_id",
        "originating_reasoning_id",
        "requirement_id",
        "episode_id",
        "source_decision_id",
        "knowledge_execution_id",
        "selected_source_reference",
        "evidence_id",
        "reasoning_result",
        "rationale_codes",
        "source_fingerprint",
    } <= fields


def test_cap17_local_evidence_reentry_uses_existing_reasoning_gateway_only() -> None:
    source = inspect.getsource(_adapter_type())
    assert "reasoning_gateway" in source
    assert ".orchestrator.context_assembler.evidence_registry" in source
    assert "register_reference" in source
    assert "reasoning_gateway.reason" in source


def test_cap17_local_evidence_reentry_accepts_only_completed_local_artifact() -> None:
    source = inspect.getsource(_adapter_type())
    assert (
        "GovernedCognitiveEvidenceLibraryBridgeStatus.LOCAL_LIBRARY_PROPOSED"
        in source
    )
    assert "GovernedRobyInitiatedLibraryAccessStatus.COMPLETED" in source
    assert "GovernedLocalLibraryConversationStatus.COMPLETED" in source
    assert "KnowledgeSourceKind.LOCAL_DOCUMENTS" in source
    assert "artifact" in source
    assert "execution" in source


def test_cap17_local_evidence_reentry_preserves_original_requirement_lineage() -> None:
    source = inspect.getsource(_adapter_type())
    assert "request.requirement.requirement_id" in source
    assert "request.originating_reasoning_id" in source
    assert "request.episode_id" in source
    assert "request.requirement.source_reference" in source
    assert "request.requirement.world_snapshot_id" in source
    assert "source_decision.decision_id" in source


def test_cap17_local_evidence_reentry_rejects_direct_authorization_requirement_lineage(
) -> None:
    source = inspect.getsource(_adapter_type())
    assert "discrimination-requirement-direct-" not in source
    assert "evidence-acquisition-plan-direct-" not in source
    assert "request.requirement.requirement_id" in source


def test_cap17_local_evidence_reentry_registers_knowledge_observation_not_truth(
) -> None:
    source = inspect.getsource(_adapter_type())
    assert "EvidenceSourceType.KNOWLEDGE" in source
    assert "EvidenceKind.OBSERVATION" in source
    assert "EvidenceSensitivity.PERSONAL" in source
    assert '"epistemic_role", "local_document_evidence_not_truth"' in source


def test_cap17_local_evidence_reentry_metadata_preserves_acquisition_provenance(
) -> None:
    source = inspect.getsource(_adapter_type())
    for token in (
        "originating_reasoning_id",
        "requirement_id",
        "episode_id",
        "source_decision_id",
        "knowledge_execution_id",
        "selected_source_reference",
        "world_snapshot_id",
        "knowledge_source",
    ):
        assert token in source


def test_cap17_local_evidence_reentry_fingerprint_is_deterministic() -> None:
    source = inspect.getsource(_adapter_type())
    assert "sha256" in source
    assert "execution.execution_id" in source
    assert "artifact.content" in source
    assert "selected_source_reference" in source


def test_cap17_local_evidence_reentry_summary_is_bounded() -> None:
    source = inspect.getsource(_adapter_type())
    assert "artifact.content" in source
    assert "_MAX_SUMMARY_CHARS" in source
    assert "summary" in source


def test_cap17_local_evidence_reentry_performs_exactly_one_reasoning_reevaluation(
) -> None:
    source = inspect.getsource(_adapter_type())
    assert "ReasoningQuery" in source
    assert "evidence_ids=(reference.evidence_id,)" in source
    assert source.count("reasoning_gateway.reason(") == 1


def test_cap17_local_evidence_reentry_is_idempotent_by_knowledge_execution() -> None:
    source = inspect.getsource(_adapter_type())
    assert "_consumed_execution_ids" in source
    assert "execution.execution_id" in source
    assert "ALREADY_CONSUMED" in source


def test_cap17_local_evidence_reentry_never_retrieves_or_selects_again() -> None:
    source = Path(_module().__file__).read_text(encoding="utf-8")
    for forbidden in (
        ".search(",
        ".read_text(",
        "DocumentReadingService",
        "GovernedLocalLibraryCatalogueV1",
        "GovernedLocalLibraryConversationV1",
        "OfficialUnifiedRetrievalExecutionRuntimeGateway",
        "BoundGovernedLocalDocumentRetrieverV1",
    ):
        assert forbidden not in source


def test_cap17_local_evidence_reentry_does_not_fake_level2_acquisition() -> None:
    source = Path(_module().__file__).read_text(encoding="utf-8")
    assert "GovernedAcquiredEvidenceEnvelope" not in source
    assert "OfficialCapabilityGateway" not in source
    assert "EvidenceSourceType.LEVEL2_ACQUIRED" not in source


def test_cap17_productive_contributor_chains_completed_bridge_to_reasoning_reentry(
) -> None:
    source = PRODUCTIVE_MODULE.read_text(encoding="utf-8")
    assert "GovernedLocalEvidenceReasoningReentryV1" in source
    assert "GovernedLocalEvidenceReasoningReentryRequest" in source
    assert "reasoning_reentry.reenter" in source
    assert "reasoning_reentry" in source


def test_cap17_runtime_factory_composes_existing_reasoning_reentry_adapter() -> None:
    source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    assert "GovernedLocalEvidenceReasoningReentryV1" in source
    assert "reasoning_gateway=governed_reasoning_runtime" in source
    assert "reasoning_reentry=" in source


def test_cap17_local_evidence_reentry_has_no_hidden_authority() -> None:
    # Guardrail remains green before production implementation.
    source = PRODUCTIVE_MODULE.read_text(encoding="utf-8").casefold()
    for forbidden in (
        "memory_gateway",
        "learning",
        "threading",
        "asyncio.create_task",
        "while true",
        "background",
    ):
        assert forbidden not in source


def test_cap17_local_evidence_reentry_keeps_retrieval_step_schema_unchanged() -> None:
    fields = set(KnowledgeRetrievalStep.__dataclass_fields__)
    assert fields == {"source", "priority", "required", "query", "step_id"}


def test_cap17_local_evidence_reentry_does_not_modify_level2_reentry_contract() -> None:
    # The historical Level-2 lane must remain a separate acquisition provenance.
    source = LEVEL2_REENTRY.read_text(encoding="utf-8")
    assert "GovernedAcquiredEvidenceEnvelope" in source
    assert "EvidenceSourceType.LEVEL2_ACQUIRED" in source
    assert "OfficialUnifiedRetrievalExecutionRuntimeGateway" not in source
