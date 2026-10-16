from __future__ import annotations

import inspect
from dataclasses import fields
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

import core.memory_runtime_integration.models as memory_models
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
)
from core.governed_reasoning.recalled_knowledge_structural_projection import (
    GovernedRecalledKnowledgeStructuralProjector,
)
from core.memory_runtime_integration.models import MemoryRuntimeContext
from core.memory_runtime_integration.runtime import MemoryRuntimeIntegration

ROOT = Path(__file__).resolve().parents[2]
CARRIER = "MemoryRuntimeRecalledAntecedentCandidate"
CONTEXT_FIELD = "recalled_antecedent_candidates"
ADMISSION_METHOD = "admit_recalled_antecedent"


def _carrier_type():
    carrier = getattr(memory_models, CARRIER, None)
    if carrier is None:
        pytest.fail(
            "RED: memory runtime does not yet expose a neutral recalled antecedent "
            "carrier built directly from official recall items"
        )
    return carrier


def _admission_method():
    method = getattr(
        GovernedLongitudinalIntellectualReconstructionFoundationV1,
        ADMISSION_METHOD,
        None,
    )
    if method is None:
        pytest.fail(
            "RED: governed_reasoning does not yet admit exactly one unambiguous "
            "recalled antecedent candidate before longitudinal reconstruction"
        )
    return method


def _candidate(*, memory_id: int, content: str):
    carrier = _carrier_type()
    return carrier(
        scoped_memory_reference=f"private:{memory_id}",
        content_fingerprint=sha256(content.encode("utf-8")).hexdigest(),
        recall_score=0.91,
    )


def test_red_memory_runtime_context_exposes_neutral_recalled_antecedent_candidates(
) -> None:
    names = {item.name for item in fields(MemoryRuntimeContext)}

    assert CONTEXT_FIELD in names, (
        "RED: exact official recall provenance is dropped before ordinary-turn "
        "longitudinal orchestration can consume it"
    )
    carrier = _carrier_type()
    carrier_names = {item.name for item in fields(carrier)}
    assert {
        "scoped_memory_reference",
        "content_fingerprint",
        "recall_score",
    }.issubset(carrier_names)


def test_red_memory_runtime_builds_carrier_directly_from_selected_recall_items(
) -> None:
    source = inspect.getsource(MemoryRuntimeIntegration.enrich)

    assert "recalled_antecedent_candidates=" in source, (
        "RED: MemoryRuntimeIntegration.enrich does not yet preserve selected recall "
        "items as neutral antecedent candidates"
    )
    assert "item.memory.content" in source
    assert "sha256" in source
    assert "decode_memory_planning_evidence" not in source


def test_red_governed_reasoning_admits_one_exact_recalled_antecedent() -> None:
    admit = _admission_method()
    foundation = GovernedLongitudinalIntellectualReconstructionFoundationV1()
    candidate = _candidate(memory_id=7, content="Exact recalled intellectual material")

    admission = admit(foundation, candidates=(candidate,))

    assert admission is not None
    assert admission.antecedent_reference == "private:7"
    assert admission.antecedent_fingerprint == candidate.content_fingerprint
    assert admission.authorizes_longitudinal_identity is False
    assert admission.is_evidence is False


def test_red_governed_reasoning_abstains_for_zero_or_multiple_candidates() -> None:
    admit = _admission_method()
    foundation = GovernedLongitudinalIntellectualReconstructionFoundationV1()
    first = _candidate(memory_id=7, content="First recalled material")
    second = _candidate(memory_id=8, content="Second recalled material")

    assert admit(foundation, candidates=()) is None
    assert admit(foundation, candidates=(first, second)) is None


def test_contract_existing_fingerprint_doctrine_hashes_exact_recalled_content() -> None:
    source = inspect.getsource(
        GovernedRecalledKnowledgeStructuralProjector._project_item
    )

    assert 'sha256(memory.content.encode("utf-8")).hexdigest()' in source
    assert "cognitive-memory:{memory.id}:{content_fingerprint[:16]}" in source


def test_contract_reconstruction_accepts_partial_state_without_synthetic_dimensions(
) -> None:
    result = GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct(
        recalled_antecedent_reference="private:7",
        recalled_antecedent_fingerprint="b" * 64,
        recalled_evidence_references=(),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )

    assert result.evidence_references == ()
    assert result.previously_established_status.value == "not_reconstructable"
    assert result.uncertainty_status.value == "insufficient"
    assert result.change_status.value == "not_comparable"
    assert result.open_status.value == "insufficient"


def test_contract_neutral_carrier_cannot_become_parallel_authority_or_store() -> None:
    forbidden = (
        "core/longitudinal_antecedent_manager.py",
        "core/longitudinal_antecedent_store.py",
        "core/reasoning_history_repository.py",
        "app/longitudinal_antecedent_authority.py",
    )
    for relative_path in forbidden:
        assert not (ROOT / relative_path).exists()

    memory_source = inspect.getsource(MemoryRuntimeIntegration.enrich)
    assert "LearningAction.STORE" not in memory_source
    assert "authorizes_longitudinal_identity" not in memory_source


def test_contract_admission_stays_inside_existing_governed_reasoning_authority(
) -> None:
    foundation = GovernedLongitudinalIntellectualReconstructionFoundationV1()

    assert foundation.CANONICAL_AUTHORITY == "governed_reasoning"
    assert not hasattr(SimpleNamespace(), "canonical_longitudinal_authority")
