from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from core.governed_reasoning import longitudinal_intellectual_reconstruction as lir

ROOT = Path(__file__).resolve().parents[2]
TARGET = (
    ROOT
    / "core"
    / "governed_reasoning"
    / "longitudinal_intellectual_reconstruction.py"
)


def _prior_support(*, status: str = "supported"):
    support_type = lir.LongitudinalIntellectualPriorEstablishedEpistemicSupport
    return support_type(
        status=status,
        evidence_references=("evidence:prior:1",),
        source_reference="reasoning:prior",
        source_fingerprint="c" * 64,
    )


def _current(*, status: str = "supported"):
    return lir.LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="epistemic-current",
        status=status,
        evidence_references=("evidence:current:1",),
        open_state_references=(),
        source_reference="reasoning:current",
        source_fingerprint="d" * 64,
    )


class _Delta:
    def __init__(self, kind: str) -> None:
        self.kind = kind
        self.before_evidence_references = ("evidence:prior:1",)
        self.after_evidence_references = ("evidence:current:1",)
        self.triggering_evidence_references = ("evidence:trigger:1",)


def _reconstruct(*, prior_support, delta):
    return lir.GovernedLongitudinalIntellectualReconstructionFoundationV1().reconstruct(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=("evidence:prior:1",),
        prior_established_epistemic_support=prior_support,
        current_epistemic_assessment=_current(),
        epistemic_delta=delta,
        open_state_references=(),
    )


def test_n1_red_prior_support_is_an_explicit_governed_input() -> None:
    signature = inspect.signature(
        lir.GovernedLongitudinalIntellectualReconstructionFoundationV1.reconstruct
    )

    assert "prior_established_epistemic_support" in signature.parameters
    support = _prior_support()
    assert support.canonical_authority == "governed_reasoning"
    assert support.derived is True
    assert support.read_only is True
    assert support.is_evidence is False
    assert support.establishes_truth is False
    assert support.establishes_falsity is False
    assert support.persists_results is False
    assert support.creates_memory is False
    assert support.modifies_world_model is False
    assert support.grants_authority is False


def test_n1_red_explicit_prior_support_reconstructs_previous_status() -> None:
    status = lir.LongitudinalIntellectualReconstructionDimensionStatus

    result = _reconstruct(
        prior_support=_prior_support(),
        delta=_Delta("evidence_changed"),
    )

    assert result.previously_established_status is status.SUPPORTED
    assert result.change_status is status.CHANGED
    assert "evidence:prior:1" in result.evidence_references
    assert "evidence:current:1" in result.evidence_references
    assert "evidence:trigger:1" in result.evidence_references
    assert "reasoning:prior" in result.source_references
    assert "reasoning:current" in result.source_references


def test_n1_red_unchanged_delta_preserves_supported_continuity() -> None:
    status = lir.LongitudinalIntellectualReconstructionDimensionStatus

    result = _reconstruct(prior_support=_prior_support(), delta=_Delta("unchanged"))

    assert result.previously_established_status is status.SUPPORTED
    assert result.change_status is status.UNCHANGED


def test_n1_red_missing_prior_support_preserves_historical_abstention() -> None:
    status = lir.LongitudinalIntellectualReconstructionDimensionStatus

    result = _reconstruct(prior_support=None, delta=_Delta("evidence_changed"))

    assert result.previously_established_status in {
        status.INSUFFICIENT,
        status.NOT_RECONSTRUCTABLE,
    }
    assert result.change_status is status.CHANGED


def test_n1_red_incompatible_prior_support_fails_closed() -> None:
    with pytest.raises(ValueError):
        _prior_support(status="")


def test_n1_red_temporal_reconstruction_does_not_gain_authority() -> None:
    result = _reconstruct(
        prior_support=_prior_support(),
        delta=_Delta("evidence_changed"),
    )

    assert result.read_only is True
    assert result.is_evidence is False
    assert result.is_claim is False
    assert result.establishes_truth is False
    assert result.establishes_falsity is False
    assert result.persists_results is False
    assert result.creates_memory is False
    assert result.creates_learning_candidate is False
    assert result.modifies_world_model is False
    assert result.invokes_planning is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_n1_red_no_parallel_temporal_authority_is_introduced() -> None:
    source = TARGET.read_text(encoding="utf-8")

    for forbidden in (
        "TemporalWorldModel",
        "TemporalReasoningManager",
        "TemporalMemory",
        "sqlite3",
        "Repository",
    ):
        assert forbidden not in source
