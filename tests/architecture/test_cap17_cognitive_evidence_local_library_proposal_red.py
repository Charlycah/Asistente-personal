from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)
from core.knowledge_source_policy import KnowledgeSourceKind

NOW = datetime(2026, 9, 1, 14, 0, tzinfo=timezone.utc)


def _bridge_module():
    return importlib.import_module("app.cognitive_evidence_local_library_bridge")


def _requirement() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-cap17-cognitive-library",
        hypothesis_ids=("hypothesis-a", "hypothesis-b"),
        source_reference="reasoning:case-17",
        world_snapshot_id="world-snapshot-17",
        known_elements=("known context",),
        missing_evidence_descriptions=(
            "historial documentado del proyecto Atlas",
            "fecha de la decisión de arquitectura",
        ),
        evidence_codes=("evidence-missing",),
    )


def test_cap17_cognitive_bridge_module_exposes_one_instrumental_bridge() -> None:
    module = _bridge_module()
    assert hasattr(module, "GovernedCognitiveEvidenceToLocalLibraryBridgeV1")
    assert hasattr(module, "GovernedCognitiveEvidenceLibraryRequest")
    assert hasattr(module, "GovernedCognitiveEvidenceLibraryProposal")
    assert hasattr(module, "GovernedCognitiveEvidenceLibraryResult")
    assert hasattr(module, "GovernedCognitiveEvidenceLibraryBridgeStatus")


def test_cap17_cognitive_bridge_status_contract_is_explicit() -> None:
    module = _bridge_module()
    values = {
        item.value for item in module.GovernedCognitiveEvidenceLibraryBridgeStatus
    }
    assert values == {
        "local_library_proposed",
        "internal_sufficient",
        "external_required",
        "verification_required",
        "withheld",
        "not_applicable",
        "library_unavailable",
    }


def test_cap17_knowledge_runtime_has_structured_evidence_requirement_entry() -> None:
    gateway = OfficialKnowledgeRuntimeGateway()
    assert hasattr(gateway, "assess_evidence_requirement")
    signature = inspect.signature(gateway.assess_evidence_requirement)
    assert tuple(signature.parameters) == (
        "requirement",
        "internal_confidence",
        "local_documents_available",
    )


def test_cap17_structured_requirement_assessment_preserves_semantic_query() -> None:
    assessment = OfficialKnowledgeRuntimeGateway().assess_evidence_requirement(
        _requirement(),
        internal_confidence=0.25,
        local_documents_available=True,
    )
    assert assessment.query == (
        "historial documentado del proyecto Atlas; fecha de la decisión de arquitectura"
    )
    assert assessment.need.query == assessment.query


def test_cap17_structured_requirement_prefers_local_documents_when_available() -> None:
    assessment = OfficialKnowledgeRuntimeGateway().assess_evidence_requirement(
        _requirement(),
        internal_confidence=0.25,
        local_documents_available=True,
    )
    assert assessment.need.local_documents_available is True
    assert assessment.need.preferred_sources == (KnowledgeSourceKind.LOCAL_DOCUMENTS,)
    assert assessment.need.internal_confidence == 0.25
    assert assessment.need.explicit_external_request is False


def test_cap17_structured_requirement_does_not_fake_conversational_markers() -> None:
    source = inspect.getsource(
        OfficialKnowledgeRuntimeGateway.assess_evidence_requirement
    )
    assert "biblioteca" not in source.casefold()
    assert "mis libros" not in source.casefold()
    assert ".assess(" not in source


def test_cap17_bridge_request_preserves_reasoning_lineage() -> None:
    module = _bridge_module()
    request = module.GovernedCognitiveEvidenceLibraryRequest(
        owner="Carlos",
        requirement=_requirement(),
        internal_confidence=0.25,
        library_available=True,
    )
    assert request.requirement.source_reference == "reasoning:case-17"
    assert request.requirement.world_snapshot_id == "world-snapshot-17"
    assert request.requirement.requirement_id.startswith("discrimination-requirement-")


def test_cap17_bridge_request_rejects_invalid_confidence() -> None:
    module = _bridge_module()
    with pytest.raises(ValueError, match="confidence"):
        module.GovernedCognitiveEvidenceLibraryRequest(
            owner="Carlos",
            requirement=_requirement(),
            internal_confidence=1.1,
            library_available=True,
        )


