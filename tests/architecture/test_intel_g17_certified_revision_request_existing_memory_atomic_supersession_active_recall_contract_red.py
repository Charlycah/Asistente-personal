from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_request import (
    GovernedKnowledgeRevisionRequest,
)
from app.memory_consolidation import OfficialMemoryGateway
from core.cognitive_memory_recall import CognitiveMemoryRecall
from core.cognitive_memory_store import CognitiveMemoryStore
from core.memory_runtime_integration.runtime import MemoryRuntimeIntegration


def test_g17_existing_official_memory_gateway_exposes_revision_execution_seam() -> None:
    method = getattr(
        OfficialMemoryGateway,
        "apply_governed_knowledge_revision",
        None,
    )
    assert method is not None, (
        "G17 seam missing: existing OfficialMemoryGateway revision execution"
    )
    signature = inspect.signature(method)
    assert "request" in signature.parameters
    annotation = signature.parameters["request"].annotation
    assert (
        annotation is GovernedKnowledgeRevisionRequest
        or "GovernedKnowledgeRevisionRequest" in str(annotation)
    )


def test_g17_existing_runtime_and_store_expose_one_atomic_revision_path() -> None:
    runtime_method = getattr(
        MemoryRuntimeIntegration,
        "apply_governed_knowledge_revision",
        None,
    )
    store_method = getattr(
        CognitiveMemoryStore,
        "apply_governed_revision_atomic",
        None,
    )
    assert runtime_method is not None, (
        "G17 seam missing: existing Memory runtime revision delegation"
    )
    assert store_method is not None, (
        "G17 seam missing: existing CognitiveMemoryStore atomic revision"
    )

    store_source = inspect.getsource(store_method)
    assert "BEGIN IMMEDIATE" in store_source
    assert "expected_current_content" in store_source
    assert "expected_target_fingerprint" in store_source
    assert "replacement_idempotency_key" in store_source


def test_g17_atomic_revision_preserves_old_new_lineage_and_fails_closed() -> None:
    store_method = getattr(
        CognitiveMemoryStore,
        "apply_governed_revision_atomic",
        None,
    )
    assert store_method is not None
    source = inspect.getsource(store_method)

    required_tokens = (
        '"superseded"',
        '"active"',
        '"superseded_by"',
        '"supersedes"',
        "revision_request_id",
        "revision_proposal_id",
        "revision_approval_id",
        "corrective_evidence_ids",
    )
    assert all(token in source for token in required_tokens)
    assert "update_content(" not in source
    assert ".archive(" not in source


def test_g17_productive_recall_excludes_superseded_memory() -> None:
    recall_source = inspect.getsource(CognitiveMemoryRecall)
    assert '"superseded"' in recall_source
    assert (
        "_is_inactive" in recall_source
        or "_is_superseded" in recall_source
        or "status" in recall_source
    )

    gateway_recall = inspect.getsource(OfficialMemoryGateway.recall)
    assert (
        "active_only" in gateway_recall
        or "superseded" in gateway_recall
        or "search_active" in gateway_recall
    )


def test_g17_reuses_single_existing_memory_authority_and_store() -> None:
    project = Path(__file__).resolve().parents[2]

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

    store_tree = ast.parse(
        (project / "core/cognitive_memory_store.py").read_text(encoding="utf-8")
    )
    store_declarations = [
        node.name
        for node in store_tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "CognitiveMemoryStore"
    ]
    assert store_declarations == ["CognitiveMemoryStore"]

    request_fields = set(
        GovernedKnowledgeRevisionRequest.__dataclass_fields__
    )
    assert {
        "target_owner",
        "target_memory_id",
        "expected_current_content",
        "expected_target_fingerprint",
        "replacement_idempotency_key",
    } <= request_fields
