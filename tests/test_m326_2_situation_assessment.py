from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    AssessmentStatus,
    DeterministicSituationAssessor,
    ObservationSeverity,
    RuntimeObservation,
    SituationAssessor,
    SituationRule,
    default_situation_rules,
    observation_from_component_health,
    observation_from_executive_event,
)
from core.executive_event_model import (
    BatteryLowEvent,
    EventPriority,
    GenericTextEvent,
    ReminderDueEvent,
)
from core.executive_recovery_health import (
    ComponentHealth,
    ComponentHealthState,
)

NOW = datetime(2026, 7, 26, 20, 0, tzinfo=timezone.utc)


def observation(**changes: object) -> RuntimeObservation:
    values: dict[str, object] = {
        "kind": "audio_input_stalled",
        "source": "audio_health",
        "observed_at": NOW,
        "facts": ("process_alive", "no_transcriptions_20s"),
        "severity": ObservationSeverity.WARNING,
        "confidence": 0.9,
        "attributes": {"component_id": "vosk"},
        "observation_id": "observation-1",
    }
    values.update(changes)
    return RuntimeObservation(**values)


def rule(**changes: object) -> SituationRule:
    values: dict[str, object] = {
        "observation_kind": "audio_input_stalled",
        "situation_kind": "audio_input_requires_recovery",
        "description": "Audio input is alive but stalled",
        "minimum_severity": ObservationSeverity.WARNING,
        "minimum_confidence": 0.8,
        "base_urgency": 0.6,
        "rule_id": "audio-stalled",
    }
    values.update(changes)
    return SituationRule(**values)


@pytest.mark.parametrize(
    "field,value",
    (
        ("kind", ""),
        ("source", " "),
        ("observation_id", ""),
    ),
)
def test_observation_rejects_blank_identity(field, value):
    with pytest.raises(ValueError):
        observation(**{field: value})


def test_observation_requires_evidence():
    with pytest.raises(ValueError):
        observation(facts=())


def test_observation_requires_aware_timestamp():
    with pytest.raises(ValueError):
        observation(observed_at=datetime(2026, 7, 26, 20, 0))


@pytest.mark.parametrize("confidence", (-0.1, 1.1))
def test_observation_validates_confidence(confidence):
    with pytest.raises(ValueError):
        observation(confidence=confidence)


def test_observation_normalizes_severity_and_attributes():
    item = observation(severity="critical", attributes={" a ": " b "})
    assert item.severity is ObservationSeverity.CRITICAL
    assert item.attributes == {"a": "b"}


@pytest.mark.parametrize(
    "field",
    ("observation_kind", "situation_kind", "description", "rule_id"),
)
def test_rule_rejects_blank_required_text(field):
    with pytest.raises(ValueError):
        rule(**{field: ""})


@pytest.mark.parametrize(
    "field,value",
    (
        ("minimum_confidence", -0.1),
        ("minimum_confidence", 1.1),
        ("base_urgency", -0.1),
        ("base_urgency", 1.1),
    ),
)
def test_rule_validates_unit_intervals(field, value):
    with pytest.raises(ValueError):
        rule(**{field: value})


def test_assessor_satisfies_protocol():
    assessor = DeterministicSituationAssessor((rule(),))
    assert isinstance(assessor, SituationAssessor)


def test_assessor_rejects_duplicate_rule_ids():
    with pytest.raises(ValueError):
        DeterministicSituationAssessor((rule(), replace(rule(), description="x")))


def test_matching_observation_creates_decision_situation():
    result = DeterministicSituationAssessor((rule(),)).assess(observation())
    assert result.status is AssessmentStatus.SITUATION_IDENTIFIED
    assert result.situation is not None
    assert result.situation.kind == "audio_input_requires_recovery"
    assert result.situation.source == "audio_health"
    assert result.situation.observed_at == NOW
    assert "rule_id=audio-stalled" in result.situation.evidence


def test_critical_severity_raises_urgency_to_one():
    result = DeterministicSituationAssessor((rule(),)).assess(
        observation(severity="critical")
    )
    assert result.situation is not None
    assert result.situation.urgency == 1.0


def test_rule_base_urgency_is_preserved_when_higher():
    result = DeterministicSituationAssessor((rule(base_urgency=0.9),)).assess(
        observation()
    )
    assert result.situation is not None
    assert result.situation.urgency == 0.9


def test_low_severity_produces_no_situation():
    result = DeterministicSituationAssessor((rule(),)).assess(
        observation(severity="notice")
    )
    assert result.status is AssessmentStatus.NO_SITUATION
    assert result.situation is None


def test_low_confidence_produces_no_situation():
    result = DeterministicSituationAssessor((rule(),)).assess(
        observation(confidence=0.79)
    )
    assert result.status is AssessmentStatus.NO_SITUATION


