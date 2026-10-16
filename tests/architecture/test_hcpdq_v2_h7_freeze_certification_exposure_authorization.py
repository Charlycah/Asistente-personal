from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"
CORPUS = BENCHMARKS / "HCPDQ_V2_H7_INDEPENDENT_CORPUS.json"
TRUTH = BENCHMARKS / "HCPDQ_V2_H7_INDEPENDENT_GROUND_TRUTH.json"
CERT = BENCHMARKS / "HCPDQ_V2_H7_FREEZE_CERTIFICATION_EXPOSURE_AUTHORIZATION.json"


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _content_hash(payload):
    clean = dict(payload)
    clean.pop("freeze_sha256", None)
    canonical = json.dumps(
        clean,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_h7_frozen_payload_hashes_are_still_exact():
    corpus = _load(CORPUS)
    truth = _load(TRUTH)
    assert _content_hash(corpus) == corpus["freeze_sha256"]
    assert _content_hash(truth) == truth["freeze_sha256"]


def test_h7_certification_binds_exact_frozen_payloads():
    cert = _load(CERT)
    corpus = _load(CORPUS)
    truth = _load(TRUTH)
    bindings = cert["certified_bindings"]
    assert bindings["corpus_freeze_sha256"] == corpus["freeze_sha256"]
    assert bindings["ground_truth_freeze_sha256"] == truth["freeze_sha256"]
    assert truth["corpus_freeze_sha256"] == corpus["freeze_sha256"]


def test_h7_certification_preserves_case_and_class_balance():
    bindings = _load(CERT)["certified_bindings"]
    assert bindings["case_count"] == 12
    assert bindings["difficulty_counts"] == {"D1": 4, "D2": 4, "D3": 4}
    assert bindings["class_counts"] == {"PLANNED": 6, "FAIL_CLOSED": 6}


def test_h7_exposure_can_use_only_roby_facing_corpus():
    protocol = _load(CERT)["exposure_protocol"]
    assert protocol["authorized_input"] == ("HCPDQ_V2_H7_INDEPENDENT_CORPUS.json only")
    assert protocol["ground_truth_access_during_exposure"] == "FORBIDDEN"
    assert protocol["ground_truth_access_during_primary_execution"] == "FORBIDDEN"


def test_h7_exposure_authorization_does_not_authorize_execution():
    protocol = _load(CERT)["exposure_protocol"]
    assert protocol["may_execute_roby"] is False
    assert protocol["may_invoke_planning"] is False
    assert protocol["may_score"] is False


def test_h7_frozen_material_cannot_be_modified_after_authorization():
    protocol = _load(CERT)["exposure_protocol"]
    assert protocol["may_modify_corpus"] is False
    assert protocol["may_modify_ground_truth"] is False


def test_h7_gate_authorizes_isolation_work_only():
    gates = _load(CERT)["go_no_go"]
    assert gates["freeze_certification"] == "GO"
    assert gates["corpus_exposure_preparation"] == "GO"
    assert gates["isolation_contract_tests"] == "GO"
    assert gates["primary_execution"] == "NO_GO"
    assert gates["ground_truth_opening"] == "NO_GO"
    assert gates["scoring"] == "NO_GO"
    assert gates["production_change"] == "NO_GO"


def test_h7_next_gate_is_exposure_isolation_protocol():
    cert = _load(CERT)
    assert cert["status"] == "FREEZE_CERTIFIED_EXPOSURE_AUTHORIZED"
    assert cert["next_gate"].endswith("Exposure / Isolation Protocol")
