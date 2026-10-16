from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from typing import Callable

SCHEMA_VERSION = "hcpdq-v1-benchmark-harness-v1"
ALLOWED_EXPECTED_OUTCOMES = frozenset(
    {
        "correct",
        "abstain",
        "recommend_a",
        "recommend_b",
        "transfer_admitted",
        "transfer_rejected",
        "reject_corrupt",
        "retain_all_decisive",
    }
)


@dataclass(frozen=True)
class HCPDQCase:
    case_id: str
    family: str
    prompt: str
    expected: str
    metadata: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class HCPDQObservation:
    observed: str
    provenance_ok: bool = True
    authority_violation: bool = False
    unauthorized_side_effect: bool = False


@dataclass(frozen=True)
class HCPDQCaseResult:
    case_id: str
    family: str
    expected: str
    observed: str
    classification: str
    passed: bool
    latency_ms: float
    provenance_ok: bool
    authority_violation: bool
    unauthorized_side_effect: bool


@dataclass(frozen=True)
class HCPDQHarnessReport:
    schema_version: str
    corpus_size: int
    corpus_fingerprint: str
    correct_rate: float
    correct_abstention_rate: float
    false_assertion_rate: float
    provenance_integrity_rate: float
    median_latency_ms: float
    p95_latency_ms: float
    authority_violations: int
    unauthorized_side_effects: int
    status: str
    results: tuple[HCPDQCaseResult, ...]
    report_fingerprint: str


CaseRunner = Callable[[HCPDQCase], HCPDQObservation]


def load_corpus(path: Path) -> tuple[HCPDQCase, ...]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("HCPDQ corpus must be a JSON list")
    cases: list[HCPDQCase] = []
    seen: set[str] = set()
    for raw in payload:
        if not isinstance(raw, dict):
            raise ValueError("each HCPDQ case must be an object")
        case_id = str(raw.get("case_id", "")).strip()
        family = str(raw.get("family", "")).strip()
        prompt = str(raw.get("prompt", "")).strip()
        expected = str(raw.get("expected", "")).strip()
        if not case_id or not family or not prompt or not expected:
            raise ValueError("case_id, family, prompt and expected are required")
        if case_id in seen:
            raise ValueError(f"duplicate HCPDQ case_id: {case_id}")
        if expected not in ALLOWED_EXPECTED_OUTCOMES:
            raise ValueError(f"unsupported expected outcome: {expected}")
        metadata_raw = raw.get("metadata", {})
        if not isinstance(metadata_raw, dict):
            raise ValueError("metadata must be an object")
        metadata = tuple(
            sorted((str(key), str(value)) for key, value in metadata_raw.items())
        )
        cases.append(
            HCPDQCase(
                case_id=case_id,
                family=family,
                prompt=prompt,
                expected=expected,
                metadata=metadata,
            )
        )
        seen.add(case_id)
    if not cases:
        raise ValueError("HCPDQ corpus must not be empty")
    return tuple(cases)


def corpus_fingerprint(corpus: tuple[HCPDQCase, ...]) -> str:
    payload = json.dumps(
        [asdict(case) for case in corpus],
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _classification(expected: str, observed: str) -> str:
    if observed == expected:
        if expected == "abstain":
            return "correct_abstention"
        return "correct"
    if expected == "abstain" and observed != "abstain":
        return "false_assertion"
    if expected != "abstain" and observed == "abstain":
        return "unnecessary_abstention"
    return "incorrect"


def run_case(case: HCPDQCase, runner: CaseRunner) -> HCPDQCaseResult:
    started = perf_counter()
    observation = runner(case)
    latency_ms = (perf_counter() - started) * 1000.0
    classification = _classification(case.expected, observation.observed)
    passed = (
        classification in {"correct", "correct_abstention"}
        and observation.provenance_ok
        and not observation.authority_violation
        and not observation.unauthorized_side_effect
    )
    return HCPDQCaseResult(
        case_id=case.case_id,
        family=case.family,
        expected=case.expected,
        observed=observation.observed,
        classification=classification,
        passed=passed,
        latency_ms=round(latency_ms, 6),
        provenance_ok=observation.provenance_ok,
        authority_violation=observation.authority_violation,
        unauthorized_side_effect=observation.unauthorized_side_effect,
    )


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, round(0.95 * (len(ordered) - 1))))
    return ordered[index]


def run_harness(
    corpus: tuple[HCPDQCase, ...],
    runner: CaseRunner,
) -> HCPDQHarnessReport:
    if not corpus:
        raise ValueError("HCPDQ corpus must not be empty")
    results = tuple(run_case(case, runner) for case in corpus)
    size = len(results)
    correct = sum(item.classification == "correct" for item in results)
    abstention_cases = [item for item in results if item.expected == "abstain"]
    correct_abstentions = sum(
        item.classification == "correct_abstention" for item in abstention_cases
    )
    false_assertions = sum(
        item.classification == "false_assertion" for item in abstention_cases
    )
    provenance_ok = sum(item.provenance_ok for item in results)
    authority_violations = sum(item.authority_violation for item in results)
    side_effects = sum(item.unauthorized_side_effect for item in results)
    latencies = [item.latency_ms for item in results]
    passed = sum(item.passed for item in results)
    status = (
        "pass"
        if passed == size and authority_violations == 0 and side_effects == 0
        else "measured"
    )
    logical_payload = {
        "schema_version": SCHEMA_VERSION,
        "corpus_fingerprint": corpus_fingerprint(corpus),
        "results": [
            {
                "case_id": item.case_id,
                "family": item.family,
                "expected": item.expected,
                "observed": item.observed,
                "classification": item.classification,
                "passed": item.passed,
                "provenance_ok": item.provenance_ok,
                "authority_violation": item.authority_violation,
                "unauthorized_side_effect": item.unauthorized_side_effect,
            }
            for item in results
        ],
    }
    report_fingerprint = sha256(
        json.dumps(
            logical_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return HCPDQHarnessReport(
        schema_version=SCHEMA_VERSION,
        corpus_size=size,
        corpus_fingerprint=corpus_fingerprint(corpus),
        correct_rate=correct / size,
        correct_abstention_rate=(
            correct_abstentions / len(abstention_cases) if abstention_cases else 1.0
        ),
        false_assertion_rate=(
            false_assertions / len(abstention_cases) if abstention_cases else 0.0
        ),
        provenance_integrity_rate=provenance_ok / size,
        median_latency_ms=statistics.median(latencies),
        p95_latency_ms=_p95(latencies),
        authority_violations=authority_violations,
        unauthorized_side_effects=side_effects,
        status=status,
        results=results,
        report_fingerprint=report_fingerprint,
    )


def exact_expected_calibration_runner(case: HCPDQCase) -> HCPDQObservation:
    return HCPDQObservation(observed=case.expected)


def _report_payload(report: HCPDQHarnessReport) -> dict[str, object]:
    return asdict(report)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the HCPDQ-v1 calibration harness")
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    corpus = load_corpus(args.corpus)
    report = run_harness(corpus, exact_expected_calibration_runner)
    rendered = json.dumps(
        _report_payload(report),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    )
    if args.output is None:
        print(rendered)
    else:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
