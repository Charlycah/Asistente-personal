from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    AssessmentStatus,
    AutonomyLevel,
    DecisionDisposition,
    DecisionPolicy,
    DeterministicControlledAutonomyOrchestrator,
    InMemoryDecisionJournal,
    ObservationSeverity,
    OrchestrationStatus,
    RuntimeObservation,
    default_controlled_autonomy_orchestrator,
)

NOW = datetime(2026, 7, 26, 20, 30, tzinfo=timezone.utc)


def observation(
    kind: str = "component_health.degraded",
    *,
    severity: ObservationSeverity = ObservationSeverity.WARNING,
    confidence: float = 1.0,
) -> RuntimeObservation:
    return RuntimeObservation(
        kind=kind,
        source="test.runtime",
        observed_at=NOW,
        facts=("component_id=audio",),
        severity=severity,
        confidence=confidence,
        observation_id="observation-1",
    )


def policy(**changes: object) -> DecisionPolicy:
    base = DecisionPolicy(
        autonomy_level=AutonomyLevel.RECOMMEND,
        simulation_mode=False,
    )
    return replace(base, **changes)


def test_default_orchestrator_completes_all_stages() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    assert result.status is OrchestrationStatus.COMPLETED
    assert result.assessment.status is AssessmentStatus.SITUATION_IDENTIFIED
    assert result.generation is not None
    assert result.risk_evaluation is not None
    assert result.policy_evaluation is not None
    assert result.gate_evaluation is not None
    assert result.journal_entry is not None


def test_completed_flow_journals_gated_decision() -> None:
    journal = InMemoryDecisionJournal()
    orchestrator = default_controlled_autonomy_orchestrator(journal=journal)

    result = orchestrator.orchestrate(observation(), policy())

    assert result.journal_entry is not None
    assert result.gate_evaluation is not None
    assert result.journal_entry.decision == result.gate_evaluation.gated_decision
    assert journal.entries() == (result.journal_entry,)


def test_pipeline_preserves_generated_candidates_and_assessments() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    assert result.generation is not None
    assert result.risk_evaluation is not None
    assert result.policy_evaluation is not None
    assert result.journal_entry is not None
    assert result.risk_evaluation.candidates == result.generation.candidates
    assert result.policy_evaluation.candidates == result.generation.candidates
    assert result.journal_entry.candidates == result.generation.candidates
    assert result.journal_entry.assessments == result.risk_evaluation.assessments


def test_recommend_policy_remains_recommendation_after_gate() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(autonomy_level=AutonomyLevel.RECOMMEND),
    )

    assert result.gate_evaluation is not None
    assert result.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.RECOMMEND
    )


def test_observe_only_policy_produces_observation() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(autonomy_level=AutonomyLevel.OBSERVE_ONLY),
    )

    assert result.gate_evaluation is not None
    assert result.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.OBSERVE
    )


def test_confirmation_policy_requests_confirmation() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(autonomy_level=AutonomyLevel.CONFIRM_BEFORE_ACTION),
    )

    assert result.gate_evaluation is not None
    assert result.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.REQUEST_CONFIRMATION
    )


def test_simulation_mode_precedes_recommendation() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(simulation_mode=True),
    )

    assert result.gate_evaluation is not None
    assert result.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.SIMULATE
    )


def test_autonomous_low_risk_can_authorize_default_degraded_candidate() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(
            autonomy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
            minimum_confidence=0.5,
        ),
    )

    assert result.gate_evaluation is not None
    assert result.gate_evaluation.gated_decision.disposition is (
        DecisionDisposition.AUTHORIZE
    )


def test_unsupported_observation_stops_after_assessment() -> None:
    journal = InMemoryDecisionJournal()
    result = default_controlled_autonomy_orchestrator(
        journal=journal
    ).orchestrate(observation("unknown.kind"), policy())

    assert result.status is OrchestrationStatus.NO_SITUATION
    assert result.assessment.status is AssessmentStatus.UNSUPPORTED
    assert result.generation is None
    assert result.risk_evaluation is None
    assert result.policy_evaluation is None
    assert result.gate_evaluation is None
    assert result.journal_entry is None
    assert journal.entries() == ()


def test_below_threshold_observation_stops_after_assessment() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(severity=ObservationSeverity.INFO),
        policy(),
    )

    assert result.status is OrchestrationStatus.NO_SITUATION
    assert result.assessment.status is AssessmentStatus.NO_SITUATION


def test_multiple_cycles_append_in_order() -> None:
    journal = InMemoryDecisionJournal()
    orchestrator = default_controlled_autonomy_orchestrator(journal=journal)

    first = orchestrator.orchestrate(observation(), policy())
    second = orchestrator.orchestrate(
        replace(observation(), observation_id="observation-2"),
        policy(),
    )

    assert first.journal_entry is not None
    assert second.journal_entry is not None
    assert journal.entries() == (first.journal_entry, second.journal_entry)


