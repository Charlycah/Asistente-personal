from __future__ import annotations

from datetime import datetime, timezone

from app.governed_independence_authorization_boundary import GovernedInitiationDecision
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_long_horizon_investigation_a2_authorization_reentry import (
    GovernedInvestigationA2AuthorizationAdmissionStatus,
    GovernedLongHorizonInvestigationA2AuthorizationReentryV1,
)
from app.governed_long_horizon_investigation_e2_execution_reentry import (
    GovernedInvestigationE2ExecutionAdmissionStatus,
    GovernedLongHorizonInvestigationE2ExecutionReentryV1,
)
from app.governed_long_horizon_investigation_p2_planning_reentry import (
    GovernedInvestigationP2PlanningAdmissionStatus,
    GovernedLongHorizonInvestigationP2PlanningReentryV1,
)
from app.governed_long_horizon_investigation_reassessment_requirement_admission import (
    GovernedInvestigationReassessmentRequirementAdmissionStatus,
    GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1,
)
from app.governed_long_horizon_investigation_rr2_terminal_closure import (
    GovernedInvestigationRR2TerminalClosureStatus,
    GovernedLongHorizonInvestigationRR2TerminalClosureV1,
)
from app.governed_multistep_investigation_authorization_reentry import (
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationStoppingReason,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedMultiStepInvestigationExecutionReentryV1,
)
from app.governed_multistep_investigation_planning_reentry import (
    GovernedMultiStepInvestigationPlanningReentryV1,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    PermissionScope,
)
from core.governed_read_only_evidence import GovernedReadOnlyEvidenceObservation
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from tests.architecture import (
    test_cap11_rr_n_to_discriminant_requirement_n_plus_1_contract_red as rrn_contract,
)
from tests.architecture import (
    test_post_m409_1_governed_multistep_investigation_execution_reentry_v1,
)

execution_v1 = (
    test_post_m409_1_governed_multistep_investigation_execution_reentry_v1
)

NOW = datetime(2026, 8, 31, 16, 0, tzinfo=timezone.utc)


class _Reader:
    def __init__(self) -> None:
        self.calls = 0

    def read_evidence(self, request, *, now):
        self.calls += 1
        assert now is NOW
        return GovernedReadOnlyEvidenceObservation(
            evidence_output=request.declared_evidence_output,
            value=40.0 + self.calls,
            source_reference=f"local-reader:cap11-full-cycle:{self.calls}",
            rationale_codes=("reader:cap11-full-cycle",),
        )


class _Reasoning:
    def __init__(self) -> None:
        self.calls = 0

    def reenter(self, envelope, *, now):
        self.calls += 1
        assert now is NOW
        return GovernedLevel2ReasoningReentryResult(
            reentry_id=(
                f"level2-reasoning-reentry-cap11-full-cycle-{self.calls}-abcdef123456"
            ),
            status=GovernedReasoningReentryStatus.REEVALUATED,
            execution_id=envelope.execution_id,
            authorization_id=envelope.authorization_id,
            requirement_id=envelope.requirement_id,
            plan_id=envelope.plan_id,
            capability_name=envelope.capability_name,
            evidence_id=f"cap11-full-cycle-evidence-{self.calls}",
            source_reference=envelope.source_reference,
            world_snapshot_id=envelope.world_snapshot_id,
            reasoning_result=None,
            rationale_codes=("reentry:cap11-full-cycle",),
            source_fingerprint=("a" if self.calls == 1 else "b") * 64,
            automatic_reevaluation_count=1,
        )


def _assessment(hypothesis_id: str, evidence_id: str):
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"proposition {hypothesis_id}",
        relation=HypothesisEvidenceRelation.UNRESOLVED,
        evidence_references=(evidence_id,),
        rationale_codes=("assessment:cap11-full-cycle",),
    )


def _report_for(closure, step: int) -> GovernedHypothesisDeepeningReport:
    assert closure.reasoning_reentry is not None
    evidence_id = closure.reasoning_reentry.evidence_id
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-cap11-full-cycle-{step}",
        status=HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=closure.source_reference,
        world_snapshot_id=closure.world_snapshot_id,
        assessments=(
            _assessment("hypothesis-1", evidence_id),
            _assessment("hypothesis-2", evidence_id),
        ),
        epistemic_gaps=(),
        evidence_codes=(f"evidence:cap11-full-cycle-{step}",),
        risk_codes=("observation_not_truth",),
        source_fingerprint=("c" if step == 3 else "d") * 64,
    )


