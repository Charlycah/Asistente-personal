from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from app.governed_knowledge_revision_application_proposal import (
    GovernedKnowledgeRevisionApplicationProposal,
)

MODULE = "app.governed_knowledge_revision_request"
REQUEST = "GovernedKnowledgeRevisionRequest"
FOUNDATION = "GovernedKnowledgeRevisionRequestFoundation"


def _module():
    try:
        return importlib.import_module(MODULE)
    except ModuleNotFoundError:
        return None


def test_g16_certified_revision_request_contract_exists() -> None:
    module = _module()
    assert module is not None, "G16 seam missing: governed revision request module"
    request_type = getattr(module, REQUEST, None)
    foundation_type = getattr(module, FOUNDATION, None)
    assert request_type is not None
    assert foundation_type is not None


def test_g16_request_preserves_g15_lineage_and_version_scoped_target() -> None:
    module = _module()
    assert module is not None
    request_type = getattr(module, REQUEST, None)
    assert request_type is not None
    fields = set(getattr(request_type, "__dataclass_fields__", {}))
    assert {
        "request_id",
        "application_proposal_id",
        "revision_approval_id",
        "revision_proposal_id",
        "target_memory_id",
        "target_owner",
        "target_category",
        "expected_current_content",
        "replacement_content",
        "corrective_evidence_ids",
        "revision_proposal_fingerprint",
        "human_approval_fingerprint",
        "application_proposal_fingerprint",
        "expected_target_fingerprint",
        "replacement_idempotency_key",
    } <= fields


def test_g16_foundation_certifies_existing_official_memory_boundary() -> None:
    module = _module()
    assert module is not None
    foundation_type = getattr(module, FOUNDATION, None)
    assert foundation_type is not None
    method = getattr(foundation_type(), "certify", None)
    assert method is not None
    signature = inspect.signature(method)
    assert "proposal" in signature.parameters

    request_type = getattr(module, REQUEST)
    dataclass_fields = request_type.__dataclass_fields__
    assert dataclass_fields["writer_authority"].default == "memory_gateway"
    assert dataclass_fields["writer_component"].default == "OfficialMemoryGateway"
    assert (
        dataclass_fields["writer_method"].default
        == "apply_governed_knowledge_revision"
    )
    assert dataclass_fields["requires_official_memory_gateway"].default is True
    assert dataclass_fields["requires_atomic_revision"].default is True
    assert dataclass_fields["preserves_prior_version"].default is True


def test_g16_certified_request_remains_inert_and_cannot_mutate_memory() -> None:
    module = _module()
    assert module is not None
    request_type = getattr(module, REQUEST, None)
    assert request_type is not None
    fields = set(getattr(request_type, "__dataclass_fields__", {}))
    assert {
        "read_only",
        "write_performed",
        "replacement_persisted",
        "supersession_applied",
        "memory_modified",
        "executes_actions",
        "grants_authority",
    } <= fields

    source = inspect.getsource(module)
    forbidden = (
        "update_content(",
        ".archive(",
        "store_candidate_idempotent(",
        "remember_governed_learning(",
        "store_governed_learning(",
        "OfficialMemoryGateway(",
        "CognitiveMemoryStore(",
        "MemoryRuntimeIntegration(",
    )
    assert not any(token in source for token in forbidden)


def test_g16_reuses_g15_proposal_and_single_existing_memory_authority() -> None:
    proposal_fields = set(
        getattr(
            GovernedKnowledgeRevisionApplicationProposal,
            "__dataclass_fields__",
            {},
        )
    )
    assert {
        "proposal_id",
        "revision_approval_id",
        "revision_proposal_id",
        "target_memory_id",
        "target_owner",
        "current_content",
        "replacement_content",
        "source_fingerprint",
    } <= proposal_fields

    project = Path(__file__).resolve().parents[2]
    memory_gateway = project / "app/memory_consolidation.py"
    tree = ast.parse(memory_gateway.read_text(encoding="utf-8"))
    official_gateways = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "OfficialMemoryGateway"
    ]
    assert official_gateways == ["OfficialMemoryGateway"]
