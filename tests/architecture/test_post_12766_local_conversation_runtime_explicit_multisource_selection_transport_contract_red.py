from __future__ import annotations

import inspect
from hashlib import sha256
from pathlib import Path

from core.end_to_end_local_conversation.runtime import EndToEndLocalConversation

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
    "core/governed_operational_conversation_pipeline/models.py": (
        "f65c3f87c64c5b8cd8525aa326f31a66550711916d564fc0c90cde3d2730b063"
    ),
}


def _converse_parameters() -> dict[str, inspect.Parameter]:
    return dict(inspect.signature(EndToEndLocalConversation.converse).parameters)


def _converse_source() -> str:
    return inspect.getsource(EndToEndLocalConversation.converse)


def test_post_12766_runtime_transports_explicit_document_ids_to_request():
    parameters = _converse_parameters()
    assert "explicit_document_ids" in parameters, (
        "RED: local conversation runtime cannot yet receive explicit document selection"
    )
    assert parameters["explicit_document_ids"].default == ()
    assert "explicit_document_ids=explicit_document_ids" in _converse_source()


def test_post_12766_runtime_transports_explicit_sources_to_request():
    parameters = _converse_parameters()
    assert "explicit_sources" in parameters, (
        "RED: local conversation runtime cannot yet receive explicit source selection"
    )
    assert parameters["explicit_sources"].default == ()
    assert "explicit_sources=explicit_sources" in _converse_source()


def test_post_12766_runtime_transports_explicit_evidence_references_to_request():
    parameters = _converse_parameters()
    assert "explicit_evidence_references" in parameters, (
        "RED: local conversation runtime cannot yet receive explicit evidence "
        "references"
    )
    assert parameters["explicit_evidence_references"].default == ()
    source = _converse_source()
    assert "explicit_evidence_references=explicit_evidence_references" in source


def test_post_12766_transport_does_not_activate_multisource_consumer():
    source = _converse_source()
    assert "ordinary_turn_multisource_reachability_adapter" not in source
    assert "admit_and_reason" not in source


def test_post_12766_certified_upstream_and_authorities_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
