from __future__ import annotations

import ast
import inspect
from dataclasses import fields
from datetime import datetime, timezone
from types import SimpleNamespace

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationContinuationDecision,
    GovernedInvestigationEpisodeStatus,
    GovernedInvestigationEpisodeTransition,
    GovernedInvestigationStoppingReason,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryResult,
    GovernedInvestigationExecutionReentryStatus,
)
from app.governed_multistep_investigation_reasoning_closure import (
    GovernedInvestigationReasoningClosureResult,
    GovernedInvestigationReasoningClosureStatus,
    GovernedMultiStepInvestigationReasoningClosureV1,
)
from app.governed_reasoning_runtime import (
    OfficialGovernedReasoningRuntimeGateway,
    build_default_governed_reasoning_orchestrator,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
)

NOW = datetime(2026, 8, 14, 14, 0, tzinfo=timezone.utc)


def _envelope(step: int) -> GovernedAcquiredEvidenceEnvelope:
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=f"level2-read-only-execution-step-{step:02d}-abcdef123456",
        status=GovernedLevel2ExecutionStatus.ACQUIRED,
        authorization_id=(f"independence-authorization-step-{step:02d}-abcdef123456"),
        requirement_id=f"discrimination-requirement-r{step}",
        plan_id=f"evidence-acquisition-plan-step-{step:02d}-abcdef123456",
        capability_name="local.sensor",
        evidence_description=f"discriminating observation {step}",
        declared_evidence_output=f"evidence_{step}",
        observed_value=20.0 + step,
        observation_source_reference=f"local-reader:e{step}",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=(f"execution:test-e{step}",),
        source_fingerprint="f" * 64,
    )


def _reentry(step: int) -> GovernedLevel2ReasoningReentryResult:
    envelope = _envelope(step)
    return GovernedLevel2ReasoningReentryResult(
        reentry_id=f"level2-reasoning-reentry-step-{step:02d}-abcdef123456",
        status=GovernedReasoningReentryStatus.REEVALUATED,
        execution_id=envelope.execution_id,
        authorization_id=envelope.authorization_id,
        requirement_id=envelope.requirement_id,
        plan_id=envelope.plan_id,
        capability_name=envelope.capability_name,
        evidence_id=f"evidence-{step}",
        source_reference=envelope.source_reference,
        world_snapshot_id=envelope.world_snapshot_id,
        reasoning_result=None,
        rationale_codes=(f"reentry:test-r{step}",),
        source_fingerprint="e" * 64,
        automatic_reevaluation_count=1,
    )


def _requirement_r2() -> DiscriminatingEvidenceRequirement:
    return DiscriminatingEvidenceRequirement(
        requirement_id="discrimination-requirement-r2",
        hypothesis_ids=("h1", "h2"),
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        known_elements=("shared-fact",),
        missing_evidence_descriptions=("discriminating observation 2",),
        evidence_codes=("comparison:indistinguishable",),
    )


def _execution_reentry() -> GovernedInvestigationExecutionReentryResult:
    boundary = GovernedMultiStepInvestigationEpisodeBoundaryV1()
    state = boundary.start(
        originating_reasoning_id="reasoning-decision-1",
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        initial_requirement_id="discrimination-requirement-r1",
    ).state
    state = boundary.record_acquisition(state, _envelope(1)).state
    state = boundary.record_reentry(state, _reentry(1)).state
    state = boundary.evaluate_continuation(state, _requirement_r2()).state
    state = boundary.record_acquisition(state, _envelope(2)).state
    auth_reentry = SimpleNamespace(
        episode_id=state.episode_id,
        source_reference=state.source_reference,
        world_snapshot_id=state.world_snapshot_id,
    )
    return GovernedInvestigationExecutionReentryResult(
        episode_id=state.episode_id,
        authorization_reentry=auth_reentry,
        status=GovernedInvestigationExecutionReentryStatus.ACQUIRED,
        evidence_envelope=_envelope(2),
        resulting_episode_state=state,
        execution_id=_envelope(2).execution_id,
        authorization_id=_envelope(2).authorization_id,
        requirement_id=_envelope(2).requirement_id,
        plan_id=_envelope(2).plan_id,
        source_reference=state.source_reference,
        world_snapshot_id=state.world_snapshot_id,
        current_step=2,
        remaining_acquisitions=0,
        execution_status=GovernedLevel2ExecutionStatus.ACQUIRED,
        rationale_codes=("execution_reentry:test-e2-recorded",),
        source_fingerprint="a" * 64,
        eligible_for_reasoning_reentry=True,
        execution_invocation_count=1,
        episode_record_invocation_count=1,
    )


def _real_reasoning_reentry() -> GovernedLevel2ReasoningReentryFoundationV1:
    runtime = OfficialGovernedReasoningRuntimeGateway(
        build_default_governed_reasoning_orchestrator()
    )
    return GovernedLevel2ReasoningReentryFoundationV1(runtime)


def test_valid_e2_reenters_reasoning_once_and_closes_episode() -> None:
    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _real_reasoning_reentry()
    ).consume(_execution_reentry(), now=NOW)

    assert result.status is GovernedInvestigationReasoningClosureStatus.CLOSED
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.episode_closed
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.CLOSED
    )
    assert (
        result.stopping_reason is GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED
    )
    assert result.remaining_acquisitions == 0


def test_rr2_preserves_exact_e2_a2_p2_r2_source_and_snapshot_lineage() -> None:
    execution = _execution_reentry()
    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _real_reasoning_reentry()
    ).consume(execution, now=NOW)

    reentry = result.reasoning_reentry
    assert reentry is not None
    assert reentry.execution_id == execution.execution_id
    assert reentry.authorization_id == execution.authorization_id
    assert reentry.plan_id == execution.plan_id
    assert reentry.requirement_id == execution.requirement_id
    assert reentry.source_reference == execution.source_reference
    assert reentry.world_snapshot_id == execution.world_snapshot_id


