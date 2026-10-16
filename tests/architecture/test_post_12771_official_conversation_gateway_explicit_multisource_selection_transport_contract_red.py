from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway

ROOT = Path(__file__).resolve().parents[2]
GATEWAY = ROOT / "app" / "official_conversation_gateway.py"
RUNTIME = ROOT / "core" / "end_to_end_local_conversation" / "runtime.py"
REQUEST_MODELS = (
    ROOT / "core" / "governed_operational_conversation_pipeline" / "models.py"
)

RUNTIME_SHA256 = "c35610823e19463c20f466703324a94d1f83ead1c78633a2966f328028eadd58"
REQUEST_MODELS_SHA256 = (
    "f65c3f87c64c5b8cd8525aa326f31a66550711916d564fc0c90cde3d2730b063"
)


def _submit_parameters():
    return inspect.signature(OfficialConversationGateway.submit).parameters


def _submit_source() -> str:
    return inspect.getsource(OfficialConversationGateway.submit)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_post_12771_gateway_transports_explicit_document_ids_to_runtime():
    parameters = _submit_parameters()
    assert "explicit_document_ids" in parameters, (
        "RED: official gateway cannot yet receive explicit document selection"
    )
    assert parameters["explicit_document_ids"].default == ()
    source = _submit_source()
    assert "explicit_document_ids=explicit_document_ids" in source


def test_post_12771_gateway_transports_explicit_sources_to_runtime():
    parameters = _submit_parameters()
    assert "explicit_sources" in parameters, (
        "RED: official gateway cannot yet receive explicit source selection"
    )
    assert parameters["explicit_sources"].default == ()
    source = _submit_source()
    assert "explicit_sources=explicit_sources" in source


def test_post_12771_gateway_transports_explicit_evidence_references_to_runtime():
    parameters = _submit_parameters()
    assert "explicit_evidence_references" in parameters, (
        "RED: official gateway cannot yet receive explicit evidence references"
    )
    assert parameters["explicit_evidence_references"].default == ()
    source = _submit_source()
    expected = "explicit_evidence_references=explicit_evidence_references"
    assert expected in source


def test_post_12771_transport_does_not_reopen_certified_runtime_or_request():
    assert _sha256(RUNTIME) == RUNTIME_SHA256
    assert _sha256(REQUEST_MODELS) == REQUEST_MODELS_SHA256


def test_post_12771_selection_does_not_become_gateway_routing_authority():
    source = _submit_source()
    assert "and not explicit_document_ids" not in source
    assert "and not explicit_sources" not in source
    assert "and not explicit_evidence_references" not in source
    assert "ordinary_turn_multisource_reachability_adapter" not in source
    assert "admit_and_reason" not in source
