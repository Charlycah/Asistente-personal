from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h6_h7_primary_run_postmortem_audit import (
    audit_primary_run_evaluation_boundary,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BENCHMARKS = PROJECT_ROOT / "benchmarks"


@dataclass(frozen=True)
class EntryPathEquivalenceRule:
    rule_id: str
    requirement: str
    mandatory: bool = True


RULES = (
    EntryPathEquivalenceRule(
        "EPE-01",
        "Calibration and held-out must enter through the same productive intake.",
    ),
    EntryPathEquivalenceRule(
        "EPE-02",
        "Held-out prompts must satisfy the same intake grammar as calibration.",
    ),
    EntryPathEquivalenceRule(
        "EPE-03",
        "No benchmark-specific translation, router or semantic adapter is allowed.",
    ),
    EntryPathEquivalenceRule(
        "EPE-04",
        "Internal re-entry certification cannot substitute for user-entry proof.",
    ),
    EntryPathEquivalenceRule(
        "EPE-05",
        "The same existing productive authority must be causally observed.",
    ),
    EntryPathEquivalenceRule(
        "EPE-06",
        "Entry-path equivalence must be certified before held-out exposure.",
    ),
    EntryPathEquivalenceRule(
        "EPE-07",
        "A consumed invalid primary run cannot be retried under the same freeze.",
    ),
)


def evaluate_entry_path_equivalence() -> dict[str, object]:
    audit = audit_primary_run_evaluation_boundary()
    h6 = audit["families"]["H6"]
    h7 = audit["families"]["H7"]

    family_results = {
        "H6": {
            "entry_path_equivalent": h6["held_out_entry_equivalent"],
            "go": False,
            "reason": (
                "Held-out natural-language prompts do not satisfy the certified "
                "Decisión/Criterios/Evidencia productive intake grammar."
            ),
        },
        "H7": {
            "entry_path_equivalent": h7["held_out_entry_equivalent"],
            "go": False,
            "reason": (
                "Calibration proved internal planning re-entry, not an equivalent "
                "conversation-entry path to the same productive authority."
            ),
        },
    }
    equivalence_pass = all(
        result["entry_path_equivalent"]
        for result in family_results.values()
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-entry-path-equivalence-contract-v1",
        "status": (
            "GO_ENTRY_PATH_EQUIVALENCE"
            if equivalence_pass
            else "NO_GO_REFREEZE_REQUIRED"
        ),
        "baseline": "12954-pass-0-fail-ruff-clean",
        "rules": [asdict(rule) for rule in RULES],
        "family_results": family_results,
        "entry_path_equivalence_certified": equivalence_pass,
        "current_h6_h7_freeze_reusable": False,
        "held_out_retry_authorized": False,
        "new_primary_execution_authorized": False,
        "benchmark_specific_translation_authorized": False,
        "benchmark_specific_router_authorized": False,
        "production_change_authorized": False,
        "ground_truth_change_authorized": False,
        "corpus_semantic_rewrite_authorized": False,
        "recontract_authorized": True,
        "recontract_scope": (
            "evaluation entry/exposure contract and a new independent freeze only"
        ),
        "architectural_determination": (
            "Entry-path equivalence is a mandatory precondition, not an "
            "after-the-fact adapter. H6 and H7 both fail the invariant under "
            "the consumed v2 freeze. The current freeze cannot be retried or "
            "reused. A new evaluation contract may proceed only by selecting "
            "forms already accepted by existing productive entry paths and "
            "independently freezing a new corpus before exposure. No ROBY "
            "production change or benchmark-specific routing is authorized."
        ),
        "next_gate": (
            "HCPDQ-v2 Entry-Path Equivalent Evaluation — "
            "Recontract / New Independent Freeze Scope"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["contract_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            evaluate_entry_path_equivalence(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
