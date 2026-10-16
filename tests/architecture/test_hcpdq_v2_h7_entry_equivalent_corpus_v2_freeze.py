from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.hcpdq_v2_h7_entry_equivalent_corpus_v2_freeze import (
    materialize_and_probe,
)

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "benchmarks" / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2.json"
CERT = (
    ROOT
    / "benchmarks"
    / "HCPDQ_V2_H7_ENTRY_EQUIVALENT_CORPUS_V2_CERTIFICATE.json"
)


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_h7v2_is_new_independent_namespace_and_keeps_old_evidence_immutable():
    corpus = _load(CORPUS)
    assert corpus["namespace"] == "V2I-H7V2"
    assert corpus["case_count"] == 12
    assert all(case["case_id"].startswith("V2I-H7V2-") for case in corpus["cases"])


def test_h7v2_all_materialized_requirement_ids_satisfy_productive_contract():
    corpus = _load(CORPUS)
    requirements = [
        case["requirement"]
        for case in corpus["cases"]
        if case["requirement"] is not None
    ]
    assert len(requirements) == 8
    assert all(
        item["requirement_id"].startswith("discrimination-requirement-")
        for item in requirements
    )


def test_h7v2_freezes_causal_state_structurally_not_only_in_prose():
    corpus = _load(CORPUS)
    required = {
        "episode_id",
        "originating_reasoning_id",
        "source_reference",
        "world_snapshot_id",
        "requirement_ids",
        "plan_ids",
        "authorization_ids",
        "execution_ids",
        "reentry_ids",
        "consumed_acquisitions",
        "current_step",
        "status",
        "stopping_reason",
    }
    assert all(
        required <= set(case["pre_continuation_state"])
        for case in corpus["cases"]
    )


def test_h7v2_real_dry_probe_materializes_every_case_through_productive_types():
    corpus = _load(CORPUS)
    observations = [
        materialize_and_probe(case)
        for case in corpus["cases"]
    ]
    assert len(observations) == 12
    assert all(item["case_id"] for item in observations)


def test_h7v2_real_dry_probe_exercises_continue_stop_and_review_topology():
    corpus = _load(CORPUS)
    observations = [
        materialize_and_probe(case)
        for case in corpus["cases"]
    ]
    decisions = [item["continuation_decision"] for item in observations]
    assert decisions.count("continue_allowed") == 4
    assert decisions.count("stop_required") == 4
    assert decisions.count("review_required") == 4


def test_h7v2_only_continue_allowed_cases_invoke_existing_planning():
    corpus = _load(CORPUS)
    observations = [
        materialize_and_probe(case)
        for case in corpus["cases"]
    ]
    invoked = [
        item for item in observations
        if item["planning_invocation_count"] == 1
    ]
    assert len(invoked) == 4
    assert all(item["planning_reentry_status"] == "planned" for item in invoked)


def test_h7v2_certificate_persists_no_case_level_probe_outputs_or_truth():
    cert = _load(CERT)
    assert cert["status"] == "REAL_DRY_PROBE_CERTIFIED_AND_FROZEN"
    assert cert["materialized_productive_type_count"] == 12
    assert cert["materialization_failures"] == 0
    assert cert["case_level_outputs_persisted"] is False
    assert cert["ground_truth_created_or_opened"] is False
    assert cert["scoring_performed"] is False
    assert cert["execution_authorized"] is False


def test_h7v2_certificate_is_hash_bound_to_frozen_corpus():
    cert = _load(CERT)
    assert hashlib.sha256(CORPUS.read_bytes()).hexdigest() == (
        cert["corpus_file_sha256"]
    )
    corpus = _load(CORPUS)
    assert cert["corpus_freeze_sha256"] == corpus["freeze_sha256"]
