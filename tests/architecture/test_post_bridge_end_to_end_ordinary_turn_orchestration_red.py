from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstruction,
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
    LongitudinalIntellectualCurrentEpistemicView,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
ORCHESTRATION_METHOD = (
    "_compose_and_enrich_productive_longitudinal_intellectual_reconstruction"
)
BRIDGE_METHOD = "_enrich_with_productive_longitudinal_intellectual_reconstruction"


def _orchestrator():
    method = getattr(GovernedRuntimePreparation, ORCHESTRATION_METHOD, None)
    if method is None:
        pytest.fail(
            "RED: ordinary-turn preparation does not yet compose the certified "
            "longitudinal reconstruction and pass it through the certified "
            "conversational bridge"
        )
    return method


def _current_view() -> LongitudinalIntellectualCurrentEpistemicView:
    return LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="assessment-current",
        status="insufficient",
        evidence_references=("evidence-current",),
        open_state_references=("open-question",),
        source_reference="current-epistemic-source",
        source_fingerprint="a" * 64,
    )


def _kwargs() -> dict[str, object]:
    return {
        "recalled_antecedent_reference": "memory:prior-intellectual-material",
        "recalled_antecedent_fingerprint": "b" * 64,
        "recalled_evidence_references": ("evidence-recalled",),
        "current_epistemic_assessment": _current_view(),
        "epistemic_delta": None,
        "open_state_references": ("open-question",),
    }


def test_red_ordinary_turn_orchestration_uses_existing_runtime_composer_and_bridge(
) -> None:
    orchestrate = _orchestrator()
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = LLMRequest(prompt="Continue the earlier intellectual question.")

    enriched = orchestrate(
        request,
        reasoning_runtime=gateway,
        **_kwargs(),
    )

    assert isinstance(enriched, LLMRequest)
    assert enriched.prompt == request.prompt
    assert "[GOVERNED LONGITUDINAL INTELLECTUAL RECONSTRUCTION]" in (
        enriched.system_prompt or ""
    )


def test_red_ordinary_turn_orchestration_preserves_core_partial_abstention() -> None:
    orchestrate = _orchestrator()
    gateway = OfficialGovernedReasoningRuntimeGateway()

    enriched = orchestrate(
        LLMRequest(prompt="What can we say now?"),
        reasoning_runtime=gateway,
        recalled_antecedent_reference="memory:prior-intellectual-material",
        recalled_antecedent_fingerprint="b" * 64,
        recalled_evidence_references=("evidence-recalled",),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )
    rendered = (enriched.system_prompt or "").casefold()

    assert "not_reconstructable" in rendered
    assert "insufficient" in rendered
    assert "not_comparable" in rendered


def test_red_ordinary_turn_orchestration_conserves_exact_admitted_provenance() -> None:
    orchestrate = _orchestrator()
    gateway = OfficialGovernedReasoningRuntimeGateway()

    enriched = orchestrate(
        LLMRequest(prompt="Continue."),
        reasoning_runtime=gateway,
        **_kwargs(),
    )
    rendered = enriched.system_prompt or ""

    for admitted in (
        "memory:prior-intellectual-material",
        "evidence-recalled",
        "evidence-current",
        "current-epistemic-source",
    ):
        assert admitted in rendered
    for forbidden in ("topic_similarity", "thread_similarity", "family_c", "same"):
        assert forbidden not in rendered.casefold()


def test_red_ordinary_turn_orchestration_does_not_fabricate_when_inputs_absent(
) -> None:
    orchestrate = _orchestrator()
    gateway = OfficialGovernedReasoningRuntimeGateway()
    request = LLMRequest(prompt="Ordinary turn", metadata={"existing": "preserved"})

    result = orchestrate(
        request,
        reasoning_runtime=gateway,
        recalled_antecedent_reference=None,
        recalled_antecedent_fingerprint=None,
        recalled_evidence_references=(),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )

    assert result == request


def test_contract_existing_runtime_composer_is_thin_core_delegation() -> None:
    composer = (
        OfficialGovernedReasoningRuntimeGateway
        .compose_productive_longitudinal_intellectual_reconstruction
    )
    source = inspect.getsource(composer)
    expected_delegation = (
        "GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct"
    )
    assert expected_delegation in source
    assert "sqlite3" not in source
    assert "LearningAction.STORE" not in source


def test_contract_existing_bridge_is_transport_only() -> None:
    bridge = getattr(GovernedRuntimePreparation, BRIDGE_METHOD)
    source = inspect.getsource(bridge)
    assert "replace(request, system_prompt=system_prompt)" in source
    assert "GovernedLongitudinalIntellectualReconstructionFoundationV1" not in source
    assert "sqlite3" not in source


def test_contract_core_reconstruction_remains_read_only_and_non_authorizing() -> None:
    reconstruction: GovernedLongitudinalIntellectualReconstruction = (
        GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct(
            recalled_antecedent_reference="memory:prior-intellectual-material",
            recalled_antecedent_fingerprint="b" * 64,
            recalled_evidence_references=("evidence-recalled",),
            current_epistemic_assessment=None,
            epistemic_delta=None,
            open_state_references=(),
        )
    )
    assert reconstruction.read_only is True
    assert reconstruction.creates_memory is False
    assert reconstruction.creates_learning_candidate is False
    assert reconstruction.invokes_investigation is False
    assert reconstruction.invokes_planning is False
    assert reconstruction.executes_actions is False
    assert reconstruction.authorizes_longitudinal_identity is False
    assert reconstruction.authorizes_autonomous_continuation is False


def test_contract_forbids_parallel_orchestration_authority() -> None:
    forbidden = (
        "app/longitudinal_orchestration_manager.py",
        "app/intellectual_continuation_authority.py",
        "core/longitudinal_orchestration_store.py",
        "core/reasoning_history_repository.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()
