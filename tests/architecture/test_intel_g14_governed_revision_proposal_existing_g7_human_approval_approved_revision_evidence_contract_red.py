from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_proposal import GovernedKnowledgeRevisionProposal
from app.m369_explicit_human_learning_approval import (
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)

EXPECTED_RESPONSE = "ExplicitHumanKnowledgeRevisionApprovalResponse"
EXPECTED_EVIDENCE = "ApprovedKnowledgeRevisionEvidence"


def _g7_module():
    import app.m369_explicit_human_learning_approval as module

    return module


def test_g14_existing_g7_authority_exposes_revision_approval_seam() -> None:
    foundation = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    method = getattr(foundation, "evaluate_revision", None)
    assert method is not None, (
        "G14 seam missing: existing G7 authority does not expose evaluate_revision"
    )
    signature = inspect.signature(method)
    assert "proposal" in signature.parameters
    assert "response" in signature.parameters


def test_g14_revision_approval_response_uses_revision_lineage_not_fake_learning_ids(
) -> None:
    module = _g7_module()
    response_type = getattr(module, EXPECTED_RESPONSE, None)
    assert response_type is not None
    fields = set(getattr(response_type, "__dataclass_fields__", {}))
    assert {
        "approval_request_id",
        "revision_proposal_id",
        "human_response_reference",
        "response_text",
        "approver",
        "exact_linkage",
    } <= fields
    assert "learning_candidate_id" not in fields
    assert "preference_candidate_id" not in fields
    assert "evaluation_report_id" not in fields


def test_g14_approved_revision_evidence_preserves_exact_g13_and_human_lineage() -> None:
    module = _g7_module()
    evidence_type = getattr(module, EXPECTED_EVIDENCE, None)
    assert evidence_type is not None
    fields = set(getattr(evidence_type, "__dataclass_fields__", {}))
    assert {
        "approval_id",
        "revision_proposal_id",
        "target_memory_id",
        "target_category",
        "current_content",
        "proposed_content",
        "corrective_evidence_ids",
        "revision_proposal_fingerprint",
        "human_response_reference",
        "approver",
        "human_approval_fingerprint",
    } <= fields
    assert "learning_candidate_id" not in fields
    assert "preference_candidate_id" not in fields


def test_g14_revision_approval_remains_inert_and_cannot_modify_memory() -> None:
    module = _g7_module()
    evidence_type = getattr(module, EXPECTED_EVIDENCE, None)
    assert evidence_type is not None
    fields = set(getattr(evidence_type, "__dataclass_fields__", {}))
    assert {
        "read_only",
        "writes_memory",
        "modifies_knowledge",
        "applies_revision",
        "archives_memory",
        "supersedes_memory",
        "persists_replacement",
        "executes_actions",
        "grants_authority",
    } <= fields

    source = inspect.getsource(module)
    forbidden = (
        "update_content(",
        ".archive(",
        "remember_governed_learning(",
        "store_governed_learning(",
        "OfficialMemoryGateway(",
    )
    assert not any(token in source for token in forbidden)


def test_g14_reuses_existing_g7_authority_without_second_approval_authority() -> None:
    project = Path(__file__).resolve().parents[2]
    g7_path = project / "app/m369_explicit_human_learning_approval.py"
    assert g7_path.exists()

    tree = ast.parse(g7_path.read_text(encoding="utf-8"))
    declared_classes = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }
    authority_like = {
        name
        for name in declared_classes
        if "Approval" in name and name.endswith(("Authority", "Manager", "Gateway"))
    }
    assert not authority_like

    foundation = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    assert foundation.classify_explicit_response("aprobado").value == "approved"

    proposal_fields = set(
        getattr(GovernedKnowledgeRevisionProposal, "__dataclass_fields__", {})
    )
    assert "approval_granted" in proposal_fields
    assert "applied" in proposal_fields
