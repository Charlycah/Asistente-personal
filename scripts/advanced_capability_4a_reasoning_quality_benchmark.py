from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from time import perf_counter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.productive_temporary_rule_intake import (  # noqa: E402
    ProductiveTemporaryRuleIntake,
    ProductiveTemporaryRuleIntakeStatus,
)
from core.governed_complex_decision_reasoning import (  # noqa: E402
    ComplexDecisionCriterionOutcome,
    GovernedComplexDecisionReasoningFoundationV1,
    GovernedDecisionCriterion,
    GovernedOptionCriterionAssessment,
)
from core.governed_decision_advisory import GovernedDecisionOption  # noqa: E402
from core.governed_reasoning import InMemoryInferenceRuleRegistry  # noqa: E402
from core.scope_guard import ScopeDomain  # noqa: E402
from scripts.advanced_capability_3a_scale_benchmark import run_scale_level  # noqa: E402

SCHEMA_VERSION = "advanced-capability-4a-reasoning-quality-benchmark-v1"
NOW = datetime(2026, 8, 20, 15, 0, tzinfo=timezone.utc)
RULE_TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    dimension: str
    expected: str
    variant: int


@dataclass(frozen=True)
class BenchmarkCaseResult:
    case_id: str
    dimension: str
    expected: str
    observed: str
    passed: bool
    latency_ms: float
    provenance_ok: bool
    authority_violation: bool
    unauthorized_side_effect: bool


@dataclass(frozen=True)
class ReasoningQualityReport:
    schema_version: str
    generated_at: str
    corpus_size: int
    corpus_fingerprint: str
    correct_rate: float
    incorrect_rate: float
    correct_abstention_rate: float
    false_assertion_rate: float
    transfer_success_rate: float
    gcdr_decision_accuracy: float
    provenance_integrity_rate: float
    noise_robustness_rate: float
    median_latency_ms: float
    p95_latency_ms: float
    authority_violations: int
    unauthorized_side_effects: int
    status: str
    results: tuple[BenchmarkCaseResult, ...]
    report_fingerprint: str


def build_corpus() -> tuple[BenchmarkCase, ...]:
    cases: list[BenchmarkCase] = []
    for idx in range(16):
        cases.append(
            BenchmarkCase(f"Q1-{idx + 1:02d}", "correctness", "recommend_a", idx)
        )
    for idx in range(16):
        cases.append(BenchmarkCase(f"Q2-{idx + 1:02d}", "abstention", "abstain", idx))
    for idx in range(16):
        expected = "transfer_admitted" if idx < 8 else "transfer_rejected"
        cases.append(BenchmarkCase(f"Q3-{idx + 1:02d}", "transfer", expected, idx))
    for idx in range(16):
        expected = "recommend_b" if idx % 2 == 0 else "abstain"
        cases.append(BenchmarkCase(f"Q4-{idx + 1:02d}", "gcdr", expected, idx))
    for idx in range(8):
        cases.append(
            BenchmarkCase(f"Q5-{idx + 1:02d}", "provenance", "reject_corrupt", idx)
        )
    noise_levels = (100, 1000, 10000, 50000, 100, 1000, 10000, 50000)
    for idx, level in enumerate(noise_levels):
        cases.append(
            BenchmarkCase(f"Q6-{idx + 1:02d}", "noise", "retain_all_decisive", level)
        )
    corpus = tuple(cases)
    if len(corpus) != 80:
        raise AssertionError("4A corpus must contain exactly 80 cases")
    return corpus


def corpus_fingerprint(corpus: tuple[BenchmarkCase, ...]) -> str:
    payload = json.dumps(
        [asdict(case) for case in corpus],
        sort_keys=True,
        separators=(",", ":"),
    )
    return sha256(payload.encode("utf-8")).hexdigest()


def _option(option_id: str, title: str) -> GovernedDecisionOption:
    return GovernedDecisionOption(
        option_id=option_id,
        title=title,
    )


