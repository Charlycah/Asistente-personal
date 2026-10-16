from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from core.adaptive_personality import (
    AdaptivePersonalityAuthority,
    AdaptivePersonalityRequest,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root.preparation import GovernedRuntimePreparation
from core.stable_personality import StablePersonalityEngine

ROOT = Path(__file__).resolve().parents[2]
PREPARATION = ROOT / "core" / "runtime_composition_root" / "preparation.py"
MODELS = ROOT / "core" / "runtime_composition_root" / "models.py"
RUNTIME_FACTORY = ROOT / "app" / "runtime_root_factory.py"
PROJECTION_METHOD = "_enrich_with_canonical_personality_expression"


def _projection():
    projection = getattr(GovernedRuntimePreparation, PROJECTION_METHOD, None)
    if projection is None:
        pytest.fail(
            "RED: ordinary runtime preparation does not yet project the existing "
            "M55/M377 personality expression into LLMRequest"
        )
    return projection


def test_red_1_preparation_has_one_bounded_personality_projection() -> None:
    projection = _projection()
    signature = inspect.signature(projection)
    assert tuple(signature.parameters) == ("request", "stable", "profile")


def test_red_2_projection_preserves_request_and_adds_expression_only() -> None:
    projection = _projection()
    stable = StablePersonalityEngine().evaluate_turn("Explica ROBY")
    profile = AdaptivePersonalityAuthority().adapt(
        stable,
        AdaptivePersonalityRequest(),
    )
    request = LLMRequest(
        prompt="Explica ROBY",
        system_prompt="existing governed context",
        model="owner-model",
        max_tokens=321,
        temperature=0.2,
        metadata={"scope": "ordinary-turn"},
    )

    enriched = projection(request, stable=stable, profile=profile)

    assert enriched.prompt == request.prompt
    assert enriched.model == request.model
    assert enriched.max_tokens == request.max_tokens
    assert enriched.temperature == request.temperature
    assert enriched.metadata == request.metadata
    assert enriched.messages == request.messages
    system_prompt = enriched.system_prompt or ""
    assert "existing governed context" in system_prompt
    assert "stable personality" in system_prompt.casefold()
    assert profile.normalized_tone.value in system_prompt
    assert profile.normalized_detail.value in system_prompt
    assert profile.normalized_structure.value in system_prompt


def test_red_3_prepare_reuses_m55_and_m377_with_default_signals_only() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "stable_personality" in source
    assert "adaptive_personality" in source
    assert "evaluate_turn(request.text" in source
    assert "AdaptivePersonalityRequest()" in source
    assert ".adapt(" in source
    assert PROJECTION_METHOD in source


def test_red_4_first_seam_does_not_infer_richer_humanization_signals() -> None:
    source = PREPARATION.read_text(encoding="utf-8")
    forbidden = (
        "GovernedExpressiveModulation",
        "SimulatedInnerState",
        "RelationshipMemory",
        "SocialRegulation",
        "requested_detail=",
        "requested_structure=",
        "affective_delivery_tone=",
        "sensitive=True",
    )
    for token in forbidden:
        assert token not in source


def test_red_5_existing_composition_boundary_owns_authority_dependencies() -> None:
    models_source = MODELS.read_text(encoding="utf-8")
    factory_source = RUNTIME_FACTORY.read_text(encoding="utf-8")
    assert "stable_personality" in models_source
    assert "adaptive_personality" in models_source
    assert "StablePersonalityEngine" in factory_source
    assert "AdaptivePersonalityAuthority" in factory_source


def test_contract_no_parallel_personality_or_humanization_runtime_is_created() -> None:
    forbidden_paths = (
        "core/humanization_engine.py",
        "core/personality_manager.py",
        "core/personality_runtime.py",
        "app/humanization_runtime.py",
        "app/personality_runtime.py",
        "app/adaptive_personality_runtime.py",
    )
    for relative_path in forbidden_paths:
        assert not (ROOT / relative_path).exists()
