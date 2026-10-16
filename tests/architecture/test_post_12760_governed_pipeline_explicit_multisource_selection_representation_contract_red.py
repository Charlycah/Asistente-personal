from __future__ import annotations

import inspect
from dataclasses import fields
from hashlib import sha256
from pathlib import Path

from core.governed_operational_conversation_pipeline.models import (
    GovernedConversationPipelineRequest,
)
from core.runtime_composition_root import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_HASHES = {
    "app/unified_brain.py": (
        "05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750"
    ),
    "app/ordinary_turn_multisource_reachability_adapter.py": (
        "b943f0d354fc4b7fa0dbb0d4e055e9e35289ce2a3d87a855038af4bcf73c7e97"
    ),
    "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
}


def _request_fields() -> dict[str, object]:
    return {item.name: item for item in fields(GovernedConversationPipelineRequest)}


def test_post_12760_request_represents_explicit_document_ids():
    request_fields = _request_fields()
    assert "explicit_document_ids" in request_fields, (
        "RED: governed ordinary-turn request cannot yet represent explicit document "
        "selection"
    )


def test_post_12760_request_represents_explicit_sources():
    request_fields = _request_fields()
    assert "explicit_sources" in request_fields, (
        "RED: governed ordinary-turn request cannot yet represent explicit source "
        "selection"
    )


def test_post_12760_request_represents_explicit_evidence_references():
    request_fields = _request_fields()
    assert "explicit_evidence_references" in request_fields, (
        "RED: governed ordinary-turn request cannot yet represent explicit evidence "
        "references"
    )


def test_post_12760_absent_selection_preserves_existing_request_construction():
    request = GovernedConversationPipelineRequest(
        owner="owner",
        session_id="session",
        text="ordinary turn",
    )
    assert request.external_evidence == ()
    assert request.integrated_visual_context is None


def test_post_12760_does_not_duplicate_visual_context_or_activate_consumer():
    request_fields = _request_fields()
    assert "visual_context_contribution" not in request_fields
    prepare_source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "ordinary_turn_multisource_reachability_adapter" not in prepare_source


def test_post_12760_upstream_ingress_and_certified_adapters_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
