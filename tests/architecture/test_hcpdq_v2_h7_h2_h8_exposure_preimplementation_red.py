from __future__ import annotations

import importlib
import inspect
from dataclasses import FrozenInstanceError, fields

import pytest

MODULE_NAME = "scripts.hcpdq_v2_h7_h2_h8_existing_authority_exposure"


def _module():
    try:
        return importlib.import_module(MODULE_NAME)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: missing HCPDQ-v2 H7/H2/H8 causal read-only exposure layer",
            pytrace=False,
        )


def test_w1_h7_exposure_preserves_existing_planning_authority_identity():
    module = _module()
    evidence = module.H7ExposureEvidence(
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
        authority_participation_evidence=("planning_foundation",),
        measurement_validity="valid",
    )
    assert evidence.existing_authority == "planning_foundation"
    assert evidence.planning_invocation_count == 1


def test_w2_h7_causal_join_requires_lineage_and_exactly_one_existing_planning_call():
    module = _module()
    evidence = module.H7ExposureEvidence(
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
    assert module.h7_exposure_certified(evidence) is True

    wrong_count = module.H7ExposureEvidence(
        **{
            **evidence.__dict__,
            "planning_invocation_count": 0,
        }
    )
    assert module.h7_exposure_certified(wrong_count) is False


def test_w3_h7_exposure_never_authorizes_execution_or_new_planning_authority():
    module = _module()
    policy = module.default_wave1_exposure_policy()
    assert policy.allow_plan_execution is False
    assert policy.allow_planner_binding is False
    assert policy.allow_new_planning_authority is False


def test_w4_h2_exposure_keeps_epistemic_sufficiency_and_response_decision_distinct():
    module = _module()
    evidence = module.H2ExposureEvidence(
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
    assert evidence.derived_context_available is True
    assert evidence.response_decision == "abstained"


def test_w5_h2_abstention_is_certified_only_with_joined_existing_response_decision():
    module = _module()
    joined = module.H2ExposureEvidence(
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
    assert module.h2_exposure_certified(joined) is True

    unjoined = module.H2ExposureEvidence(
        **{
            **joined.__dict__,
            "causal_join_evidence": (),
        }
    )
    assert module.h2_exposure_certified(unjoined) is False


def test_w6_h2_exposure_cannot_decide_to_answer_or_abstain():
    module = _module()
    policy = module.default_wave1_exposure_policy()
    assert policy.allow_response_decision is False
    assert policy.allow_stopping_decision is False
    assert policy.allow_epistemic_threshold_change is False


def test_w7_h8_exposure_preserves_provenance_and_existing_conflict_resolution():
    module = _module()
    evidence = module.H8ExposureEvidence(
        family="H8",
        provenance_id="reasoning-method-provenance-1",
        consumed_assessment_id="reasoning-method-context-1",
        conflict_ids=("conflict-1",),
        resolution_statuses=("resolved",),
        selected_claim_ids=("claim-2",),
        requires_review=False,
        confidence=0.75,
        authority_participation_evidence=(
            "governed_reasoning",
            "conflict-1",
        ),
        measurement_validity="valid",
    )
    assert evidence.provenance_id.startswith("reasoning-method-provenance-")
    assert evidence.selected_claim_ids == ("claim-2",)


def test_w8_h8_causal_join_requires_existing_resolution_evidence_not_provenance_alone():
    module = _module()
    joined = module.H8ExposureEvidence(
        family="H8",
        provenance_id="reasoning-method-provenance-1",
        consumed_assessment_id="reasoning-method-context-1",
        conflict_ids=("conflict-1",),
        resolution_statuses=("resolved",),
        selected_claim_ids=("claim-2",),
        requires_review=False,
        confidence=0.75,
        authority_participation_evidence=(
            "governed_reasoning",
            "conflict-1",
        ),
        measurement_validity="valid",
    )
    assert module.h8_exposure_certified(joined) is True

    provenance_only = module.H8ExposureEvidence(
        **{
            **joined.__dict__,
            "conflict_ids": (),
            "resolution_statuses": (),
            "selected_claim_ids": (),
            "authority_participation_evidence": ("governed_reasoning",),
        }
    )
    assert module.h8_exposure_certified(provenance_only) is False


def test_w9_h8_exposure_cannot_rank_sources_select_claims_or_change_conflict_policy():
    module = _module()
    policy = module.default_wave1_exposure_policy()
    assert policy.allow_source_ranking is False
    assert policy.allow_claim_selection is False
    assert policy.allow_conflict_policy_change is False


def test_w10_all_wave1_evidence_models_are_frozen_and_ground_truth_blind():
    module = _module()
    forbidden = {
        "expected",
        "expected_answer",
        "ground_truth",
        "rubric",
        "human_answer",
        "score",
        "previous_score",
        "held_out_solution",
    }
    for model in (
        module.H7ExposureEvidence,
        module.H2ExposureEvidence,
        module.H8ExposureEvidence,
    ):
        names = {field.name for field in fields(model)}
        assert forbidden.isdisjoint(names)
        assert getattr(model, "__dataclass_params__").frozen is True

    policy = module.default_wave1_exposure_policy()
    with pytest.raises(FrozenInstanceError):
        policy.allow_claim_selection = True


def test_w11_wave1_mapping_is_family_metadata_only_and_has_no_prompt_classifier():
    module = _module()
    signature = inspect.signature(module.exposure_kind_for_family)
    assert tuple(signature.parameters) == ("family",)
    source = inspect.getsource(module.exposure_kind_for_family)
    assert "prompt" not in source
    assert "classify" not in source
    assert "semantic" not in source.casefold()


def test_w12_wave1_fails_closed_and_keeps_held_out_no_go():
    module = _module()
    assert module.measurement_failure_classification(
        causal_join_present=False,
        degraded=False,
    ) == "NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2"
    assert module.held_out_authorized(
        {"H6": True, "H7": False, "H2": False, "H8": False}
    ) is False

    policy = module.default_wave1_exposure_policy()
    assert policy.allow_held_out_construction is False
    assert policy.allow_human_comparison is False
    assert policy.allow_persistence_or_adaptation is False
    assert policy.allow_new_authority is False
