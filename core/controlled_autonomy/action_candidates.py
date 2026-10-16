from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .contracts import ActionCandidate, DecisionSituation, Reversibility


class CandidateGenerationStatus(str, Enum):
    CANDIDATES_GENERATED = "candidates_generated"
    NO_CANDIDATES = "no_candidates"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class ActionTemplate:
    """Declarative action description; it contains no execution callable."""

    action: str
    description: str
    rationale: tuple[str, ...]
    reversible: Reversibility | str
    estimated_cost: float = 0.0

    def __post_init__(self) -> None:
        _require_text(self.action, "action template name")
        _require_text(self.description, "action template description")
        _require_items(self.rationale, "action template rationale")
        object.__setattr__(self, "reversible", Reversibility(self.reversible))
        if self.estimated_cost < 0.0:
            raise ValueError("action template estimated cost must not be negative")


@dataclass(frozen=True)
class CandidateRule:
    """Ordered templates applicable to one normalized situation kind."""

    situation_kind: str
    templates: tuple[ActionTemplate, ...]
    rule_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.situation_kind, "candidate rule situation kind")
        _require_text(self.rule_id, "candidate rule id")
        if not self.templates:
            raise ValueError("candidate rule must contain templates")
        actions = tuple(template.action for template in self.templates)
        if len(set(actions)) != len(actions):
            raise ValueError("candidate rule action names must be unique")


@dataclass(frozen=True)
class CandidateGenerationResult:
    status: CandidateGenerationStatus | str
    situation: DecisionSituation
    candidates: tuple[ActionCandidate, ...]
    rationale: tuple[str, ...]
    matched_rule_id: str | None = None
    generation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.generation_id, "candidate generation id")
        _require_items(self.rationale, "candidate generation rationale")
        status = CandidateGenerationStatus(self.status)
        object.__setattr__(self, "status", status)
        if status is CandidateGenerationStatus.CANDIDATES_GENERATED:
            if not self.candidates or not _has_text(self.matched_rule_id):
                raise ValueError(
                    "generated result requires candidates and a matched rule id"
                )
        elif self.candidates or self.matched_rule_id is not None:
            raise ValueError(
                "non-generated result must not contain candidates or a rule id"
            )
        identifiers = tuple(candidate.candidate_id for candidate in self.candidates)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("generated candidate ids must be unique")


@runtime_checkable
class ActionCandidateGenerator(Protocol):
    def generate(
        self,
        situation: DecisionSituation,
    ) -> CandidateGenerationResult: ...


class DeterministicActionCandidateGenerator:
    """First-match generator that only constructs immutable candidates."""

    def __init__(self, rules: tuple[CandidateRule, ...]) -> None:
        identifiers = tuple(rule.rule_id for rule in rules)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("candidate rule ids must be unique")
        kinds = tuple(rule.situation_kind for rule in rules)
        if len(set(kinds)) != len(kinds):
            raise ValueError("candidate situation kinds must be unique")
        self._rules = rules

    @property
    def rules(self) -> tuple[CandidateRule, ...]:
        return self._rules

    def generate(
        self,
        situation: DecisionSituation,
    ) -> CandidateGenerationResult:
        rule = next(
            (
                item
                for item in self._rules
                if item.situation_kind == situation.kind
            ),
            None,
        )
        if rule is None:
            return CandidateGenerationResult(
                status=CandidateGenerationStatus.UNSUPPORTED,
                situation=situation,
                candidates=(),
                rationale=("no_rule_for_situation_kind",),
            )
        candidates = tuple(
            _candidate_from_template(situation, rule, template, index)
            for index, template in enumerate(rule.templates, start=1)
        )
        if not candidates:
            return CandidateGenerationResult(
                status=CandidateGenerationStatus.NO_CANDIDATES,
                situation=situation,
                candidates=(),
                rationale=("matched_rule_produced_no_candidates",),
            )
        return CandidateGenerationResult(
            status=CandidateGenerationStatus.CANDIDATES_GENERATED,
            situation=situation,
            candidates=candidates,
            rationale=(
                "situation_matched_candidate_rule",
                "ordered_templates_materialized",
            ),
            matched_rule_id=rule.rule_id,
        )


