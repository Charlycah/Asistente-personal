from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
    LongitudinalIntellectualCurrentEpistemicView,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
METHOD = "_enrich_with_productive_longitudinal_intellectual_reconstruction"


def _bridge():
    bridge = getattr(GovernedRuntimePreparation, METHOD, None)
    if bridge is None:
        pytest.fail(
            "RED: ordinary runtime preparation does not yet transport the certified "
            "longitudinal intellectual reconstruction into conversational inference"
        )
    return bridge


def _reconstruction(*, partial: bool = False):
    current = None
    open_refs: tuple[str, ...] = ()
    if not partial:
        current = LongitudinalIntellectualCurrentEpistemicView(
            assessment_id="assessment-current",
            status="insufficient",
            evidence_references=("evidence-current",),
            open_state_references=("open-question",),
            source_reference="current-epistemic-source",
            source_fingerprint="a" * 64,
        )
        open_refs = ("open-question",)
    return GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct(
        recalled_antecedent_reference="memory:prior-intellectual-material",
        recalled_antecedent_fingerprint="b" * 64,
        recalled_evidence_references=("evidence-recalled",),
        current_epistemic_assessment=current,
        epistemic_delta=None,
        open_state_references=open_refs,
    )


def test_red_bridge_enriches_existing_llm_request_without_replacing_user_prompt(
) -> None:
    bridge = _bridge()
    original = LLMRequest(prompt="Continue the earlier intellectual question.")

    enriched = bridge(original, reconstruction=_reconstruction())

    assert isinstance(enriched, LLMRequest)
    assert enriched is not original
    assert enriched.prompt == original.prompt
    assert enriched.system_prompt != original.system_prompt or enriched.messages != ()


def test_red_bridge_preserves_partial_abstention_in_conversational_context() -> None:
    bridge = _bridge()
    original = LLMRequest(prompt="What can we say now?")
    reconstruction = _reconstruction(partial=True)

    enriched = bridge(original, reconstruction=reconstruction)
    rendered = "\n".join(
        part
        for part in (
            enriched.system_prompt or "",
            *(message.content for message in enriched.messages),
        )
        if part
    ).casefold()

    assert reconstruction.previously_established_status.value in rendered
    assert reconstruction.uncertainty_status.value in rendered
    assert reconstruction.change_status.value in rendered
    assert reconstruction.open_status.value in rendered


def test_red_bridge_conserves_exact_reconstruction_provenance() -> None:
    bridge = _bridge()
    reconstruction = _reconstruction()

    enriched = bridge(LLMRequest(prompt="Continue."), reconstruction=reconstruction)
    rendered = "\n".join(
        part
        for part in (
            enriched.system_prompt or "",
            *(message.content for message in enriched.messages),
        )
        if part
    )

    for reference in reconstruction.evidence_references:
        assert reference in rendered
    for reference in reconstruction.source_references:
        assert reference in rendered
    assert reconstruction.source_fingerprint in rendered


def test_red_bridge_is_transport_only_and_does_not_mutate_reconstruction() -> None:
    bridge = _bridge()
    reconstruction = _reconstruction()
    before = reconstruction.to_dict()
    request = LLMRequest(prompt="Continue.", metadata={"existing": "preserved"})

    enriched = bridge(request, reconstruction=reconstruction)

    assert reconstruction.to_dict() == before
    assert enriched.metadata["existing"] == "preserved"


def test_contract_reuses_existing_llm_request_carrier() -> None:
    request = LLMRequest(prompt="Question", metadata={"lineage": "existing"})
    updated = replace(request, system_prompt="Governed context")

    assert updated.prompt == request.prompt
    assert updated.metadata == request.metadata
    assert updated.system_prompt == "Governed context"


def test_contract_forbids_parallel_longitudinal_conversation_authority() -> None:
    forbidden = (
        "app/longitudinal_conversation_manager.py",
        "app/intellectual_response_authority.py",
        "core/longitudinal_intellectual_store.py",
        "core/reasoning_history_repository.py",
        "app/governed_longitudinal_reasoning_productive_consumption.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()

    source = inspect.getsource(GovernedRuntimePreparation)
    assert "sqlite3" not in source
    assert "LearningAction.STORE" not in source