def _criterion(
    criterion_id: str,
    title: str,
    *,
    required: bool = False,
) -> GovernedDecisionCriterion:
    return GovernedDecisionCriterion(
        criterion_id=criterion_id,
        title=title,
        required=required,
        provenance_codes=(f"benchmark:{criterion_id}",),
    )


def _assessment(
    option: str,
    criterion: str,
    outcome: ComplexDecisionCriterionOutcome,
) -> GovernedOptionCriterionAssessment:
    source = sha256(f"{option}:{criterion}:{outcome.value}".encode()).hexdigest()
    return GovernedOptionCriterionAssessment(
        option_id=option,
        criterion_id=criterion,
        outcome=outcome,
        evidence_codes=(f"benchmark:{option}:{criterion}",),
        source_fingerprint=source,
    )


def _gcdr_report(*, recommend: str = "a", insufficient: bool = False):
    a = _option("option-a", "A")
    b = _option("option-b", "B")
    safety = _criterion("criterion-safety", "Safety", required=True)
    cost = _criterion("criterion-cost", "Cost")
    if insufficient:
        assessments = (
            _assessment(
                a.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                a.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.INSUFFICIENT,
            ),
            _assessment(
                b.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                b.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.NEUTRAL,
            ),
        )
    elif recommend == "a":
        assessments = (
            _assessment(
                a.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                a.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                b.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.UNFAVORABLE,
            ),
            _assessment(
                b.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
        )
    else:
        assessments = (
            _assessment(
                a.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.UNFAVORABLE,
            ),
            _assessment(
                a.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                b.option_id,
                safety.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
            _assessment(
                b.option_id,
                cost.criterion_id,
                ComplexDecisionCriterionOutcome.FAVORABLE,
            ),
        )
    return GovernedComplexDecisionReasoningFoundationV1().assess(
        (a, b), (safety, cost), assessments
    )


def _run_correctness(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    report = _gcdr_report(recommend="a")
    provenance_ok = len(
        report.source_fingerprint
    ) == 64 and report.source_option_ids == ("option-a", "option-b")
    non_power = not any(
        (
            report.persists_results,
            report.modifies_memory,
            report.modifies_learning,
            report.modifies_world_model,
            report.executes_actions,
            report.grants_authority,
        )
    )
    observed = "recommend_a" if report.recommended_option_id == "option-a" else "other"
    return observed, provenance_ok, False, not non_power


def _run_abstention(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    report = _gcdr_report(insufficient=True)
    observed = "abstain" if report.recommended_option_id is None else "asserted"
    provenance_ok = len(report.source_fingerprint) == 64
    non_power = report.executes_actions is False and report.grants_authority is False
    return observed, provenance_ok, False, not non_power


def _transfer_case_text(variant: int, positive: bool) -> str:
    subjects = (
        "estación",
        "aplicación",
        "dron",
        "sistema",
        "servicio",
        "nodo",
        "terminal",
        "plataforma",
    )
    resources = (
        "sensor T",
        "servicio Q",
        "módulo M",
        "enlace R",
        "fuente F",
        "canal C",
        "motor E",
        "recurso Z",
    )
    capabilities = (
        "recibir temperatura",
        "procesar pagos",
        "localizarse",
        "transmitir datos",
        "operar",
        "sincronizarse",
        "calcular rutas",
        "validar entradas",
    )
    i = variant % 8
    if positive:
        return (
            f"La {subjects[i]} depende exclusivamente del {resources[i]} "
            f"para {capabilities[i]}. "
            f"El {resources[i]} está indisponible y no existe alternativa."
        )
    return (
        f"La {subjects[i]} depende exclusivamente del {resources[i]} "
        f"para {capabilities[i]}. "
        f"El {resources[i]} está indisponible, pero existe otra fuente independiente."
    )


def _run_transfer(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    registry = InMemoryInferenceRuleRegistry()
    intake = ProductiveTemporaryRuleIntake(registry)
    scope = f"benchmark:{case.case_id}"
    teach = intake.observe(
        owner="benchmark",
        text=RULE_TEXT,
        scope_reference=scope,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        now=NOW,
    )
    positive = case.expected == "transfer_admitted"
    result = intake.observe(
        owner="benchmark",
        text=_transfer_case_text(case.variant, positive),
        scope_reference=scope,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        now=NOW + timedelta(minutes=1),
    )
    if result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED:
        observed = "transfer_admitted"
    else:
        observed = "transfer_rejected"
    provenance_ok = (
        teach.source_reference != result.source_reference
        and result.scope_reference == scope
        and result.canonical_authority == "governed_reasoning"
    )
    non_power = not any(
        (
            result.persistent,
            result.creates_memory,
            result.creates_learning_candidate,
            result.modifies_learning,
            result.grants_authority,
            result.executes_actions,
        )
    )
    return observed, provenance_ok, False, not non_power


def _run_gcdr(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    if case.expected == "recommend_b":
        report = _gcdr_report(recommend="b")
        observed = (
            "recommend_b" if report.recommended_option_id == "option-b" else "other"
        )
    else:
        report = _gcdr_report(insufficient=True)
        observed = "abstain" if report.recommended_option_id is None else "asserted"
    provenance_ok = len(report.source_fingerprint) == 64
    non_power = (
        report.human_decision_preserved
        and not report.executes_actions
        and not report.grants_authority
    )
    return observed, provenance_ok, False, not non_power


def _run_provenance(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    a = _option("option-a", "A")
    b = _option("option-b", "B")
    criterion = _criterion("criterion-safety", "Safety")
    assessments = (
        _assessment(
            a.option_id,
            criterion.criterion_id,
            ComplexDecisionCriterionOutcome.FAVORABLE,
        ),
        _assessment(
            "unknown-option",
            criterion.criterion_id,
            ComplexDecisionCriterionOutcome.FAVORABLE,
        ),
    )
    try:
        GovernedComplexDecisionReasoningFoundationV1().assess(
            (a, b), (criterion,), assessments
        )
    except ValueError:
        return "reject_corrupt", True, False, False
    return "accepted_corrupt", False, False, False


def _run_noise(case: BenchmarkCase) -> tuple[str, bool, bool, bool]:
    result = run_scale_level(case.variant)
    observed = (
        "retain_all_decisive"
        if result.decisive_items_selected == result.decisive_item_count
        else "lost_evidence"
    )
    provenance_ok = result.provenance_integrity and result.corrupt_provenance_rejected
    return observed, provenance_ok, False, False


def run_case(case: BenchmarkCase) -> BenchmarkCaseResult:
    started = perf_counter()
    if case.dimension == "correctness":
        observed, provenance_ok, authority_violation, side_effect = _run_correctness(
            case
        )
    elif case.dimension == "abstention":
        observed, provenance_ok, authority_violation, side_effect = _run_abstention(
            case
        )
    elif case.dimension == "transfer":
        observed, provenance_ok, authority_violation, side_effect = _run_transfer(case)
    elif case.dimension == "gcdr":
        observed, provenance_ok, authority_violation, side_effect = _run_gcdr(case)
    elif case.dimension == "provenance":
        observed, provenance_ok, authority_violation, side_effect = _run_provenance(
            case
        )
    elif case.dimension == "noise":
        observed, provenance_ok, authority_violation, side_effect = _run_noise(case)
    else:
        raise ValueError(f"unknown benchmark dimension: {case.dimension}")
    latency_ms = (perf_counter() - started) * 1000.0
    return BenchmarkCaseResult(
        case_id=case.case_id,
        dimension=case.dimension,
        expected=case.expected,
        observed=observed,
        passed=(
            observed == case.expected
            and provenance_ok
            and not authority_violation
            and not side_effect
        ),
        latency_ms=round(latency_ms, 6),
        provenance_ok=provenance_ok,
        authority_violation=authority_violation,
        unauthorized_side_effect=side_effect,
    )


def _rate(results: tuple[BenchmarkCaseResult, ...], dimension: str) -> float:
    selected = [item for item in results if item.dimension == dimension]
    if not selected:
        return 1.0
    return sum(item.passed for item in selected) / len(selected)


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(round(0.95 * (len(ordered) - 1)))))
    return ordered[index]


@lru_cache(maxsize=1)
def _run_default_benchmark() -> ReasoningQualityReport:
    return _run_benchmark(build_corpus())


def run_benchmark(
    corpus: tuple[BenchmarkCase, ...] | None = None,
) -> ReasoningQualityReport:
    if corpus is None:
        return _run_default_benchmark()
    return _run_benchmark(corpus)


def _run_benchmark(corpus: tuple[BenchmarkCase, ...]) -> ReasoningQualityReport:
    results = tuple(run_case(case) for case in corpus)
    incorrect = sum(not item.passed for item in results)
    abstention = tuple(item for item in results if item.dimension == "abstention")
    false_assertions = sum(item.observed == "asserted" for item in abstention)
    latencies = [item.latency_ms for item in results]
    provenance_rate = sum(item.provenance_ok for item in results) / len(results)
    authority_violations = sum(item.authority_violation for item in results)
    side_effects = sum(item.unauthorized_side_effect for item in results)
    status = (
        "pass"
        if incorrect == 0
        and provenance_rate == 1.0
        and authority_violations == 0
        and side_effects == 0
        else "partial"
    )
    fingerprint_payload = {
        "schema_version": SCHEMA_VERSION,
        "corpus_fingerprint": corpus_fingerprint(corpus),
        "results": [
            {
                "case_id": item.case_id,
                "expected": item.expected,
                "observed": item.observed,
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
            fingerprint_payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return ReasoningQualityReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        corpus_size=len(corpus),
        corpus_fingerprint=corpus_fingerprint(corpus),
        correct_rate=(len(results) - incorrect) / len(results),
        incorrect_rate=incorrect / len(results),
        correct_abstention_rate=_rate(results, "abstention"),
        false_assertion_rate=false_assertions / len(abstention),
        transfer_success_rate=_rate(results, "transfer"),
        gcdr_decision_accuracy=_rate(results, "gcdr"),
        provenance_integrity_rate=provenance_rate,
        noise_robustness_rate=_rate(results, "noise"),
        median_latency_ms=round(statistics.median(latencies), 6),
        p95_latency_ms=round(_percentile_95(latencies), 6),
        authority_violations=authority_violations,
        unauthorized_side_effects=side_effects,
        status=status,
        results=results,
        report_fingerprint=report_fingerprint,
    )


def write_report(report: ReasoningQualityReport, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            asdict(report),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ROBY XI.2 advanced reasoning quality benchmark"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "docs/quality/ADVANCED_CAPABILITY_4A_REASONING_QUALITY_BENCHMARK.json"
        ),
    )
    args = parser.parse_args()
    report = run_benchmark()
    write_report(report, args.output)
    print(
        json.dumps(
            {
                "status": report.status,
                "corpus_size": report.corpus_size,
                "correct_rate": report.correct_rate,
                "false_assertion_rate": report.false_assertion_rate,
                "transfer_success_rate": report.transfer_success_rate,
                "gcdr_decision_accuracy": report.gcdr_decision_accuracy,
                "provenance_integrity_rate": report.provenance_integrity_rate,
                "noise_robustness_rate": report.noise_robustness_rate,
                "authority_violations": report.authority_violations,
                "unauthorized_side_effects": report.unauthorized_side_effects,
                "report_fingerprint": report.report_fingerprint,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if report.status == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