def test_orchestrator_exposes_injected_journal() -> None:
    journal = InMemoryDecisionJournal()
    orchestrator = default_controlled_autonomy_orchestrator(journal=journal)

    assert orchestrator.journal is journal


def test_result_rejects_blank_orchestration_id() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="orchestration id"):
        replace(result, orchestration_id=" ")


def test_result_rejects_empty_rationale() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="orchestration rationale"):
        replace(result, rationale=())


def test_no_situation_result_rejects_later_stage_data() -> None:
    completed = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )
    stopped = default_controlled_autonomy_orchestrator().orchestrate(
        observation("unknown.kind"),
        policy(),
    )

    with pytest.raises(ValueError, match="stop after assessment"):
        replace(stopped, generation=completed.generation)


def test_completed_result_requires_every_stage() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="every pipeline stage"):
        replace(result, gate_evaluation=None)


def test_completed_result_rejects_no_situation_assessment() -> None:
    completed = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )
    stopped = default_controlled_autonomy_orchestrator().orchestrate(
        observation("unknown.kind"),
        policy(),
    )

    with pytest.raises(ValueError, match="identified situation"):
        replace(completed, assessment=stopped.assessment)


def test_result_rejects_assessment_for_other_observation() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    with pytest.raises(ValueError, match="input observation"):
        replace(result, observation=replace(observation(), observation_id="other"))


def test_default_factory_uses_independent_journals() -> None:
    first = default_controlled_autonomy_orchestrator()
    second = default_controlled_autonomy_orchestrator()

    first.orchestrate(observation(), policy())

    assert len(first.journal.entries()) == 1
    assert second.journal.entries() == ()


def test_orchestrator_contains_no_execution_methods() -> None:
    forbidden = {
        "execute",
        "run_action",
        "retry",
        "revert",
        "notify",
        "restart",
    }

    assert forbidden.isdisjoint(dir(DeterministicControlledAutonomyOrchestrator))


def test_protocol_runtime_shape_is_satisfied() -> None:
    from core.controlled_autonomy import ControlledAutonomyOrchestrator

    orchestrator = default_controlled_autonomy_orchestrator()

    assert isinstance(orchestrator, ControlledAutonomyOrchestrator)


def test_result_status_accepts_string_value() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    rebuilt = replace(result, status="completed")

    assert rebuilt.status is OrchestrationStatus.COMPLETED


def test_journal_entry_has_no_outcome_before_execution() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    assert result.journal_entry is not None
    assert result.journal_entry.outcome is None


def test_policy_is_preserved_in_result() -> None:
    configured = policy(minimum_confidence=0.65, maximum_attempts=3)

    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        configured,
    )

    assert result.policy == configured


def test_selected_candidate_matches_gated_decision() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    assert result.gate_evaluation is not None
    selected = result.gate_evaluation.candidate
    assert selected is not None
    assert selected.candidate_id == result.gate_evaluation.gated_decision.candidate_id


def test_selected_assessment_matches_candidate() -> None:
    result = default_controlled_autonomy_orchestrator().orchestrate(
        observation(),
        policy(),
    )

    assert result.gate_evaluation is not None
    candidate = result.gate_evaluation.candidate
    assessment = result.gate_evaluation.assessment
    assert candidate is not None
    assert assessment is not None
    assert assessment.candidate_id == candidate.candidate_id


def test_journal_protocol_can_be_minimal_append_only_adapter() -> None:
    class CollectingJournal:
        def __init__(self) -> None:
            self.recorded = []

        def append(self, entry: object) -> None:
            self.recorded.append(entry)

        def entries(self) -> tuple[object, ...]:
            return tuple(self.recorded)

    journal = CollectingJournal()
    orchestrator = default_controlled_autonomy_orchestrator(journal=journal)

    result = orchestrator.orchestrate(observation(), policy())

    assert journal.entries() == (result.journal_entry,)


def test_constructor_accepts_explicit_validated_stage_dependencies() -> None:
    default = default_controlled_autonomy_orchestrator()
    orchestrator = DeterministicControlledAutonomyOrchestrator(
        assessor=default._assessor,
        candidate_generator=default._candidate_generator,
        risk_evaluator=default._risk_evaluator,
        policy_engine=default._policy_engine,
        autonomy_gate=default._autonomy_gate,
        journal=InMemoryDecisionJournal(),
    )

    assert orchestrator.orchestrate(observation(), policy()).status is (
        OrchestrationStatus.COMPLETED
    )
