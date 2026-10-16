from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts.hcpdq_v2_h6_freeze_certification_exposure_authorization import (
    certify_h6_freeze_for_exposure,
)

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
CASES = BENCH / "hcpdq_v2_h6_entry_path_equivalent_held_out_cases.json"
TRUTH = BENCH / "hcpdq_v2_h6_entry_path_equivalent_ground_truth.json"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_h6_exposure_isolation_protocol() -> dict[str, object]:
    certification = certify_h6_freeze_for_exposure()
    certified = bool(
        certification["freeze_certified"] is True
        and certification["exposure_authorized"] is True
        and certification["primary_execution_authorized"] is False
    )

    protocol = {
        "input_surface": (
            "case_id plus frozen prompt only; prompt delivered unchanged through "
            "the certified productive H6 conversation entry path"
        ),
        "ground_truth_boundary": (
            "ground-truth file is not loaded, passed, imported or exposed by "
            "the exposure adapter"
        ),
        "response_capture": (
            "capture one immutable response record per case_id without scoring"
        ),
        "case_isolation": (
            "fresh evaluation context per case; no prior held-out response is "
            "provided to a later case"
        ),
        "retry_policy": "exactly one attempt per case; retries prohibited",
        "learning_policy": (
            "learning, adaptation, memory writeback and benchmark feedback "
            "prohibited during exposure"
        ),
        "mutation_policy": (
            "corpus, ground truth, prompts and captured responses are immutable"
        ),
        "scoring_policy": (
            "no scoring, labels, expected decisions or ground-truth comparison "
            "during exposure"
        ),
        "failure_policy": (
            "route failure, exception or incomplete capture is recorded as-is; "
            "no retry or repair during exposure"
        ),
    }

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-exposure-isolation-protocol-v1",
        "status": (
            "PROTOCOL_FROZEN_PRE_EXECUTION_TESTS_REQUIRED"
            if certified
            else "NO_GO_EXPOSURE_PROTOCOL_PRECONDITION_FAILED"
        ),
        "baseline": "12986-pass-0-fail-ruff-clean",
        "family": "H6",
        "case_count": certification["case_count"],
        "corpus_sha256": _sha(CASES),
        "ground_truth_sha256": _sha(TRUTH),
        "protocol": protocol,
        "protocol_frozen": certified,
        "exposure_adapter_implemented": False,
        "pre_execution_red_tests_written": False,
        "held_out_prompt_exposure_occurred": False,
        "ground_truth_exposure_occurred": False,
        "scoring_occurred": False,
        "primary_execution_authorized": False,
        "retries_authorized": False,
        "learning_or_adaptation_authorized": False,
        "memory_writeback_authorized": False,
        "benchmark_feedback_authorized": False,
        "production_change_authorized": False,
        "benchmark_translation_authorized": False,
        "benchmark_router_authorized": False,
        "corpus_mutation_authorized": False,
        "ground_truth_mutation_authorized": False,
        "response_mutation_after_capture_authorized": False,
        "architectural_determination": (
            "The exposure boundary is frozen before implementation. The future "
            "adapter may see only frozen case IDs and prompts, must use the "
            "already certified productive H6 entry path, must isolate cases, "
            "must capture exactly one unscored response per case and must never "
            "load ground truth. This gate performs no held-out exposure. "
            "Implementation is blocked until RED isolation contract tests exist."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 ROBY Evaluation Run — "
            "Pre-Execution RED / Isolation Contract Tests"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["protocol_fingerprint"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_h6_exposure_isolation_protocol(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