def test_unknown_observation_kind_is_unsupported():
    result = DeterministicSituationAssessor((rule(),)).assess(
        observation(kind="unknown")
    )
    assert result.status is AssessmentStatus.UNSUPPORTED
    assert result.rationale == ("no_rule_for_observation_kind",)


def test_first_eligible_rule_wins_deterministically():
    second = rule(
        situation_kind="second",
        description="Second",
        rule_id="second",
    )
    result = DeterministicSituationAssessor((rule(), second)).assess(observation())
    assert result.matched_rule_id == "audio-stalled"


def test_result_rejects_identified_status_without_situation():
    with pytest.raises(ValueError):
        from core.controlled_autonomy import SituationAssessmentResult

        SituationAssessmentResult(
            status="situation_identified",
            observation=observation(),
            situation=None,
            rationale=("x",),
            matched_rule_id="rule",
        )


def test_event_adapter_preserves_traceability():
    event = BatteryLowEvent(
        battery_percent=9,
        priority=EventPriority.CRITICAL,
        occurred_at=NOW,
        event_id="battery-event",
    )
    item = observation_from_executive_event(event)
    assert item.kind == "executive_event.battery_low"
    assert item.source == "executive_event.battery"
    assert item.severity is ObservationSeverity.CRITICAL
    assert "event_id=battery-event" in item.facts


@pytest.mark.parametrize(
    "priority,severity",
    (
        (EventPriority.BACKGROUND, ObservationSeverity.INFO),
        (EventPriority.NORMAL, ObservationSeverity.NOTICE),
        (EventPriority.HIGH, ObservationSeverity.WARNING),
        (EventPriority.CRITICAL, ObservationSeverity.CRITICAL),
    ),
)
def test_event_adapter_maps_priority(priority, severity):
    event = GenericTextEvent(text="x", priority=priority, occurred_at=NOW)
    assert observation_from_executive_event(event).severity is severity


@pytest.mark.parametrize(
    "state,severity",
    (
        (ComponentHealthState.HEALTHY, ObservationSeverity.INFO),
        (ComponentHealthState.RECOVERING, ObservationSeverity.NOTICE),
        (ComponentHealthState.DEGRADED, ObservationSeverity.WARNING),
        (ComponentHealthState.UNHEALTHY, ObservationSeverity.CRITICAL),
    ),
)
def test_health_adapter_maps_state(state, severity):
    health = ComponentHealth(
        component_id="vosk",
        state=state,
        updated_at=NOW,
    )
    item = observation_from_component_health(health)
    assert item.severity is severity
    assert item.attributes["component_id"] == "vosk"


def test_health_adapter_includes_failure_evidence():
    health = ComponentHealth(
        component_id="vosk",
        state=ComponentHealthState.UNHEALTHY,
        consecutive_failures=3,
        recovery_attempts=2,
        last_error="no transcription",
        updated_at=NOW,
    )
    item = observation_from_component_health(health)
    assert "consecutive_failures=3" in item.facts
    assert "recovery_attempts=2" in item.facts
    assert "last_error=no transcription" in item.facts


def test_default_rules_assess_unhealthy_component():
    health = ComponentHealth(
        component_id="vosk",
        state=ComponentHealthState.UNHEALTHY,
        updated_at=NOW,
    )
    assessor = DeterministicSituationAssessor(default_situation_rules())
    result = assessor.assess(observation_from_component_health(health))
    assert result.status is AssessmentStatus.SITUATION_IDENTIFIED
    assert result.situation is not None
    assert result.situation.kind == "runtime_component_unhealthy"


def test_default_rules_assess_due_reminder():
    event = ReminderDueEvent(
        reminder_id="r1",
        title="Medication",
        occurred_at=NOW,
        priority=EventPriority.NORMAL,
    )
    assessor = DeterministicSituationAssessor(default_situation_rules())
    result = assessor.assess(observation_from_executive_event(event))
    assert result.status is AssessmentStatus.SITUATION_IDENTIFIED
    assert result.situation is not None
    assert result.situation.kind == "reminder_requires_delivery"


def test_healthy_component_does_not_match_default_rules():
    health = ComponentHealth(
        component_id="vosk",
        state=ComponentHealthState.HEALTHY,
        updated_at=NOW,
    )
    assessor = DeterministicSituationAssessor(default_situation_rules())
    result = assessor.assess(observation_from_component_health(health))
    assert result.status is AssessmentStatus.UNSUPPORTED


def test_assessment_never_generates_or_executes_action_candidates():
    result = DeterministicSituationAssessor((rule(),)).assess(observation())
    assert not hasattr(result, "candidates")
    assert not hasattr(result, "execute")
