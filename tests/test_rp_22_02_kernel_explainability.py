from core.cognitive_planning import (
    CognitiveDecisionExplainer,
    CognitiveDecisionKernel,
    CognitiveDecisionPolicy,
    CognitivePlanner,
    CognitivePlanOutcomeAssessment,
    CognitivePolicyResolution,
    ShadowAssessmentStatus,
)


def test_kernel_publishes_structured_explanation():
    plan = CognitivePlanner().plan("Hola")

    decision = CognitiveDecisionKernel().consolidate(plan)

    assert decision.explanation.schema_version == "rp22.02"
    assert decision.explanation.decision == decision.policy.value
    assert decision.explanation.decisive_rule == "policies_satisfied"
    assert "risk:low" in decision.explanation.evaluated_rules
    assert "confidence:" in " ".join(decision.explanation.evaluated_rules)


def test_explanation_preserves_conflicts_and_decisive_rule():
    plan = CognitivePlanner().plan("¿Qué pasó hoy en Argentina?")
    outcome = CognitivePlanOutcomeAssessment(
        status=ShadowAssessmentStatus.PARTIAL,
        freshness_satisfied=True,
        evidence_satisfied=False,
        abstention_consistent=False,
        observed_evidence_count=1,
        observed_conflicting_sources=True,
        observed_freshness="live",
        observed_verification="partial",
        observed_abstention=False,
        rationale_codes=("conflicting_sources_observed",),
    )

    decision = CognitiveDecisionKernel().consolidate(plan, outcome=outcome)

    assert decision.policy is CognitiveDecisionPolicy.ABSTAIN_IF_UNVERIFIED
    assert decision.explanation.decisive_rule == "required_evidence_not_satisfied"
    assert "contradictory_sources" in decision.explanation.conflict_codes
    assert "conflicting_sources_observed" in decision.explanation.evidence_codes


def test_explanation_transport_is_deterministic_and_json_ready():
    plan = CognitivePlanner().plan("Hola")
    explanation = CognitiveDecisionKernel().consolidate(plan).explanation

    payload = explanation.as_dict()

    assert payload["schema_version"] == "rp22.02"
    assert isinstance(payload["evaluated_rules"], list)
    assert isinstance(payload["conflict_codes"], list)
    assert isinstance(payload["evidence_codes"], list)
    assert payload == explanation.as_dict()


def test_explainer_does_not_change_policy_resolution():
    plan = CognitivePlanner().plan("Hola")
    resolution = CognitivePolicyResolution(
        policy="respond_with_caution",
        decisive_rule="elevated_risk",
        conflict_codes=(),
        rationale_codes=("policy_resolution:respond_with_caution",),
        fallback_required=False,
    )

    explanation = CognitiveDecisionExplainer().explain(
        plan,
        resolution,
        risk="moderate",
        confidence="high",
    )

    assert explanation.decision == resolution.policy
    assert explanation.fallback_required is resolution.fallback_required
    assert "elevated_risk" in explanation.narrative


def test_explanation_failure_is_fail_open_and_preserves_decision():
    class BrokenExplainer:
        def explain(self, *args, **kwargs):
            del args, kwargs
            raise RuntimeError("unavailable")

    plan = CognitivePlanner().plan("Hola")
    kernel = CognitiveDecisionKernel(decision_explainer=BrokenExplainer())
    decision = kernel.consolidate(plan)

    assert decision.policy is CognitiveDecisionPolicy.RESPOND
    assert decision.explanation.decision == "respond"
    assert decision.explanation.evidence_codes == ("explanation_engine_failure",)
