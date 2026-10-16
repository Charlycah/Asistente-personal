from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Mapping, Protocol, runtime_checkable
from uuid import uuid4

from core.executive_event_model import EventPriority, ExecutiveEvent
from core.executive_recovery_health import ComponentHealth, ComponentHealthState

from .contracts import DecisionSituation


class ObservationSeverity(str, Enum):
    INFO = "info"
    NOTICE = "notice"
    WARNING = "warning"
    CRITICAL = "critical"


class AssessmentStatus(str, Enum):
    SITUATION_IDENTIFIED = "situation_identified"
    NO_SITUATION = "no_situation"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class RuntimeObservation:
    """Immutable runtime fact used to assess a possible situation."""

    kind: str
    source: str
    observed_at: datetime
    facts: tuple[str, ...]
    severity: ObservationSeverity | str = ObservationSeverity.INFO
    confidence: float = 1.0
    attributes: Mapping[str, str] = field(default_factory=dict)
    observation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.kind, "observation kind")
        _require_text(self.source, "observation source")
        _require_text(self.observation_id, "observation id")
        _require_items(self.facts, "observation facts")
        _require_aware(self.observed_at, "observation timestamp")
        _require_unit_interval(self.confidence, "observation confidence")
        object.__setattr__(self, "severity", ObservationSeverity(self.severity))
        normalized: dict[str, str] = {}
        for key, value in self.attributes.items():
            _require_text(key, "observation attribute name")
            _require_text(value, "observation attribute value")
            normalized[key.strip()] = value.strip()
        object.__setattr__(self, "attributes", normalized)


@dataclass(frozen=True)
class SituationRule:
    """Deterministic rule mapping one observation kind to a situation."""

    observation_kind: str
    situation_kind: str
    description: str
    minimum_severity: ObservationSeverity | str = ObservationSeverity.NOTICE
    minimum_confidence: float = 0.0
    base_urgency: float = 0.5
    rule_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.observation_kind, "rule observation kind")
        _require_text(self.situation_kind, "rule situation kind")
        _require_text(self.description, "rule description")
        _require_text(self.rule_id, "rule id")
        _require_unit_interval(self.minimum_confidence, "rule confidence")
        _require_unit_interval(self.base_urgency, "rule urgency")
        object.__setattr__(
            self,
            "minimum_severity",
            ObservationSeverity(self.minimum_severity),
        )


@dataclass(frozen=True)
class SituationAssessmentResult:
    status: AssessmentStatus | str
    observation: RuntimeObservation
    situation: DecisionSituation | None
    rationale: tuple[str, ...]
    matched_rule_id: str | None = None
    assessment_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.assessment_id, "assessment id")
        _require_items(self.rationale, "assessment rationale")
        status = AssessmentStatus(self.status)
        object.__setattr__(self, "status", status)
        if status is AssessmentStatus.SITUATION_IDENTIFIED:
            if self.situation is None or not _has_text(self.matched_rule_id):
                raise ValueError(
                    "identified assessment requires a situation and rule id"
                )
        elif self.situation is not None or self.matched_rule_id is not None:
            raise ValueError("non-identified assessment must not include a situation")


@runtime_checkable
class SituationAssessor(Protocol):
    def assess(
        self,
        observation: RuntimeObservation,
    ) -> SituationAssessmentResult: ...


class DeterministicSituationAssessor:
    """First-match deterministic assessor with no execution capability."""

    def __init__(self, rules: tuple[SituationRule, ...]) -> None:
        identifiers = [rule.rule_id for rule in rules]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("situation rule ids must be unique")
        self._rules = rules

    @property
    def rules(self) -> tuple[SituationRule, ...]:
        return self._rules

    def assess(
        self,
        observation: RuntimeObservation,
    ) -> SituationAssessmentResult:
        matching = tuple(
            rule for rule in self._rules if rule.observation_kind == observation.kind
        )
        if not matching:
            return SituationAssessmentResult(
                status=AssessmentStatus.UNSUPPORTED,
                observation=observation,
                situation=None,
                rationale=("no_rule_for_observation_kind",),
            )
        for rule in matching:
            if not _severity_at_least(
                observation.severity,
                rule.minimum_severity,
            ):
                continue
            if observation.confidence < rule.minimum_confidence:
                continue
            urgency = max(
                rule.base_urgency,
                _severity_urgency(observation.severity),
            )
            evidence = observation.facts + (
                f"observation_id={observation.observation_id}",
                f"rule_id={rule.rule_id}",
            )
            situation = DecisionSituation(
                kind=rule.situation_kind,
                description=rule.description,
                evidence=evidence,
                observed_at=observation.observed_at,
                source=observation.source,
                urgency=urgency,
            )
            return SituationAssessmentResult(
                status=AssessmentStatus.SITUATION_IDENTIFIED,
                observation=observation,
                situation=situation,
                rationale=(
                    "observation_matched_rule",
                    "thresholds_satisfied",
                ),
                matched_rule_id=rule.rule_id,
            )
        return SituationAssessmentResult(
            status=AssessmentStatus.NO_SITUATION,
            observation=observation,
            situation=None,
            rationale=("matching_rules_below_threshold",),
        )


