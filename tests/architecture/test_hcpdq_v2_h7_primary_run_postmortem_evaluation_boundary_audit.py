from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H7_PRIMARY_RUN_POSTMORTEM_EVALUATION_BOUNDARY_AUDIT.json"
)


def _audit():
    return json.loads(AUDIT.read_text(encoding="utf-8"))


def test_h7_postmortem_classifies_run_as_evaluation_design_invalid():
    audit = _audit()
    assert audit["status"] == "EVALUATION_DESIGN_INVALID_RECONTRACT_REQUIRED"
    assert audit["cognitive_scoring_valid"] is False
    assert audit["performance_conclusion_authorized"] is False


def test_h7_all_frozen_requirement_ids_fail_productive_identifier_contract():
    finding = _audit()["findings"]["requirement_identifier_equivalence"]
    assert finding["frozen_case_count"] == 12
    assert finding["productive_compatible_count"] == 0
    assert finding["productive_incompatible_count"] == 12
    assert finding["determination"] == "FAIL"


def test_h7_corpus_did_not_freeze_required_causal_state():
    finding = _audit()["findings"]["causal_state_serialization"]
    missing = " ".join(
        finding["required_productive_conditions_not_structurally_frozen"]
    )
    assert "eligible_for_existing_planning" in missing
    assert "resulting_state.status" in missing
    assert "current_step" in missing
    assert "plan_ids" in missing
    assert finding["determination"] == "FAIL"


def test_h7_dry_probe_constructibility_was_a_false_positive():
    gap = _audit()["findings"]["dry_probe_gap"]
    assert gap["determination"] == ("FALSE_POSITIVE_CONSTRUCTIBILITY_CERTIFICATION")
    assert "exact productive requirement/continuation" in gap["missing_check"]


def test_h7_abort_does_not_demonstrate_adapter_or_cognitive_failure():
    findings = _audit()["findings"]
    assert findings["adapter_determination"]["fault_demonstrated"] is False
    assert (
        findings["productive_roby_determination"]["cognitive_failure_demonstrated"]
        is False
    )


def test_h7_postmortem_keeps_truth_scoring_retry_and_production_closed():
    audit = _audit()
    gates = audit["go_no_go"]
    assert audit["ground_truth_inspected_in_audit"] is False
    assert audit["ground_truth_validity_determined"] is False
    assert gates["old_corpus_retry"] == "NO_GO"
    assert gates["old_primary_rerun"] == "NO_GO"
    assert gates["old_ground_truth_opening"] == "NO_GO"
    assert gates["old_run_scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"


def test_h7_postmortem_forbids_benchmark_translation_patch():
    gates = _audit()["go_no_go"]
    assert gates["benchmark_translation_patch"] == "NO_GO"
    assert _audit()["benchmark_translation_authorized"] is False


def test_h7_postmortem_requires_new_independent_entry_equivalent_freeze():
    audit = _audit()
    gates = audit["go_no_go"]
    assert gates["new_independent_recontract"] == "GO"
    assert gates["new_independent_freeze_scope"] == "GO_AFTER_RECONTRACT"
    requirements = " ".join(audit["required_recontract_properties"])
    assert "new independent H7 corpus namespace" in requirements
    assert "exact governed productive input types" in requirements
    assert "structurally encoded" in requirements
    assert audit["next_gate"].endswith("Recontract / New Independent Freeze Scope")