def default_candidate_rules() -> tuple[CandidateRule, ...]:
    return (
        CandidateRule(
            situation_kind="runtime_component_degraded",
            templates=(
                _template(
                    "verify_component_health",
                    "Verify whether the degraded component has recovered",
                    "verification_before_intervention",
                    Reversibility.FULL,
                    0.1,
                ),
                _template(
                    "notify_user",
                    "Inform the user that a component is degraded",
                    "preserve_user_awareness",
                    Reversibility.FULL,
                    0.1,
                ),
                _template(
                    "do_nothing",
                    "Keep observing without changing runtime state",
                    "observation_is_a_valid_candidate",
                    Reversibility.FULL,
                    0.0,
                ),
            ),
            rule_id="component-degraded-candidates",
        ),
        CandidateRule(
            situation_kind="runtime_component_unhealthy",
            templates=(
                _template(
                    "restart_component",
                    "Restart the unhealthy runtime component",
                    "attempt_local_recovery",
                    Reversibility.PARTIAL,
                    0.3,
                ),
                _template(
                    "enter_degraded_mode",
                    "Keep the runtime available with reduced capability",
                    "preserve_partial_service",
                    Reversibility.FULL,
                    0.2,
                ),
                _template(
                    "notify_user",
                    "Inform the user that a component is unhealthy",
                    "preserve_user_awareness",
                    Reversibility.FULL,
                    0.1,
                ),
                _template(
                    "do_nothing",
                    "Keep observing without changing runtime state",
                    "observation_is_a_valid_candidate",
                    Reversibility.FULL,
                    0.0,
                ),
            ),
            rule_id="component-unhealthy-candidates",
        ),
        CandidateRule(
            situation_kind="battery_requires_attention",
            templates=(
                _template(
                    "notify_user",
                    "Inform the user that battery attention is required",
                    "preserve_user_awareness",
                    Reversibility.FULL,
                    0.1,
                ),
                _template(
                    "enable_power_saving",
                    "Request a power-saving operating profile",
                    "reduce_energy_consumption",
                    Reversibility.FULL,
                    0.2,
                ),
                _template(
                    "do_nothing",
                    "Keep observing without changing runtime state",
                    "observation_is_a_valid_candidate",
                    Reversibility.FULL,
                    0.0,
                ),
            ),
            rule_id="battery-attention-candidates",
        ),
        CandidateRule(
            situation_kind="reminder_requires_delivery",
            templates=(
                _template(
                    "deliver_reminder",
                    "Present the due reminder to the user",
                    "fulfil_due_reminder",
                    Reversibility.NONE,
                    0.1,
                ),
                _template(
                    "postpone_reminder",
                    "Defer reminder delivery for later assessment",
                    "allow_temporary_deferral",
                    Reversibility.FULL,
                    0.1,
                ),
                _template(
                    "do_nothing",
                    "Keep observing without changing runtime state",
                    "observation_is_a_valid_candidate",
                    Reversibility.FULL,
                    0.0,
                ),
            ),
            rule_id="reminder-delivery-candidates",
        ),
    )


def _candidate_from_template(
    situation: DecisionSituation,
    rule: CandidateRule,
    template: ActionTemplate,
    index: int,
) -> ActionCandidate:
    rationale = template.rationale + (
        f"situation_id={situation.situation_id}",
        f"candidate_rule_id={rule.rule_id}",
        f"candidate_order={index}",
    )
    return ActionCandidate(
        action=template.action,
        description=template.description,
        rationale=rationale,
        reversible=template.reversible,
        estimated_cost=template.estimated_cost,
        candidate_id=f"{situation.situation_id}:{rule.rule_id}:{index}",
    )


def _template(
    action: str,
    description: str,
    rationale: str,
    reversible: Reversibility,
    estimated_cost: float,
) -> ActionTemplate:
    return ActionTemplate(
        action=action,
        description=description,
        rationale=(rationale,),
        reversible=reversible,
        estimated_cost=estimated_cost,
    )


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")
