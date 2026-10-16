from __future__ import annotations

import inspect
from pathlib import Path

from app.longitudinal_intellectual_reconstruction_productive_adapter import (
    LongitudinalIntellectualReconstructionProductiveAdapterV1,
)
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    LongitudinalIntellectualCurrentEpistemicView,
)
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
PROJECTION_METHOD = "project_current_epistemic_view"
ORCHESTRATION_HELPER = (
    "_compose_and_enrich_productive_longitudinal_intellectual_reconstruction"
)
EPISTEMIC_BINDING_HELPER = "_bind_productive_epistemic_episode"


def test_red_existing_productive_adapter_exposes_bounded_current_view_projection() -> (
    None
):
    projection = getattr(
        LongitudinalIntellectualReconstructionProductiveAdapterV1,
        PROJECTION_METHOD,
        None,
    )
    assert callable(projection), (
        "RED: the existing longitudinal reconstruction productive adapter does not "
        "yet project an already-governed productive epistemic episode into the "
        "existing LongitudinalIntellectualCurrentEpistemicView contract"
    )


def test_red_projection_contract_reuses_existing_current_view_type() -> None:
    projection = getattr(
        LongitudinalIntellectualReconstructionProductiveAdapterV1,
        PROJECTION_METHOD,
        None,
    )
    assert callable(projection), "RED: bounded current epistemic projection is absent"
    annotation = inspect.signature(projection).return_annotation
    assert annotation in {
        LongitudinalIntellectualCurrentEpistemicView,
        "LongitudinalIntellectualCurrentEpistemicView | None",
    }, (
        "RED: projection must reuse the existing current epistemic view rather than "
        "introducing a parallel longitudinal state DTO"
    )


def test_red_prepare_binds_epistemic_episode_before_longitudinal_reconstruction() -> (
    None
):
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    bind_at = source.find(EPISTEMIC_BINDING_HELPER)
    reconstruct_at = source.find(ORCHESTRATION_HELPER)

    assert bind_at >= 0, "RED: ordinary prepare() lacks existing epistemic binding"
    assert reconstruct_at >= 0, "RED: ordinary prepare() lacks reconstruction wiring"
    assert bind_at < reconstruct_at, (
        "RED: longitudinal reconstruction still runs before the same-turn governed "
        "epistemic episode is available for bounded current-view projection"
    )


def test_red_prepare_supplies_projected_current_epistemic_view() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert PROJECTION_METHOD in source, (
        "RED: ordinary prepare() does not yet ask the existing bounded productive "
        "adapter to project the same-turn epistemic episode"
    )
    assert "current_epistemic_assessment=current_epistemic_view" in source, (
        "RED: the projected current epistemic view does not yet reach the existing "
        "longitudinal reconstruction consumer"
    )


def test_protective_prepare_does_not_synthesize_unproven_longitudinal_inputs() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "recalled_evidence_references=()" in source
    assert "epistemic_delta=None" in source
    assert "open_state_references=()" in source


def test_protective_projection_stays_outside_canonical_reasoning_runtime() -> None:
    source = (ROOT / "app/governed_reasoning_runtime.py").read_text(encoding="utf-8")
    assert f"def {PROJECTION_METHOD}" not in source, (
        "bounded transport projection must not become a second semantic authority "
        "inside the protected canonical reasoning runtime"
    )