def test_rr2_is_new_relative_to_rr1_and_becomes_terminal_lineage() -> None:
    execution = _execution_reentry()
    old_reentry_ids = execution.resulting_episode_state.reentry_ids
    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _real_reasoning_reentry()
    ).consume(execution, now=NOW)

    assert result.reasoning_reentry_id not in old_reentry_ids
    assert result.resulting_episode_state.reentry_ids == (
        *old_reentry_ids,
        result.reasoning_reentry_id,
    )


def test_closed_result_exposes_no_third_step_eligibility_or_authority() -> None:
    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _real_reasoning_reentry()
    ).consume(_execution_reentry(), now=NOW)

    assert result.episode_closed
    assert not result.eligible_for_existing_planning
    assert not result.eligible_for_authorization
    assert not result.eligible_for_existing_execution
    assert not result.eligible_for_reasoning_reentry
    assert not result.creates_requirement
    assert not result.invokes_planning
    assert not result.invokes_authorization
    assert not result.invokes_execution
    assert not result.invokes_curiosity


def test_noneligible_execution_does_not_reenter_reasoning() -> None:
    execution = _execution_reentry()
    object.__setattr__(execution, "eligible_for_reasoning_reentry", False)

    class NeverCalled:
        calls = 0

        def reenter(self, envelope, *, now):
            self.calls += 1
            raise AssertionError("reasoning must not run")

    reasoning = NeverCalled()
    result = GovernedMultiStepInvestigationReasoningClosureV1(reasoning).consume(
        execution, now=NOW
    )

    assert result.status is GovernedInvestigationReasoningClosureStatus.NOT_ELIGIBLE
    assert result.reasoning_reentry_invocation_count == 0
    assert result.episode_record_invocation_count == 0
    assert reasoning.calls == 0


def test_reasoning_failure_fails_closed_without_retry_or_episode_record() -> None:
    class FailingReasoning:
        calls = 0

        def reenter(self, envelope, *, now):
            self.calls += 1
            raise RuntimeError("synthetic reasoning failure")

    reasoning = FailingReasoning()
    result = GovernedMultiStepInvestigationReasoningClosureV1(reasoning).consume(
        _execution_reentry(), now=NOW
    )

    assert reasoning.calls == 1
    assert result.status is GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 0
    assert not result.episode_closed
    assert not result.permits_retry


def test_reused_rr1_is_rejected_before_episode_record() -> None:
    execution = _execution_reentry()
    rr1 = _reentry(1)

    class ReusedReasoning:
        def reenter(self, envelope, *, now):
            return GovernedLevel2ReasoningReentryResult(
                reentry_id=rr1.reentry_id,
                status=GovernedReasoningReentryStatus.REEVALUATED,
                execution_id=envelope.execution_id,
                authorization_id=envelope.authorization_id,
                requirement_id=envelope.requirement_id,
                plan_id=envelope.plan_id,
                capability_name=envelope.capability_name,
                evidence_id="evidence-reused",
                source_reference=envelope.source_reference,
                world_snapshot_id=envelope.world_snapshot_id,
                reasoning_result=None,
                rationale_codes=("reentry:synthetic-reuse",),
                source_fingerprint="b" * 64,
                automatic_reevaluation_count=1,
            )

    result = GovernedMultiStepInvestigationReasoningClosureV1(
        ReusedReasoning()
    ).consume(execution, now=NOW)

    assert result.status is GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED
    assert result.episode_record_invocation_count == 0
    assert not result.episode_closed


def test_nonterminal_episode_boundary_result_is_rejected() -> None:
    class NonterminalBoundary:
        def record_reentry(self, state, reentry):
            return GovernedInvestigationEpisodeTransition(
                decision=GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED,
                state=state,
                rationale_codes=("investigation:synthetic-nonterminal",),
            )

    result = GovernedMultiStepInvestigationReasoningClosureV1(
        _real_reasoning_reentry(),
        episode_boundary=NonterminalBoundary(),
    ).consume(_execution_reentry(), now=NOW)

    assert result.status is GovernedInvestigationReasoningClosureStatus.REVIEW_REQUIRED
    assert result.reasoning_reentry_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert not result.episode_closed


def test_contract_defaults_forbid_r3_retry_and_side_effect_paths() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedInvestigationReasoningClosureResult)
    }
    for name in (
        "eligible_for_existing_planning",
        "eligible_for_authorization",
        "eligible_for_existing_execution",
        "eligible_for_reasoning_reentry",
        "creates_requirement",
        "invokes_planning",
        "invokes_authorization",
        "invokes_execution",
        "invokes_curiosity",
        "creates_questions",
        "emits_conversation",
        "modifies_memory",
        "modifies_world_model",
        "permits_retry",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_adapter_has_no_planning_authorization_execution_or_loop_calls() -> None:
    source = inspect.getsource(GovernedMultiStepInvestigationReasoningClosureV1)
    tree = ast.parse(source)

    for forbidden in (
        "GovernedMultiStepInvestigationPlanningReentryV1",
        "GovernedMultiStepInvestigationAuthorizationReentryV1",
        "GovernedMultiStepInvestigationExecutionReentryV1",
        "OfficialCapabilityGateway",
        "OfficialMemoryGateway",
        "OfficialConversationGateway",
        "GovernedEpistemicCuriosity",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source
    assert all(
        not (
            isinstance(node, ast.FunctionDef)
            and node.name
            in {
                "plan",
                "authorize",
                "execute",
                "retry",
                "run",
                "run_episode",
                "run_next_step",
            }
        )
        for node in ast.walk(tree)
    )
