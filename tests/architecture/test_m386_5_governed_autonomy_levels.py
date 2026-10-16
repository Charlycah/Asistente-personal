from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_maturity import (
    AUTONOMY_GOVERNANCE_POLICY,
    GOVERNED_AUTONOMY_STAGES,
    GovernedAutonomyStage,
    PermissionMode,
    governed_autonomy_stage,
)
from core.controlled_autonomy import AutonomyLevel, RiskLevel

EXPECTED_STAGES = {
    GovernedAutonomyStage.INFORM,
    GovernedAutonomyStage.RECOMMEND,
    GovernedAutonomyStage.PREPARE,
    GovernedAutonomyStage.EXECUTE_PREVALIDATED,
    GovernedAutonomyStage.RESOLVE_MINOR_EXCEPTIONS,
    GovernedAutonomyStage.REQUEST_EXPANSION,
}


def test_m386_5_defines_the_six_agreed_stages_in_order() -> None:
    stages = tuple(item.stage for item in GOVERNED_AUTONOMY_STAGES)
    assert set(stages) == EXPECTED_STAGES
    assert stages == tuple(GovernedAutonomyStage)
    assert tuple(int(stage) for stage in stages) == tuple(range(6))


def test_m386_5_stages_reuse_the_existing_runtime_authority() -> None:
    assert governed_autonomy_stage(0).runtime_level is AutonomyLevel.OBSERVE_ONLY
    assert governed_autonomy_stage(1).runtime_level is AutonomyLevel.RECOMMEND
    assert (
        governed_autonomy_stage(2).runtime_level
        is AutonomyLevel.CONFIRM_BEFORE_ACTION
    )
    assert (
        governed_autonomy_stage(3).runtime_level
        is AutonomyLevel.AUTONOMOUS_LOW_RISK
    )


def test_m386_5_only_stages_three_and_four_may_describe_execution() -> None:
    executable = {item.stage for item in GOVERNED_AUTONOMY_STAGES if item.may_execute}
    assert executable == {
        GovernedAutonomyStage.EXECUTE_PREVALIDATED,
        GovernedAutonomyStage.RESOLVE_MINOR_EXCEPTIONS,
    }


def test_m386_5_execution_remains_delegated_reversible_audited_and_low_risk() -> None:
    executable = [item for item in GOVERNED_AUTONOMY_STAGES if item.may_execute]
    for definition in executable:
        assert definition.permitted_permission_modes == {PermissionMode.DELEGABLE}
        assert definition.maximum_runtime_risk is RiskLevel.LOW
        assert definition.requires_active_delegation is True
        assert definition.requires_reversibility is True
        assert definition.requires_audit is True


def test_m386_5_preparation_is_not_execution() -> None:
    definition = governed_autonomy_stage(GovernedAutonomyStage.PREPARE)
    assert definition.may_execute is False
    assert PermissionMode.CONFIRMATION_REQUIRED in (
        definition.permitted_permission_modes
    )
    assert any(
        "preparación" in item.casefold()
        for item in definition.forbidden_behaviors
    )


def test_m386_5_minor_exception_cannot_change_goal_capability_or_scope() -> None:
    definition = governed_autonomy_stage(
        GovernedAutonomyStage.RESOLVE_MINOR_EXCEPTIONS
    )
    forbidden = " ".join(definition.forbidden_behaviors)
    required = " ".join(definition.required_conditions)
    assert "Cambiar de objetivo o capacidad" in forbidden
    assert "alcance" in required
    assert definition.may_expand_scope is False


def test_m386_5_level_five_only_requests_and_never_grants_expansion() -> None:
    definition = governed_autonomy_stage(GovernedAutonomyStage.REQUEST_EXPANSION)
    assert definition.request_only is True
    assert definition.may_execute is False
    assert definition.may_expand_scope is False
    assert definition.runtime_level is AutonomyLevel.RECOMMEND


def test_m386_5_no_stage_grants_action_authority() -> None:
    assert all(not item.grants_action_authority for item in GOVERNED_AUTONOMY_STAGES)
    assert all(not item.may_expand_scope for item in GOVERNED_AUTONOMY_STAGES)


def test_m386_5_invalid_execution_stage_is_rejected_by_construction() -> None:
    definition = governed_autonomy_stage(
        GovernedAutonomyStage.EXECUTE_PREVALIDATED
    )
    with pytest.raises(ValueError, match="only stages three and four"):
        replace(
            definition,
            stage=GovernedAutonomyStage.RECOMMEND,
        )


def test_m386_5_revocation_conflict_or_high_risk_blocks_autonomy() -> None:
    policy = " ".join(AUTONOMY_GOVERNANCE_POLICY)
    assert "denegación, revocación o conflicto bloquea" in policy
    assert "altas, críticas, irreversibles" in policy
    assert "Carlos o Cristina" in policy


def test_m386_5_definitions_are_immutable_and_unknown_stage_is_rejected() -> None:
    definition = governed_autonomy_stage(GovernedAutonomyStage.INFORM)
    with pytest.raises(FrozenInstanceError):
        definition.title = "altered"
    with pytest.raises(ValueError):
        governed_autonomy_stage(99)
