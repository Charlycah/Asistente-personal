from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "benchmarks" / "HCPDQ_V2_H7_INDEPENDENT_SCOPE_CONTRACT.json"


def _contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_h7_is_authorized_as_independent_cycle():
    contract = _contract()
    assert contract["status"] == "H7_INDEPENDENT_CYCLE_AUTHORIZED_GO"
    assert contract["go_no_go"]["scope_independence"] == "GO"
    assert contract["baseline"] == "13080-pass-0-fail-ruff-clean"


def test_h6_remains_closed_and_only_productive_baseline_is_inherited():
    predecessor = _contract()["predecessor_h6"]
    assert predecessor["status"] == "CLOSED_FROZEN"
    assert predecessor["historical_primary_result"] == "0/12 SEALED_PRESERVED"
    assert predecessor["productive_fix_status"] == (
        "part_of_current_production_baseline"
    )


def test_h7_forbids_privileged_h6_experimental_transfer():
    forbidden = _contract()["forbidden_h6_transfer"]
    joined = " ".join(forbidden)
    assert "ground-truth" in joined
    assert "observed ROBY answers" in joined
    assert "scoring outcomes" in joined
    assert "benchmark-specific" in joined


def test_h7_exposure_execution_and_scoring_remain_no_go():
    gates = _contract()["go_no_go"]
    assert gates["roby_exposure"] == "NO_GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"


def test_h7_requires_ground_truth_freeze_before_roby_exposure():
    controls = _contract()["required_separation_controls"]
    assert "ground truth must be frozen before ROBY exposure" in controls
    scope = _contract()["h7_scope_freeze"]
    assert scope["roby_exposure_status"] == ("FORBIDDEN_BEFORE_FREEZE_CERTIFICATION")


def test_h7_does_not_authorize_production_change_or_h6_reopen():
    contract = _contract()
    assert contract["production_change_authorized"] is False
    assert contract["h6_reopen_authorized"] is False


def test_next_gate_defines_h7_before_corpus_construction():
    contract = _contract()
    assert contract["next_gate"].endswith("Hypothesis / Measurable Family Contract")
    assert contract["h7_scope_freeze"]["corpus_status"] == "NOT_CONSTRUCTED"
    assert contract["h7_scope_freeze"]["ground_truth_status"] == ("NOT_CONSTRUCTED")
