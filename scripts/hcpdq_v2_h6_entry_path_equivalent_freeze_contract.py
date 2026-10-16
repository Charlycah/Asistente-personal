from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256

from scripts.hcpdq_v2_entry_path_equivalent_recontract_scope import (
    freeze_recontract_scope,
)


@dataclass(frozen=True)
class H6IndependentFreezeRule:
    rule_id: str
    requirement: str
    mandatory: bool = True


RULES = (
    H6IndependentFreezeRule(
        "H6F-01",
        "Every case must use the existing Decisión/Criterios/Evidencia intake.",
    ),
    H6IndependentFreezeRule(
        "H6F-02",
        "Case identifiers and case content must be new and independently "
        "authored.",
    ),
    H6IndependentFreezeRule(
        "H6F-03",
        "No consumed HCPDQ-v2 case may be reused, paraphrased or "
        "semantically rewritten.",
    ),
    H6IndependentFreezeRule(
        "H6F-04",
        "Ground truth must be authored and frozen before any ROBY exposure.",
    ),
    H6IndependentFreezeRule(
        "H6F-05",
        "Ground truth must not be visible to the evaluation subject or intake path.",
    ),
    H6IndependentFreezeRule(
        "H6F-06",
        "The productive H6 entry path must be certified on representative dry probes.",
    ),
    H6IndependentFreezeRule(
        "H6F-07",
        "Dry probes may verify routing only and must not reveal future held-out cases.",
    ),
    H6IndependentFreezeRule(
        "H6F-08",
        "No benchmark-specific translation, semantic router or production "
        "change is allowed.",
    ),
    H6IndependentFreezeRule(
        "H6F-09",
        "Corpus construction and ground-truth freeze do not authorize ROBY execution.",
    ),
)


def freeze_h6_independent_construction_contract() -> dict[str, object]:
    scope = freeze_recontract_scope()
    h6 = scope["families"]["H6"]
    authorized = bool(
        scope["status"] == "SCOPE_FROZEN_H6_GO_H7_NO_GO"
        and h6["measurable_now"] is True
        and h6["independent_freeze_authorized"] is True
        and h6["allowed_entry_form"]
        == "existing explicit Decisión/Criterios/Evidencia intake grammar"
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-independent-freeze-contract-v1",
        "status": (
            "CONTRACT_FROZEN_CONSTRUCTION_NOT_YET_AUTHORIZED"
            if authorized
            else "NO_GO_H6_FREEZE_CONTRACT_PRECONDITION_FAILED"
        ),
        "baseline": "12964-pass-0-fail-ruff-clean",
        "family": "H6",
        "entry_path": h6["allowed_entry_form"],
        "existing_authority": h6["existing_authority"],
        "rules": [asdict(rule) for rule in RULES],
        "case_count_frozen": False,
        "difficulty_distribution_frozen": False,
        "case_content_created": False,
        "ground_truth_created": False,
        "ground_truth_frozen": False,
        "dry_probe_cases_are_held_out": False,
        "roby_exposure_authorized": False,
        "primary_execution_authorized": False,
        "human_comparison_authorized": False,
        "production_change_authorized": False,
        "benchmark_translation_authorized": False,
        "benchmark_router_authorized": False,
        "consumed_v2_case_reuse_authorized": False,
        "consumed_v2_case_paraphrase_authorized": False,
        "construction_contract_frozen": authorized,
        "construction_authorized": False,
        "next_required_decision": (
            "freeze case-count/difficulty design and certify representative "
            "entry-path dry probes before constructing any held-out case"
        ),
        "architectural_determination": (
            "H6 can support a new independent evaluation only through its "
            "existing structured productive intake. This contract freezes the "
            "construction constraints but intentionally does not yet authorize "
            "case creation. First, representative non-held-out dry probes must "
            "demonstrate that the exact frozen intake form reaches the same "
            "productive H6 authority without translation or routing."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 Entry-Path Equivalent Corpus — "
            "Dry-Probe Certification / Construction Authorization"
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
            freeze_h6_independent_construction_contract(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
