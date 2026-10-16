from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = (
    ROOT / "benchmarks" / "HCPDQ_V2_H7_HYPOTHESIS_MEASURABLE_FAMILY_CONTRACT.json"
)


def _contract():
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_h7_hypothesis_and_measurable_family_are_frozen():
    contract = _contract()
    assert contract["status"] == "H7_HYPOTHESIS_MEASURABLE_FAMILY_FROZEN_GO"
    assert contract["family"] == "H7"
    assert contract["baseline"] == "13087-pass-0-fail-ruff-clean"


def test_h7_uses_only_preexisting_certified_productive_surface():
    hypothesis = _contract()["hypothesis"]
    assert hypothesis["productive_surface"] == (
        "GovernedMultiStepInvestigationPlanningReentryV1"
    )
    assert hypothesis["canonical_authority"] == "planning_foundation"
    assert "exactly once" in hypothesis["statement"]


def test_h7_pass_requires_lineage_single_invocation_and_nonexecution():
    positive = " ".join(_contract()["pass_contract"]["positive_case"])
    assert "exactly 1" in positive
    assert "lineage is preserved" in positive
    assert "execution_authorized is false" in positive
    assert "mutation flags remain false" in positive


def test_h7_fail_closed_contract_blocks_semantic_expansion():
    fail_closed = " ".join(_contract()["pass_contract"]["fail_closed_case"])
    assert "must not fabricate PLANNED" in fail_closed
    assert "more than once" in fail_closed
    assert "cannot be scored as success" in fail_closed
    assert "planning authority" in fail_closed


def test_h7_scope_excludes_execution_general_planning_and_state_writes():
    excluded = " ".join(_contract()["explicit_non_scope"])
    assert "plan execution" in excluded
    assert "general task planning" in excluded
    assert "learning" in excluded
    assert "world-model mutation" in excluded
    assert "benchmark-specific" in excluded


def test_h7_construction_remains_independent_from_h6_and_prior_h7():
    constraints = " ".join(_contract()["construction_constraints"])
    assert "H6 prompts" in constraints
    assert "prior H7 held-out cases" in constraints
    assert "calibration prompts" in constraints
    assert "ROBY outputs" in constraints


def test_h7_difficulty_levels_are_defined_without_expanding_authority():
    dimensions = _contract()["difficulty_dimensions"]
    assert set(dimensions) == {"D1", "D2", "D3"}
    assert "evidence-acquisition" in dimensions["D1"]
    assert "fail-closed" in dimensions["D2"]
    assert "without changing authority" in dimensions["D3"]


def test_h7_corpus_construction_is_go_but_exposure_remains_no_go():
    gates = _contract()["go_no_go"]
    assert gates["corpus_construction"] == "GO"
    assert gates["ground_truth_freeze"] == "GO_AFTER_INDEPENDENT_CONSTRUCTION"
    assert gates["roby_exposure"] == "NO_GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"