def observation_from_executive_event(
    event: ExecutiveEvent,
) -> RuntimeObservation:
    severity = _event_severity(event.priority)
    facts = (
        f"event_id={event.event_id}",
        f"event_kind={event.kind.value}",
        f"event_priority={event.priority.name.lower()}",
    )
    return RuntimeObservation(
        kind=f"executive_event.{event.kind.value}",
        source=f"executive_event.{event.source.value}",
        observed_at=event.occurred_at,
        facts=facts,
        severity=severity,
        confidence=1.0,
        attributes={"event_id": event.event_id},
    )


def observation_from_component_health(
    health: ComponentHealth,
) -> RuntimeObservation:
    severity = _health_severity(health.state)
    facts = [
        f"component_id={health.component_id}",
        f"health_state={health.state.value}",
        f"consecutive_failures={health.consecutive_failures}",
        f"recovery_attempts={health.recovery_attempts}",
    ]
    if health.last_error:
        facts.append(f"last_error={health.last_error}")
    return RuntimeObservation(
        kind=f"component_health.{health.state.value}",
        source=f"component_health.{health.component_id}",
        observed_at=health.updated_at,
        facts=tuple(facts),
        severity=severity,
        confidence=1.0,
        attributes={"component_id": health.component_id},
    )


def default_situation_rules() -> tuple[SituationRule, ...]:
    return (
        SituationRule(
            observation_kind="audio_runtime.error",
            situation_kind="audio_runtime_requires_diagnosis",
            description="The local audio runtime reported an error",
            minimum_severity=ObservationSeverity.WARNING,
            base_urgency=0.7,
            rule_id="audio-runtime-error",
        ),
        SituationRule(
            observation_kind="component_health.degraded",
            situation_kind="runtime_component_degraded",
            description="A runtime component is operating in degraded mode",
            minimum_severity=ObservationSeverity.WARNING,
            base_urgency=0.6,
            rule_id="component-health-degraded",
        ),
        SituationRule(
            observation_kind="component_health.unhealthy",
            situation_kind="runtime_component_unhealthy",
            description="A runtime component is unhealthy",
            minimum_severity=ObservationSeverity.CRITICAL,
            base_urgency=0.9,
            rule_id="component-health-unhealthy",
        ),
        SituationRule(
            observation_kind="executive_event.battery_low",
            situation_kind="battery_requires_attention",
            description="Battery level requires executive attention",
            minimum_severity=ObservationSeverity.WARNING,
            base_urgency=0.7,
            rule_id="executive-battery-low",
        ),
        SituationRule(
            observation_kind="executive_event.reminder_due",
            situation_kind="reminder_requires_delivery",
            description="A due reminder requires delivery assessment",
            minimum_severity=ObservationSeverity.NOTICE,
            base_urgency=0.5,
            rule_id="executive-reminder-due",
        ),
    )


def _event_severity(priority: EventPriority) -> ObservationSeverity:
    if priority >= EventPriority.CRITICAL:
        return ObservationSeverity.CRITICAL
    if priority >= EventPriority.HIGH:
        return ObservationSeverity.WARNING
    if priority >= EventPriority.NORMAL:
        return ObservationSeverity.NOTICE
    return ObservationSeverity.INFO


def _health_severity(state: ComponentHealthState) -> ObservationSeverity:
    if state is ComponentHealthState.UNHEALTHY:
        return ObservationSeverity.CRITICAL
    if state is ComponentHealthState.DEGRADED:
        return ObservationSeverity.WARNING
    if state is ComponentHealthState.RECOVERING:
        return ObservationSeverity.NOTICE
    return ObservationSeverity.INFO


def _severity_urgency(severity: ObservationSeverity) -> float:
    return {
        ObservationSeverity.INFO: 0.1,
        ObservationSeverity.NOTICE: 0.4,
        ObservationSeverity.WARNING: 0.7,
        ObservationSeverity.CRITICAL: 1.0,
    }[severity]


def _severity_at_least(
    actual: ObservationSeverity,
    required: ObservationSeverity,
) -> bool:
    order = {
        ObservationSeverity.INFO: 0,
        ObservationSeverity.NOTICE: 1,
        ObservationSeverity.WARNING: 2,
        ObservationSeverity.CRITICAL: 3,
    }
    return order[actual] >= order[required]


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _require_text(value: str, name: str) -> None:
    if not value.strip():
        raise ValueError(f"{name} must not be blank")


def _require_items(values: tuple[str, ...], name: str) -> None:
    if not values or any(not item.strip() for item in values):
        raise ValueError(f"{name} must contain non-blank items")


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def _require_unit_interval(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
