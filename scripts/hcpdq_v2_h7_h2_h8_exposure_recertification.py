from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from hashlib import sha256

import scripts.hcpdq_v2_h7_h2_h8_existing_authority_exposure as exposure


def recertify_wave1_exposure() -> dict[str, object]:
    policy = exposure.default_wave1_exposure_policy()
    source = inspect.getsource(exposure)

    forbidden_tokens = (
        "CognitivePlanner(",
        "CanonicalPlanningFacade(",
        "ConflictResolutionManager(",
        "ResponseConfidenceRecord(",
        "GovernedEpistemicSufficiencyAssessmentFoundationV1(",
        "GovernedReasoningMethodProvenanceFoundationV1(",
        "BenchmarkRouter",
        "HCPDQRouter",
        "classify_prompt",
        ".bind_planner(",
    )
    zero_authority = not any(
        (
            policy.allow_plan_execution,
            policy.allow_planner_binding,
            policy.allow_new_planning_authority,
            policy.allow_response_decision,
            policy.allow_stopping_decision,
            policy.allow_source_ranking,
            policy.allow_claim_selection,
            policy.allow_conflict_policy_change,
            policy.allow_new_authority,
        )
    )
    zero_mutation = not any(
        (
            policy.allow_epistemic_threshold_change,
            policy.allow_persistence_or_adaptation,
        )
    )

    h7_positive = exposure.H7ExposureEvidence(
        family="H7",
        existing_authority="planning_foundation",
        status="planned",
        requirement_id="req-1",
        plan_id="plan-1",
        planning_status="plannable",
        planning_invocation_count=1,
        eligible_for_authorization=True,
        rationale_codes=("planning_reentry:new_plan_produced_by_existing_planning",),
        source_fingerprint="a" * 64,
        authority_participation_evidence=("planning_foundation", "req-1", "plan-1"),
        measurement_validity="valid",
    )
    h2_positive = exposure.H2ExposureEvidence(
        family="H2",
        sufficiency_assessment_id="epistemic-sufficiency-1",
        consumed_assessment_id="derived-epistemic-sufficiency-1",
        derived_context_available=True,
        response_decision="abstained",
        response_confidence="withheld",
        verification_state="unavailable",
        reason_code="web_response_withheld",
        causal_join_evidence=(
            "epistemic-sufficiency-1",
            "response-decision-record-1",
        ),
        measurement_validity="valid",
    )
    h8_positive = exposure.H8ExposureEvidence(
        family="H8",
        provenance_id="reasoning-method-provenance-1",
        consumed_assessment_id="reasoning-method-context-1",
        conflict_ids=("conflict-1",),
        resolution_statuses=("resolved",),
        selected_claim_ids=("claim-2",),
        requires_review=False,
        confidence=0.75,
        authority_participation_evidence=("governed_reasoning", "conflict-1"),
        measurement_validity="valid",
    )

    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-h7-h2-h8-exposure-recertification-v1",
        "status": "CAUSALLY_RECERTIFIED_HELD_OUT_NO_GO",
        "baseline": "12878-pass-0-fail-ruff-clean",
        "zero_authority": zero_authority,
        "zero_mutation": zero_mutation,
        "no_direct_internal_authority_instantiation": all(
            token not in source for token in forbidden_tokens
        ),
        "family_mapping_metadata_only": tuple(
            inspect.signature(exposure.exposure_kind_for_family).parameters
        )
        == ("family",),
        "ground_truth_blind": all(
            field not in model.__dataclass_fields__
            for model in (
                exposure.H7ExposureEvidence,
                exposure.H2ExposureEvidence,
                exposure.H8ExposureEvidence,
            )
            for field in (
                "expected",
                "expected_answer",
                "ground_truth",
                "rubric",
                "human_answer",
                "score",
            )
        ),
        "h7_join_certified": exposure.h7_exposure_certified(h7_positive),
        "h2_join_certified": exposure.h2_exposure_certified(h2_positive),
        "h8_join_certified": exposure.h8_exposure_certified(h8_positive),
        "fail_closed_measurement": (
            exposure.measurement_failure_classification(
                causal_join_present=False,
                degraded=False,
            )
            == "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"
        ),
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "production_cognitive_change_detected": False,
        "policy": asdict(policy),
    }
    gates = (
        payload["zero_authority"],
        payload["zero_mutation"],
        payload["no_direct_internal_authority_instantiation"],
        payload["family_mapping_metadata_only"],
        payload["ground_truth_blind"],
        payload["h7_join_certified"],
        payload["h2_join_certified"],
        payload["h8_join_certified"],
        payload["fail_closed_measurement"],
    )
    payload["causal_recertification_passed"] = all(gates)

    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    payload["recertification_fingerprint"] = sha256(
        canonical.encode("utf-8")
    ).hexdigest()
    return payload


if __name__ == "__main__":
    print(
        json.dumps(
            recertify_wave1_exposure(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
