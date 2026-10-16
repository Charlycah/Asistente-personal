from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from scripts.hcpdq_v2_h6_h7_freeze_certification import (
    certify_h6_h7_held_out_freeze,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"
CASES = BENCHMARKS / "hcpdq_v2_h6_h7_held_out_cases.json"
GROUND_TRUTH = BENCHMARKS / "hcpdq_v2_h6_h7_ground_truth.json"


@dataclass(frozen=True)
class ExposureIsolationPolicy:
    allowed_families: tuple[str, ...] = ("H6", "H7")
    allow_ground_truth_read: bool = False
    allow_memory_writes: bool = False
    allow_learning_writes: bool = False
    allow_threshold_adaptation: bool = False
    allow_self_improvement: bool = False
    allow_persistent_state_writes: bool = False
    allow_production_changes: bool = False
    allow_human_comparison: bool = False
    allow_primary_execution: bool = False


@dataclass(frozen=True)
class SubjectEnvelope:
    case_id: str
    family: str
    difficulty: str
    prompt: str


def default_isolation_policy() -> ExposureIsolationPolicy:
    return ExposureIsolationPolicy()


def build_subject_envelope(case: dict[str, Any]) -> SubjectEnvelope:
    allowed = {"case_id", "family_code", "difficulty", "prompt"}
    if not allowed.issubset(case):
        raise ValueError("held-out case lacks required subject fields")
    family = str(case["family_code"]).strip().upper()
    if family not in {"H6", "H7"}:
        raise ValueError("case is outside frozen HCPDQ-v2 scope")
    return SubjectEnvelope(
        case_id=str(case["case_id"]),
        family=family,
        difficulty=str(case["difficulty"]),
        prompt=str(case["prompt"]),
    )


def subject_envelope_contains_ground_truth(envelope: SubjectEnvelope) -> bool:
    serialized = asdict(envelope)
    forbidden = {
        "ground_truth_reference",
        "expected_outcome",
        "rationale",
        "required_structure",
    }
    return bool(forbidden & set(serialized))


def freeze_exposure_isolation_protocol() -> dict[str, object]:
    certification = certify_h6_h7_held_out_freeze()
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    envelopes = [build_subject_envelope(case) for case in cases]
    policy = default_isolation_policy()

    certified = (
        certification["status"] == "CERTIFIED_EXPOSURE_AUTHORIZED"
        and certification["roby_exposure_authorized"] is True
        and certification["held_out_execution_authorized"] is False
    )
    isolated = all(
        not subject_envelope_contains_ground_truth(envelope)
        for envelope in envelopes
    )
    policy_closed = all(
        (
            not policy.allow_ground_truth_read,
            not policy.allow_memory_writes,
            not policy.allow_learning_writes,
            not policy.allow_threshold_adaptation,
            not policy.allow_self_improvement,
            not policy.allow_persistent_state_writes,
            not policy.allow_production_changes,
            not policy.allow_human_comparison,
            not policy.allow_primary_execution,
        )
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-exposure-isolation-protocol-v1",
        "status": (
            "PROTOCOL_FROZEN_PREEXECUTION_RED_AUTHORIZED"
            if certified and isolated and policy_closed
            else "NO_GO_PROTOCOL_ISOLATION_FAILED"
        ),
        "baseline": "12918-pass-0-fail-ruff-clean",
        "certified_scope": ["H6", "H7"],
        "case_count": len(envelopes),
        "subject_envelope_fields": [
            "case_id",
            "family",
            "difficulty",
            "prompt",
        ],
        "ground_truth_path": str(GROUND_TRUTH.relative_to(PROJECT_ROOT)),
        "ground_truth_available_to_subject": False,
        "ground_truth_loaded_by_subject_adapter": False,
        "scoring_occurs_after_raw_capture": True,
        "fresh_case_context_required": True,
        "cross_case_result_visibility": False,
        "retries": 0,
        "order": "case_id",
        "policy": asdict(policy),
        "certification_precondition_pass": certified,
        "subject_envelope_isolated": isolated,
        "policy_closed": policy_closed,
        "controlled_exposure_authorized": True,
        "preexecution_red_tests_authorized": True,
        "primary_execution_authorized": False,
        "human_comparison_authorized": False,
        "production_change_authorized": False,
        "architectural_determination": (
            "The evaluation subject may receive only case identity, frozen "
            "family/difficulty metadata and prompt text. Ground truth and "
            "scoring remain outside the subject boundary. No memory, learning, "
            "adaptation, persistence, production mutation or cross-case state "
            "is authorized. This freezes the protocol only; primary held-out "
            "execution remains blocked pending RED isolation tests and a "
            "minimal adapter certification."
        ),
        "next_gate": (
            "HCPDQ-v2 H6/H7 ROBY Evaluation Run — Pre-Execution RED / "
            "Isolation Contract Tests"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["protocol_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_exposure_isolation_protocol(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
