from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

import pytest

EXPECTED_MODULE = "app.governed_knowledge_revision_proposal"
EXPECTED_FOUNDATION = "GovernedKnowledgeRevisionProposalFoundation"
EXPECTED_PROPOSAL = "GovernedKnowledgeRevisionProposal"


def _module():
    try:
        return importlib.import_module(EXPECTED_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "G13 seam missing: governed durable-knowledge revision proposal "
            "contract is not exposed"
        )


def test_g13_exposes_inert_governed_revision_proposal_contract() -> None:
    module = _module()
    proposal_type = getattr(module, EXPECTED_PROPOSAL, None)
    assert proposal_type is not None
    fields = getattr(proposal_type, "__dataclass_fields__", {})
    assert {
        "proposal_id",
        "target_memory_id",
        "target_category",
        "current_content",
        "proposed_content",
        "corrective_evidence_ids",
        "source_fingerprint",
    } <= set(fields)


def test_g13_revision_proposal_is_linked_to_existing_stable_knowledge() -> None:
    module = _module()
    foundation = getattr(module, EXPECTED_FOUNDATION, None)
    assert foundation is not None
    signature = inspect.signature(foundation().propose)
    assert "target_memory" in signature.parameters
    assert "corrective_evidence" in signature.parameters


def test_g13_revision_proposal_preserves_corrective_evidence_lineage() -> None:
    module = _module()
    proposal_type = getattr(module, EXPECTED_PROPOSAL, None)
    assert proposal_type is not None
    source = inspect.getsource(proposal_type)
    assert "corrective_evidence_ids" in source
    assert "source_fingerprint" in source
    assert "target_memory_id" in source


def test_g13_proposal_cannot_approve_apply_or_write_revision() -> None:
    module = _module()
    foundation = getattr(module, EXPECTED_FOUNDATION, None)
    proposal_type = getattr(module, EXPECTED_PROPOSAL, None)
    assert foundation is not None and proposal_type is not None
    source = inspect.getsource(module)
    forbidden = (
        "update_content(",
        ".archive(",
        "remember_governed_learning(",
        "store_governed_learning(",
        "OfficialMemoryGateway(",
    )
    assert not any(token in source for token in forbidden)
    fields = getattr(proposal_type, "__dataclass_fields__", {})
    assert {"write_performed", "approval_granted", "applied"} <= set(fields)


def test_g13_does_not_duplicate_existing_memory_learning_or_reasoning_authorities() -> (
    None
):
    project = Path(__file__).resolve().parents[2]
    existing = {
        "memory_gateway": project / "app/memory_consolidation.py",
        "safe_learning": project / "app/safe_learning_policies.py",
        "reasoning": project / "app/governed_reasoning_runtime.py",
    }
    for path in existing.values():
        assert path.exists()

    candidate = project / "app/governed_knowledge_revision_proposal.py"
    if not candidate.exists():
        return

    tree = ast.parse(candidate.read_text(encoding="utf-8"))
    declared_classes = {
        node.name for node in tree.body if isinstance(node, ast.ClassDef)
    }
    assert "OfficialMemoryGateway" not in declared_classes
    assert "SafeLearningPolicies" not in declared_classes
    assert "OfficialGovernedReasoningRuntimeGateway" not in declared_classes

    source = candidate.read_text(encoding="utf-8")
    assert "CognitiveMemoryStore(" not in source
    assert "MemoryRuntimeIntegration(" not in source
