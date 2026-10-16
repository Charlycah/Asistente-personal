from __future__ import annotations

from pathlib import Path

import pytest

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstruction,
    LongitudinalIntellectualCurrentEpistemicView,
    LongitudinalIntellectualReconstructionDimensionStatus,
)

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "app" / "governed_reasoning_runtime.py"
METHOD = "compose_productive_longitudinal_intellectual_reconstruction"


def _require_wiring(gateway: OfficialGovernedReasoningRuntimeGateway):
    wiring = getattr(gateway, METHOD, None)
    if wiring is None:
        pytest.fail(
            "RED: governed reasoning runtime does not yet consume the certified "
            "longitudinal intellectual reconstruction core composition"
        )
    return wiring


def test_red_1_runtime_exposes_only_a_consumer_of_the_existing_core_authority() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    assert callable(_require_wiring(gateway))


def test_red_2_productive_wiring_preserves_partial_abstention() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    wiring = _require_wiring(gateway)

    result = wiring(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=(),
        current_epistemic_assessment=None,
        epistemic_delta=None,
        open_state_references=(),
    )

    assert isinstance(result, GovernedLongitudinalIntellectualReconstruction)
    assert result.previously_established_status in {
        LongitudinalIntellectualReconstructionDimensionStatus.INSUFFICIENT,
        LongitudinalIntellectualReconstructionDimensionStatus.NOT_RECONSTRUCTABLE,
    }
    assert (
        result.change_status
        is LongitudinalIntellectualReconstructionDimensionStatus.NOT_COMPARABLE
    )


def test_red_3_productive_wiring_delegates_current_epistemic_semantics_to_core(
) -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    wiring = _require_wiring(gateway)
    current = LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="epistemic-sufficiency-current",
        status="insufficient",
        evidence_references=("evidence:current:1",),
        open_state_references=("gap:current:1",),
        source_reference="reasoning:current",
        source_fingerprint="b" * 64,
    )

    result = wiring(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=(),
        current_epistemic_assessment=current,
        epistemic_delta=None,
        open_state_references=("gap:current:1",),
    )

    assert (
        result.uncertainty_status
        is LongitudinalIntellectualReconstructionDimensionStatus.SUPPORTED
    )
    assert result.open_status is (
        LongitudinalIntellectualReconstructionDimensionStatus.SUPPORTED
    )


def test_red_4_productive_wiring_cannot_expand_admitted_provenance() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()
    wiring = _require_wiring(gateway)
    current = LongitudinalIntellectualCurrentEpistemicView(
        assessment_id="epistemic-sufficiency-current",
        status="insufficient",
        evidence_references=("evidence:current:1",),
        open_state_references=("gap:current:1",),
        source_reference="reasoning:current",
        source_fingerprint="b" * 64,
    )
    admitted = {
        "memory:41",
        "evidence:prior:1",
        "evidence:current:1",
        "gap:current:1",
        "reasoning:current",
    }

    result = wiring(
        recalled_antecedent_reference="memory:41",
        recalled_antecedent_fingerprint="a" * 64,
        recalled_evidence_references=("evidence:prior:1",),
        current_epistemic_assessment=current,
        epistemic_delta=None,
        open_state_references=("gap:current:1",),
    )

    assert set(result.evidence_references).issubset(admitted)
    assert set(result.source_references).issubset(admitted)


def test_red_5_wiring_introduces_no_new_authority_store_or_identity_path() -> None:
    source = RUNTIME.read_text(encoding="utf-8")

    assert "LongitudinalIntellectualStateManager" not in source
    assert "ReasoningHistoryRepository" not in source
    assert "longitudinal_intellectual_identity" not in source
    assert "governed_longitudinal_reasoning_productive_consumption" not in source
