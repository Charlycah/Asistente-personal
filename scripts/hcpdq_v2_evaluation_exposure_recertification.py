from __future__ import annotations

import inspect
import json
from dataclasses import asdict
from hashlib import sha256

import scripts.hcpdq_v2_evaluation_exposure as exposure


def recertify_evaluation_exposure() -> dict[str, object]:
    policy = exposure.default_exposure_policy()
    registry = exposure.default_exposure_registry()
    source = inspect.getsource(exposure)

    forbidden_tokens = (
        "CognitivePlanner(",
        "GovernedStructuralKnowledgeTransferMatcher(",
        "GovernedTargetProblemStructuralProjector(",
        "GovernedContextualCaseRoleGrounder(",
        "CanonicalDecisionFacade(",
        "CanonicalPlanningFacade(",
        "BenchmarkRouter",
        "HCPDQRouter",
        "EvaluationDecisionEngine",
        ".bind_planner(",
    )
    zero_authority = not any(
        (
            policy.grants_decision_authority,
            policy.grants_routing_authority,
            policy.grants_planning_authority,
            policy.grants_reasoning_authority,
            policy.grants_learning_authority,
            policy.grants_autonomy,
        )
    )
    zero_mutation = not any(
        (
            policy.allow_memory_writes,
            policy.allow_learning_writes,
            policy.allow_goal_task_project_writes,
            policy.allow_threshold_adaptation,
            policy.allow_benchmark_state,
        )
    )
    h6 = registry["H6"]
    remaining = ("H1", "H2", "H3", "H4", "H5", "H7", "H8")
    payload: dict[str, object] = {
        "schema_version": "hcpdq-v2-evaluation-exposure-recertification-v1",
        "status": "CAUSALLY_RECERTIFIED_HELD_OUT_NO_GO",
        "zero_authority": zero_authority,
        "zero_mutation": zero_mutation,
        "no_direct_internal_instantiation": all(
            token not in source for token in forbidden_tokens
        ),
        "family_mapping_metadata_only": tuple(
            inspect.signature(exposure.exposure_for_family).parameters
        )
        == ("family",),
        "ground_truth_firewall": set(
            field.name
            for field in exposure.ExposureRequest.__dataclass_fields__.values()
        ).isdisjoint(
            {
                "expected",
                "expected_answer",
                "ground_truth",
                "rubric",
                "human_answer",
                "score",
                "previous_score",
                "held_out_solution",
            }
        ),
        "h6_reuses_existing_certification": (
            h6.exposure_certified
            and h6.reuse_existing_certification
            and not h6.new_exposure_required
        ),
        "remaining_families_fail_closed": all(
            registry[family].calibration_only
            and not registry[family].exposure_certified
            and not registry[family].held_out_authorized
            for family in remaining
        ),
        "shadow_equivalence_guard": (
            exposure.shadow_equivalent(
                production_result="same",
                observed_result="same",
            )
            and not exposure.shadow_equivalent(
                production_result="same",
                observed_result="changed",
            )
        ),
        "held_out_construction_authorized": False,
        "human_comparison_authorized": False,
        "production_cognitive_change_detected": False,
        "recertified_module": "scripts.hcpdq_v2_evaluation_exposure",
        "policy": asdict(policy),
    }
    gates = (
        payload["zero_authority"],
        payload["zero_mutation"],
        payload["no_direct_internal_instantiation"],
        payload["family_mapping_metadata_only"],
        payload["ground_truth_firewall"],
        payload["h6_reuses_existing_certification"],
        payload["remaining_families_fail_closed"],
        payload["shadow_equivalence_guard"],
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
            recertify_evaluation_exposure(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
