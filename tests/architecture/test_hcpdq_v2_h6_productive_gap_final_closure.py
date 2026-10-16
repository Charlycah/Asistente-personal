from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLOSURE = ROOT / "benchmarks" / "HCPDQ_V2_H6_PRODUCTIVE_GAP_FINAL_CLOSURE.json"


def _closure():
    return json.loads(CLOSURE.read_text(encoding="utf-8"))


def test_h6_productive_gap_is_formally_closed():
    closure = _closure()
    assert closure["decision"] == "CLOSE"
    assert closure["status"] == "PRODUCTIVE_GAP_CLOSED"
    assert closure["baseline"] == "13074-pass-0-fail-ruff-clean"


def test_historical_zero_of_twelve_remains_sealed():
    historical = _closure()["historical_primary_result"]
    assert historical["status"] == "SEALED_PRESERVED"
    assert historical["pass"] == 0
    assert historical["fail"] == 12
    assert historical["accuracy"] == 0.0


def test_closure_does_not_require_historical_rerun_or_rescoring():
    closure = _closure()
    assert closure["held_out_rerun_required"] is False
    assert closure["old_primary_rescoring_required"] is False
    assert closure["old_primary_result_must_remain_unchanged"] is True


def test_closure_keeps_broad_incomplete_evidence_dominance_forbidden():
    closure = _closure()
    assert closure["generic_incomplete_evidence_dominance_authorized"] is False
    assert closure["benchmark_specific_behavior_present"] is False


def test_closure_surface_is_green():
    surface = _closure()["closure_surface"]
    assert surface["pass"] == 48
    assert surface["fail"] == 0


def test_closure_defines_explicit_reopen_conditions():
    closure = _closure()
    assert len(closure["reopen_conditions"]) == 5
    assert any(
        "multiple required-constraint survivors" in item
        for item in closure["reopen_conditions"]
    )
