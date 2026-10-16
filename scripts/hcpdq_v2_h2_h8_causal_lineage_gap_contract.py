from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from hashlib import sha256
from pathlib import Path

from core.governed_operational_conversation_pipeline.response_origin import (
    ResponseConfidenceRecord,
)
from core.governed_reasoning.conflicts import ConflictAnalysis
from core.governed_reasoning.derived_epistemic_sufficiency_assessment import (
    GovernedDerivedEpistemicSufficiencyContextAssessment,
)
from core.governed_reasoning.derived_reasoning_method_provenance import (
    GovernedReasoningMethodProvenanceContextItem,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class CausalLineageGapContract:
    family: str
    existing_components: tuple[str, ...]
    shared_causal_lineage_present: bool
    productive_join_present: bool
    disposition: str
    reason: tuple[str, ...]
    preimplementation_red_authorized: bool = False
    production_change_authorized: bool = False
    new_authority_authorized: bool = False
    held_out_authorized: bool = False


def _field_names(model: type[object]) -> set[str]:
    return {field.name for field in fields(model)}


def freeze_h2_h8_causal_lineage_gap_contract() -> dict[str, object]:
    h2_sufficiency = _field_names(GovernedDerivedEpistemicSufficiencyContextAssessment)
    h2_response = _field_names(ResponseConfidenceRecord)
    h8_provenance = _field_names(GovernedReasoningMethodProvenanceContextItem)
    h8_conflict = _field_names(ConflictAnalysis)

    h2_shared = bool(
        h2_sufficiency
        & {
            "response_decision_id",
            "response_confidence_record_id",
            "response_origin_id",
        }
    ) or bool(
        h2_response
        & {
            "sufficiency_assessment_id",
            "consumed_assessment_id",
            "epistemic_sufficiency_id",
        }
    )
    h8_shared = bool(
        h8_provenance
        & {
            "conflict_ids",
            "conflict_analysis_id",
            "resolution_ids",
        }
    ) or bool(
        h8_conflict
        & {
            "provenance_id",
            "consumed_assessment_id",
            "reasoning_method_provenance_id",
        }
    )

    contracts = (
        CausalLineageGapContract(
            family="H2",
            existing_components=(
                "GovernedDerivedEpistemicSufficiencyContextAssessment",
                "ResponseConfidenceRecord",
            ),
            shared_causal_lineage_present=h2_shared,
            productive_join_present=False,
            disposition="NO_GO_EXCLUDE_FROM_HCPDQ_V2_MEASURABLE_SCOPE",
            reason=(
                "Both existing components are independently observable.",
                "No existing productive path joins sufficiency consumption to a "
                "specific response decision.",
                "Adding identifiers alone would manufacture correlation rather "
                "than expose an already-existing causal join.",
                "HCPDQ must fail closed instead of changing response semantics.",
            ),
        ),
        CausalLineageGapContract(
            family="H8",
            existing_components=(
                "GovernedReasoningMethodProvenanceContextItem",
                "ConflictAnalysis",
            ),
            shared_causal_lineage_present=h8_shared,
            productive_join_present=False,
            disposition="NO_GO_EXCLUDE_FROM_HCPDQ_V2_MEASURABLE_SCOPE",
            reason=(
                "Method provenance and conflict analysis both exist.",
                "No existing productive path joins a derived provenance context item "
                "to a specific conflict analysis or resolution decision.",
                "Source/world similarity is insufficient causal evidence.",
                "HCPDQ may not create a conflict-selection or provenance bridge.",
            ),
        ),
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h2-h8-causal-lineage-gap-contract-v1",
        "status": "NO_GO_EXCLUDE_H2_H8_FROM_V2_MEASURABLE_SCOPE",
        "baseline": "12888-pass-0-fail-ruff-clean",
        "families": {item.family: asdict(item) for item in contracts},
        "existing_authority_determination": (
            "The required authorities/components exist, but the causal joins "
            "required by H2 and H8 do not exist as productive observable paths."
        ),
        "metadata_only_lineage_patch_authorized": False,
        "preimplementation_red_authorized": False,
        "minimal_production_implementation_authorized": False,
        "new_bridge_authorized": False,
        "new_authority_authorized": False,
        "response_semantic_change_authorized": False,
        "conflict_policy_change_authorized": False,
        "persistence_or_adaptation_authorized": False,
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "measurement_failure_classification": ("NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"),
        "architectural_determination": (
            "A RED gate is not justified because there is no already-existing "
            "productive causal join for a read-only adapter to expose. Creating "
            "one would cross the evaluation boundary into production integration."
        ),
        "next_gate": (
            "HCPDQ-v2 Measurable Family Set — Scope Freeze / Held-Out "
            "Readiness Reassessment"
        ),
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["contract_fingerprint"] = sha256(canonical.encode("utf-8")).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            freeze_h2_h8_causal_lineage_gap_contract(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
