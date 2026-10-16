from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from app.official_conversation_gateway import OfficialConversationGateway

ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = ROOT / "benchmarks"
HELD_OUT_PATH = BENCHMARKS / "hcpdq_v1_held_out_cases.json"
GROUND_TRUTH_PATH = BENCHMARKS / "hcpdq_v1_ground_truth.json"
RUBRICS_PATH = BENCHMARKS / "hcpdq_v1_rubrics.json"
FREEZE_MANIFEST_PATH = BENCHMARKS / "HCPDQ_V1_FREEZE_MANIFEST.json"
RUN_MANIFEST_PATH = BENCHMARKS / "HCPDQ_V1_ROBY_PRIMARY_RUN_MANIFEST.json"
PRIMARY_CASE_COUNT = 120


@dataclass(frozen=True)
class RunPolicy:
    retries: int = 0
    order: str = "case_id"
    isolation: str = "fresh_case_context"
    allow_memory_writes: bool = False
    allow_learning_writes: bool = False
    allow_threshold_adaptation: bool = False
    allow_self_improvement: bool = False


@dataclass(frozen=True)
class CaseContext:
    case_id: str
    previous_results: tuple[object, ...] = ()


@dataclass(frozen=True)
class RawObservation:
    case_id: str
    raw_response: str | None
    latency_ms: float
    provenance_ok: bool
    authority_violation: bool
    unauthorized_side_effect: bool


@dataclass(frozen=True)
class ExecutionOutcome:
    observed: str | None
    timeout: bool
    infrastructure_error: str | None


@dataclass(frozen=True)
class RunManifest:
    status: str
    roby_version: str
    baseline: str
    package_fingerprint: str
    held_out_fingerprint: str
    ground_truth_fingerprint: str
    rubric_fingerprint: str
    retries: int
    case_order: tuple[str, ...]


def _canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _fingerprint(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def default_run_policy() -> RunPolicy:
    return RunPolicy()


def build_subject_payload(case: dict[str, Any]) -> dict[str, Any]:
    return {
        key: case[key]
        for key in ("case_id", "family", "difficulty", "prompt")
    }


def new_case_context(case_id: str) -> CaseContext:
    return CaseContext(case_id=case_id)


def validate_primary_run_cases(cases: list[dict[str, Any]]) -> None:
    if len(cases) != PRIMARY_CASE_COUNT:
        raise ValueError("primary HCPDQ-v1 run requires exactly 120 cases")
    case_ids = [str(case["case_id"]) for case in cases]
    if len(set(case_ids)) != PRIMARY_CASE_COUNT:
        raise ValueError("primary HCPDQ-v1 case IDs must be unique")


def verify_frozen_artifacts(
    *,
    held_out: list[dict[str, Any]],
    ground_truth: dict[str, Any],
    rubrics: dict[str, Any],
    freeze_manifest: dict[str, Any],
) -> None:
    validate_primary_run_cases(held_out)
    expected = {
        "held_out": freeze_manifest["held_out"]["fingerprint"],
        "ground_truth": freeze_manifest["ground_truth_fingerprint"],
        "rubrics": freeze_manifest["rubric_fingerprint"],
    }
    actual = {
        "held_out": _fingerprint(held_out),
        "ground_truth": _fingerprint(ground_truth),
        "rubrics": _fingerprint(rubrics),
    }
    if actual != expected:
        raise ValueError("HCPDQ-v1 frozen artifact fingerprint mismatch")


def evaluate_subject_case(
    gateway: OfficialConversationGateway,
    subject_payload: dict[str, Any],
):
    """Evaluate only through ROBY's existing official conversation boundary."""
    return gateway.converse(str(subject_payload["prompt"]))


def capture_raw_observation(
    *,
    case_id: str,
    gateway: OfficialConversationGateway,
    subject_payload: dict[str, Any],
    provenance_ok: bool = True,
    authority_violation: bool = False,
    unauthorized_side_effect: bool = False,
) -> RawObservation:
    started = perf_counter()
    turn = evaluate_subject_case(gateway, subject_payload)
    latency_ms = (perf_counter() - started) * 1000.0
    return RawObservation(
        case_id=case_id,
        raw_response=getattr(turn, "response_text", None),
        latency_ms=latency_ms,
        provenance_ok=provenance_ok,
        authority_violation=authority_violation,
        unauthorized_side_effect=unauthorized_side_effect,
    )


def score_captured_observation(
    raw: RawObservation,
    scorer: Callable[[RawObservation], object],
) -> object:
    """Score an already immutable observation outside the productive call."""
    return scorer(raw)


def normalize_execution_outcome(
    *,
    raw_response: str | None,
    timed_out: bool,
    infrastructure_error: str | None,
) -> ExecutionOutcome:
    if timed_out:
        return ExecutionOutcome(
            observed=None,
            timeout=True,
            infrastructure_error=infrastructure_error,
        )
    if infrastructure_error is not None:
        return ExecutionOutcome(
            observed=None,
            timeout=False,
            infrastructure_error=infrastructure_error,
        )
    observed = raw_response.strip() if isinstance(raw_response, str) else None
    return ExecutionOutcome(
        observed=observed,
        timeout=False,
        infrastructure_error=None,
    )


def case_can_pass(
    *,
    cognitively_correct: bool,
    provenance_ok: bool,
    authority_violation: bool,
    unauthorized_side_effect: bool,
) -> bool:
    return bool(
        cognitively_correct
        and provenance_ok
        and not authority_violation
        and not unauthorized_side_effect
    )


def build_run_manifest(
    *,
    roby_version: str,
    baseline: str,
    package_fingerprint: str,
    held_out_fingerprint: str,
    ground_truth_fingerprint: str,
    rubric_fingerprint: str,
) -> RunManifest:
    cases = _load_json(HELD_OUT_PATH)
    validate_primary_run_cases(cases)
    policy = default_run_policy()
    return RunManifest(
        status="pre_exposure_frozen",
        roby_version=roby_version,
        baseline=baseline,
        package_fingerprint=package_fingerprint,
        held_out_fingerprint=held_out_fingerprint,
        ground_truth_fingerprint=ground_truth_fingerprint,
        rubric_fingerprint=rubric_fingerprint,
        retries=policy.retries,
        case_order=tuple(sorted(str(case["case_id"]) for case in cases)),
    )


def preflight_frozen_run() -> RunManifest:
    held_out = _load_json(HELD_OUT_PATH)
    ground_truth = _load_json(GROUND_TRUTH_PATH)
    rubrics = _load_json(RUBRICS_PATH)
    freeze_manifest = _load_json(FREEZE_MANIFEST_PATH)
    frozen_inputs = {
        "held_out": held_out,
        "ground_truth": ground_truth,
        "rubrics": rubrics,
        "freeze_manifest": freeze_manifest,
    }
    verify_frozen_artifacts(**frozen_inputs)
    return build_run_manifest(
        roby_version="XI.2",
        baseline="12808-pass-0-fail-ruff-clean",
        package_fingerprint=(
            _load_json(RUN_MANIFEST_PATH)["package_sha256"]
        ),
        held_out_fingerprint=freeze_manifest["held_out"]["fingerprint"],
        ground_truth_fingerprint=freeze_manifest["ground_truth_fingerprint"],
        rubric_fingerprint=freeze_manifest["rubric_fingerprint"],
    )
