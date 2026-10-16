from __future__ import annotations

import inspect
from datetime import datetime, timezone
from importlib import import_module

from app.governed_multistep_investigation_authorization_reentry import (
    GovernedInvestigationAuthorizationReentryStatus,
    GovernedMultiStepInvestigationAuthorizationReentryV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeStatus,
)
from app.governed_multistep_investigation_execution_reentry import (
    GovernedInvestigationExecutionReentryStatus,
    GovernedMultiStepInvestigationExecutionReentryV1,
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

auth_red = import_module(
    "tests.architecture."
    "test_cap11_planning_step_n_to_existing_authorization_reentry_contract_red"
)
execution_v1 = import_module(
    "tests.architecture."
    "test_post_m409_1_governed_multistep_investigation_execution_reentry_v1"
)

NOW = datetime(2026, 8, 30, 18, 0, tzinfo=timezone.utc)


class _ContractReader:
    def __init__(self) -> None:
        self.calls = 0

    def read_evidence(self, request, *, now):
        self.calls += 1
        return GovernedReadOnlyEvidenceObservation(
            evidence_output="next discriminating observation",
            value=24.5,
            source_reference="local-reader:cap11-step-n",
            rationale_codes=("reader:local_read_only",),
        )


def _runtime_for_contract():
    manager = CapabilityRegistryManager()
    runtime = OfficialRuntimeCapabilityRegistry(manager)
    reader = _ContractReader()
    runtime.register(
        name="local.sensor",
        description="Local deterministic evidence reader.",
        interceptor=execution_v1._NoopInterceptor(),
        evidence_reader=reader,
        evidence_outputs=("next discriminating observation",),
        initiation_policy=CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS,
        effect_class=CapabilityEffectClass.READ_ONLY,
        interaction_scope=CapabilityInteractionScope.INTERNAL,
        permission_scope=PermissionScope.READ,
    )
    return manager, runtime, reader


def _authorization_to(step: int, *, budget: int = 4):
    manager, planning, requirement = auth_red._planning_to(step, budget=budget)
    authorization = GovernedMultiStepInvestigationAuthorizationReentryV1(
        manager
    ).consume(planning)
    assert (
        authorization.status
        is GovernedInvestigationAuthorizationReentryStatus.AUTHORIZED
    )
    return manager, authorization, requirement


def test_red_step_three_executes_existing_gateway_once_and_records_e3() -> None:
    manager, authorization, requirement = _authorization_to(3)
    _, runtime, reader = _runtime_for_contract()
    # The execution owner receives the runtime authority; the authorization lineage
    # remains the exact canonical A3 produced from the separately built registry.
    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.requirement_id == requirement.requirement_id
    assert result.authorization_id == authorization.authorization_id
    assert result.plan_id == authorization.plan_id
    assert result.current_step == 3
    assert reader.calls == 1


def test_red_step_four_executes_existing_gateway_once_and_records_e4() -> None:
    _, authorization, requirement = _authorization_to(4)
    _, runtime, reader = _runtime_for_contract()

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.requirement_id == requirement.requirement_id
    assert result.current_step == 4
    assert result.remaining_acquisitions == 0
    assert reader.calls == 1


def test_red_acquired_e3_with_budget_remaining_is_reasoning_reentry_eligible() -> None:
    _, authorization, _ = _authorization_to(3)
    _, runtime, _ = _runtime_for_contract()

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert (
        result.resulting_episode_state.status
        is GovernedInvestigationEpisodeStatus.AWAITING_REENTRY
    )
    assert result.remaining_acquisitions == 1
    assert result.eligible_for_reasoning_reentry
    assert not result.invokes_reasoning
    assert not result.permits_retry


def test_legacy_a2_e2_budget_two_remains_exactly_supported() -> None:
    _, authorization, _ = _authorization_to(2, budget=2)
    _, runtime, reader = _runtime_for_contract()

    result = GovernedMultiStepInvestigationExecutionReentryV1(runtime).consume(
        authorization,
        now=NOW,
    )

    assert result.status is GovernedInvestigationExecutionReentryStatus.ACQUIRED
    assert result.execution_invocation_count == 1
    assert result.episode_record_invocation_count == 1
    assert result.current_step == 2
    assert result.remaining_acquisitions == 0
    assert result.eligible_for_reasoning_reentry
    assert reader.calls == 1


def test_red_generalization_removes_e2_terminal_guards_without_new_executor() -> None:
    source = inspect.getsource(GovernedMultiStepInvestigationExecutionReentryV1)

    assert "current_step != 2" not in source
    assert "remaining_acquisitions != 1" not in source
    assert "transition.state.remaining_acquisitions != 0" not in source
    assert "and state.remaining_acquisitions == 0" not in source

    for forbidden in (
        "GovernedLevel2ReasoningReentryFoundationV1",
        "GovernedMultiStepInvestigationReasoningClosureV1",
        "ResearchLoop",
        "HorizonManager",
    ):
        assert forbidden not in source
