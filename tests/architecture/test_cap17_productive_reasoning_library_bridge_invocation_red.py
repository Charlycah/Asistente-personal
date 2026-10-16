from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from app.governed_explanatory_model_investigation_reentry import (
    GovernedExplanatoryModelInvestigationReentry,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

MODULE = "app.productive_reasoning_local_library_bridge_invocation"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_FACTORY = PROJECT_ROOT / "app/runtime_root_factory.py"
REENTRY_MODULE = (
    PROJECT_ROOT / "app/governed_explanatory_model_investigation_reentry.py"
)


def _module():
    return importlib.import_module(MODULE)


def _contributor_type():
    return _module().GovernedProductiveReasoningLibraryBridgeContributorV1


def test_cap17_productive_invocation_module_exposes_one_thin_contributor() -> None:
    module = _module()
    assert hasattr(module, "GovernedProductiveReasoningLibraryBridgeContributorV1")
    assert hasattr(module, "GovernedProductiveReasoningLibraryInvocationStatus")
    assert hasattr(module, "GovernedProductiveReasoningLibraryInvocationResult")


def test_cap17_productive_invocation_status_contract_is_explicit() -> None:
    values = {
        item.value
        for item in _module().GovernedProductiveReasoningLibraryInvocationStatus
    }
    assert values == {
        "invoked",
        "library_unavailable",
        "no_reasoning_episode",
        "no_investigation_reentry",
        "not_admitted",
        "lineage_mismatch",
    }


def test_cap17_productive_contributor_matches_existing_runtime_port() -> None:
    contributor = _contributor_type()
    signature = inspect.signature(contributor.contribute)
    assert tuple(signature.parameters) == (
        "self",
        "owner",
        "session_id",
        "text",
        "request",
        "now",
    )
    assert getattr(contributor, "name", "") == "local_library_evidence"


def test_cap17_productive_contributor_exposes_auditable_consumption_result() -> None:
    contributor = _contributor_type()
    assert hasattr(contributor, "consume")
    result_type = _module().GovernedProductiveReasoningLibraryInvocationResult
    fields = set(result_type.__dataclass_fields__)
    assert {
        "status",
        "turn_id",
        "reasoning_id",
        "requirement_id",
        "bridge_result",
    } <= fields


def test_cap17_productive_invocation_derives_same_turn_identity_canonically() -> None:
    source = inspect.getsource(_contributor_type())
    assert "build_governed_conversation_turn_identity" in source
    assert "GovernedConversationPipelineRequest" in source
    assert "turn_id" in source


def test_cap17_productive_invocation_reads_exact_productive_reasoning_episode() -> None:
    source = inspect.getsource(_contributor_type())
    assert "productive_episode" in source
    assert "owner=owner" in source
    assert "session_id=session_id" in source
    assert "turn_id=" in source


def test_cap17_productive_invocation_reads_exact_same_turn_reentry() -> None:
    source = inspect.getsource(_contributor_type())
    assert "productive_explanatory_investigation_reentry" in source
    assert "GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED" in source


def test_cap17_productive_invocation_preserves_reasoning_lineage_exactly() -> None:
    source = inspect.getsource(_contributor_type())
    assert "originating_reasoning_id" in source
    assert "episode.result.result_id" in source
    assert "requirement.requirement_id" in source


def test_cap17_productive_invocation_uses_canonical_episode_confidence() -> None:
    source = inspect.getsource(_contributor_type())
    assert "episode.result.decision.confidence_score" in source
    assert "internal_confidence=" in source
    for forbidden in ("internal_confidence=0", "internal_confidence = 0"):
        assert forbidden not in source


def test_cap17_productive_invocation_uses_exact_admitted_requirement() -> None:
    source = inspect.getsource(_contributor_type())
    assert "reentry.requirement" in source
    assert "GovernedCognitiveEvidenceLibraryRequest" in source
    assert "requirement=requirement" in source


def test_cap17_productive_invocation_derives_library_availability_from_wiring() -> None:
    source = inspect.getsource(_contributor_type())
    assert "GovernedLocalLibraryRuntimeProvisionStatus.PROVISIONED" in source
    assert "cognitive_bridge" in source
    assert "library_available=True" not in source


def test_cap17_productive_invocation_dispatches_only_after_admission() -> None:
    source = inspect.getsource(_contributor_type())
    admitted = source.find(
        "GovernedExplanatoryModelInvestigationReentryStatus.ADMITTED"
    )
    dispatch = source.find("cognitive_bridge.handle")
    assert admitted >= 0
    assert dispatch > admitted


def test_cap17_productive_invocation_fail_closed_for_zero_n_or_review() -> None:
    source = inspect.getsource(_contributor_type())
    assert "NO_DISCRIMINATING_INQUIRY" in source
    assert "AMBIGUOUS_INQUIRY" in source
    assert "REVIEW_REQUIRED" in source
    assert "NOT_ADMITTED" in source


def test_cap17_productive_invocation_never_reads_or_selects_library_directly() -> None:
    source = inspect.getsource(_contributor_type())
    for forbidden in (
        ".search(",
        ".read_text(",
        "DocumentReadingService",
        "GovernedLocalLibraryCatalogueV1",
        "GovernedLocalLibraryConversationV1",
        "handle_admitted_request",
    ):
        assert forbidden not in source


def test_cap17_productive_invocation_has_no_hidden_authority() -> None:
    source = Path(_module().__file__).read_text(encoding="utf-8").casefold()
    for forbidden in (
        "memory_gateway",
        "learning",
        "threading",
        "asyncio.create_task",
        "while true",
        "background",
        "d:\\biblioteca",
        "d:/biblioteca",
    ):
        assert forbidden not in source


def test_cap17_runtime_factory_imports_productive_library_contributor() -> None:
    source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    assert "GovernedProductiveReasoningLibraryBridgeContributorV1" in source
    assert "productive_reasoning_local_library_bridge_invocation" in source


def test_cap17_runtime_factory_constructs_contributor_after_library_wiring() -> None:
    source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    wiring = source.index("build_governed_local_library_runtime_from_environment")
    contributor = source.index("GovernedProductiveReasoningLibraryBridgeContributorV1(")
    assert contributor > wiring
    assert "governed_local_library_runtime" in source[wiring : contributor + 500]
    assert "governed_reasoning_runtime" in source[wiring : contributor + 500]


def test_cap17_runtime_factory_injects_existing_cognitive_runtime() -> None:
    source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    assert "CognitiveRuntimeOrchestrator" in source
    assert "GovernedProductiveReasoningLibraryBridgeContributorV1" in source
    assert "cognitive_runtime=" in source


def test_cap17_runtime_factory_does_not_create_library_specific_orchestrator() -> None:
    source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    for forbidden in (
        "LibraryOrchestrator",
        "LibraryEvidencePlanner",
        "LibraryReasoner",
        "LibraryAgent",
        "LibraryIntentRouter",
    ):
        assert forbidden not in source


def test_cap17_productive_invocation_keeps_retrieval_step_schema_unchanged() -> None:
    fields = set(KnowledgeRetrievalStep.__dataclass_fields__)
    assert fields == {"source", "priority", "required", "query", "step_id"}


def test_cap17_existing_reentry_remains_read_only_and_library_free() -> None:
    defaults = GovernedExplanatoryModelInvestigationReentry.__dataclass_fields__
    assert defaults["read_only"].default is True
    assert defaults["invokes_capabilities"].default is False
    assert defaults["acquires_evidence"].default is False
    source = REENTRY_MODULE.read_text(encoding="utf-8")
    assert "cognitive_bridge" not in source
    assert "DocumentReadingService" not in source
