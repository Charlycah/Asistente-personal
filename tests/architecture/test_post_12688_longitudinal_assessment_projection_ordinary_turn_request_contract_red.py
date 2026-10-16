from __future__ import annotations

import hashlib
import inspect
from dataclasses import fields
from pathlib import Path

import pytest

from core.governed_reasoning.longitudinal_reasoning_conversational_projection import (
    GovernedLongitudinalReasoningConversationalProjection,
    GovernedLongitudinalReasoningConversationalProjectorV1,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
PREPARATION = ROOT / "core" / "runtime_composition_root" / "preparation.py"
PROTECTED_RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
EXPECTED_PROTECTED_RUNTIME_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
TRANSPORT_METHOD = "_enrich_with_productive_longitudinal_reasoning_projection"


def _transport():
    transport = getattr(GovernedRuntimePreparation, TRANSPORT_METHOD, None)
    if transport is None:
        pytest.fail(
            "RED: ordinary runtime preparation does not yet transport the certified "
            "longitudinal reasoning conversational projection into LLMRequest"
        )
    return transport


def test_red_1_productive_preparation_reaches_certified_projector() -> None:
    source = PREPARATION.read_text(encoding="utf-8")
    assert "_project_productive_longitudinal_reasoning_assessment(" in source
    assert "longitudinal_reasoning_assessment" in source


def test_red_2_transport_accepts_projection_and_existing_llm_request_only() -> None:
    transport = _transport()
    signature = inspect.signature(transport)
    assert tuple(signature.parameters) == ("request", "projection")
    source = inspect.getsource(transport)
    assert "GovernedLongitudinalReasoningConversationalProjection" in source
    assert "GovernedLongitudinalReasoningAssessment" not in source


def test_red_3_transport_enriches_request_without_replacing_existing_content() -> None:
    transport = _transport()
    projection = GovernedLongitudinalReasoningConversationalProjection(
        status=__import__(
            "core.governed_reasoning.longitudinal_reasoning_assessment",
            fromlist=["GovernedLongitudinalReasoningStatus"],
        ).GovernedLongitudinalReasoningStatus.INSUFFICIENT_HISTORY,
        episode_count=1,
        conversation_context="Comparable reasoning history is insufficient.",
        source_assessment_id="longitudinal-reasoning-contract-red",
        source_reference="source:contract-red",
        source_fingerprint="fingerprint-contract-red",
    )
    request = LLMRequest(
        prompt="owner prompt",
        system_prompt="existing governed context",
        model="owner-model",
        max_tokens=321,
        temperature=0.2,
        metadata={"scope": "ordinary-turn"},
    )
    enriched = transport(request, projection=projection)
    assert enriched.prompt == request.prompt
    assert enriched.model == request.model
    assert enriched.max_tokens == request.max_tokens
    assert enriched.temperature == request.temperature
    assert enriched.metadata == request.metadata
    assert "existing governed context" in (enriched.system_prompt or "")
    assert projection.conversation_context in (enriched.system_prompt or "")


def test_red_4_prepare_wires_exact_derived_assessment_to_projection_then_request(
) -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "longitudinal_reasoning_assessment = (" in source
    assert "_compose_productive_longitudinal_reasoning_assessment(" in source
    assert "_project_productive_longitudinal_reasoning_assessment(" in source
    assert TRANSPORT_METHOD in source
    assert "retention.retrieve" not in source


def test_red_5_productive_wiring_stops_at_descriptive_request_transport() -> None:
    transport = _transport()
    source = inspect.getsource(transport).lower()
    assert "replace(request, system_prompt=" in source
    forbidden = (
        "memory",
        "learning",
        "reflection",
        "initiative",
        "planning",
        "authorization",
        "execution",
        "retain(",
        "retrieve(",
        "same",
        "identity",
        "temporal trend",
    )
    for token in forbidden:
        assert token not in source


def test_contract_projection_remains_the_only_semantic_transport_input() -> None:
    projection_fields = {field.name for field in fields(
        GovernedLongitudinalReasoningConversationalProjection
    )}
    assert "conversation_context" in projection_fields
    projector_source = inspect.getsource(
        GovernedLongitudinalReasoningConversationalProjectorV1
    ).lower()
    assert "recurrent_review_required" in projector_source
    assert "does not grant review authority" in projector_source
    assert "insufficient_history" in projector_source


def test_contract_raw_assessment_serialization_is_not_an_allowed_transport_pattern(
) -> None:
    source = PREPARATION.read_text(encoding="utf-8").lower()
    forbidden = (
        "str(longitudinal_reasoning_assessment)",
        "repr(longitudinal_reasoning_assessment)",
        "asdict(longitudinal_reasoning_assessment)",
        "longitudinal_reasoning_assessment.__dict__",
        "longitudinal_reasoning_assessment.rationale",
    )
    for token in forbidden:
        assert token not in source


def test_contract_existing_reconstruction_transport_remains_present() -> None:
    source = PREPARATION.read_text(encoding="utf-8")
    assert "_enrich_with_productive_longitudinal_intellectual_reconstruction" in source
    assert "[GOVERNED LONGITUDINAL INTELLECTUAL RECONSTRUCTION]" in source
    assert "replace(request, system_prompt=system_prompt)" in source


def test_contract_no_new_carrier_manager_store_or_authority_is_introduced() -> None:
    forbidden_paths = (
        "core/longitudinal_metacognition_manager.py",
        "core/longitudinal_reasoning_request.py",
        "core/longitudinal_reasoning_context_carrier.py",
        "core/longitudinal_assessment_repository.py",
        "app/longitudinal_metacognition_runtime.py",
        "app/longitudinal_assessment_store.py",
    )
    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists()


def test_contract_protected_reasoning_runtime_remains_byte_identical() -> None:
    digest = hashlib.sha256(PROTECTED_RUNTIME.read_bytes()).hexdigest()
    assert digest == EXPECTED_PROTECTED_RUNTIME_SHA256
