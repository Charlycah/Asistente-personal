from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_request import GovernedKnowledgeRevisionRequest
from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


def test_g18_official_conversation_gateway_accepts_exact_g16_request() -> None:
    signature = inspect.signature(OfficialConversationGateway.submit)
    assert "governed_knowledge_revision_request" in signature.parameters, (
        "G18 seam missing: OfficialConversationGateway must accept the "
        "certified G16 revision request"
    )


def test_g18_existing_productive_wiring_exposes_revision_execution_seam() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "execute_certified_revision_request",
        None,
    )
    assert method is not None, (
        "G18 seam missing: reuse existing ProductiveGovernedLearningWiring"
    )
    signature = inspect.signature(method)
    assert "request" in signature.parameters
    annotation = signature.parameters["request"].annotation
    assert (
        annotation is GovernedKnowledgeRevisionRequest
        or "GovernedKnowledgeRevisionRequest" in str(annotation)
    )


def test_g18_existing_wiring_forwards_exact_request_to_official_memory() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "execute_certified_revision_request",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert "apply_governed_knowledge_revision(request)" in source
    assert "GovernedKnowledgeRevisionRequestFoundation" not in source
    assert ".certify(" not in source


def test_g18_official_gateway_routes_revision_through_same_existing_wiring() -> None:
    source = inspect.getsource(OfficialConversationGateway.submit)
    assert "governed_knowledge_revision_request" in source
    assert "execute_certified_revision_request" in source
    assert "_productive_governed_learning_wiring" in inspect.getsource(
        OfficialConversationGateway
    )
    assert "apply_governed_knowledge_revision(" not in source


def test_g18_reuses_one_wiring_and_one_memory_authority() -> None:
    project = Path(__file__).resolve().parents[2]

    wiring_tree = ast.parse(
        (project / "app/productive_governed_learning_wiring.py").read_text(
            encoding="utf-8"
        )
    )
    wiring_declarations = [
        node.name
        for node in wiring_tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ProductiveGovernedLearningWiring"
    ]
    assert wiring_declarations == ["ProductiveGovernedLearningWiring"]

    gateway_tree = ast.parse(
        (project / "app/memory_consolidation.py").read_text(encoding="utf-8")
    )
    gateway_declarations = [
        node.name
        for node in gateway_tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "OfficialMemoryGateway"
    ]
    assert gateway_declarations == ["OfficialMemoryGateway"]

    app_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (project / "app").glob("*.py")
    )
    assert "class ProductiveKnowledgeRevisionWiring" not in app_sources
    assert "class RevisionMemoryGateway" not in app_sources
