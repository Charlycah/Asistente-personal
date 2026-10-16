from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v1_roby_evaluation_run import preflight_frozen_run

ROOT = Path(__file__).resolve().parents[2]
BENCHMARKS = ROOT / "benchmarks"


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def test_primary_run_manifest_is_pre_exposure_frozen():
    manifest = json.loads(
        (BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    assert manifest["status"] == "pre_exposure_frozen"
    assert manifest["run_id"] == "HCPDQ-V1-ROBY-XI2-PRIMARY-001"
    assert manifest["baseline"] == "12808-pass-0-fail-ruff-clean"


def test_primary_run_manifest_freezes_exact_case_order():
    manifest = json.loads(
        (BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    order = manifest["execution_policy"]["case_order"]
    assert len(order) == 120
    assert len(set(order)) == 120
    assert order == sorted(order)


def test_primary_run_manifest_freezes_isolation_and_zero_retries():
    manifest = json.loads(
        (BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    policy = manifest["execution_policy"]
    assert policy["retries"] == 0
    assert policy["timeout_seconds_per_case"] == 30
    assert policy["isolation"] == "fresh_case_context"
    assert policy["feedback_between_cases"] is False
    assert policy["memory_writes"] is False
    assert policy["learning_writes"] is False


def test_primary_run_manifest_fingerprint_is_reproducible():
    manifest = json.loads(
        (BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    expected = manifest.pop("manifest_fingerprint")
    actual = sha256(_canonical_json(manifest).encode("utf-8")).hexdigest()
    assert actual == expected


def test_final_preflight_uses_official_12808_package_identity():
    manifest = json.loads(
        (BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json").read_text(
            encoding="utf-8"
        )
    )
    preflight = preflight_frozen_run()
    assert preflight.baseline == "12808-pass-0-fail-ruff-clean"
    assert preflight.package_fingerprint == manifest["package_sha256"]
    assert preflight.case_order == tuple(
        manifest["execution_policy"]["case_order"]
    )