def test_green_long_horizon_budget_four_closes_one_real_n_step_cycle() -> None:
    admission_owner = (
        GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1()
    )

    r3 = admission_owner.consume(rrn_contract._closure(2), rrn_contract._report(2))
    assert r3.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert r3.source_requirement is not None
    assert r3.resulting_episode_state is not None
    assert r3.resulting_episode_state.current_step == 3
    assert r3.resulting_episode_state.remaining_acquisitions == 2

    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reader = _Reader()
    runtime.register(
        name="local.sensor",
        description="Local deterministic governed evidence reader.",
        interceptor=execution_v1._NoopInterceptor(),
        evidence_reader=reader,
        evidence_outputs=r3.source_requirement.missing_evidence_descriptions,
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        permission_scope=PermissionScope.READ,
    )

    planning_owner = GovernedMultiStepInvestigationPlanningReentryV1(manager)
    authorization_owner = GovernedMultiStepInvestigationAuthorizationReentryV1(manager)
    execution_owner = GovernedMultiStepInvestigationExecutionReentryV1(runtime)
    reasoning = _Reasoning()
    reasoning_owner = GovernedMultiStepInvestigationReasoningClosureV1(reasoning)

    def run_step(admission):
        planning = GovernedLongHorizonInvestigationP2PlanningReentryV1(
            planning_reentry=planning_owner
        ).consume(admission)
        assert planning.status is GovernedInvestigationP2PlanningAdmissionStatus.PLANNED
        assert planning.planning_reentry is not None

        authorization = GovernedLongHorizonInvestigationA2AuthorizationReentryV1(
            authorization_reentry=authorization_owner
        ).consume(planning)
        assert authorization.status is (
            GovernedInvestigationA2AuthorizationAdmissionStatus.AUTHORIZED
        )
        assert authorization.decision is GovernedInitiationDecision.MAY_INITIATE
        assert authorization.authorization_reentry is not None

        execution = GovernedLongHorizonInvestigationE2ExecutionReentryV1(
            execution_reentry=execution_owner
        ).consume(authorization, now=NOW)
        assert execution.status is (
            GovernedInvestigationE2ExecutionAdmissionStatus.ACQUIRED
        )
        assert execution.execution_reentry is not None

        closure = GovernedLongHorizonInvestigationRR2TerminalClosureV1(
            reasoning_closure=reasoning_owner
        ).consume(execution, now=NOW)
        assert closure.closure is not None
        return planning, authorization, execution, closure

    p3, a3, e3, rr3 = run_step(r3)
    assert p3.planning_reentry.current_step == 3
    assert a3.authorization_reentry.current_step == 3
    assert e3.execution_reentry.current_step == 3
    assert rr3.status is GovernedInvestigationRR2TerminalClosureStatus.RECORDED
    assert rr3.closure.status is GovernedInvestigationReasoningClosureStatus.RECORDED
    assert rr3.resulting_episode_state is not None
    assert rr3.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT
    )
    assert rr3.resulting_episode_state.remaining_acquisitions == 1
    assert rr3.stopping_reason is GovernedInvestigationStoppingReason.NONE

    r4 = admission_owner.consume(rr3.closure, _report_for(rr3.closure, 3))
    assert r4.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.ADMITTED
    )
    assert r4.resulting_episode_state is not None
    assert r4.resulting_episode_state.current_step == 4
    assert r4.resulting_episode_state.remaining_acquisitions == 1

    p4, a4, e4, rr4 = run_step(r4)
    assert p4.planning_reentry.current_step == 4
    assert a4.authorization_reentry.current_step == 4
    assert e4.execution_reentry.current_step == 4
    assert e4.execution_reentry.remaining_acquisitions == 0
    assert rr4.status is GovernedInvestigationRR2TerminalClosureStatus.CLOSED
    assert rr4.closure.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert rr4.resulting_episode_state is not None
    assert rr4.resulting_episode_state.status is (
        GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert rr4.resulting_episode_state.remaining_acquisitions == 0
    assert rr4.stopping_reason is (GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED)

    r5 = admission_owner.consume(rr4.closure, _report_for(rr4.closure, 4))
    assert r5.status is (
        GovernedInvestigationReassessmentRequirementAdmissionStatus.NOT_ELIGIBLE
    )
    assert r5.discrimination_invocation_count == 0
    assert r5.continuation_invocation_count == 0
    assert not r5.invokes_planning

    state = rr4.resulting_episode_state
    assert state.requirement_ids[-2:] == (
        r3.source_requirement.requirement_id,
        r4.source_requirement.requirement_id,
    )
    assert state.plan_ids[-2:] == (p3.plan_id, p4.plan_id)
    assert state.authorization_ids[-2:] == (a3.authorization_id, a4.authorization_id)
    assert state.execution_ids[-2:] == (e3.execution_id, e4.execution_id)
    assert state.reentry_ids[-2:] == (
        rr3.reasoning_reentry_id,
        rr4.reasoning_reentry_id,
    )
    assert reader.calls == 2
    assert reasoning.calls == 2
