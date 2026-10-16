from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_request import GovernedKnowledgeRevisionRequest
from app.m369_explicit_human_learning_approval import ApprovedKnowledgeRevisionEvidence
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


class _NoMutationMemoryGateway:
    def remember_governed_learning(self, request):  # pragma: no cover - must not run
        raise AssertionError("POST-G20 preparation must not write governed learning")

    def apply_governed_knowledge_revision(self, request):  # pragma: no cover
        raise AssertionError("POST-G20 preparation must stop before Memory mutation")


def _approved_revision() -> ApprovedKnowledgeRevisionEvidence:
    return ApprovedKnowledgeRevisionEvidence(
        approval_id="approved-knowledge-revision-evidence-contract-red",
        revision_proposal_id="governed-knowledge-revision-proposal-contract-red",
        target_memory_id="stable-knowledge-contract-red",
        target_category="STABLE_KNOWLEDGE",
        current_content="ROBY utiliza conocimiento durable versión uno.",
        proposed_content="ROBY utiliza conocimiento durable versión dos.",
        corrective_evidence_ids=("corrective-evidence-contract-red",),
        revision_proposal_fingerprint="1" * 64,
        human_response_reference="human-response-contract-red",
        approver="Carlos y Cristina",
        human_approval_fingerprint="2" * 64,
    )


def test_post_g20_existing_productive_wiring_exposes_approved_revision_preparation_seam() -> (  # noqa: E501
    None
):
    method = getattr(
        ProductiveGovernedLearningWiring,
        "prepare_approved_knowledge_revision",
        None,
    )
    assert method is not None, (
        "POST-G20 seam missing: existing ProductiveGovernedLearningWiring must "
        "prepare exact G14 approved evidence through existing G15 and G16"
    )
    signature = inspect.signature(method)
    assert "approved_revision" in signature.parameters
    assert "owner" in signature.parameters


def test_post_g20_preparation_reuses_existing_g15_and_g16_foundations() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "prepare_approved_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert ".propose(" in source
    assert ".certify(" in source

    module_source = inspect.getsource(
        __import__(
            "app.productive_governed_learning_wiring",
            fromlist=["ProductiveGovernedLearningWiring"],
        )
    )
    assert "GovernedKnowledgeRevisionApplicationProposalFoundation" in module_source
    assert "GovernedKnowledgeRevisionRequestFoundation" in module_source


def test_post_g20_exact_g14_evidence_uses_owner_and_lineage() -> None:
    wiring = ProductiveGovernedLearningWiring(_NoMutationMemoryGateway())
    method = getattr(wiring, "prepare_approved_knowledge_revision", None)
    assert method is not None

    approved = _approved_revision()
    request = method(approved, owner="  Carlos y Cristina  ")

    assert isinstance(request, GovernedKnowledgeRevisionRequest)
    assert request.revision_approval_id == approved.approval_id
    assert request.revision_proposal_id == approved.revision_proposal_id
    assert request.target_memory_id == approved.target_memory_id
    assert request.target_owner == "Carlos y Cristina"
    assert request.expected_current_content == approved.current_content
    assert request.replacement_content == approved.proposed_content
    assert request.corrective_evidence_ids == approved.corrective_evidence_ids
    assert (
        request.revision_proposal_fingerprint == approved.revision_proposal_fingerprint
    )
    assert request.human_approval_fingerprint == approved.human_approval_fingerprint
    assert request.read_only is True
    assert request.write_performed is False
    assert request.memory_modified is False


def test_post_g20_preparation_stops_before_g17_g18_or_memory_execution() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "prepare_approved_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    forbidden = (
        "execute_certified_revision_request",
        "apply_governed_knowledge_revision",
        "remember_governed_learning",
        "store_governed_learning",
        "update_content(",
        ".archive(",
    )
    for token in forbidden:
        assert token not in source


def test_post_g20_contract_introduces_no_duplicate_revision_or_memory_authority() -> (
    None
):
    project = Path(__file__).resolve().parents[2]
    wiring_path = project / "app/productive_governed_learning_wiring.py"
    tree = ast.parse(wiring_path.read_text(encoding="utf-8"))
    declared_classes = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }
    forbidden_classes = {
        "RevisionApprovalManager",
        "KnowledgeRevisionApprovalAuthority",
        "RevisionApplicationManager",
        "RevisionExecutionManager",
        "KnowledgeRevisionManager",
        "ProductiveKnowledgeRevisionWiring",
        "RevisionProposalInbox",
        "RevisionMemoryGateway",
    }
    assert declared_classes.isdisjoint(forbidden_classes)

    module_source = wiring_path.read_text(encoding="utf-8")
    assert "OfficialMemoryGateway(" not in module_source
    assert (
        module_source.count("M369ExplicitHumanLearningApprovalEvidenceFoundation()")
        == 1
    )
