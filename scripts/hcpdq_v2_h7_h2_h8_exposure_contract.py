from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Wave1FamilyContract:
    family: str
    go_no_go: str
    existing_authority: str
    productive_surface: str
    observable_evidence: tuple[str, ...]
    exposure_may_observe: tuple[str, ...]
    exposure_must_not_infer: tuple[str, ...]
    red_gate_required: bool
    held_out_authorized: bool = False
    production_change_authorized: bool = False


_REQUIRED: tuple[tuple[str, str], ...] = (
    (
        "app/governed_multistep_investigation_planning_reentry.py",
        "new_plan_produced_by_existing_planning",
    ),
    (
        "app/governed_multistep_investigation_planning_reentry.py",
        'canonical_planning_authority: str = "planning_foundation"',
    ),
    (
        "core/governed_reasoning/derived_epistemic_sufficiency_assessment.py",
        "authorizes_stopping: bool = False",
    ),
    (
        "core/governed_operational_conversation_pipeline/response_origin.py",
        "class ResponseDecision",
    ),
    (
        "core/governed_operational_conversation_pipeline/response_origin.py",
        "ABSTAINED =",
    ),
    (
        "core/governed_reasoning/derived_reasoning_method_provenance.py",
        "selects_method: bool = False",
    ),
    (
        "app/governed_reasoning_runtime.py",
        "Official observable facade over ROBY's governed reasoning pipeline.",
    ),
    (
        "core/governed_reasoning/conflicts.py",
        "class ConflictResolutionManager",
    ),
)


def _evidence_present(root: Path) -> bool:
    return all(
        (root / relative).is_file()
        and needle
        in (root / relative).read_text(
            encoding="utf-8",
            errors="ignore",
        )
        for relative, needle in _REQUIRED
    )


def freeze_wave1_contract(
    root: Path = PROJECT_ROOT,
) -> dict[str, object]:
    if not _evidence_present(root):
        raise RuntimeError("H7/H2/H8 exposure evidence drifted; fail closed")

    contracts = (
        Wave1FamilyContract(
            family="H7",
            go_no_go="CONDITIONAL_GO_TO_PREIMPLEMENTATION_RED",
            existing_authority="planning_foundation",
            productive_surface=("GovernedMultiStepInvestigationPlanningReentryV1"),
            observable_evidence=(
                "planning invocation count is 0 or 1",
                "planned result preserves requirement/plan/source/snapshot lineage",
                "successful re-entry records new plan from existing planning",
                "execution, authorization, reasoning and state mutation remain false",
            ),
            exposure_may_observe=(
                "status",
                "requirement_id",
                "plan_id",
                "planning_status",
                "planning_invocation_count",
                "eligible_for_authorization",
                "rationale_codes",
                "source_fingerprint",
            ),
            exposure_must_not_infer=(
                "all H7 planning semantics are covered",
                "plan execution is authorized",
                "a new planning authority exists",
                "unbound CanonicalPlanningFacade should be bound for HCPDQ",
            ),
            red_gate_required=True,
        ),
        Wave1FamilyContract(
            family="H2",
            go_no_go="CONDITIONAL_GO_TO_PREIMPLEMENTATION_RED",
            existing_authority=(
                "governed_reasoning + governed operational response decision"
            ),
            productive_surface=(
                "GovernedDerivedEpistemicSufficiencyContextAssessment + "
                "ResponseConfidenceRecord"
            ),
            observable_evidence=(
                "epistemic assessment is available as derived read-only context",
                "derived carrier does not invoke reasoning or stopping",
                "response decision explicitly distinguishes ANSWERED/ABSTAINED",
                "abstention requires WITHHELD confidence and unavailable verification",
            ),
            exposure_may_observe=(
                "sufficiency assessment lineage",
                "derived-context availability",
                "response decision",
                "response confidence",
                "verification state",
                "reason code",
            ),
            exposure_must_not_infer=(
                "derived epistemic context availability itself caused abstention",
                "the evaluation layer may decide to stop or answer",
                "absence of a joined lineage proves H2 capability absence",
            ),
            red_gate_required=True,
        ),
        Wave1FamilyContract(
            family="H8",
            go_no_go="CONDITIONAL_GO_TO_PREIMPLEMENTATION_RED",
            existing_authority="governed_reasoning",
            productive_surface=(
                "GovernedReasoningMethodProvenanceContextItem + "
                "OfficialGovernedReasoningRuntimeGateway conflict analysis"
            ),
            observable_evidence=(
                "method provenance is exposed as derived read-only context",
                "provenance consumer cannot rank/select/recommend methods",
                "governed reasoning contains existing conflict-resolution decisions",
                "official runtime exposes the existing governed reasoning pipeline",
            ),
            exposure_may_observe=(
                "provenance lineage",
                "conflict identifiers",
                "resolution status",
                "selected claim identifier when already resolved",
                "review requirement",
                "confidence",
            ),
            exposure_must_not_infer=(
                "provenance availability itself resolved a conflict",
                "the evaluation layer may rank sources or select claims",
                "benchmark-specific conflict policy is authorized",
            ),
            red_gate_required=True,
        ),
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h7-h2-h8-exposure-contract-v1",
        "status": "CONTRACT_FROZEN_CONDITIONAL_GO_HELD_OUT_NO_GO",
        "baseline": "12855-pass-0-fail-ruff-clean",
        "wave": ["H7", "H2", "H8"],
        "families": {contract.family: asdict(contract) for contract in contracts},
        "go_to_preimplementation_red": True,
        "minimal_production_implementation_authorized": False,
        "new_authority_authorized": False,
        "benchmark_specific_routing_authorized": False,
        "direct_internal_authority_instantiation_authorized": False,
        "ground_truth_available_to_exposure": False,
        "persistence_or_adaptation_authorized": False,
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "cross_family_substitution_authorized": False,
        "causal_join_rule": (
            "A family may become exposure-certified only when read-only evidence "
            "shows the existing authority/productive path actually participated in "
            "the observed outcome; metadata presence alone is insufficient."
        ),
        "failure_rule": (
            "Missing, ambiguous, unjoined or degraded evidence fails closed as "
            "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2, never CAPABILITY_ABSENT."
        ),
        "next_gate": (
            "HCPDQ-v2 H7/H2/H8 Existing-Authority Exposure — "
            "Pre-Implementation RED Contract Tests"
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
            freeze_wave1_contract(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
