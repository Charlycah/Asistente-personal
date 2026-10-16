from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    AutonomyLevel,
    CapabilityRunStatus,
    DecisionDisposition,
    DecisionPolicy,
    DeterministicFirstAutonomousCapabilityRunner,
    ObservationSeverity,
    OutcomeDirective,
    OutcomeStatus,
    RuntimeObservation,
    VerifyComponentHealthCapability,
    default_first_autonomous_capability_runner,
)
from core.executive_recovery_health import ComponentHealth, ComponentHealthState

NOW = datetime(2026, 7, 26, 21, 0, tzinfo=timezone.utc)


class HealthReader:
    def __init__(self, health: ComponentHealth) -> None:
        self.health = health
        self.calls: list[str] = []

    def get(self, component_id: str) -> ComponentHealth:
        self.calls.append(component_id)
        return self.health


class FailingHealthReader:
    def get(self, component_id: str) -> ComponentHealth:
        raise LookupError(component_id)


def health(state: ComponentHealthState) -> ComponentHealth:
    return ComponentHealth(
        component_id="audio",
        state=state,
        updated_at=NOW,
    )


def observation(
    kind: str = "component_health.degraded",
    *,
    component_id: str = "audio",
) -> RuntimeObservation:
    return RuntimeObservation(
        kind=kind,
        source="component_health.audio",
        observed_at=NOW,
        facts=(f"component_id={component_id}",),
        severity=ObservationSeverity.WARNING,
        confidence=1.0,
        attributes={"component_id": component_id},
        observation_id="observation-1",
    )


def policy(**changes: object) -> DecisionPolicy:
    base = DecisionPolicy(
        autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        minimum_confidence=0.5,
        simulation_mode=False,
    )
    return replace(base, **changes)


def runner(reader: object) -> DeterministicFirstAutonomousCapabilityRunner:
    return default_first_autonomous_capability_runner(reader)


def test_authorized_health_verification_executes_once() -> None:
    reader = HealthReader(health(ComponentHealthState.HEALTHY))

    result = runner(reader).run(observation(), policy())

    assert result.status is CapabilityRunStatus.EXECUTED
    assert reader.calls == ["audio"]
    assert result.candidate is not None
    assert result.candidate.action == "verify_component_health"


def test_healthy_component_produces_successful_outcome() -> None:
    result = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(),
    )

    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.SUCCEEDED
    assert "healthy" in result.outcome.summary
    assert result.supervision is not None
    assert result.supervision.directive is OutcomeDirective.COMPLETE


@pytest.mark.parametrize(
    "state",
    [
        ComponentHealthState.DEGRADED,
        ComponentHealthState.UNHEALTHY,
        ComponentHealthState.RECOVERING,
        ComponentHealthState.DISABLED,
    ],
)
def test_non_healthy_component_produces_degraded_outcome(
    state: ComponentHealthState,
) -> None:
    result = runner(HealthReader(health(state))).run(observation(), policy())

    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.DEGRADED
    assert result.supervision is not None
    assert result.supervision.directive is OutcomeDirective.DEGRADE
    assert result.supervision.notify_user is True


def test_unknown_component_health_produces_unknown_outcome() -> None:
    result = runner(HealthReader(health(ComponentHealthState.UNKNOWN))).run(
        observation(),
        policy(),
    )

    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.UNKNOWN
    assert result.supervision is not None
    assert result.supervision.notify_user is True


def test_reader_failure_becomes_failed_outcome() -> None:
    result = runner(FailingHealthReader()).run(observation(), policy())

    assert result.status is CapabilityRunStatus.EXECUTED
    assert result.outcome is not None
    assert result.outcome.status is OutcomeStatus.FAILED
    assert "LookupError" in result.outcome.evidence[1]
    assert result.supervision is not None
    assert result.supervision.directive is OutcomeDirective.REVERT


def test_recommendation_never_executes_capability() -> None:
    reader = HealthReader(health(ComponentHealthState.HEALTHY))

    result = runner(reader).run(
        observation(),
        policy(autonomy_level=AutonomyLevel.RECOMMEND),
    )

    assert result.status is CapabilityRunStatus.NOT_AUTHORIZED
    assert result.outcome is None
    assert result.supervision is None
    assert reader.calls == []


def test_simulation_never_executes_capability() -> None:
    reader = HealthReader(health(ComponentHealthState.HEALTHY))

    result = runner(reader).run(observation(), policy(simulation_mode=True))

    assert result.status is CapabilityRunStatus.NOT_AUTHORIZED
    assert result.orchestration.gate_evaluation is not None
    assert result.orchestration.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.SIMULATE
    )
    assert reader.calls == []


def test_no_situation_stops_before_capability() -> None:
    reader = HealthReader(health(ComponentHealthState.HEALTHY))

    result = runner(reader).run(observation("unknown.kind"), policy())

    assert result.status is CapabilityRunStatus.NO_SITUATION
    assert result.candidate is None
    assert result.outcome is None
    assert reader.calls == []


def test_outcome_references_governed_decision() -> None:
    result = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(),
    )

    assert result.outcome is not None
    assert result.orchestration.gate_evaluation is not None
    assert result.outcome.decision_id == (
        result.orchestration.gate_evaluation.gated_decision.decision_id
    )


def test_execution_preserves_component_evidence() -> None:
    result = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(component_id="audio"),
        policy(),
    )

    assert result.outcome is not None
    assert "component_id=audio" in result.outcome.evidence
    assert "health_state=healthy" in result.outcome.evidence


def test_missing_component_attribute_is_rejected_before_adapter_call() -> None:
    reader = HealthReader(health(ComponentHealthState.HEALTHY))
    invalid = replace(observation(), attributes={})

    with pytest.raises(ValueError, match="component id observation attribute"):
        runner(reader).run(invalid, policy())

    assert reader.calls == []


def test_capability_rejects_non_authorized_decision() -> None:
    normal = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(autonomy_level=AutonomyLevel.RECOMMEND),
    )
    assert normal.candidate is not None
    assert normal.orchestration.gate_evaluation is not None
    capability = VerifyComponentHealthCapability(
        HealthReader(health(ComponentHealthState.HEALTHY)),
        clock=lambda: NOW,
    )

    with pytest.raises(ValueError, match="requires authorization"):
        capability.execute(
            normal.orchestration.gate_evaluation.gated_decision,
            normal.candidate,
            "audio",
        )


def test_run_result_rejects_blank_run_id() -> None:
    result = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="capability run id"):
        replace(result, run_id=" ")


def test_run_result_rejects_empty_rationale() -> None:
    result = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="capability run rationale"):
        replace(result, rationale=())


def test_non_executed_result_rejects_outcome() -> None:
    blocked = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(autonomy_level=AutonomyLevel.RECOMMEND),
    )
    executed = runner(HealthReader(health(ComponentHealthState.HEALTHY))).run(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="non-executed"):
        replace(blocked, outcome=executed.outcome)


def test_first_capability_has_no_restart_or_mutation_methods() -> None:
    capability = VerifyComponentHealthCapability(
        HealthReader(health(ComponentHealthState.HEALTHY))
    )

    assert not hasattr(capability, "restart")
    assert not hasattr(capability, "recover")
    assert not hasattr(capability, "record_success")
    assert not hasattr(capability, "record_failure")