def test_cap17_local_proposal_preserves_source_and_world_snapshot_lineage() -> None:
    module = _bridge_module()
    fields = set(module.GovernedCognitiveEvidenceLibraryProposal.__dataclass_fields__)
    assert {
        "owner",
        "search_query",
        "reason",
        "source_reference",
        "world_snapshot_id",
        "requirement_id",
        "source_decision_id",
    } <= fields


def test_cap17_bridge_uses_canonical_knowledge_source_policy() -> None:
    source = inspect.getsource(
        _bridge_module().GovernedCognitiveEvidenceToLocalLibraryBridgeV1
    )
    assert "KnowledgeSourcePolicy" in source
    assert "KnowledgeSourcePolicyRequest" in source
    assert "KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED" in source


def test_cap17_bridge_only_dispatches_after_local_source_preferred() -> None:
    source = inspect.getsource(
        _bridge_module().GovernedCognitiveEvidenceToLocalLibraryBridgeV1
    )
    local_check = source.find("KnowledgeSourceStatus.LOCAL_SOURCE_PREFERRED")
    dispatch = source.find("handle_proposal")
    assert local_check >= 0
    assert dispatch > local_check


def test_cap17_bridge_does_not_search_or_read_library_directly() -> None:
    source = inspect.getsource(
        _bridge_module().GovernedCognitiveEvidenceToLocalLibraryBridgeV1
    )
    assert ".search(" not in source
    assert ".read_text(" not in source
    assert "DocumentReadingService" not in source
    assert "GovernedLocalLibraryCatalogueV1" not in source


def test_cap17_bridge_has_no_memory_learning_or_background_authority() -> None:
    source = Path(_bridge_module().__file__).read_text(encoding="utf-8").casefold()
    for forbidden in (
        "memory_gateway",
        "learning",
        "threading",
        "asyncio.create_task",
        "while true",
        "background",
    ):
        assert forbidden not in source


def test_cap17_conversation_exposes_neutral_admitted_request_path() -> None:
    from app.governed_local_library_conversation import (
        GovernedLocalLibraryConversationV1,
    )

    assert hasattr(GovernedLocalLibraryConversationV1, "handle_admitted_request")
    signature = inspect.signature(
        GovernedLocalLibraryConversationV1.handle_admitted_request
    )
    assert tuple(signature.parameters) == (
        "self",
        "owner",
        "search_query",
        "now",
    )


def test_cap17_user_request_converges_through_neutral_admitted_path() -> None:
    from app.governed_local_library_conversation import (
        GovernedLocalLibraryConversationV1,
    )

    source = inspect.getsource(GovernedLocalLibraryConversationV1.handle_user_request)
    assert "handle_admitted_request" in source


def test_cap17_roby_initiated_path_no_longer_fakes_human_library_text() -> None:
    from app.governed_roby_initiated_library_access import (
        GovernedRobyInitiatedLibraryAccessV1,
    )

    source = inspect.getsource(GovernedRobyInitiatedLibraryAccessV1.handle_proposal)
    assert 'text="Consultá la biblioteca personal."' not in source
    assert "handle_user_request" not in source
    assert "handle_admitted_request" in source


def test_cap17_productive_wiring_exposes_cognitive_bridge_reference() -> None:
    from app.governed_local_library_runtime_wiring import (
        GovernedLocalLibraryRuntimeWiring,
    )

    fields = set(GovernedLocalLibraryRuntimeWiring.__dataclass_fields__)
    assert "cognitive_bridge" in fields


def test_cap17_productive_wiring_builds_bridge_only_when_library_is_provisioned() -> (
    None
):
    import app.governed_local_library_runtime_wiring as wiring

    source = inspect.getsource(
        wiring.build_governed_local_library_runtime_from_environment
    )
    assert "GovernedCognitiveEvidenceToLocalLibraryBridgeV1" in source
    assert "cognitive_bridge=" in source
    not_provisioned = source.index(
        "GovernedLocalLibraryRuntimeProvisionStatus.NOT_PROVISIONED"
    )
    bridge = source.index("GovernedCognitiveEvidenceToLocalLibraryBridgeV1")
    assert bridge > not_provisioned


def test_cap17_cognitive_bridge_does_not_modify_retrieval_step_schema() -> None:
    from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

    fields = set(KnowledgeRetrievalStep.__dataclass_fields__)
    assert fields == {"source", "priority", "required", "query", "step_id"}


def test_cap17_cognitive_bridge_has_no_hardcoded_personal_library_root() -> None:
    module = _bridge_module()
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "D:\\Biblioteca" not in source
    assert "D:/Biblioteca" not in source
    assert "ROBY_LOCAL_LIBRARY_ROOT" not in source
