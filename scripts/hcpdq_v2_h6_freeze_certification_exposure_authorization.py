from __future__ import annotations

import hashlib
import json
from pathlib import Path

from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
)

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "benchmarks"
CASES = BENCH / "hcpdq_v2_h6_entry_path_equivalent_held_out_cases.json"
TRUTH = BENCH / "hcpdq_v2_h6_entry_path_equivalent_ground_truth.json"
FREEZE = BENCH / "HCPDQ_V2_H6_ENTRY_PATH_EQUIVALENT_CORPUS_FREEZE.json"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def certify_h6_freeze_for_exposure() -> dict[str, object]:
    cases = _load(CASES)
    truth = _load(TRUTH)
    freeze = _load(FREEZE)
    parser = ExplicitComplexDecisionIntakeEnvelopeFoundationV1()

    corpus_hash_match = _sha(CASES) == freeze["corpus_sha256"]
    truth_hash_match = _sha(TRUTH) == freeze["ground_truth_sha256"]
    ids = [case["case_id"] for case in cases]
    truth_ids = [item["case_id"] for item in truth]
    ids_aligned = ids == truth_ids == freeze["case_ids"]
    unique_ids = len(ids) == len(set(ids)) == freeze["case_count"]
    intake_statuses = {
        case["case_id"]: parser.analyze(case["prompt"]).status.value
        for case in cases
    }
    all_entry_equivalent = all(
        status == "complete" for status in intake_statuses.values()
    )
    frozen_clean = bool(
        freeze["corpus_frozen"] is True
        and freeze["ground_truth_frozen"] is True
        and freeze["roby_exposure_occurred"] is False
        and freeze["roby_execution_occurred"] is False
        and freeze["ground_truth_exposed_to_roby"] is False
    )
    certified = all(
        (
            corpus_hash_match,
            truth_hash_match,
            ids_aligned,
            unique_ids,
            all_entry_equivalent,
            frozen_clean,
        )
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-freeze-certification-v1",
        "status": (
            "FREEZE_CERTIFIED_EXPOSURE_AUTHORIZED"
            if certified
            else "NO_GO_FREEZE_CERTIFICATION_FAILED"
        ),
        "baseline": "12980-pass-0-fail-ruff-clean",
        "family": "H6",
        "case_count": len(cases),
        "corpus_hash_match": corpus_hash_match,
        "ground_truth_hash_match": truth_hash_match,
        "case_ids_aligned": ids_aligned,
        "case_ids_unique": unique_ids,
        "entry_path_statuses": intake_statuses,
        "entry_path_equivalent": all_entry_equivalent,
        "pre_certification_exposure_absent": frozen_clean,
        "freeze_certified": certified,
        "exposure_authorized": certified,
        "exposure_scope": (
            "read-only corpus prompts through the already certified H6 "
            "productive entry path"
        ),
        "ground_truth_exposure_authorized": False,
        "scoring_authorized_during_exposure": False,
        "learning_or_adaptation_authorized": False,
        "production_change_authorized": False,
        "benchmark_translation_authorized": False,
        "benchmark_router_authorized": False,
        "primary_execution_authorized": False,
        "corpus_mutation_authorized": False,
        "ground_truth_mutation_authorized": False,
        "architectural_determination": (
            "The frozen H6 corpus and ground truth retain their exact bound "
            "hashes, aligned unique case IDs and complete productive intake "
            "grammar. No prior ROBY or ground-truth exposure is recorded. "
            "First read-only corpus exposure is authorized solely through the "
            "existing certified H6 path. Ground truth, scoring, adaptation, "
            "production changes and primary execution remain prohibited."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 ROBY Evaluation Run — "
            "Exposure / Isolation Protocol"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["certification_fingerprint"] = hashlib.sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            certify_h6_freeze_for_exposure(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
