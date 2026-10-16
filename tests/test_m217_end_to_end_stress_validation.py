from datetime import datetime, timezone

import pytest

from core.end_to_end_stress_validation import (
    EndToEndStressReport,
    EndToEndStressValidationRuntimeContributor,
    EndToEndStressValidator,
    StressScenario,
    StressScenarioResult,
    StressValidationStatus,
)
from core.llm_provider import LLMRequest
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m206_executive_arbitration import dependencies
from tests.test_m216_concurrent_cognitive_execution import concurrent_stack

NOW = datetime(2026, 7, 14, 21, 0, tzinfo=timezone.utc)


def stress_stack(**kwargs):
    *stack, executor = concurrent_stack(**kwargs)
    validator = EndToEndStressValidator(executor, max_cycles=32)
    return (*stack, executor, validator)


def test_default_validation_runs_bounded_end_to_end_profiles():
    *_, validator = stress_stack()
    report = validator.validate(owner="Carlos", session_id="main", now=NOW)
    assert report.total_cycles == 10
    assert tuple(item.name for item in report.scenarios) == (
        "nominal",
        "load_sweep",
        "recovery_probe",
    )


def test_nominal_profile_passes_without_failures():
    *_, validator = stress_stack(capacity=4)
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("nominal", (1, 2, 3)),),
        now=NOW,
    )
    assert report.status is StressValidationStatus.PASSED
    assert report.total_task_failures == 0


def test_saturated_profile_is_reported_as_degraded_when_blocked():
    *_, validator = stress_stack(capacity=1)
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("saturated", (4, 5)),),
        now=NOW,
    )
    assert report.status in {
        StressValidationStatus.DEGRADED,
        StressValidationStatus.FAILED,
    }
    assert report.scenarios[0].blocked >= 1


def test_injected_failure_is_isolated_and_counted():
    *_, validator = stress_stack()
    action = "maintain_cross_domain_alignment"
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("failure", (1,), (action,)),),
        now=NOW,
    )
    assert report.total_task_failures == 1
    assert report.status is StressValidationStatus.DEGRADED


def test_custom_handler_is_used_for_matching_action():
    *_, validator = stress_stack()
    action = "maintain_cross_domain_alignment"
    called = []
    validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("custom", (1,)),),
        handlers={action: lambda: called.append(action) or "ok"},
        now=NOW,
    )
    assert called == [action]


def test_validation_rejects_excessive_cycle_count():
    *_, executor = concurrent_stack()
    validator = EndToEndStressValidator(executor, max_cycles=2)
    with pytest.raises(ValueError, match="bounded cycle limit"):
        validator.validate(
            owner="Carlos",
            session_id="main",
            scenarios=(StressScenario("too_many", (1, 2, 3)),),
            now=NOW,
        )


def test_scenario_rejects_blank_name():
    with pytest.raises(ValueError, match="name"):
        StressScenario(" ", (1,))


def test_scenario_rejects_negative_demand():
    with pytest.raises(ValueError, match="non-negative"):
        StressScenario("bad", (-1,))


def test_result_requires_complete_cycle_accounting():
    with pytest.raises(ValueError, match="accounting"):
        StressScenarioResult("bad", 2, 1, 0, 0, 0, 0, 1, ())


def test_report_rejects_naive_timestamp():
    result = StressScenarioResult("ok", 1, 1, 0, 0, 0, 0, 1, ("source",))
    with pytest.raises(ValueError, match="timezone-aware"):
        EndToEndStressReport(
            "Carlos",
            "main",
            "passed",
            (result,),
            1,
            0,
            ("source",),
            datetime(2026, 1, 1),
        )


def test_report_identity_is_deterministic_for_same_inputs():
    *_, first_validator = stress_stack()
    *_, second_validator = stress_stack()
    *_, third_validator = stress_stack()
    scenario = (StressScenario("same", (1,)),)
    first = first_validator.validate(
        owner="Carlos", session_id="main", scenarios=scenario, now=NOW
    )
    second = second_validator.validate(
        owner="Carlos", session_id="other", scenarios=scenario, now=NOW
    )
    third = third_validator.validate(
        owner="Carlos", session_id="main", scenarios=scenario, now=NOW
    )
    assert first.report_id == third.report_id
    assert first.report_id != second.report_id


def test_runtime_contributor_publishes_stress_status():
    board, *_, validator = stress_stack()
    contribution = EndToEndStressValidationRuntimeContributor(
        validator, board
    ).contribute(
        owner="Carlos",
        session_id="main",
        text="valida",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert contribution.stage == "end_to_end_stress_validation"
    assert (
        board.snapshot(owner="Carlos", session_id="main", now=NOW).latest(
            "end_to_end_stress_validation"
        )
        is not None
    )


def test_official_composition_orders_m217_after_m216():
    (
        board,
        state,
        bus,
        domain_coordinator,
        scheduler,
        arbitrator,
        fusion,
        health,
        optimizer,
        integrator,
        framework,
        engine,
        recovery,
        high_load,
        monitor,
        executor,
        validator,
    ) = stress_stack()
    runtime = (
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                global_cognitive_state=state,
                cognitive_event_bus=bus,
                cross_domain_coordinator=domain_coordinator,
                unified_cognitive_scheduler=scheduler,
                executive_arbitrator=arbitrator,
                global_context_fusion=fusion,
                cognitive_health_monitor=health,
                cognitive_performance_optimizer=optimizer,
                whole_system_integrator=integrator,
                cognitive_resilience_framework=framework,
                graceful_degradation_engine=engine,
                fault_recovery_coordinator=recovery,
                high_load_cognitive_scheduler=high_load,
                long_running_stability_monitor=monitor,
                concurrent_cognitive_executor=executor,
                end_to_end_stress_validator=validator,
            )
        )
        .compose()
        .preparation.dependencies.cognitive_runtime
    )
    result = runtime.enrich(
        owner="Carlos",
        session_id="main",
        text="Integra M217",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    assert result.activated_stages[-2:] == (
        "concurrent_cognitive_execution",
        "end_to_end_stress_validation",
    )


def test_composition_requires_concurrent_execution():
    board, *_, validator = stress_stack()
    with pytest.raises(ValueError, match="requires concurrent execution"):
        RuntimeCompositionRoot(
            dependencies(
                unified_cognitive_blackboard=board,
                end_to_end_stress_validator=validator,
            )
        ).compose()


def test_validator_tracks_last_report():
    *_, validator = stress_stack()
    report = validator.validate(
        owner="Carlos",
        session_id="main",
        scenarios=(StressScenario("one", (1,)),),
        now=NOW,
    )
    assert validator.last_report is report


def test_validator_has_no_provider_or_infrastructure_mutation_api():
    *_, validator = stress_stack()
    assert not hasattr(validator, "restart_provider")
    assert not hasattr(validator, "scale_cluster")
    assert not hasattr(validator, "mutate_infrastructure")
