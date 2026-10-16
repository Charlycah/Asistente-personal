from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
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

SCHEMA_VERSION = "advanced-capability-4b-independent-runner-v1"
NOW = datetime(2026, 8, 20, 18, 0, tzinfo=timezone.utc)


@dataclass(frozen=True)
class IndependentObservation:
    case_id: str
    dimension: str
    observed: str
    latency_ms: float
    provenance_ok: bool
    authority_violation: bool
    unauthorized_side_effect: bool


@dataclass(frozen=True)
class IndependentRunReport:
    schema_version: str
    generated_at: str
    case_count: int
    cases_fingerprint: str
    observations: tuple[IndependentObservation, ...]
    observations_fingerprint: str


def _fingerprint(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()


def load_cases(path: Path) -> tuple[dict[str, object], ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases = tuple(raw["cases"])
    if not cases or len({str(item["case_id"]) for item in cases}) != len(cases):
        raise ValueError("4B cases must be non-empty and uniquely identified")
    return cases


def _option(item: dict[str, object]) -> GovernedDecisionOption:
    return GovernedDecisionOption(option_id=str(item["id"]), title=str(item["title"]))


def _criterion(item: dict[str, object]) -> GovernedDecisionCriterion:
    cid = str(item["id"])
    importance = item.get("importance")
    return GovernedDecisionCriterion(
        criterion_id=cid,
        title=str(item["title"]),
        required=bool(item.get("required", False)),
        explicit_importance=None if importance is None else float(importance),
        provenance_codes=(f"4b:{cid}",),
    )


def _assessment(item: dict[str, object]) -> GovernedOptionCriterionAssessment:
    oid = str(item["option_id"])
    cid = str(item["criterion_id"])
    outcome = ComplexDecisionCriterionOutcome(str(item["outcome"]))
    source = sha256(f"4b:{oid}:{cid}:{outcome.value}".encode()).hexdigest()
    return GovernedOptionCriterionAssessment(
        option_id=oid,
        criterion_id=cid,
        outcome=outcome,
        evidence_codes=(f"4b:{oid}:{cid}",),
        source_fingerprint=source,
    )


def _run_gcdr(data: dict[str, object]) -> tuple[str, bool, bool]:
    options = tuple(_option(item) for item in data["options"])
    criteria = tuple(_criterion(item) for item in data["criteria"])
    assessments = tuple(_assessment(item) for item in data["assessments"])
    report = GovernedComplexDecisionReasoningFoundationV1().assess(
        options, criteria, assessments
    )
    observed = (
        "abstain"
        if report.recommended_option_id is None
        else f"recommend_{report.recommended_option_id}"
    )
    provenance_ok = len(report.source_fingerprint) == 64
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
    return observed, provenance_ok, not non_power


def _run_transfer(data: dict[str, object]) -> tuple[str, bool, bool]:
    registry = InMemoryInferenceRuleRegistry()
    intake = ProductiveTemporaryRuleIntake(registry)
    scope = str(data["scope"])
    teach = intake.observe(
        owner="benchmark",
        text=str(data["rule_text"]),
        scope_reference=scope,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        now=NOW,
    )
    result = intake.observe(
        owner="benchmark",
        text=str(data["case_text"]),
        scope_reference=scope,
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        now=NOW + timedelta(minutes=1),
    )
    observed = (
        "transfer_admitted"
        if result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
        else "transfer_rejected"
    )
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
    return observed, provenance_ok, not non_power


def _run_abstention(data: dict[str, object]) -> tuple[str, bool, bool]:
    option_ids = tuple(str(item) for item in data["options"])
    criterion_ids = tuple(str(item) for item in data["criteria"])
    options = tuple(GovernedDecisionOption(item, item.title()) for item in option_ids)
    criteria = tuple(
        GovernedDecisionCriterion(
            item,
            item.title(),
            provenance_codes=(f"4b:{item}",),
        )
        for item in criterion_ids
    )
    assessments = []
    omit = tuple(data.get("omit_pair", ()))
    for oid in option_ids:
        for cid in criterion_ids:
            if (oid, cid) == omit:
                continue
            outcome = (
                ComplexDecisionCriterionOutcome.INSUFFICIENT
                if data["mode"] == "insufficient"
                else ComplexDecisionCriterionOutcome.FAVORABLE
            )
            assessments.append(
                _assessment(
                    {"option_id": oid, "criterion_id": cid, "outcome": outcome.value}
                )
            )
    try:
        report = GovernedComplexDecisionReasoningFoundationV1().assess(
            options, criteria, tuple(assessments)
        )
    except ValueError:
        return "abstain", True, False
    observed = "abstain" if report.recommended_option_id is None else "asserted"
    return observed, len(report.source_fingerprint) == 64, report.grants_authority


def _run_provenance(data: dict[str, object]) -> tuple[str, bool, bool]:
    options = (
        GovernedDecisionOption("a", "A"),
        GovernedDecisionOption("b", "B"),
    )
    criteria = (
        GovernedDecisionCriterion("c1", "C1", provenance_codes=("4b:c1",)),
        GovernedDecisionCriterion("c2", "C2", provenance_codes=("4b:c2",)),
    )
    pairs = [
        {"option_id": "a", "criterion_id": "c1", "outcome": "favorable"},
        {"option_id": "a", "criterion_id": "c2", "outcome": "neutral"},
        {"option_id": "b", "criterion_id": "c1", "outcome": "neutral"},
        {"option_id": "b", "criterion_id": "c2", "outcome": "favorable"},
    ]
    attack = str(data["attack"])
    if attack == "unknown_option":
        pairs[-1]["option_id"] = "ghost"
    elif attack == "unknown_criterion":
        pairs[-1]["criterion_id"] = "ghost"
    elif attack == "duplicate_pair":
        pairs[-1] = dict(pairs[0])
    elif attack == "missing_pair":
        pairs.pop()
    else:
        raise ValueError("unknown provenance attack")
    try:
        GovernedComplexDecisionReasoningFoundationV1().assess(
            options,
            criteria,
            tuple(_assessment(item) for item in pairs),
        )
    except ValueError:
        return "reject_corrupt", True, False
    return "accepted_corrupt", False, False


def _run_noise(data: dict[str, object]) -> tuple[str, bool, bool]:
    result = run_scale_level(int(data["item_count"]))
    observed = (
        "retain_all_decisive"
        if result.decisive_items_selected == result.decisive_item_count
        else "lost_evidence"
    )
    provenance_ok = result.provenance_integrity and result.corrupt_provenance_rejected
    return observed, provenance_ok, False


def _run_case(case: dict[str, object]) -> IndependentObservation:
    started = perf_counter()
    kind = str(case["kind"])
    data = case["input"]
    if kind == "transfer":
        observed, provenance_ok, side_effect = _run_transfer(data)
    elif kind == "gcdr":
        observed, provenance_ok, side_effect = _run_gcdr(data)
    elif kind == "abstention":
        observed, provenance_ok, side_effect = _run_abstention(data)
    elif kind == "provenance":
        observed, provenance_ok, side_effect = _run_provenance(data)
    elif kind == "noise":
        observed, provenance_ok, side_effect = _run_noise(data)
    elif kind == "compositional":
        left, left_ok, left_side = _run_transfer(data)
        right, right_ok, right_side = _run_gcdr(data["gcdr"])
        observed = f"{left}|{right}"
        provenance_ok = left_ok and right_ok
        side_effect = left_side or right_side
    else:
        raise ValueError(f"unknown 4B case kind: {kind}")
    return IndependentObservation(
        case_id=str(case["case_id"]),
        dimension=str(case["dimension"]),
        observed=observed,
        latency_ms=round((perf_counter() - started) * 1000.0, 6),
        provenance_ok=provenance_ok,
        authority_violation=False,
        unauthorized_side_effect=side_effect,
    )


def run_cases(cases: tuple[dict[str, object], ...]) -> IndependentRunReport:
    observations = tuple(_run_case(case) for case in cases)
    logical = [
        {
            "case_id": item.case_id,
            "dimension": item.dimension,
            "observed": item.observed,
            "provenance_ok": item.provenance_ok,
            "authority_violation": item.authority_violation,
            "unauthorized_side_effect": item.unauthorized_side_effect,
        }
        for item in observations
    ]
    return IndependentRunReport(
        schema_version=SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        case_count=len(cases),
        cases_fingerprint=_fingerprint(cases),
        observations=observations,
        observations_fingerprint=_fingerprint(logical),
    )


def write_report(report: IndependentRunReport, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="ROBY XI.2 independent 4B runner")
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path("benchmarks/advanced_capability_4b_cases.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/quality/ADVANCED_CAPABILITY_4B_OBSERVATIONS.json"),
    )
    args = parser.parse_args()
    write_report(run_cases(load_cases(args.cases)), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
