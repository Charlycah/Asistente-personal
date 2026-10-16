from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from app.m369_explicit_human_learning_approval import ApprovedKnowledgeRevisionEvidence

MODULE = "app.governed_knowledge_revision_application_proposal"
PROPOSAL = "GovernedKnowledgeRevisionApplicationProposal"
FOUNDATION = "GovernedKnowledgeRevisionApplicationProposalFoundation"


def _module():
    try:
        return importlib.import_module(MODULE)
    except ModuleNotFoundError:
        return None


def test_g15_inert_governed_revision_application_proposal_contract_exists() -> None:
    module = _module()
    assert module is not None, "G15 seam missing: revision application proposal module"
    proposal_type = getattr(module, PROPOSAL, None)
    foundation_type = getattr(module, FOUNDATION, None)
    assert proposal_type is not None
    assert foundation_type is not None


def test_g15_proposal_preserves_g14_lineage_and_explicit_memory_owner() -> None:
    module = _module()
    assert module is not None
    proposal_type = getattr(module, PROPOSAL, None)
    assert proposal_type is not None
    fields = set(getattr(proposal_type, "__dataclass_fields__", {}))
    assert {
        "proposal_id",
        "revision_approval_id",
        "revision_proposal_id",
        "target_memory_id",
        "target_owner",
        "target_category",
        "current_content",
        "replacement_content",
        "corrective_evidence_ids",
        "revision_proposal_fingerprint",
        "human_approval_fingerprint",
        "source_fingerprint",
    } <= fields


def test_g15_foundation_accepts_approved_revision_and_preserves_official_boundary(
) -> None:
    module = _module()
    assert module is not None
    foundation_type = getattr(module, FOUNDATION, None)
    assert foundation_type is not None
    method = getattr(foundation_type(), "propose", None)
    assert method is not None
    signature = inspect.signature(method)
    assert "approved_revision" in signature.parameters
    assert "owner" in signature.parameters

    proposal_type = getattr(module, PROPOSAL)
    fields = set(getattr(proposal_type, "__dataclass_fields__", {}))
    assert "canonical_memory_authority" in fields
    default = proposal_type.__dataclass_fields__["canonical_memory_authority"].default
    assert default == "OfficialMemoryGateway"


def test_g15_application_proposal_is_inert_and_performs_no_memory_mutation() -> None:
    module = _module()
    assert module is not None
    proposal_type = getattr(module, PROPOSAL, None)
    assert proposal_type is not None
    fields = set(getattr(proposal_type, "__dataclass_fields__", {}))
    assert {
        "read_only",
        "write_performed",
        "replacement_persisted",
        "supersession_applied",
        "archive_performed",
        "memory_modified",
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
        "CognitiveMemoryStore(",
        "MemoryRuntimeIntegration(",
    )
    assert not any(token in source for token in forbidden)


def test_g15_reuses_existing_memory_authority_and_g14_approval_evidence() -> None:
    project = Path(__file__).resolve().parents[2]
    memory_gateway = project / "app/memory_consolidation.py"
    tree = ast.parse(memory_gateway.read_text(encoding="utf-8"))
    official_gateways = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "OfficialMemoryGateway"
    ]
    assert official_gateways == ["OfficialMemoryGateway"]

    fields = set(
        getattr(ApprovedKnowledgeRevisionEvidence, "__dataclass_fields__", {})
    )
    assert {
        "approval_id",
        "revision_proposal_id",
        "target_memory_id",
        "proposed_content",
        "human_approval_fingerprint",
        "writes_memory",
        "applies_revision",
    } <= fields
