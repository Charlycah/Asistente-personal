from core.cognitive_planning import (
    CognitiveDecisionKernel,
    CognitiveKernelMetricsCollector,
    CognitivePlanner,
    CognitivePlanOutcomeAssessment,
    ShadowAssessmentStatus,
)


def _unsatisfied_outcome():
    return CognitivePlanOutcomeAssessment(
        status=ShadowAssessmentStatus.UNSATISFIED,
        freshness_satisfied=False,
        evidence_satisfied=False,
        abstention_consistent=False,
        observed_evidence_count=0,
        observed_conflicting_sources=False,
        observed_freshness="unknown",
        observed_verification="unverified",
        observed_abstention=False,
        rationale_codes=("outcome_unsatisfied",),
    )


def test_kernel_metrics_start_empty_and_versioned():
    snapshot = CognitiveDecisionKernel().metrics_snapshot

    assert snapshot.schema_version == "rp22.04"
    assert snapshot.total_decisions == 0
    assert snapshot.average_calibration_score == 0.0


def test_kernel_metrics_count_policies_and_calibration_states():
    kernel = CognitiveDecisionKernel()
    planner = CognitivePlanner()

    kernel.consolidate(planner.plan("Hola"))
    kernel.consolidate(planner.plan("Hola otra vez"))

    snapshot = kernel.metrics_snapshot
    assert snapshot.total_decisions == 2
    assert dict(snapshot.policy_counts)["respond"] == 2
    assert snapshot.incomplete_calibrations == 2
    assert snapshot.average_calibration_score == 1.0


def test_kernel_metrics_count_divergences_without_changing_decision():
    kernel = CognitiveDecisionKernel()
    decision = kernel.consolidate(
        CognitivePlanner().plan("Hola"),
        outcome=_unsatisfied_outcome(),
    )

    snapshot = kernel.metrics_snapshot
    assert decision.policy.value == "fallback"
    assert snapshot.fallback_decisions == 1
    assert snapshot.partial_calibrations == 1
    assert dict(snapshot.divergence_counts)["outcome_divergence"] == 1


def test_metrics_snapshot_is_deterministic_and_json_ready():
    kernel = CognitiveDecisionKernel()
    kernel.consolidate(CognitivePlanner().plan("Hola"))

    payload = kernel.metrics_snapshot.as_dict()

    assert payload["schema_version"] == "rp22.04"
    assert isinstance(payload["policy_counts"], dict)
    assert payload == kernel.metrics_snapshot.as_dict()


def test_metrics_reset_is_explicit_and_collector_failure_is_open():
    class FailingCollector(CognitiveKernelMetricsCollector):
        def observe(self, resolution, calibration):
            raise RuntimeError("metrics unavailable")

    kernel = CognitiveDecisionKernel(metrics_collector=FailingCollector())
    decision = kernel.consolidate(CognitivePlanner().plan("Hola"))

    assert decision.policy.value == "respond"
    assert kernel.metrics_snapshot.total_decisions == 0
    kernel.reset_metrics()
    assert kernel.metrics_snapshot.total_decisions == 0
