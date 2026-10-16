from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from app.official_conversation_gateway import OfficialConversationGateway
from core.explicit_complex_decision_intake_envelope import (
    ExplicitComplexDecisionIntakeEnvelopeFoundationV1,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"
CASES = BENCHMARKS / "hcpdq_v2_h6_h7_held_out_cases.json"
RUN_EVIDENCE = BENCHMARKS / "HCPDQ_V2_H6_H7_FIRST_PRIMARY_HELD_OUT_EXECUTION.json"


@dataclass(frozen=True)
class FamilyBoundaryFinding:
    family: str
    certified_path_kind: str
    held_out_entry_equivalent: bool
    observed_boundary_failure: str
    root_cause: str
    production_change_authorized: bool = False
    benchmark_translation_authorized: bool = False


class _RuntimeStub:
    bootstrap = object()
    history: tuple[object, ...] = ()
    traces: tuple[object, ...] = ()

    def converse(self, text: str, **kwargs: object):
        del text, kwargs
        return type(
            "_Turn",
            (),
            {
                "response_text": "fallback",
                "status": "completed",
                "session_id": "postmortem",
            },
        )()


def audit_primary_run_evaluation_boundary() -> dict[str, object]:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    run = json.loads(RUN_EVIDENCE.read_text(encoding="utf-8"))

    h6_cases = [case for case in cases if case["family_code"] == "H6"]
    parser = ExplicitComplexDecisionIntakeEnvelopeFoundationV1()
    h6_statuses = {
        case["case_id"]: parser.analyze(case["prompt"]).status.value
        for case in h6_cases
    }
    h6_all_not_envelope = all(
        status == "not_envelope" for status in h6_statuses.values()
    )

    gateway = OfficialConversationGateway(_RuntimeStub())
    planning_bound = gateway._canonical_planning.bound

    findings = (
        FamilyBoundaryFinding(
            family="H6",
            certified_path_kind=(
                "official_conversation_gateway_explicit_complex_decision_intake"
            ),
            held_out_entry_equivalent=not h6_all_not_envelope,
            observed_boundary_failure=(
                "all 15 frozen H6 prompts bypass the certified explicit "
                "Decisión/Criterios/Evidencia intake envelope"
            ),
            root_cause=(
                "calibration certified one strict structured intake grammar, "
                "while the frozen held-out corpus uses natural-language "
                "decision prompts that the productive intake classifies as "
                "NOT_ENVELOPE"
            ),
        ),
        FamilyBoundaryFinding(
            family="H7",
            certified_path_kind=(
                "internal governed multistep investigation planning re-entry"
            ),
            held_out_entry_equivalent=False,
            observed_boundary_failure=(
                "frozen H7 prompts enter the conversation boundary, but the "
                "certified H7 path was not a conversational prompt path"
            ),
            root_cause=(
                "H7 calibration constructed internal requirement/evidence/"
                "re-entry objects and invoked planning_foundation directly; "
                "OfficialConversationGateway exposes an unbound "
                "CanonicalPlanningFacade for conversational planning"
            ),
        ),
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-h7-primary-run-postmortem-audit-v1",
        "status": "EVALUATION_DESIGN_INVALID_RECONTRACT_REQUIRED",
        "baseline": "12949-pass-0-fail-ruff-clean",
        "primary_run_status": run["status"],
        "primary_run_authorization_consumed": run["authorization_consumed"],
        "primary_run_reusable": run["authorization_reusable"],
        "cognitive_scoring_valid": False,
        "performance_conclusion_authorized": False,
        "h6_all_frozen_prompts_not_envelope": h6_all_not_envelope,
        "h6_prompt_statuses": h6_statuses,
        "h7_gateway_canonical_planning_bound": planning_bound,
        "families": {finding.family: asdict(finding) for finding in findings},
        "shared_failure": (
            "calibration-to-held-out entry-path equivalence was not frozen "
            "before primary execution"
        ),
        "corpus_content_invalid": False,
        "ground_truth_invalid": False,
        "roby_cognitive_failure_demonstrated": False,
        "production_change_authorized": False,
        "benchmark_specific_router_authorized": False,
        "held_out_retry_authorized": False,
        "new_primary_execution_authorized": False,
        "architectural_determination": (
            "The v2 primary run is invalid as cognitive-performance evidence. "
            "H6 failed because the frozen natural-language prompts are not "
            "instances of the strict structured intake grammar actually "
            "certified during calibration. H7 failed because its certification "
            "proved an internal planning re-entry path, not a conversational "
            "prompt-to-planning path. The missing invariant is entry-path "
            "equivalence between calibration and held-out exposure. No "
            "production or benchmark-specific routing change is authorized."
        ),
        "next_gate": (
            "HCPDQ-v2 Evaluation Entry-Path Equivalence — Contract / Go-No-Go"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["audit_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            audit_primary_run_evaluation_boundary(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
