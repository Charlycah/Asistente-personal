from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "app" / "hcpdq_v2_h7_isolation_adapter.py"
RECERT = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H7_MINIMAL_ISOLATION_ADAPTER_CAUSAL_RECERTIFICATION.json"
)


def _recert():
    return json.loads(RECERT.read_text(encoding="utf-8"))


def _imported_modules():
    tree = ast.parse(ADAPTER.read_text(encoding="utf-8"))
    return {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }


def test_h7_adapter_green_is_causally_bound_to_missing_adapter_red():
    findings = _recert()["causal_findings"]
    assert findings["red_cause"] == ("dedicated H7 isolation adapter module was absent")
    assert findings["red_now_green"] is True
    assert findings["protective_contracts_still_green"] is True
    assert findings["unrelated_productive_authority_modified"] is False


def test_h7_adapter_imports_only_existing_productive_planning_surface():
    modules = _imported_modules()
    assert "app.governed_multistep_investigation_planning_reentry" in modules
    assert not any("ground_truth" in module for module in modules)
    assert not any("scor" in module for module in modules)


def test_h7_adapter_owns_no_cognitive_or_planning_authority():
    audit = _recert()["authority_audit"]
    assert audit["cognitive_authority_owned_by_adapter"] is False
    assert audit["planning_authority_created"] is False
    assert audit["direct_internal_planner_imported"] is False
    assert audit["benchmark_answer_router_present"] is False


def test_h7_boundary_preserves_single_attempt_and_raw_seal():
    boundary = _recert()["boundary_audit"]
    assert boundary["corpus_only_validation"] is True
    assert boundary["ground_truth_fields_rejected"] is True
    assert boundary["single_attempt_enforced"] is True
    assert boundary["retry_forbidden"] is True
    assert boundary["raw_capture_single_write_sha256_sealed"] is True


def test_h7_boundary_exposes_no_prior_results_or_writeback():
    boundary = _recert()["boundary_audit"]
    assert boundary["prior_results_visible"] is False
    assert boundary["learning_memory_world_writeback_authorized"] is False
    assert boundary["primary_execution_blocked"] is True


def test_h7_recertification_did_not_execute_or_score():
    execution = _recert()["execution_attestation"]
    assert execution["roby_primary_executed"] is False
    assert execution["planning_invoked_for_evaluation"] is False
    assert execution["ground_truth_opened"] is False
    assert execution["scoring_performed"] is False


def test_h7_recertification_authorizes_only_final_preflight():
    gates = _recert()["go_no_go"]
    assert gates["causal_recertification"] == "GO"
    assert gates["architectural_recertification"] == "GO"
    assert gates["final_preflight_manifest_freeze"] == "GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["ground_truth_opening"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"
