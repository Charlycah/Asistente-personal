from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_proposal import (
    GovernedKnowledgeRevisionProposal,
)
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


def test_g19_existing_productive_wiring_exposes_revision_proposal_seam() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "propose_knowledge_revision",
        None,
    )
    assert method is not None, (
        "G19 seam missing: reuse existing ProductiveGovernedLearningWiring "
        "to reach the existing G13 proposal foundation"
    )
    signature = inspect.signature(method)
    for name in (
        "target_memory",
        "corrective_evidence",
        "proposed_content",
        "session_id",
    ):
        assert name in signature.parameters


def test_g19_revision_proposal_seam_reuses_existing_g13_foundation() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "propose_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert "GovernedKnowledgeRevisionProposalFoundation" in inspect.getsource(
        ProductiveGovernedLearningWiring
    )
    assert ".propose(" in source
    assert "target_memory" in source
    assert "corrective_evidence" in source
    assert "proposed_content" in source


def test_g19_pending_revision_review_is_session_scoped_and_exact() -> None:
    cls_source = inspect.getsource(ProductiveGovernedLearningWiring)
    assert "_pending_revision" in cls_source
    assert "session_id" in cls_source
    method = getattr(
        ProductiveGovernedLearningWiring,
        "pending_revision_proposal",
        None,
    )
    assert method is not None
    signature = inspect.signature(method)
    assert "session_id" in signature.parameters
    annotation = signature.return_annotation
    assert (
        annotation is GovernedKnowledgeRevisionProposal
        or "GovernedKnowledgeRevisionProposal" in str(annotation)
    )


def test_g19_proposal_stage_remains_inert_and_stops_before_g14_or_memory() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "propose_knowledge_revision",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert "evaluate_revision(" not in source
    assert "apply_governed_knowledge_revision(" not in source
    assert "execute_certified_revision_request(" not in source
    assert "GovernedKnowledgeRevisionApplicationProposalFoundation" not in source
    assert "GovernedKnowledgeRevisionRequestFoundation" not in source


def test_g19_reuses_one_productive_wiring_and_one_g13_proposal_authority() -> None:
    project = Path(__file__).resolve().parents[2]
    wiring_tree = ast.parse(
        (project / "app/productive_governed_learning_wiring.py").read_text(
            encoding="utf-8"
        )
    )
    assert sum(
        isinstance(node, ast.ClassDef)
        and node.name == "ProductiveGovernedLearningWiring"
        for node in wiring_tree.body
    ) == 1

    proposal_tree = ast.parse(
        (project / "app/governed_knowledge_revision_proposal.py").read_text(
            encoding="utf-8"
        )
    )
    assert sum(
        isinstance(node, ast.ClassDef)
        and node.name == "GovernedKnowledgeRevisionProposalFoundation"
        for node in proposal_tree.body
    ) == 1

    app_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (project / "app").glob("*.py")
    )
    assert "class KnowledgeRevisionManager" not in app_sources
    assert "class RevisionProposalInbox" not in app_sources
    assert "class ProductiveKnowledgeRevisionWiring" not in app_sources
