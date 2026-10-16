from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

from scripts.hcpdq_v2_h2_h8_causal_lineage_gap_contract import (
    freeze_h2_h8_causal_lineage_gap_contract,
)
from scripts.hcpdq_v2_h7_h2_h8_exposure_calibration_certification import (
    certify_wave1_calibration,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FamilyScopeDecision:
    family: str
    measurable_in_v2: bool
    disposition: str
    evidence_basis: tuple[str, ...]
    held_out_use_authorized: bool = False


def _load_json(name: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / "benchmarks" / name).read_text(encoding="utf-8"))


def freeze_measurable_family_scope() -> dict[str, object]:
    original = _load_json("HCPDQ_V2_CALIBRATION_PATH_COVERAGE_CERTIFICATION.json")
    prioritization = _load_json(
        "HCPDQ_V2_REMAINING_FAMILY_EXPOSURE_PRIORITIZATION.json"
    )
    wave1 = certify_wave1_calibration()
    h2_h8 = freeze_h2_h8_causal_lineage_gap_contract()

    h6 = original["family_results"]["H6"]
    h7 = wave1["families"]["H7"]

    decisions = (
        FamilyScopeDecision(
            family="H1",
            measurable_in_v2=False,
            disposition="PENDING_SHADOW_OBSERVABILITY_AUDIT",
            evidence_basis=(
                "authority exists",
                "shadow runtime exists and is observational",
                "ordinary-turn H1 causal exposure is not yet certified",
            ),
        ),
        FamilyScopeDecision(
            family="H2",
            measurable_in_v2=False,
            disposition="EXCLUDED_NOT_VALIDLY_MEASURABLE",
            evidence_basis=tuple(h2_h8["families"]["H2"]["reason"]),
        ),
        FamilyScopeDecision(
            family="H3",
            measurable_in_v2=False,
            disposition="PENDING_SHADOW_OBSERVABILITY_AUDIT",
            evidence_basis=(
                "context-sensitive authority evidence exists",
                "shadow runtime exists and is observational",
                "ordinary-turn H3 causal exposure is not yet certified",
            ),
        ),
        FamilyScopeDecision(
            family="H4",
            measurable_in_v2=False,
            disposition="EXCLUDED_NO_PRODUCTIVE_EXPOSURE",
            evidence_basis=tuple(prioritization["families"]["H4"]["rationale"]),
        ),
        FamilyScopeDecision(
            family="H5",
            measurable_in_v2=False,
            disposition="EXCLUDED_NO_PRODUCTIVE_EXPOSURE",
            evidence_basis=tuple(prioritization["families"]["H5"]["rationale"]),
        ),
        FamilyScopeDecision(
            family="H6",
            measurable_in_v2=True,
            disposition="CERTIFIED_CALIBRATION_PATH",
            evidence_basis=tuple(h6["evidence"]),
        ),
        FamilyScopeDecision(
            family="H7",
            measurable_in_v2=True,
            disposition="CERTIFIED_CALIBRATION_EXPOSURE",
            evidence_basis=tuple(h7["evidence"]),
        ),
        FamilyScopeDecision(
            family="H8",
            measurable_in_v2=False,
            disposition="EXCLUDED_NOT_VALIDLY_MEASURABLE",
            evidence_basis=tuple(h2_h8["families"]["H8"]["reason"]),
        ),
    )

    measurable = [item.family for item in decisions if item.measurable_in_v2]
    pending = [
        item.family
        for item in decisions
        if item.disposition == "PENDING_SHADOW_OBSERVABILITY_AUDIT"
    ]
    excluded = [
        item.family for item in decisions if item.disposition.startswith("EXCLUDED_")
    ]

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-measurable-family-scope-freeze-v1",
        "status": "SCOPE_PARTIALLY_FROZEN_HELD_OUT_NO_GO",
        "baseline": "12893-pass-0-fail-ruff-clean",
        "families": {item.family: asdict(item) for item in decisions},
        "measurable_families": measurable,
        "pending_scope_families": pending,
        "excluded_families": excluded,
        "required_family_count": 8,
        "measurable_family_count": len(measurable),
        "scope_freeze_complete": not pending,
        "held_out_readiness": "NO_GO",
        "held_out_construction_authorized": False,
        "held_out_execution_authorized": False,
        "human_comparison_authorized": False,
        "production_changes_authorized": False,
        "new_authority_authorized": False,
        "reason": (
            "H6 and H7 are measurably certified. H2/H8 are excluded for "
            "missing productive causal lineage; H4/H5 are excluded for missing "
            "productive exposure. H1/H3 remain unresolved because an existing "
            "read-only shadow runtime is present and must be audited before the "
            "v2 measurable scope can be frozen without leaving reachable "
            "evidence unexamined."
        ),
        "next_gate": (
            "HCPDQ-v2 H1/H3 Shadow Observability — Existing-Path Audit / "
            "Scope Resolution"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["scope_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_measurable_family_scope(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
