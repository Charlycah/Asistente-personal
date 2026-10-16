from __future__ import annotations

from dataclasses import dataclass

from core.cognitive_planning import (
    CognitiveCapabilitySelectionAssessment,
    CognitiveCapabilitySelectionAssessor,
    CognitiveContextSelectionAssessment,
    CognitiveContextSelectionAssessor,
    CognitiveDecisionContext,
    CognitiveDecisionKernel,
    CognitiveExecutiveActivationAssessment,
    CognitiveExecutiveActivationPolicy,
    CognitiveKernelMetricsCollector,
    CognitiveKernelMetricsSnapshot,
    CognitiveKernelObservabilityExport,
    CognitiveObservabilityProfile,
    CognitivePlan,
    CognitivePlanner,
    CognitivePlanOutcomeAssessment,
    CognitivePlanOutcomeAssessor,
    ExecutiveActivationDecision,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class CognitivePlannerShadowSnapshot:
    evaluations: int
    failures: int
    outcome_evaluations: int
    outcome_failures: int
    capability_evaluations: int
    capability_failures: int
    context_evaluations: int
    context_failures: int
    last_session_id: str | None
    last_plan: CognitivePlan | None
    last_assessment: CognitivePlanOutcomeAssessment | None
    last_capability_assessment: CognitiveCapabilitySelectionAssessment | None
    last_context_assessment: CognitiveContextSelectionAssessment | None
    executive_activation_evaluations: int
    executive_activation_failures: int
    executive_activations: int
    executive_skips: int
    executive_fallbacks: int
    last_executive_activation: CognitiveExecutiveActivationAssessment | None
    kernel_consolidations: int
    kernel_failures: int
    last_decision_context: CognitiveDecisionContext | None
    kernel_metrics: CognitiveKernelMetricsSnapshot


class CognitivePlannerShadowRuntime:
    """Observe plans and outcomes without affecting execution or responses."""

    def __init__(
        self,
        planner: CognitivePlanner | None = None,
        assessor: CognitivePlanOutcomeAssessor | None = None,
        capability_assessor: CognitiveCapabilitySelectionAssessor | None = None,
        context_assessor: CognitiveContextSelectionAssessor | None = None,
        executive_activation_policy: CognitiveExecutiveActivationPolicy | None = None,
        executive_activation_enabled: bool = False,
        decision_kernel: CognitiveDecisionKernel | None = None,
    ) -> None:
        self.planner = planner or CognitivePlanner()
        self.assessor = assessor or CognitivePlanOutcomeAssessor()
        self.context_assessor = context_assessor or CognitiveContextSelectionAssessor()
        self.capability_assessor = (
            capability_assessor or CognitiveCapabilitySelectionAssessor()
        )
        self.executive_activation_policy = (
            executive_activation_policy or CognitiveExecutiveActivationPolicy()
        )
        self.executive_activation_enabled = executive_activation_enabled
        self.decision_kernel = decision_kernel or CognitiveDecisionKernel()
        self._empty_kernel_metrics = CognitiveKernelMetricsCollector().snapshot
        self._evaluations = 0
        self._failures = 0
        self._outcome_evaluations = 0
        self._outcome_failures = 0
        self._capability_evaluations = 0
        self._capability_failures = 0
        self._context_evaluations = 0
        self._context_failures = 0
        self._executive_activation_evaluations = 0
        self._executive_activation_failures = 0
        self._executive_activations = 0
        self._executive_skips = 0
        self._executive_fallbacks = 0
        self._kernel_consolidations = 0
        self._kernel_failures = 0
        self._last_session_id: str | None = None
        self._last_plan: CognitivePlan | None = None
        self._last_assessment: CognitivePlanOutcomeAssessment | None = None
        self._last_context_assessment: CognitiveContextSelectionAssessment | None = None
        self._last_executive_activation: (
            CognitiveExecutiveActivationAssessment | None
        ) = None
        self._last_decision_context: CognitiveDecisionContext | None = None
        self._last_capability_assessment: (
            CognitiveCapabilitySelectionAssessment | None
        ) = None
        self._plans_by_session: dict[str, CognitivePlan] = {}
        self._assessments_by_session: dict[str, CognitivePlanOutcomeAssessment] = {}
        self._context_assessments_by_session: dict[
            str, CognitiveContextSelectionAssessment
        ] = {}
        self._decision_contexts_by_session: dict[str, CognitiveDecisionContext] = {}
        self._capability_assessments_by_session: dict[
            str, CognitiveCapabilitySelectionAssessment
        ] = {}

    @property
    def snapshot(self) -> CognitivePlannerShadowSnapshot:
        return CognitivePlannerShadowSnapshot(
            evaluations=self._evaluations,
            failures=self._failures,
            outcome_evaluations=self._outcome_evaluations,
            outcome_failures=self._outcome_failures,
            capability_evaluations=self._capability_evaluations,
            capability_failures=self._capability_failures,
            context_evaluations=self._context_evaluations,
            context_failures=self._context_failures,
            last_session_id=self._last_session_id,
            last_plan=self._last_plan,
            last_assessment=self._last_assessment,
            last_capability_assessment=self._last_capability_assessment,
            last_context_assessment=self._last_context_assessment,
            executive_activation_evaluations=self._executive_activation_evaluations,
            executive_activation_failures=self._executive_activation_failures,
            executive_activations=self._executive_activations,
            executive_skips=self._executive_skips,
            executive_fallbacks=self._executive_fallbacks,
            last_executive_activation=self._last_executive_activation,
            kernel_consolidations=self._kernel_consolidations,
            kernel_failures=self._kernel_failures,
            last_decision_context=self._last_decision_context,
            kernel_metrics=getattr(
                self.decision_kernel,
                "metrics_snapshot",
                self._empty_kernel_metrics,
            ),
        )


    def decision_context_for_session(
        self,
        session_id: str,
    ) -> CognitiveDecisionContext | None:
        return self._decision_contexts_by_session.get(session_id)

    def export_kernel_observability(
        self,
        session_id: str | None = None,
        *,
        profile: CognitiveObservabilityProfile = CognitiveObservabilityProfile.SUMMARY,
    ) -> CognitiveKernelObservabilityExport | None:
        decision = (
            self._last_decision_context
            if session_id is None
            else self._decision_contexts_by_session.get(session_id)
        )
        exporter = getattr(self.decision_kernel, "export_observability", None)
        if exporter is None:
            return None
        try:
            return exporter(decision, profile=profile)
        except Exception:
            return None

    def _refresh_decision_context(self, session_id: str) -> None:
        plan = self._plans_by_session.get(session_id)
        if plan is None:
            return
        self._kernel_consolidations += 1
        try:
            decision = self.decision_kernel.consolidate(
                plan,
                outcome=self._assessments_by_session.get(session_id),
                capability=self._capability_assessments_by_session.get(session_id),
                context=self._context_assessments_by_session.get(session_id),
                activation=self._last_executive_activation
                if self._last_session_id == session_id
                else None,
            )
        except Exception:
            self._kernel_failures += 1
            return
        self._last_decision_context = decision
        self._decision_contexts_by_session[session_id] = decision


    def assess_executive_activation(
        self,
        request: GovernedConversationPipelineRequest,
        descriptor,
        *,
        now,
    ) -> CognitiveExecutiveActivationAssessment | None:
        del now
        if not self.executive_activation_enabled:
            return None
        self._executive_activation_evaluations += 1
        plan = self._plans_by_session.get(request.session_id)
        try:
            assessment = self.executive_activation_policy.assess_semantic_candidate(
                plan, descriptor
            )
        except Exception:
            self._executive_activation_failures += 1
            return None
        self._last_executive_activation = assessment
        self._refresh_decision_context(request.session_id)
        if assessment.decision is ExecutiveActivationDecision.EXECUTE:
            self._executive_activations += 1
        elif assessment.decision is ExecutiveActivationDecision.SKIP:
            self._executive_skips += 1
        else:
            self._executive_fallbacks += 1
        return assessment

    def plan_for_session(self, session_id: str) -> CognitivePlan | None:
        return self._plans_by_session.get(session_id)

    def assessment_for_session(
        self,
        session_id: str,
    ) -> CognitivePlanOutcomeAssessment | None:
        return self._assessments_by_session.get(session_id)

    def context_assessment_for_session(
        self,
        session_id: str,
    ) -> CognitiveContextSelectionAssessment | None:
        return self._context_assessments_by_session.get(session_id)

    def observe_context_selection(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        available_conversation_turns: int,
        selected_conversation_turns: int,
        now,
    ) -> CognitiveContextSelectionAssessment | None:
        del now
        plan = self._plans_by_session.get(request.session_id)
        if plan is None:
            return None
        self._context_evaluations += 1
        try:
            assessment = self.context_assessor.assess(
                plan,
                available_conversation_turns=available_conversation_turns,
                selected_conversation_turns=selected_conversation_turns,
            )
        except Exception:
            self._context_failures += 1
            return None
        self._last_context_assessment = assessment
        self._context_assessments_by_session[request.session_id] = assessment
        self._refresh_decision_context(request.session_id)
        return assessment

    def capability_assessment_for_session(
        self,
        session_id: str,
    ) -> CognitiveCapabilitySelectionAssessment | None:
        return self._capability_assessments_by_session.get(session_id)

    def observe_capability_selection(
        self,
        request: GovernedConversationPipelineRequest,
        descriptor,
        *,
        origin: str,
        now,
    ) -> CognitiveCapabilitySelectionAssessment | None:
        del now
        plan = self._plans_by_session.get(request.session_id)
        if plan is None:
            return None
        self._capability_evaluations += 1
        try:
            assessment = self.capability_assessor.assess(
                plan, descriptor, origin=origin
            )
        except Exception:
            self._capability_failures += 1
            return None
        self._last_capability_assessment = assessment
        self._capability_assessments_by_session[request.session_id] = assessment
        self._refresh_decision_context(request.session_id)
        return assessment

    def observe(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now,
    ) -> CognitivePlan | None:
        del now
        self._evaluations += 1
        self._last_session_id = request.session_id
        try:
            plan = self.planner.plan(request.text)
        except Exception:
            self._failures += 1
            return None
        self._last_plan = plan
        self._plans_by_session[request.session_id] = plan
        self._refresh_decision_context(request.session_id)
        return plan

    def observe_result(
        self,
        request: GovernedConversationPipelineRequest,
        result: GovernedOperationalInterception,
        *,
        now,
    ) -> CognitivePlanOutcomeAssessment | None:
        del now
        plan = self._plans_by_session.get(request.session_id)
        if plan is None:
            return None
        self._outcome_evaluations += 1
        try:
            assessment = self.assessor.assess(plan, result.origin)
        except Exception:
            self._outcome_failures += 1
            return None
        self._last_assessment = assessment
        self._assessments_by_session[request.session_id] = assessment
        self._refresh_decision_context(request.session_id)
        return assessment
