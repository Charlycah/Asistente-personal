from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path


def freeze_h6_productive_gap_contract() -> dict[str, object]:
    root = Path(__file__).resolve().parents[1]
    audit = json.loads(
        (
            root
            / "benchmarks"
            / "HCPDQ_V2_H6_SCORING_POSTMORTEM_COGNITIVE_RESULT_AUDIT.json"
        ).read_text(encoding="utf-8")
    )

    localized = bool(
        audit["status"]
        == "COGNITIVE_RESULT_AUDIT_PASS_PRODUCTIVE_GAP_LOCALIZED"
        and audit["architectural_determination"]["productive_cognitive_gap"]
        is True
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h6-productive-gap-contract-v1",
        "status": (
            "LIMITED_PRODUCTIVE_CHANGE_AUTHORIZED_GO"
            if localized
            else "NO_GO_PRODUCTIVE_GAP_NOT_CERTIFIED"
        ),
        "baseline": "13048-pass-0-fail-ruff-clean",
        "family": "H6",
        "existing_authority": (
            "governed complex-decision evidence-completeness / "
            "recommendation-withholding policy"
        ),
        "authorized_change_scope": (
            "required-criterion survivor recommendation only"
        ),
        "contract_rules": {
            "R1": (
                "An explicitly unfavorable required criterion continues to "
                "BLOCK an option."
            ),
            "R2": (
                "Missing evidence is not negative evidence and must never be "
                "converted to UNFAVORABLE."
            ),
            "R3": (
                "Missing evidence on non-required criteria normally remains "
                "INSUFFICIENT and preserves epistemic uncertainty."
            ),
            "R4": (
                "A recommendation may be emitted when exactly one option "
                "survives all explicit required criteria and every competing "
                "option is BLOCKED by at least one explicit required criterion."
            ),
            "R5": (
                "Under R4, missing evidence on non-required criteria may not "
                "veto the sole required-criterion survivor, but must remain "
                "visible in rationale/tradeoff evidence."
            ),
            "R6": (
                "No recommendation is authorized merely because one option "
                "has more favorable observations when criterion importance "
                "or complete comparative evidence is absent."
            ),
            "R7": (
                "Explicit importance relations may support a future general "
                "dominance rule only under a separate contract; they are not "
                "part of this change."
            ),
            "R8": (
                "The change must live in the existing governed complex-decision "
                "authority; no benchmark router, adapter rule or parallel "
                "decision authority is permitted."
            ),
        },
        "hcpdq_case_disposition": {
            "V2E-H6-001_to_006": (
                "NO_CHANGE_AUTHORIZED_FROM_THIS_RESULT; current prompts do not "
                "express a required criterion or frozen importance relation "
                "sufficient for a principled recommendation under incomplete "
                "evidence."
            ),
            "V2E-H6-007_to_012": (
                "IN_SCOPE; each prompt explicitly marks one criterion required, "
                "one option fails it, and the competing option satisfies it."
            ),
        },
        "generic_missing_evidence_relaxation_authorized": False,
        "required_constraint_weakening_authorized": False,
        "benchmark_specific_behavior_authorized": False,
        "adapter_change_authorized": False,
        "entry_path_change_authorized": False,
        "scoring_change_authorized": False,
        "ground_truth_change_authorized": False,
        "production_implementation_authorized": localized,
        "implementation_must_be_general": True,
        "held_out_rerun_authorized": False,
        "rescoring_old_primary_result_authorized": False,
        "architectural_determination": (
            "The certified productive gap is real but only a narrow general "
            "policy change is justified by the evidence. ROBY may recommend "
            "the sole survivor of explicit required constraints while keeping "
            "unknown non-required evidence visible. The first six H6 cases do "
            "not justify a broader incomplete-evidence dominance heuristic."
        ),
        "next_gate": (
            "HCPDQ-v2 H6 Productive Gap — "
            "Pre-Implementation RED Contract Tests"
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
            freeze_h6_productive_gap_contract(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
