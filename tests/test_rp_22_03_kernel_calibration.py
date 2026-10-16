from core.cognitive_planning import (
    CognitiveCalibrationStatus,
    CognitiveDecisionKernel,
    CognitiveKernelCalibrationEngine,
    CognitivePlanner,
    CognitivePlanOutcomeAssessment,
    CognitivePolicyResolution,
    ShadowAssessmentStatus,
)


def _outcome(*, status=ShadowAssessmentStatus.SATISFIED, abstained=False):
    return CognitivePlanOutcomeAssessment(
        status=status,
        freshness_satisfied=True,
        evidence_satisfied=True,
        abstention_consistent=True,
        observed_evidence_count=2,
        observed_conflicting_sources=False,
        observed_freshness="current",
        observed_verification="verified",
        observed_abstention=abstained,
        rationale_codes=("outcome_observed",),
    )


def test_kernel_publishes_versioned_calibration():
    decision = CognitiveDecisionKernel().consolidate(CognitivePlanner().plan("Hola"))

    assert decision.calibration.schema_version == "rp22.03"
    assert decision.calibration.status is CognitiveCalibrationStatus.INCOMPLETE
    assert decision.calibration.plan_policy_aligned is True
    assert decision.calibration.score == 1.0


def test_calibration_marks_fully_observed_alignment():
    plan = CognitivePlanner().plan("Hola")
    decision = CognitiveDecisionKernel().consolidate(plan, outcome=_outcome())

    assert decision.calibration.outcome_aligned is True
    assert decision.calibration.status is CognitiveCalibrationStatus.INCOMPLETE
    assert decision.calibration.divergence_codes == ()


def test_calibration_detects_outcome_divergence():
    plan = CognitivePlanner().plan("Hola")
    decision = CognitiveDecisionKernel().consolidate(
        plan,
        outcome=_outcome(status=ShadowAssessmentStatus.UNSATISFIED),
    )

    assert decision.calibration.outcome_aligned is False
    assert "outcome_divergence" in decision.calibration.divergence_codes
    assert decision.calibration.status is CognitiveCalibrationStatus.PARTIAL


def test_calibration_transport_is_deterministic_and_json_ready():
    calibration = CognitiveDecisionKernel().consolidate(
        CognitivePlanner().plan("Hola")
    ).calibration

    payload = calibration.as_dict()

    assert payload["schema_version"] == "rp22.03"
    assert payload["status"] == "incomplete"
    assert isinstance(payload["divergence_codes"], list)
    assert payload == calibration.as_dict()


def test_calibration_engine_is_observational_only():
    plan = CognitivePlanner().plan("Hola")
    resolution = CognitivePolicyResolution(
        policy="respond",
        decisive_rule="policies_satisfied",
        conflict_codes=(),
        rationale_codes=("policy_resolution:respond",),
        fallback_required=False,
    )

    calibration = CognitiveKernelCalibrationEngine().calibrate(plan, resolution)

    assert resolution.policy == "respond"
    assert calibration.plan_policy_aligned is True
    assert calibration.observation_codes[-1] == "decisive_rule:policies_satisfied"
