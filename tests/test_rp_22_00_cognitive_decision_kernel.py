from datetime import datetime, timezone

from app.cognitive_planner_shadow_runtime import CognitivePlannerShadowRuntime
from core.cognitive_planning import (
    CognitiveConfidenceLevel,
    CognitiveDecisionKernel,
    CognitiveDecisionPolicy,
    CognitivePlanner,
    CognitiveRiskLevel,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def test_kernel_consolidates_current_information_plan():
    plan = CognitivePlanner().plan("¿Qué pasó hoy en Argentina?")

    decision = CognitiveDecisionKernel().consolidate(plan)

    assert decision.plan is plan
    assert decision.risk is CognitiveRiskLevel.HIGH
    assert decision.confidence is CognitiveConfidenceLevel.HIGH
    assert decision.policy is CognitiveDecisionPolicy.ABSTAIN_IF_UNVERIFIED
    assert "kernel_policy:abstain_if_unverified" in decision.rationale_codes


def test_kernel_keeps_simple_conversation_low_risk():
    plan = CognitivePlanner().plan("Hola, ¿cómo estás?")

    decision = CognitiveDecisionKernel().consolidate(plan)

    assert decision.risk is CognitiveRiskLevel.LOW
    assert decision.policy is CognitiveDecisionPolicy.RESPOND


def test_shadow_runtime_publishes_decision_context_per_session():
    runtime = CognitivePlannerShadowRuntime()
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="kernel-session",
        text="¿Cómo estará el clima hoy?",
    )

    plan = runtime.observe(request, now=datetime.now(timezone.utc))
    decision = runtime.decision_context_for_session("kernel-session")

    assert plan is not None
    assert decision is not None
    assert decision.plan is plan
    assert runtime.snapshot.kernel_consolidations == 1
    assert runtime.snapshot.last_decision_context is decision


def test_kernel_failure_is_fail_open_and_preserves_plan():
    class BrokenKernel:
        def consolidate(self, plan, **kwargs):
            del plan, kwargs
            raise RuntimeError("unavailable")

    runtime = CognitivePlannerShadowRuntime(decision_kernel=BrokenKernel())
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="kernel-failure",
        text="Hola",
    )

    plan = runtime.observe(request, now=datetime.now(timezone.utc))

    assert plan is not None
    assert runtime.plan_for_session("kernel-failure") is plan
    assert runtime.decision_context_for_session("kernel-failure") is None
    assert runtime.snapshot.kernel_failures == 1
