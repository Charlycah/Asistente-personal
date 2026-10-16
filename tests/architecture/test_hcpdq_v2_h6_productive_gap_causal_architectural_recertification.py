from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

from core import governed_complex_decision_reasoning as reasoner

ROOT = Path(__file__).resolve().parents[2]
REPORT = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H6_PRODUCTIVE_GAP_CAUSAL_ARCHITECTURAL_RECERTIFICATION.json"
)


def _report():
    return json.loads(REPORT.read_text(encoding="utf-8"))


def test_recertification_keeps_existing_governed_authority():
    report = _report()
    assert report["existing_authority_preserved"] is True
    assert report["authority_class"] == ("GovernedComplexDecisionReasoningFoundationV1")
    assert report["canonical_authority_preserved"] == ("unified_cognitive_coordination")
    assert report["canonical_facade_preserved"] == "CanonicalDecisionFacade"


def test_recertification_contains_no_benchmark_or_truth_dependency():
    report = _report()
    assert report["benchmark_specific_imports_present"] is False
    assert report["hcpdq_specific_literals_present"] is False
    assert report["ground_truth_dependency_present"] is False
    assert report["adapter_dependency_present"] is False
    assert report["entry_path_dependency_present"] is False


def test_required_survivor_helper_is_general_and_fail_closed():
    source = inspect.getsource(reasoner.GovernedComplexDecisionReasoningFoundationV1)
    tree = ast.parse(source)
    names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert "_sole_required_constraint_survivor" in names
    assert "hcpdq" not in source.casefold()
    assert "ground_truth" not in source.casefold()


def test_recertification_preserves_missing_evidence_and_blocking_semantics():
    report = _report()
    mechanism = report["causal_mechanism"]
    assert "INSUFFICIENT" in mechanism["missing_evidence_semantics"]
    assert "BLOCKED" in mechanism["blocked_option_semantics"]
    assert mechanism["generic_dominance_relaxation"] is False


def test_recertification_confirms_contract_and_regression_surfaces_green():
    report = _report()
    assert report["red_contracts_green"] == 6
    assert report["focused_reasoner_surface_pass"] == 28
    assert report["relevant_gcdr_surface_pass"] == 118
    assert report["status"] == "CAUSAL_ARCHITECTURAL_RECERTIFIED"


def test_recertification_does_not_reopen_experimental_boundary():
    report = _report()
    assert report["held_out_rerun_performed"] is False
    assert report["old_primary_rescoring_performed"] is False
    assert report["production_tuning_outside_contract_performed"] is False
    assert report["next_gate"].endswith("Calibration / Generalization Certification")
