from core.cognitive_planning import (
    CognitiveCapabilitySelectionAssessment,
    CognitiveContextSelectionAssessment,
    CognitiveDecisionKernel,
    CognitiveDecisionPolicy,
    CognitivePlanner,
    CognitivePlanOutcomeAssessment,
    CognitivePolicyResolutionEngine,
    ContextRequirement,
    ShadowAssessmentStatus,
)


def test_required_evidence_has_priority_over_other_policies():
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
    assert decision.policy_resolution.decisive_rule == "required_evidence_not_satisfied"
    assert "contradictory_sources" in decision.policy_resolution.conflict_codes


def test_context_failure_resolves_to_legacy_fallback():
    plan = CognitivePlanner().plan("¿Y por qué?")
    context = CognitiveContextSelectionAssessment(
        status=ShadowAssessmentStatus.UNSATISFIED,
        required_context=(ContextRequirement.CONVERSATION,),
        available_conversation_turns=2,
        selected_conversation_turns=0,
        conversation_context_required=True,
        conversation_context_satisfied=False,
        personal_memory_required=False,
        context_applied=False,
        over_injection_observed=False,
        rationale_codes=("planned_conversation_context_missing",),
    )

    decision = CognitiveDecisionKernel().consolidate(plan, context=context)

    assert decision.policy is CognitiveDecisionPolicy.FALLBACK
    assert decision.policy_resolution.fallback_required is True
    assert decision.policy_resolution.decisive_rule == "low_confidence"
    assert "context_unsatisfied" in decision.policy_resolution.conflict_codes


def test_capability_mismatch_is_recorded_and_resolved_conservatively():
    plan = CognitivePlanner().plan("Creá una nota")
    capability = CognitiveCapabilitySelectionAssessment(
        capability_name="calendar",
        capability_kind="calendar",
        matched_requirement=None,
        compatible=False,
        governed=True,
        provider_agnostic=True,
        rationale_codes=("planned_tool_requirement_not_matched",),
    )

    decision = CognitiveDecisionKernel().consolidate(plan, capability=capability)

    assert decision.policy is CognitiveDecisionPolicy.FALLBACK
    assert "capability_mismatch" in decision.policy_resolution.conflict_codes
    assert "policy_resolution:fallback" in decision.rationale_codes


def test_resolution_engine_failure_is_fail_open():
    class BrokenPolicyResolutionEngine:
        def resolve(self, *args, **kwargs):
            del args, kwargs
            raise RuntimeError("unavailable")

    plan = CognitivePlanner().plan("Hola")
    kernel = CognitiveDecisionKernel(
        policy_resolution_engine=BrokenPolicyResolutionEngine()
    )

    decision = kernel.consolidate(plan)

    assert decision.policy is CognitiveDecisionPolicy.FALLBACK
    assert decision.policy_resolution.fallback_required is True
    assert decision.policy_resolution.decisive_rule == "resolution_engine_failure"


def test_policy_resolution_engine_returns_normal_response_when_satisfied():
    plan = CognitivePlanner().plan("Hola")

    resolution = CognitivePolicyResolutionEngine().resolve(
        plan,
        risk="low",
        confidence="high",
    )

    assert resolution.policy == "respond"
    assert resolution.decisive_rule == "policies_satisfied"
    assert resolution.conflict_codes == ()
