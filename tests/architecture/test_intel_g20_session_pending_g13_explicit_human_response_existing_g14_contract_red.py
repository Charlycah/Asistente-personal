from __future__ import annotations

import inspect

from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


def test_g20_existing_productive_wiring_exposes_pending_revision_approval_seam(
) -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "evaluate_pending_knowledge_revision",
        None,
    )
    assert method is not None, (
        "G20 seam missing: reuse existing ProductiveGovernedLearningWiring "
        "to evaluate the exact session-scoped pending G13 proposal via G14"
    )


def test_g20_pending_revision_approval_reuses_existing_g14_authority() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "evaluate_pending_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert "pending_revision_proposal" in source or "_pending_revision" in source
    assert "self._approval.evaluate_revision" in source
    assert "revision_proposal_id" in source
    assert "exact_linkage" in source


def test_g20_official_conversation_exposes_explicit_revision_response_seam() -> None:
    signature = inspect.signature(OfficialConversationGateway.submit)
    assert "knowledge_revision_approval_response" in signature.parameters
    source = inspect.getsource(OfficialConversationGateway.submit)
    assert "evaluate_pending_knowledge_revision" in source
    assert "effective_session_id" in source


def test_g20_human_approval_stage_stops_before_g15_g16_or_memory() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "evaluate_pending_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    forbidden = (
        "GovernedKnowledgeRevisionApplicationProposalFoundation",
        "GovernedKnowledgeRevisionRequestFoundation",
        "execute_certified_revision_request",
        "apply_governed_knowledge_revision",
        "remember_governed_learning",
    )
    for token in forbidden:
        assert token not in source
    assert "evaluate_revision" in source


def test_g20_reuses_one_wiring_one_g14_authority_and_one_memory_gateway() -> None:
    wiring_source = inspect.getsource(ProductiveGovernedLearningWiring)
    assert wiring_source.count(
        "M369ExplicitHumanLearningApprovalEvidenceFoundation()"
    ) == 1

    module_source = inspect.getsource(
        __import__(
            "app.productive_governed_learning_wiring",
            fromlist=["ProductiveGovernedLearningWiring"],
        )
    )
    assert "RevisionApprovalManager" not in module_source
    assert "KnowledgeRevisionApprovalAuthority" not in module_source

    conversation_source = inspect.getsource(
        __import__(
            "app.official_conversation_gateway",
            fromlist=["OfficialConversationGateway"],
        )
    )
    assert "RevisionApprovalManager" not in conversation_source
    assert "RevisionMemoryGateway" not in conversation_source
