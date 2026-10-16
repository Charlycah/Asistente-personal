from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256

from scripts.hcpdq_v2_h1_h3_shadow_observability_audit import (
    audit_h1_h3_shadow_observability,
)
from scripts.hcpdq_v2_h2_h8_causal_lineage_gap_contract import (
    freeze_h2_h8_causal_lineage_gap_contract,
)
from scripts.hcpdq_v2_h7_h2_h8_exposure_calibration_certification import (
    certify_wave1_calibration,
)


@dataclass(frozen=True)
class FinalFamilyScope:
    family: str
    measurable_in_v2: bool
    disposition: str


def freeze_final_measurable_scope() -> dict[str, object]:
    h1_h3 = audit_h1_h3_shadow_observability()
    h2_h8 = freeze_h2_h8_causal_lineage_gap_contract()
    wave1 = certify_wave1_calibration()

    families = (
        FinalFamilyScope("H1", False, h1_h3["families"]["H1"]["disposition"]),
        FinalFamilyScope("H2", False, h2_h8["families"]["H2"]["disposition"]),
        FinalFamilyScope("H3", False, h1_h3["families"]["H3"]["disposition"]),
        FinalFamilyScope("H4", False, "EXCLUDED_NO_PRODUCTIVE_EXPOSURE"),
        FinalFamilyScope("H5", False, "EXCLUDED_NO_PRODUCTIVE_EXPOSURE"),
        FinalFamilyScope("H6", True, "CERTIFIED_CALIBRATION_PATH"),
        FinalFamilyScope("H7", True, wave1["families"]["H7"]["verdict"]),
        FinalFamilyScope("H8", False, h2_h8["families"]["H8"]["disposition"]),
    )
    measurable = [item.family for item in families if item.measurable_in_v2]
    excluded = [item.family for item in families if not item.measurable_in_v2]

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-final-measurable-scope-freeze-v1",
        "status": "FINAL_SCOPE_FROZEN_HELD_OUT_CONSTRUCTION_GO",
        "baseline": "12903-pass-0-fail-ruff-clean",
        "families": {item.family: asdict(item) for item in families},
        "measurable_families": measurable,
        "excluded_families": excluded,
        "pending_families": [],
        "scope_freeze_complete": True,
        "held_out_scope": {
            "families": measurable,
            "family_count": len(measurable),
            "difficulty_levels": ["D1", "D2", "D3"],
            "must_be_new_independent_corpus": True,
            "must_not_reuse_v1_held_out_cases": True,
            "must_not_reuse_calibration_prompts": True,
            "ground_truth_must_be_frozen_before_roby_exposure": True,
        },
        "held_out_readiness": "GO_FOR_CONSTRUCTION_AND_FREEZE_ONLY",
        "held_out_construction_authorized": True,
        "held_out_ground_truth_freeze_authorized": True,
        "held_out_roby_exposure_authorized": False,
        "held_out_execution_authorized": False,
        "human_comparison_authorized": False,
        "production_changes_authorized": False,
        "new_authority_authorized": False,
        "v1_corpus_reuse_authorized": False,
        "architectural_determination": (
            "The HCPDQ-v2 measurable family set is finally frozen to H6/H7. "
            "All other families are explicitly excluded from v2 measurement. "
            "A new independent held-out corpus limited to H6/H7 may now be "
            "constructed and ground-truth frozen. ROBY exposure remains blocked "
            "until that corpus receives an independent freeze certification."
        ),
        "next_gate": (
            "HCPDQ-v2 H6/H7 Held-Out Corpus — Construction / Independent "
            "Ground-Truth Freeze"
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
            freeze_final_measurable_scope(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
